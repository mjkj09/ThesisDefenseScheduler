import csv
import json
from typing import List
from src.algorithm import Schedule
from src.models.defense import Defense
from fpdf import FPDF
import os

class ScheduleExporter:
    @staticmethod
    def export_to_csv(schedule: Schedule, filepath: str) -> None:
        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Student', 'Thesis Title', 'Supervisor', 'Reviewer', 'Chairman', 'Room', 'Time Slot'])

            for slot in schedule.slots:
                if slot.defense:
                    defense = slot.defense
                    writer.writerow([
                        defense.student_name,
                        defense.thesis_title,
                        defense.supervisor.name,
                        defense.reviewer.name,
                        defense.chairman.name if defense.chairman else '',
                        slot.room.name,
                        str(slot.time_slot)
                    ])

    @staticmethod
    def export_to_json(schedule: Schedule, filepath: str) -> None:
        data = []
        for slot in schedule.slots:
            if slot.defense:
                defense = slot.defense
                data.append({
                    'student': defense.student_name,
                    'thesis_title': defense.thesis_title,
                    'supervisor': defense.supervisor.name,
                    'reviewer': defense.reviewer.name,
                    'chairman': defense.chairman.name if defense.chairman else '',
                    'room': slot.room.name,
                    'time_slot': str(slot.time_slot)
                })

        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    @staticmethod
    def export_to_pdf(schedule, filepath: str) -> None:
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            # Czcionka Unicode
            font_path = os.path.join(os.path.dirname(__file__), "fonts", "NotoSans-Regular.ttf")
            pdf.add_font("NotoSans", "", font_path, uni=True)
            pdf.set_font("NotoSans", "", 14)

            # Marginesy i szerokość strony
            left_margin = 10
            right_margin = 10
            page_width = pdf.w
            usable_width = page_width - left_margin - right_margin

            # Nagłówek
            pdf.set_x(left_margin)
            pdf.cell(usable_width, 10, "Thesis Defense Schedule", ln=True, align='C')
            pdf.ln(8)

            pdf.set_font("NotoSans", "", 10)

            for i, slot in enumerate(schedule.slots, start=1):
                if slot.defense:
                    d = slot.defense

                    # Linia
                    pdf.set_draw_color(200, 200, 200)
                    y = pdf.get_y()
                    pdf.line(left_margin, y, page_width - right_margin, y)
                    pdf.ln(4)

                    pdf.set_x(left_margin)
                    pdf.cell(usable_width, 8, f"{i}. {slot.time_slot}   |   Room: {slot.room.name}", ln=True)

                    pdf.set_x(left_margin)
                    pdf.multi_cell(usable_width, 6, f"Student: {d.student_name}")

                    pdf.set_x(left_margin)
                    pdf.multi_cell(usable_width, 6, f"Thesis: {d.thesis_title}")

                    pdf.set_x(left_margin)
                    pdf.multi_cell(usable_width, 6,
                        f"Supervisor: {d.supervisor.name}\n"
                        f"Reviewer: {d.reviewer.name}\n"
                        f"Chairman: {d.chairman.name if d.chairman else '—'}"
                    )

                    pdf.ln(6)

            pdf.output(filepath)
        
        except Exception as e:
            # Dodaj ten print, by złapać dokładny błąd
            print("Export to PDF failed:", e)
            raise e