# file: src/algorithm/backtracking_scheduler.py
from __future__ import annotations
from typing import List, Tuple, Optional
import time

from src.models import Defense, Person
from src.algorithm.scheduler import Schedule, ScheduleSlot, SchedulingConflict, SchedulingAlgorithm


class BacktrackingScheduler(SchedulingAlgorithm):
    """
    Any-time backtracking:
    - warm-start z PriorityGreedy (żeby nigdy nie być gorszym),
    - MRV: w każdym kroku wybieramy obronę z najmniejszą liczbą *aktualnie* dostępnych slotów,
    - min-conflicts dla przewodniczącego,
    - budżet: limit czasu i limit liczby odwiedzonych węzłów,
    - zrzut najlepszego częściowego rozwiązania i zwrot lepszego z (baseline, BT).
    """

    # --- ustawienia budżetu (możesz zmienić) ---
    TIME_LIMIT_SEC: float = 90.0         # limit czasu na przeszukiwanie
    NODE_LIMIT: int = 1_000_000          # górny limit liczby węzłów (prób umieszczeń)

    # ---------- API ----------
    def schedule(self, defenses: List[Defense]) -> Tuple[Schedule, List[SchedulingConflict]]:
        # 1) dwa baseline’y: simple i priority — bierzemy lepszy
        from .simple_scheduler import SimpleGreedyScheduler, PriorityGreedyScheduler

        simple_sched, simple_conf = SimpleGreedyScheduler(
            parameters=self.parameters,
            rooms=self.rooms,
            available_chairmen=self.available_chairmen
        ).schedule(defenses)

        priority_sched, priority_conf = PriorityGreedyScheduler(
            parameters=self.parameters,
            rooms=self.rooms,
            available_chairmen=self.available_chairmen
        ).schedule(defenses)

        def _score(s: Schedule) -> int:
            return len(s.get_scheduled_defenses())

        baseline_sched, baseline_conflicts = (
            (priority_sched, priority_conf)
            if _score(priority_sched) >= _score(simple_sched)
            else (simple_sched, simple_conf)
        )

        # 2) inicjalizacja BT (any-time)
        start = time.perf_counter()
        node_counter = 0
        empty = self.create_empty_schedule()

        remaining: List[Defense] = list(defenses)
        best_assignments: List[tuple[Defense, ScheduleSlot, Person]] = []
        best_count: int = 0

        self._bt(
            schedule=empty,
            remaining=remaining,
            start_time=start,
            node_counter_ref=[node_counter],
            best_ref=[best_count, best_assignments],
        )

        # 3) zbuduj schedule z najlepszego częściowego wyniku BT
        bt_sched = self.create_empty_schedule()
        for d, slot, chair in best_assignments:
            target = self._find_slot(bt_sched, slot.time_slot, slot.room)
            if target and target.is_free():
                bt_sched.add_defense(d, target, chair)

        # 4) zwróć lepsze z (baseline, BT)
        if _score(bt_sched) >= _score(baseline_sched):
            return bt_sched, self._conflicts_for_unplaced(defenses, bt_sched)
        else:
            return baseline_sched, baseline_conflicts

    # ---------- backtracking core ----------

    def _bt(self,
            schedule: Schedule,
            remaining: List[Defense],
            start_time: float,
            node_counter_ref: List[int],
            best_ref: List[object]) -> bool:
        """Zwraca True tylko gdy udało się umieścić WSZYSTKIE obrony przed upływem limitów."""
        # budżet
        if (time.perf_counter() - start_time) > self.TIME_LIMIT_SEC:
            return False
        if node_counter_ref[0] > self.NODE_LIMIT:
            return False

        # aktualizacja najlepszego częściowego
        placed_now = len(schedule.get_scheduled_defenses())
        if placed_now > best_ref[0]:
            best_ref[0] = placed_now
            best_ref[1].clear()
            # snapshot obecnych przypisań
            for sl in schedule.slots:
                if sl.defense and sl.defense.chairman:
                    best_ref[1].append((sl.defense, sl, sl.defense.chairman))

            # jeśli już mamy komplet – sukces globalny
            if placed_now == len(remaining) + placed_now:  # tautologia, ale zostawiamy czytelnie
                pass

        if not remaining:
            return True  # wszystko umieszczone

        # MRV: wybierz obronę o najmniejszej liczbie *aktualnie* dopuszczalnych slotów
        idx, defense, domain = self._pick_mrv_defense(remaining, schedule)

        # jeśli brak dopuszczalnych slotów – ślepa uliczka
        if not domain:
            return False

        # spróbuj każdy slot z uporządkowanej domeny
        for slot in domain:
            node_counter_ref[0] += 1
            chair = self._pick_chairman_min_conflicts(defense, slot, schedule)
            if not chair:
                continue

            schedule.add_defense(defense, slot, chair)

            # rekurencja z listą bez wybranej obrony
            new_remaining = remaining[:idx] + remaining[idx+1:]
            if self._bt(schedule, new_remaining, start_time, node_counter_ref, best_ref):
                return True

            schedule.remove_defense(defense)

        return False

    # ---------- heurystyki / pomocnicze ----------

    def _feasible_slots(self, defense: Defense, schedule: Schedule) -> List[ScheduleSlot]:
        feas: List[ScheduleSlot] = []
        for slot in schedule.get_free_slots():
            ok, _ = self.can_schedule_defense(defense, slot, schedule)
            if ok:
                feas.append(slot)
        # porządek: najwcześniejsze najpierw (stabilniejsze wyniki)
        feas.sort(key=lambda s: (s.time_slot.start, s.room.number))
        return feas

    def _pick_mrv_defense(self, remaining: List[Defense], schedule: Schedule):
        """Zwraca (index, defense, domena_slotów) – defense z najmniejszą domeną."""
        best_i = 0
        best_d = remaining[0]
        best_domain = self._feasible_slots(best_d, schedule)

        for i in range(1, len(remaining)):
            d = remaining[i]
            dom = self._feasible_slots(d, schedule)
            if (not best_domain) or (dom and len(dom) < len(best_domain)):
                best_i, best_d, best_domain = i, d, dom
        return best_i, best_d, best_domain

    def _chairman_candidates(self, defense: Defense) -> List[Person]:
        """Preferuj osoby spoza komisji; dopuszczaj promotora/recenzenta gdy trzeba."""
        sup = defense.supervisor.email
        rev = defense.reviewer.email
        cands = list(self.available_chairmen)
        cands.sort(key=lambda p: (p.email in (sup, rev), p.email))  # spoza komisji najpierw
        return cands

    def _pick_chairman_min_conflicts(self, defense: Defense, slot: ScheduleSlot, schedule: Schedule) -> Optional[Person]:
        """Wybierz przewodniczącego z minimalnym 'konfliktem w przyszłości' (min-conflicts)."""
        best: Optional[Person] = None
        best_score = float("inf")
        scheduled = schedule.get_scheduled_defenses()

        for cand in self._chairman_candidates(defense):
            # czy dostępny teraz?
            if self.conflict_checker.check_person_availability(cand, slot.time_slot, scheduled) is not None:
                continue

            # policz "przyszłe konflikty": w ilu slotach mógłby on jeszcze pracować
            score = 0
            for other_slot in schedule.get_free_slots():
                # liczymy tylko sloty, które nie kolidują czasowo
                if other_slot.time_slot == slot.time_slot:
                    continue
                if self.conflict_checker.check_person_availability(cand, other_slot.time_slot, scheduled) is not None:
                    score += 1  # im większy score, tym gorzej

            if score < best_score:
                best_score = score
                best = cand

        return best

    def _find_slot(self, schedule: Schedule, time_slot, room) -> Optional[ScheduleSlot]:
        for s in schedule.slots:
            if s.time_slot == time_slot and s.room == room:
                return s
        return None

    def _conflicts_for_unplaced(self, all_defenses: List[Defense], schedule: Schedule) -> List[SchedulingConflict]:
        # zamiast set(defense) użyj set(id(defense)) – obiekty Defense są niehashowalne
        placed_ids = {id(d) for d in schedule.get_scheduled_defenses()}
        ret: List[SchedulingConflict] = []
        for d in all_defenses:
            if id(d) not in placed_ids:
                ret.append(SchedulingConflict(f"Could not schedule defense for {d.student_name}", defense=d))
        return ret
