from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
from collections import defaultdict

from src.models import Defense, Person
from src.algorithm.scheduler import Schedule, ScheduleSlot, SchedulingAlgorithm


@dataclass
class OptimizationWeights:
    """Wagi funkcji celu."""
    gap_weight: float = 1.0        # kara za przerwy (idle) w salach i u osób
    group_weight: float = 1.0      # bonus (ujemna kara) za ciągłość osób między kolejnymi slotami
    span_weight: float = 0.5       # kara za całkowitą rozpiętość sesji
    chair_block_weight: float = 1.0  # dodatkowy bonus za ciągłe bloki pracy przewodniczącego


class ScheduleOptimizer:
    """
    Prosty optymalizator lokalny:
    - wykonuje ruchy SWAP (zamiana slotów) i MOVE (przeniesienie obrony do wolnego slotu),
    - akceptuje ruchy, które obniżają koszt (mniej przerw, lepsze grupowanie, krótsza sesja),
    - sprawdza feasibility przez SchedulingAlgorithm.can_schedule_defense() oraz dobiera przewodniczącego.
    """

    def __init__(self, weights: OptimizationWeights = OptimizationWeights()):
        self.w = weights

    # ----------------- Public API -----------------

    def optimize(self, algo: SchedulingAlgorithm, schedule: Schedule, max_iters: int = 300) -> Schedule:
        best_cost = self._cost(schedule)
        all_slots = [s for s in schedule.slots if s.time_slot]

        for _ in range(max_iters):
            improved = False

            # 1) SWAP — zamiana dwóch slotów (również z pustym)
            for i in range(len(all_slots)):
                for j in range(i + 1, len(all_slots)):
                    if self._try_swap(algo, schedule, all_slots[i], all_slots[j]):
                        c = self._cost(schedule)
                        if c < best_cost:
                            best_cost = c
                            improved = True
                        else:
                            # cofnięcie — swap z powrotem bez checków
                            self._try_swap(algo, schedule, all_slots[i], all_slots[j], revert_only=True)

            # 2) MOVE — przeniesienie obrony do lepszego wolnego slotu
            free_slots = [s for s in all_slots if s.is_free()]
            if free_slots:
                for src in all_slots:
                    if not src.defense:
                        continue
                    moved_ok = False
                    for dst in free_slots:
                        if dst is src or not dst.is_free():
                            continue
                        if self._try_move(algo, schedule, src, dst):
                            c = self._cost(schedule)
                            if c < best_cost:
                                best_cost = c
                                improved = True
                                moved_ok = True
                                break
                            else:
                                # cofnięcie
                                self._try_move(algo, schedule, dst, src)
                    if moved_ok:
                        break

            if not improved:
                break  # lokalne optimum

            # pętla idzie dalej, dopóki znajdujemy ulepszenia

        return schedule

    # ----------------- Ruchy -----------------

    def _try_swap(self, algo: SchedulingAlgorithm, schedule: Schedule,
                  a: ScheduleSlot, b: ScheduleSlot, revert_only: bool = False) -> bool:
        da, db = a.defense, b.defense

        if revert_only:
            a.defense, b.defense = db, da
            if a.defense:
                a.defense.time_slot, a.defense.room = a.time_slot, a.room
            if b.defense:
                b.defense.time_slot, b.defense.room = b.time_slot, b.room
            return True

        if not da and not db:
            return False

        chair_a = da.chairman if da else None
        chair_b = db.chairman if db else None

        # 1) zdejmij
        a.defense = None
        if da:
            da.time_slot = None; da.room = None; da.chairman = None
        b.defense = None
        if db:
            db.time_slot = None; db.room = None; db.chairman = None

        # 2) feasibility po zamianie
        if da:
            can_a, _ = algo.can_schedule_defense(da, b, schedule)
            if not can_a:
                # revert
                a.defense = da; b.defense = db
                if da: da.time_slot, da.room, da.chairman = a.time_slot, a.room, chair_a
                if db: db.time_slot, db.room, db.chairman = b.time_slot, b.room, chair_b
                return False

        if db:
            can_b, _ = algo.can_schedule_defense(db, a, schedule)
            if not can_b:
                # revert
                a.defense = da; b.defense = db
                if da: da.time_slot, da.room, da.chairman = a.time_slot, a.room, chair_a
                if db: db.time_slot, db.room, db.chairman = b.time_slot, b.room, chair_b
                return False

        # 3) wstaw da -> b z nowym przewodniczącym
        if da:
            chair = algo.find_available_chairman(b.time_slot, schedule.get_scheduled_defenses())
            if not chair:
                a.defense = da; b.defense = db
                da.time_slot, da.room, da.chairman = a.time_slot, a.room, chair_a
                if db: db.time_slot, db.room, db.chairman = b.time_slot, b.room, chair_b
                return False
            schedule.add_defense(da, b, chair)

        # 4) wstaw db -> a
        if db:
            chair = algo.find_available_chairman(a.time_slot, schedule.get_scheduled_defenses())
            if not chair:
                # zdejmij da z b (przed chwilą dodany)
                if b.defense is da:
                    b.defense = None
                    da.time_slot = None; da.room = None; da.chairman = None
                a.defense = da; b.defense = db
                if da: da.time_slot, da.room, da.chairman = a.time_slot, a.room, chair_a
                if db: db.time_slot, db.room, db.chairman = b.time_slot, b.room, chair_b
                return False
            schedule.add_defense(db, a, chair)

        return True

    def _try_move(self, algo: SchedulingAlgorithm, schedule: Schedule,
                  src: ScheduleSlot, dst: ScheduleSlot) -> bool:
        if not src.defense or not dst.is_free():
            return False

        d = src.defense
        old_chair = d.chairman

        # zdejmij z obecnego slotu
        src.defense = None
        d.time_slot = None; d.room = None; d.chairman = None

        can, _ = algo.can_schedule_defense(d, dst, schedule)
        if not can:
            # revert
            src.defense = d
            d.time_slot, d.room, d.chairman = src.time_slot, src.room, old_chair
            return False

        chair = algo.find_available_chairman(dst.time_slot, schedule.get_scheduled_defenses())
        if not chair:
            src.defense = d
            d.time_slot, d.room, d.chairman = src.time_slot, src.room, old_chair
            return False

        schedule.add_defense(d, dst, chair)
        return True

    # ----------------- Funkcja kosztu -----------------

    def _cost(self, schedule: Schedule) -> float:
        used = [s for s in schedule.slots if s.defense]
        if not used:
            return 10_000.0

        gap_penalty = self._gap_penalty(schedule)
        group_bonus = self._group_bonus(schedule)              # ujemna kara
        chair_bonus = self._chairman_block_bonus(schedule)     # ujemna kara
        span_penalty = self._span_penalty(schedule)

        return (
            self.w.gap_weight * gap_penalty +
            self.w.group_weight * group_bonus +
            self.w.chair_block_weight * chair_bonus +
            self.w.span_weight * span_penalty
        )

    def _gap_penalty(self, schedule: Schedule) -> float:
        """Sumuje przerwy (minuty) w liniach czasu: per sala oraz per osoba."""
        def timeline_gaps(slots: List[ScheduleSlot]) -> float:
            if len(slots) < 2:
                return 0.0
            slots.sort(key=lambda s: s.time_slot.start)
            g = 0.0
            for a, b in zip(slots, slots[1:]):
                diff = (b.time_slot.start - a.time_slot.end).total_seconds() / 60.0
                if diff > 0:
                    g += diff
            return g

        penalty = 0.0
        by_room: Dict[str, List[ScheduleSlot]] = defaultdict(list)
        by_person: Dict[str, List[ScheduleSlot]] = defaultdict(list)

        for s in schedule.slots:
            if not s.defense:
                continue
            by_room[s.room.number].append(s)
            for p in s.defense.get_committee():
                key = getattr(p, "email", str(id(p)))
                by_person[key].append(s)

        for slots in by_room.values():
            penalty += timeline_gaps(slots)
        for slots in by_person.values():
            penalty += timeline_gaps(slots)

        return penalty

    def _group_bonus(self, schedule: Schedule) -> float:
        """
        Bonus (ujemna kara) za to, że ci sami ludzie pojawiają się w kolejnych „turach” (ten sam start).
        Zwiększa szansę na grupowanie komisji/superwizorów/reviewerów.
        """
        buckets = defaultdict(list)  # start -> [sloty]
        for s in schedule.slots:
            if s.defense:
                buckets[s.time_slot.start].append(s)

        times = sorted(buckets.keys())

        def people_emails(slots: List[ScheduleSlot]) -> set[str]:
            emails = set()
            for sl in slots:
                for p in sl.defense.get_committee():
                    emails.add(getattr(p, "email", str(id(p))))
            return emails

        bonus = 0.0
        for i in range(1, len(times)):
            prev = people_emails(buckets[times[i - 1]])
            cur = people_emails(buckets[times[i]])
            overlap = len(prev & cur)
            if overlap:
                bonus -= overlap * 0.5
        return bonus

    def _chairman_block_bonus(self, schedule: Schedule) -> float:
        """
        Dodatkowy bonus (ujemna kara) za długie ciągłe bloki pracy przewodniczących.
        Motywuje do „obsadzania” sali przewodniczącym bez dziur.
        """
        # zbuduj linię czasu dla każdego przewodniczącego
        by_chair = defaultdict(list)  # email przewodniczącego -> [sloty]
        for s in schedule.slots:
            if s.defense and s.defense.chairman:
                email = getattr(s.defense.chairman, "email", str(id(s.defense.chairman)))
                by_chair[email].append(s)

        bonus = 0.0
        for slots in by_chair.values():
            slots.sort(key=lambda s: s.time_slot.start)
            # sumuj długości ciągłych „ciągów” bez przerw
            chain_len = 1
            for a, b in zip(slots, slots[1:]):
                contiguous = (a.time_slot.end == b.time_slot.start) and (a.room == b.room)
                if contiguous:
                    chain_len += 1
                else:
                    if chain_len > 1:
                        bonus -= (chain_len - 1) * 0.75  # im dłuższy ciąg, tym większy bonus
                    chain_len = 1
            if chain_len > 1:
                bonus -= (chain_len - 1) * 0.75
        return bonus

    def _span_penalty(self, schedule: Schedule) -> float:
        """Kara za całkowitą rozpiętość sesji w minutach (pierwszy start -> ostatni koniec)."""
        used = [s for s in schedule.slots if s.defense]
        first = min(s.time_slot.start for s in used)
        last = max(s.time_slot.end for s in used)
        return (last - first).total_seconds() / 60.0
