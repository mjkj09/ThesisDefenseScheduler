import tkinter as tk
from datetime import datetime, date, time
from tkinter import ttk, messagebox


class AvailabilityDialog:
    """Dialog for managing person availability."""

    def __init__(self, parent, person, session_date=None):
        self.person = person
        self.session_date = session_date or date.today()
        self.unavailable_slots = person.unavailable_slots.copy()

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Availability - {person.name}")
        self.dialog.geometry("600x500")

        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_widgets()
        self._refresh_slots_list()

    def _create_widgets(self):
        # Header
        header = ttk.Label(self.dialog, text=f"Mark unavailable times for {self.person.name}",
                           font=('Arial', 12, 'bold'))
        header.pack(pady=10)

        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Time slot entry
        left_frame = ttk.LabelFrame(main_frame, text="Add Unavailable Time", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Date
        ttk.Label(left_frame, text="Date:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar(value=self.session_date.strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(left_frame, textvariable=self.date_var, width=15)
        date_entry.grid(row=0, column=1, pady=5, padx=5)

        # Start time
        ttk.Label(left_frame, text="Start Time:").grid(row=1, column=0, sticky=tk.W, pady=5)
        time_frame_start = ttk.Frame(left_frame)
        time_frame_start.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)

        self.start_hour = ttk.Spinbox(time_frame_start, from_=0, to=23, width=3, format="%02.0f")
        self.start_hour.set("09")
        self.start_hour.pack(side=tk.LEFT)
        ttk.Label(time_frame_start, text=":").pack(side=tk.LEFT)
        self.start_min = ttk.Spinbox(time_frame_start, from_=0, to=59, width=3, format="%02.0f", increment=15)
        self.start_min.set("00")
        self.start_min.pack(side=tk.LEFT)

        # End time
        ttk.Label(left_frame, text="End Time:").grid(row=2, column=0, sticky=tk.W, pady=5)
        time_frame_end = ttk.Frame(left_frame)
        time_frame_end.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)

        self.end_hour = ttk.Spinbox(time_frame_end, from_=0, to=23, width=3, format="%02.0f")
        self.end_hour.set("10")
        self.end_hour.pack(side=tk.LEFT)
        ttk.Label(time_frame_end, text=":").pack(side=tk.LEFT)
        self.end_min = ttk.Spinbox(time_frame_end, from_=0, to=59, width=3, format="%02.0f", increment=15)
        self.end_min.set("00")
        self.end_min.pack(side=tk.LEFT)

        # Add button
        ttk.Button(left_frame, text="Add Unavailable Slot",
                   command=self._add_slot).grid(row=3, column=0, columnspan=2, pady=20)

        # Right panel - List of unavailable slots
        right_frame = ttk.LabelFrame(main_frame, text="Unavailable Times", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Listbox with scrollbar
        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.slots_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.slots_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.slots_listbox.yview)

        # Remove button
        ttk.Button(right_frame, text="Remove Selected",
                   command=self._remove_slot).pack(pady=10)

        # Bottom buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Save", command=self._save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)

    def _add_slot(self):
        """Add unavailable time slot."""
        try:
            # Parse date and times
            date_str = self.date_var.get()
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

            start_h = int(self.start_hour.get())
            start_m = int(self.start_min.get())
            end_h = int(self.end_hour.get())
            end_m = int(self.end_min.get())

            start_time = datetime.combine(date_obj, time(start_h, start_m))
            end_time = datetime.combine(date_obj, time(end_h, end_m))

            # Create TimeSlot
            from src.models.time_slot import TimeSlot
            slot = TimeSlot(start=start_time, end=end_time)

            # Check for overlaps
            for existing in self.unavailable_slots:
                if existing.overlaps_with(slot):
                    messagebox.showerror("Error", "This time slot overlaps with an existing one")
                    return

            self.unavailable_slots.append(slot)
            self._refresh_slots_list()

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

    def _remove_slot(self):
        """Remove selected time slot."""
        selection = self.slots_listbox.curselection()
        if selection:
            index = selection[0]
            del self.unavailable_slots[index]
            self._refresh_slots_list()

    def _refresh_slots_list(self):
        """Refresh the list of unavailable slots."""
        self.slots_listbox.delete(0, tk.END)
        for slot in sorted(self.unavailable_slots, key=lambda s: s.start):
            self.slots_listbox.insert(tk.END, str(slot))

    def _save(self):
        """Save changes and close dialog."""
        self.person.unavailable_slots = self.unavailable_slots
        self.dialog.destroy()