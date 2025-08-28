import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from src.algorithm import SimpleGreedyScheduler, PriorityGreedyScheduler
from src.gui.availability_dialog import AvailabilityDialog
from src.gui.dialogs import PersonDialog, DefenseDialog
from src.gui.import_dialog import ImportCSVDialog
from src.gui.parameters_dialog import SessionParametersDialog
from src.gui.room_dialog import RoomManagementDialog
from src.models import Room
from src.utils.csv_handler import CSVHandler
from src.utils.project_io import load_project, save_project
from src.utils.schedule_exporter import ScheduleExporter
from src.algorithm.optimizer import ScheduleOptimizer, OptimizationWeights
from datetime import datetime


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Thesis Defense Scheduler")
        self.root.geometry("1000x700")

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Data storage
        self.persons = []
        self.defenses = []
        self.schedule = None
        self.session_parameters = None

        # Default rooms
        self.rooms = [
            Room("Sala 101", "101", 30),
            Room("Sala 102", "102", 25),
            Room("Sala 201", "201", 20)
        ]

        # Dialogs
        self.person_listbox = None
        self.defense_listbox = None

        self._create_menu()
        self._create_toolbar()
        self._create_notebook()
        self._create_status_bar()

    def _create_menu(self):
        """Create application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Project...", command=self.open_project, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Project", command=self.save_project, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Import CSV...", command=self.import_csv)
        file_menu.add_command(label="Export Schedule...", command=self.export_schedule)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Person", command=self.add_person)
        edit_menu.add_command(label="Add Defense", command=self.add_defense)
        edit_menu.add_separator()
        edit_menu.add_command(label="Session Parameters", command=self.edit_parameters)
        edit_menu.add_command(label="Manage Rooms", command=self.manage_rooms)

        # Schedule menu
        schedule_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Schedule", menu=schedule_menu)
        schedule_menu.add_command(label="Generate Schedule", command=self.generate_schedule, accelerator="F5")
        schedule_menu.add_command(label="Clear Schedule", command=self.clear_schedule)
        schedule_menu.add_separator()
        schedule_menu.add_command(label="Validate", command=self.validate_schedule)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_docs)
        help_menu.add_command(label="About", command=self.show_about)

        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_project())
        self.root.bind('<Control-o>', lambda e: self.open_project())
        self.root.bind('<Control-s>', lambda e: self.save_project())
        self.root.bind('<F5>', lambda e: self.generate_schedule())

    def _create_toolbar(self):
        """Create application toolbar."""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Toolbar buttons
        ttk.Button(toolbar, text="New", command=self.new_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Open", command=self.open_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save", command=self.save_project).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar, text="Generate Schedule", command=self.generate_schedule).pack(side=tk.LEFT, padx=2)

    def _create_notebook(self):
        """Create tabbed interface."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Data tab
        self.data_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.data_frame, text="Data Input")
        self._create_data_tab()

        # Schedule tab
        self.schedule_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.schedule_frame, text="Schedule")
        self._create_schedule_tab()

        # Export tab
        self.export_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.export_frame, text="Export")
        self._create_export_tab()

    def _create_data_tab(self):
        """Create content for data input tab."""
        # Create main container
        main_container = ttk.Frame(self.data_frame)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Top section - Persons and Defenses
        top_paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        top_paned.pack(fill=tk.BOTH, expand=True)

        # Left panel - Persons
        persons_frame = ttk.LabelFrame(top_paned, text="Faculty Members", padding=10)
        top_paned.add(persons_frame, weight=1)

        # Person buttons
        person_buttons = ttk.Frame(persons_frame)
        person_buttons.pack(pady=5)
        ttk.Button(person_buttons, text="Add Person", command=self.add_person).pack(side=tk.LEFT, padx=2)
        ttk.Button(person_buttons, text="Edit Availability", command=self.edit_person_availability).pack(side=tk.LEFT,
                                                                                                         padx=2)
        ttk.Button(person_buttons, text="Export CSV", command=self.export_persons_csv).pack(side=tk.LEFT, padx=2)

        self.person_listbox = tk.Listbox(persons_frame, height=10)
        self.person_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        # Right panel - Defenses
        defenses_frame = ttk.LabelFrame(top_paned, text="Thesis Defenses", padding=10)
        top_paned.add(defenses_frame, weight=1)

        # Defense buttons
        defense_buttons = ttk.Frame(defenses_frame)
        defense_buttons.pack(pady=5)
        ttk.Button(defense_buttons, text="Add Defense", command=self.add_defense).pack(side=tk.LEFT, padx=2)
        ttk.Button(defense_buttons, text="Export CSV", command=self.export_defenses_csv).pack(side=tk.LEFT, padx=2)

        self.defense_listbox = tk.Listbox(defenses_frame, height=10)
        self.defense_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        # Bottom section - Room info
        room_frame = ttk.LabelFrame(main_container, text="Rooms", padding=10)
        room_frame.pack(fill=tk.X, pady=10, padx=5)

        self.room_info_label = ttk.Label(room_frame, text="")
        self.room_info_label.pack(side=tk.LEFT, padx=10)
        ttk.Button(room_frame, text="Manage Rooms", command=self.manage_rooms).pack(side=tk.RIGHT, padx=10)

        self._update_room_info()

    def _create_schedule_tab(self):
        """Create content for schedule tab."""
        # Control panel
        control_frame = ttk.Frame(self.schedule_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        # Algorithm selection (równy odstęp dla wszystkich opcji)
        ttk.Label(control_frame, text="Algorithm:").pack(side=tk.LEFT, padx=(0, 6))

        self.algorithm_var = tk.StringVar(value="simple")

        algo_frame = ttk.Frame(control_frame)
        algo_frame.pack(side=tk.LEFT)

        ttk.Radiobutton(
            algo_frame, text="Simple Greedy",
            variable=self.algorithm_var, value="simple"
        ).pack(side=tk.LEFT, padx=(0, 12))

        ttk.Radiobutton(
            algo_frame, text="Priority Based",
            variable=self.algorithm_var, value="priority"
        ).pack(side=tk.LEFT, padx=(0, 12))

        ttk.Radiobutton(
            algo_frame, text="Backtracking",
            variable=self.algorithm_var, value="backtracking"
        ).pack(side=tk.LEFT, padx=(0, 12))

        # Separator
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Buttons
        ttk.Button(control_frame, text="Generate Schedule",
                   command=self.generate_schedule).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear Schedule",
                   command=self.clear_schedule).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Validate",
                   command=self.validate_schedule).pack(side=tk.LEFT, padx=5)

        # Schedule display placeholder
        self.schedule_display_frame = ttk.Frame(self.schedule_frame)
        self.schedule_display_frame.pack(fill=tk.BOTH, expand=True)

        schedule_label = ttk.Label(self.schedule_display_frame,
                                   text="Generated schedule will appear here",
                                   font=('Arial', 12))
        schedule_label.pack(expand=True)

    def _create_export_tab(self):
        """Create content for export tab."""
        export_options = ttk.LabelFrame(self.export_frame, text="Export Options", padding=20)
        export_options.pack(padx=20, pady=20)

        ttk.Button(export_options, text="Export to CSV",
                   command=lambda: self.export_schedule('csv')).pack(pady=5)
        ttk.Button(export_options, text="Export to JSON",
                   command=lambda: self.export_schedule('json')).pack(pady=5)
        ttk.Button(export_options, text="Export to PDF",
                   command=lambda: self.export_schedule('pdf')).pack(pady=5)

    def _create_status_bar(self):
        """Create status bar at bottom of window."""
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _update_room_info(self):
        """Update room information display."""
        if hasattr(self, 'room_info_label'):
            room_text = f"Available rooms: {len(self.rooms)}"
            if self.rooms:
                room_names = ", ".join([f"{r.name}" for r in self.rooms[:3]])
                if len(self.rooms) > 3:
                    room_names += "..."
                room_text += f" ({room_names})"
            self.room_info_label.config(text=room_text)

    def _display_schedule(self):
        """Display the generated schedule in the schedule tab."""
        if not self.schedule:
            return

        # Clear existing content in schedule display frame
        for widget in self.schedule_display_frame.winfo_children():
            widget.destroy()

        # Create scrollable frame
        canvas = tk.Canvas(self.schedule_display_frame)
        scrollbar = ttk.Scrollbar(self.schedule_display_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Display schedule header
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, pady=10)

        ttk.Label(header_frame, text="Generated Schedule",
                  font=('Arial', 14, 'bold')).pack()

        # Display summary
        scheduled_count = len(self.schedule.get_scheduled_defenses())
        total_slots = len([s for s in self.schedule.slots if s.time_slot])
        used_slots = len([s for s in self.schedule.slots if s.defense])

        summary_text = (f"Scheduled: {scheduled_count} defenses | "
                        f"Used slots: {used_slots}/{total_slots} | "
                        f"Rooms: {self.session_parameters.room_count}")
        ttk.Label(header_frame, text=summary_text,
                  font=('Arial', 10)).pack()

        # Group by time slot
        time_slots = {}
        for slot in self.schedule.slots:
            if slot.defense:
                time_key = str(slot.time_slot)
                if time_key not in time_slots:
                    time_slots[time_key] = []
                time_slots[time_key].append(slot)

        # Display each time slot
        for time_str in sorted(time_slots.keys()):
            time_frame = ttk.LabelFrame(scrollable_frame, text=time_str, padding=10)
            time_frame.pack(fill=tk.X, padx=20, pady=5)

            # Create columns for rooms
            for slot in time_slots[time_str]:
                defense = slot.defense

                # Create frame for each defense
                defense_frame = ttk.Frame(time_frame, relief=tk.RIDGE, borderwidth=2)
                defense_frame.pack(fill=tk.X, pady=3, padx=5)

                # Room and student info
                ttk.Label(defense_frame, text=f"Room {slot.room.name}: {defense.student_name}",
                          font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=5, pady=2)

                # Committee info
                committee_text = (f"Chairman: {defense.chairman.name}\n"
                                  f"Supervisor: {defense.supervisor.name}\n"
                                  f"Reviewer: {defense.reviewer.name}")
                ttk.Label(defense_frame, text=committee_text,
                          font=('Arial', 9)).pack(anchor=tk.W, padx=5, pady=2)

        self.show_statistics(scrollable_frame)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_statistics(self, parent_frame):
        stats_frame = ttk.LabelFrame(parent_frame, text="Summary Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)

        defense_count = len(self.schedule.get_scheduled_defenses())
        slot_count = len([s for s in self.schedule.slots if s.time_slot])
        used_slots = len([s for s in self.schedule.slots if s.defense])
        room_usage = {}
        role_count = {"supervisor": {}, "reviewer": {}, "chairman": {}}
        role_time = {"supervisor": {}, "reviewer": {}, "chairman": {}}
        total_work_time = {}

        for slot in self.schedule.slots:
            if not slot.defense:
                continue

            duration_minutes = int((slot.time_slot.end - slot.time_slot.start).total_seconds() // 60)
            room_name = slot.room.name
            room_usage[room_name] = room_usage.get(room_name, 0) + 1

            d = slot.defense
            for role, person in [("supervisor", d.supervisor), ("reviewer", d.reviewer), ("chairman", d.chairman)]:
                if person:
                    name = person.name

                    # Liczba wystąpień
                    role_count[role][name] = role_count[role].get(name, 0) + 1

                    # Czas w danej roli
                    role_time[role][name] = role_time[role].get(name, 0) + duration_minutes

                    # Całkowity czas pracy (łącznie we wszystkich rolach)
                    total_work_time[name] = total_work_time.get(name, 0) + duration_minutes

        # Room usage
        usage_str = "Room Utilization:\n" + "\n".join([f"{room}: {count} times" for room, count in room_usage.items()])
        ttk.Label(stats_frame, text=usage_str, font=('Arial', 10)).pack(anchor=tk.W)

        # Workload
        ttk.Label(stats_frame, text="Workload Distribution:", font=('Arial', 10, 'bold')).pack(anchor=tk.W,
                                                                                               pady=(10, 0))
        for role in ["supervisor", "reviewer", "chairman"]:
            title = role.capitalize() + "s:"
            ttk.Label(stats_frame, text=title, font=('Arial', 10, 'underline')).pack(anchor=tk.W)
            for name in sorted(role_count[role], key=lambda n: -role_count[role][n]):
                count = role_count[role][name]
                minutes = role_time[role][name]
                hours = minutes // 60
                minutes_rem = minutes % 60
                ttk.Label(stats_frame, text=f"  {name}: {count} defenses ({hours}h {minutes_rem}min)",
                          font=('Arial', 10)).pack(anchor=tk.W)

        # Całkowity czas pracy każdej osoby (łącznie we wszystkich rolach)
        ttk.Label(stats_frame, text="Total Work Time:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 0))
        for name, minutes in sorted(total_work_time.items(), key=lambda x: -x[1]):
            hours, mins = divmod(minutes, 60)
            total_defenses = sum(role_count[role].get(name, 0) for role in role_count)
            ttk.Label(stats_frame, text=f"  {name}: {hours}h {mins}min ({total_defenses} defenses)",
                      font=('Arial', 10)).pack(anchor=tk.W)

        # Podsumowanie
        ttk.Label(stats_frame, text=f"\nTotal Scheduled Defenses: {defense_count}", font=('Arial', 10, 'italic')).pack(
            anchor=tk.W, pady=(10, 0))
        ttk.Label(stats_frame, text=f"Used Slots: {used_slots}/{slot_count}", font=('Arial', 10, 'italic')).pack(
            anchor=tk.W)

    def update_status(self, message):
        """Update status bar message."""
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    # Menu command implementations
    def new_project(self):
        """Create new project - clear all data."""
        if self.schedule or self.persons or self.defenses:
            if not messagebox.askyesno("New Project",
                                       "This will clear all current data. Continue?"):
                return

        self.update_status("New project created")
        self.persons = []
        self.defenses = []
        self.schedule = None
        self.session_parameters = None

        # Reset rooms to default
        self.rooms = [
            Room("Sala 101", "101", 30),
            Room("Sala 102", "102", 25),
            Room("Sala 201", "201", 20)
        ]

        # Clear displays
        self._refresh_persons()
        self._refresh_defenses()
        self._update_room_info()

        # Clear schedule display
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()
        self._create_schedule_tab()

        # Switch to first tab
        self.notebook.select(0)

    def open_project(self):
        """Open full project from a JSON file."""

        filepath = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("Project files", "*.json"), ("All files", "*.*")]
        )
        if not filepath:
            return
        try:
            persons, defenses, rooms, params, schedule = load_project(filepath)

            # set state
            self.persons = persons
            self.defenses = defenses
            self.rooms = rooms
            self.session_parameters = params
            self.schedule = schedule

            # refresh UI
            self._refresh_persons()
            self._refresh_defenses()
            self._update_room_info()
            self._display_schedule()
            self.show_schedule_table()

            self.update_status(f"Project loaded: {filepath}")
        except Exception as e:
            messagebox.showerror("Open Error", f"Error opening project:\n{e}")
            self.update_status("Open failed")

    def save_project(self):
        """Save full project to a JSON file."""

        if not self.session_parameters:
            messagebox.showwarning("No Parameters", "Set session parameters before saving.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Save Project As",
            defaultextension=".json",
            filetypes=[("Project files", "*.json"), ("All files", "*.*")]
        )
        if not filepath:
            return
        try:
            save_project(
                filepath=filepath,
                persons=self.persons,
                defenses=self.defenses,
                rooms=self.rooms,
                session_parameters=self.session_parameters,
            )
            self.update_status(f"Project saved: {filepath}")
            messagebox.showinfo("Save Project", f"Project saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving project:\n{e}")
            self.update_status("Save failed")

    def import_csv(self):
        """Import data from CSV file."""
        dialog = ImportCSVDialog(self.root)
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            import_type, filepath = dialog.result

            try:
                if import_type == 'persons':
                    imported = CSVHandler.import_persons(filepath)
                    self.persons.extend(imported)
                    self._refresh_persons()
                    self.update_status(f"Imported {len(imported)} persons from CSV")
                    messagebox.showinfo("Import Success",
                                        f"Successfully imported {len(imported)} persons")

                elif import_type == 'defenses':
                    if not self.persons:
                        messagebox.showwarning("No Persons",
                                               "Import persons first before importing defenses")
                        return

                    imported = CSVHandler.import_defenses(filepath, self.persons)
                    self.defenses.extend(imported)
                    self._refresh_defenses()
                    self.update_status(f"Imported {len(imported)} defenses from CSV")
                    messagebox.showinfo("Import Success",
                                        f"Successfully imported {len(imported)} defenses")

            except Exception as e:
                messagebox.showerror("Import Error", f"Error importing CSV: {str(e)}")

    def export_persons_csv(self):
        """Export persons to CSV file."""
        if not self.persons:
            messagebox.showwarning("No Data", "No persons to export")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Persons to CSV"
        )

        if filepath:
            try:
                CSVHandler.export_persons(self.persons, filepath)
                self.update_status(f"Exported {len(self.persons)} persons to CSV")
                messagebox.showinfo("Export Success",
                                    f"Successfully exported {len(self.persons)} persons to {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting CSV: {str(e)}")

    def export_defenses_csv(self):
        """Export defenses to CSV file."""
        if not self.defenses:
            messagebox.showwarning("No Data", "No defenses to export")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Defenses to CSV"
        )

        if filepath:
            try:
                CSVHandler.export_defenses(self.defenses, filepath)
                self.update_status(f"Exported {len(self.defenses)} defenses to CSV")
                messagebox.showinfo("Export Success",
                                    f"Successfully exported {len(self.defenses)} defenses to {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting CSV: {str(e)}")

    def export_schedule(self, format=None):
        """Export schedules to CSV/PDF/JSON file."""
        if not self.schedule:
            messagebox.showwarning("No Schedule", "No schedule to export")
            return

        filetypes = {
            'csv': ("CSV files", "*.csv"),
            'json': ("JSON files", "*.json"),
            'pdf': ("PDF files", "*.pdf")
        }

        if format not in filetypes:
            format = 'csv'  # default

        filepath = filedialog.asksaveasfilename(
            defaultextension=f".{format}",
            filetypes=[filetypes[format]],
            title=f"Export Schedule as {format.upper()}"
        )

        if not filepath:
            return

        try:
            if format == 'csv':
                ScheduleExporter.export_to_csv(self.schedule, filepath)
            elif format == 'json':
                ScheduleExporter.export_to_json(self.schedule, filepath)
            elif format == 'pdf':
                ScheduleExporter.export_to_pdf(self.schedule, filepath)
            else:
                raise ValueError("Unsupported export format")

            self.update_status(f"Exported schedule to {filepath}")
            messagebox.showinfo("Export Success", f"Schedule exported to:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting schedule: {str(e)}")
            self.update_status("Export failed")

    def add_person(self):
        dialog = PersonDialog(self.root)
        if dialog.result:
            self.persons.append(dialog.result)
            self.update_status(f"Added person: {dialog.result.name}")
            self._refresh_persons()

    def add_defense(self):
        if not self.persons:
            messagebox.showwarning("No Faculty", "Add at least one person before adding defenses.")
            return

        dialog = DefenseDialog(self.root, self.persons)
        if dialog.result:
            self.defenses.append(dialog.result)
            self.update_status(f"Added defense: {dialog.result.student_name}")
            self._refresh_defenses()

    def manage_rooms(self):
        """Open room management dialog."""
        dialog = RoomManagementDialog(self.root, self.rooms)
        if dialog.result:
            self.rooms = dialog.result
            self._update_room_info()
            self.update_status(f"Updated rooms: {len(self.rooms)} rooms available")

    def edit_parameters(self):
        dialog = SessionParametersDialog(self.root, self.session_parameters)
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            self.session_parameters = dialog.result
            self.update_status("Session parameters updated")

    def edit_person_availability(self):
        if not self.person_listbox.curselection():
            messagebox.showwarning("No Selection", "Please select a person first")
            return

        index = self.person_listbox.curselection()[0]
        person = self.persons[index]

        dialog = AvailabilityDialog(self.root, person,
                                    self.session_parameters.session_date if self.session_parameters else None)
        self.root.wait_window(dialog.dialog)
        self.update_status(f"Updated availability for {person.name}")

    def generate_schedule(self):
        """Generate schedule using selected algorithm."""
        # Validation (same as before)
        if not self.defenses:
            messagebox.showwarning("No Data", "Please add defenses first")
            return

        if not self.session_parameters:
            messagebox.showwarning("No Parameters", "Please set session parameters first")
            return

        if not self.rooms:
            messagebox.showwarning("No Rooms", "Please add rooms first")
            return

        # Get available chairmen
        available_chairmen = [p for p in self.persons if p.can_be_chairman()]
        if not available_chairmen:
            messagebox.showwarning("No Chairmen",
                                   "No faculty members with chairman role available")
            return

        try:
            self.update_status("Generating schedule...")

            # Choose algorithm based on selection
            if self.algorithm_var.get() == "priority":
                scheduler = PriorityGreedyScheduler(
                    parameters=self.session_parameters,
                    rooms=self.rooms,
                    available_chairmen=available_chairmen
                )
                algo_name = "Priority-based"
            elif self.algorithm_var.get() == "backtracking":
                from src.algorithm.backtracking_scheduler import BacktrackingScheduler
                scheduler = BacktrackingScheduler(
                    parameters=self.session_parameters,
                    rooms=self.rooms,
                    available_chairmen=available_chairmen
                )
                algo_name = "Backtracking"
            else:
                scheduler = SimpleGreedyScheduler(
                    parameters=self.session_parameters,
                    rooms=self.rooms,
                    available_chairmen=available_chairmen
                )
                algo_name = "Simple greedy"

            # Generate schedule
            schedule, conflicts = scheduler.schedule(self.defenses)
            self.schedule = schedule

            try:
                opt = ScheduleOptimizer(OptimizationWeights(
                    gap_weight=1.0,
                    group_weight=1.0,
                    span_weight=0.5,
                    chair_block_weight=1.0
                ))
                optimized = opt.optimize(scheduler, self.schedule, max_iters=250)
                self.schedule = optimized
            except Exception:
                pass

            used = [s for s in self.schedule.slots if s.defense]
            if used:
                last_used = max(s.time_slot.end for s in used)
                end_h, end_m = map(int, self.session_parameters.end_time.split(':'))
                configured_end = datetime.combine(
                    self.session_parameters.session_date,
                    datetime.min.time().replace(hour=end_h, minute=end_m)
                )
                if last_used < configured_end:
                    minutes_saved = int((configured_end - last_used).total_seconds() // 60)
                    self.update_status(f"Optimization has reduced session of. {minutes_saved} min")

            # Show results
            scheduled_count = len(schedule.get_scheduled_defenses())
            total_count = len(self.defenses)

            if conflicts:
                conflict_msg = "\n".join([str(c) for c in conflicts[:5]])
                if len(conflicts) > 5:
                    conflict_msg += f"\n... and {len(conflicts) - 5} more conflicts"

                messagebox.showwarning("Scheduling Issues",
                                       f"Algorithm: {algo_name}\n"
                                       f"Scheduled {scheduled_count}/{total_count} defenses.\n\n"
                                       f"Conflicts:\n{conflict_msg}")
            else:
                messagebox.showinfo("Success",
                                    f"Algorithm: {algo_name}\n"
                                    f"Successfully scheduled all {scheduled_count} defenses!")

            self.update_status(f"Schedule generated using {algo_name}: "
                               f"{scheduled_count}/{total_count} defenses scheduled")
            self._display_schedule()
            self.show_schedule_table()

        except Exception as e:
            messagebox.showerror("Error", f"Error generating schedule: {str(e)}")
            self.update_status("Schedule generation failed")

    def clear_schedule(self):
        """Clear the current schedule and its display."""
        if self.schedule and messagebox.askyesno("Clear Schedule", "Are you sure you want to clear the schedule?"):
            self.schedule = None

            # Usuń standardowy harmonogram (labelki)
            for widget in self.schedule_display_frame.winfo_children():
                widget.destroy()

            # Usuń tabelkę, jeśli istnieje
            if hasattr(self, 'table_frame'):
                self.table_frame.destroy()
                del self.table_frame

            if hasattr(self, 'tree'):
                del self.tree

            # Pokaż placeholder
            schedule_label = ttk.Label(self.schedule_display_frame,
                                       text="Generated schedule will appear here",
                                       font=('Arial', 12))
            schedule_label.pack(expand=True)

            self.update_status("Schedule cleared")

    def validate_schedule(self):
        """Run structural and time-conflict validation and show a report."""
        from src.utils.validators import Validator

        if not self.defenses:
            messagebox.showwarning("No Data", "Add defenses first.")
            return

        if not self.schedule:
            messagebox.showwarning("No Schedule",
                                   "No schedule to validate. Generate a schedule first.")
            return

        self.update_status("Validating schedule...")

        report = Validator.validate_schedule(self.schedule.get_scheduled_defenses())

        if report:
            messagebox.showwarning("Validation Report", "• " + "\n• ".join(report))
        else:
            messagebox.showinfo("Validation Report", "No issues found. ✔")

        self.update_status("Validation finished")

    def show_docs(self):
        messagebox.showinfo("Documentation",
                            "See README.md for documentation")

    def show_about(self):
        messagebox.showinfo("About",
                            "Thesis Defense Scheduler\nVersion 1.0\n\n"
                            "Automatic scheduling system for thesis defenses")

    def _refresh_persons(self):
        if self.person_listbox:
            self.person_listbox.delete(0, tk.END)
            for p in self.persons:
                roles = ', '.join(r.name.capitalize() for r in p.roles)
                self.person_listbox.insert(tk.END, f"{p.name} ({roles})")

    def _refresh_defenses(self):
        if self.defense_listbox:
            self.defense_listbox.delete(0, tk.END)
            for d in self.defenses:
                self.defense_listbox.insert(tk.END,
                                            f"{d.student_name} - {d.thesis_title} ({d.supervisor.name}/{d.reviewer.name})")

    def show_schedule_table(self):
        if hasattr(self, 'table_frame'):
            self.table_frame.destroy()

        self.table_frame = ttk.Frame(self.schedule_frame)
        self.table_frame.pack(fill='both', expand=True)

        columns = ("time", "student", "room", "supervisor", "reviewer", "chairman")

        self.tree = ttk.Treeview(self.table_frame, columns=columns, show='headings', height=20)
        self.tree.pack(side='left', fill='both', expand=True)

        # Nagłówki
        self.tree.heading("time", text="Time Slot")
        self.tree.heading("student", text="Student")
        self.tree.heading("room", text="Room")
        self.tree.heading("supervisor", text="Supervisor")
        self.tree.heading("reviewer", text="Reviewer")
        self.tree.heading("chairman", text="Chairman")

        # Kolumny
        for col in columns:
            self.tree.column(col, width=120, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Style tagów
        style = ttk.Style()
        style.map("Treeview", background=[('selected', '#cccccc')])
        self.tree.tag_configure("conflict", background="#ffcccc")
        self.tree.tag_configure("room101", background="#e6f2ff")
        self.tree.tag_configure("room102", background="#e6ffe6")

        # Wypełnienie danych
        if not self.schedule:
            messagebox.showinfo("No schedule", "No schedule generated.")
            return

        times_seen = {}  # (room, time) → True
        for slot in self.schedule.slots:
            if not slot.defense:
                continue

            d = slot.defense
            time_str = str(slot.time_slot)
            room = slot.room.name
            key = (room, time_str)

            tag = "room101" if "101" in room else "room102"
            if key in times_seen:
                tag = "conflict"
            else:
                times_seen[key] = True

            self.tree.insert("", "end", values=(
                time_str,
                d.student_name,
                room,
                d.supervisor.name,
                d.reviewer.name,
                d.chairman.name if d.chairman else "—"
            ), tags=(tag,))
