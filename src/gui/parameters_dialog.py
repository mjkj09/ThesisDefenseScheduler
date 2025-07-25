import tkinter as tk
from datetime import datetime, date
from tkinter import ttk, messagebox


class SessionParametersDialog:
    """Dialog for editing session parameters."""

    def __init__(self, parent, parameters=None):
        self.result = None
        self.parameters = parameters

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Session Parameters")
        self.dialog.geometry("450x400")
        self.dialog.resizable(False, False)

        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_widgets()
        if parameters:
            self._load_data()

    def _create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Session date
        ttk.Label(main_frame, text="Session Date:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(main_frame, textvariable=self.date_var, width=15).grid(row=0, column=1, pady=5, padx=5)

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

        # Breaks list
        breaks_frame = ttk.Frame(main_frame)
        breaks_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.breaks_listbox = tk.Listbox(breaks_frame, height=4)
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

        self.breaks = []  # List of break TimeSlots

    def _add_break(self):
        """Add a break period."""
        # Simple dialog for break times
        messagebox.showinfo("Add Break",
                            "Break addition dialog would be implemented here\n"
                            "For now, use default lunch break 12:00-13:00")
        # Add default lunch break
        self.breaks_listbox.insert(tk.END, "12:00 - 13:00")

    def _remove_break(self):
        """Remove selected break."""
        selection = self.breaks_listbox.curselection()
        if selection:
            self.breaks_listbox.delete(selection[0])

    def _load_data(self):
        """Load existing parameters."""
        if self.parameters:
            self.date_var.set(self.parameters.session_date.strftime("%Y-%m-%d"))
            self.start_time_var.set(self.parameters.start_time)
            self.end_time_var.set(self.parameters.end_time)
            self.duration_var.set(self.parameters.defense_duration)
            self.rooms_var.set(self.parameters.room_count)

    def _ok_clicked(self):
        """Save parameters and close."""
        try:
            from src.models.session_parameters import SessionParameters

            # Parse date
            session_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d").date()

            # Create parameters object
            self.result = SessionParameters(
                session_date=session_date,
                start_time=self.start_time_var.get(),
                end_time=self.end_time_var.get(),
                defense_duration=self.duration_var.get(),
                room_count=self.rooms_var.get()
            )
            self.dialog.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))