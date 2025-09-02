import tkinter as tk
from datetime import datetime, date, time
from tkinter import ttk, messagebox, simpledialog

from src.models.time_slot import TimeSlot


class SessionParametersDialog:
    """Dialog for editing session parameters (with real breaks support)."""

    def __init__(self, parent, parameters=None):
        self.result = None
        self.parameters = parameters

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Session Parameters")
        self.dialog.geometry("450x480")
        self.dialog.resizable(False, False)

        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_widgets()
        if parameters:
            self._load_data()
        else:
            self.breaks = []  # List[TimeSlot]

    def _create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Session date
        ttk.Label(main_frame, text="Session Date:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(main_frame, textvariable=self.date_var, width=15).grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)

        # Start time
        ttk.Label(main_frame, text="Start Time:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.start_time_var = tk.StringVar(value="09:00")
        ttk.Entry(main_frame, textvariable=self.start_time_var, width=10).grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)

        # End time
        ttk.Label(main_frame, text="End Time:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.end_time_var = tk.StringVar(value="17:00")
        ttk.Entry(main_frame, textvariable=self.end_time_var, width=10).grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)

        # Defense duration
        ttk.Label(main_frame, text="Defense Duration (minutes):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.duration_var = tk.IntVar(value=30)
        ttk.Spinbox(main_frame, from_=15, to=90, textvariable=self.duration_var,
                    width=10, increment=5).grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)

        # Number of rooms
        ttk.Label(main_frame, text="Number of Rooms:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.rooms_var = tk.IntVar(value=1)
        ttk.Spinbox(main_frame, from_=1, to=5, textvariable=self.rooms_var,
                    width=10).grid(row=4, column=1, pady=5, padx=5, sticky=tk.W)

        # Breaks section
        breaks_label = ttk.Label(main_frame, text="Breaks:", font=('Arial', 10, 'bold'))
        breaks_label.grid(row=5, column=0, columnspan=2, pady=(15, 5))

        breaks_frame = ttk.Frame(main_frame)
        breaks_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.breaks_listbox = tk.Listbox(breaks_frame, height=6)
        self.breaks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        breaks_buttons = ttk.Frame(breaks_frame)
        breaks_buttons.pack(side=tk.RIGHT, padx=5)
        ttk.Button(breaks_buttons, text="Add", command=self._add_break).pack(pady=2)
        ttk.Button(breaks_buttons, text="Remove", command=self._remove_break).pack(pady=2)

        # Bottom buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)

        self.breaks = []  # List[TimeSlot]

    def _add_break(self):
        """Add a break period (HH:MM → HH:MM)."""
        try:
            start_str = simpledialog.askstring("Add Break", "Start (HH:MM):", parent=self.dialog)
            if not start_str:
                return
            end_str = simpledialog.askstring("Add Break", "End (HH:MM):", parent=self.dialog)
            if not end_str:
                return

            s_h, s_m = map(int, start_str.split(":"))
            e_h, e_m = map(int, end_str.split(":"))

            dt = datetime.strptime(self.date_var.get(), "%Y-%m-%d").date()
            start_dt = datetime.combine(dt, time(s_h, s_m))
            end_dt = datetime.combine(dt, time(e_h, e_m))

            slot = TimeSlot(start=start_dt, end=end_dt)

            # Check overlap with existing breaks
            for b in self.breaks:
                if slot.overlaps_with(b):
                    messagebox.showerror("Error", "Break overlaps with existing break.")
                    return

            self.breaks.append(slot)
            self._refresh_breaks_listbox()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid break time: {e}")

    def _remove_break(self):
        """Remove selected break."""
        selection = self.breaks_listbox.curselection()
        if selection:
            idx = selection[0]
            del self.breaks[idx]
            self._refresh_breaks_listbox()

    def _refresh_breaks_listbox(self):
        self.breaks_listbox.delete(0, tk.END)
        for b in sorted(self.breaks, key=lambda x: x.start):
            self.breaks_listbox.insert(tk.END, f"{b.start.strftime('%H:%M')} - {b.end.strftime('%H:%M')}")

    def _load_data(self):
        """Load existing parameters."""
        if self.parameters:
            self.date_var.set(self.parameters.session_date.strftime("%Y-%m-%d"))
            self.start_time_var.set(self.parameters.start_time)
            self.end_time_var.set(self.parameters.end_time)
            self.duration_var.set(self.parameters.defense_duration)
            self.rooms_var.set(self.parameters.room_count)
            self.breaks = list(self.parameters.breaks or [])
            self._refresh_breaks_listbox()

    def _ok_clicked(self):
        """Save parameters and close."""
        try:
            from src.models.session_parameters import SessionParameters

            # Parse date
            session_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d").date()

            # Rebase existing breaks to selected date (keep hours/minutes)
            rebased_breaks: list[TimeSlot] = []
            for b in self.breaks:
                s_time = time(b.start.hour, b.start.minute)
                e_time = time(b.end.hour, b.end.minute)
                s_dt = datetime.combine(session_date, s_time)
                e_dt = datetime.combine(session_date, e_time)
                rebased_breaks.append(TimeSlot(start=s_dt, end=e_dt))

            # Create parameters object
            self.result = SessionParameters(
                session_date=session_date,
                start_time=self.start_time_var.get(),
                end_time=self.end_time_var.get(),
                defense_duration=self.duration_var.get(),
                room_count=self.rooms_var.get(),
                breaks=rebased_breaks
            )
            self.dialog.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))
