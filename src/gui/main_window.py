import tkinter as tk
from tkinter import ttk, messagebox
from .dialogs import PersonDialog, DefenseDialog

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
        # Create paned window for persons and defenses
        paned = ttk.PanedWindow(self.data_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left panel - Persons
        persons_frame = ttk.LabelFrame(paned, text="Faculty Members", padding=10)
        paned.add(persons_frame, weight=1)

        ttk.Button(persons_frame, text="Add Person", command=self.add_person).pack(pady=5)
        self.person_listbox = tk.Listbox(persons_frame, height=10)
        self.person_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        # Right panel - Defenses
        defenses_frame = ttk.LabelFrame(paned, text="Thesis Defenses", padding=10)
        paned.add(defenses_frame, weight=1)

        ttk.Button(defenses_frame, text="Add Defense", command=self.add_defense).pack(pady=5)
        self.defense_listbox = tk.Listbox(defenses_frame, height=10)
        self.defense_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

    def _create_schedule_tab(self):
        """Create content for schedule tab."""
        # Control panel
        control_frame = ttk.Frame(self.schedule_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(control_frame, text="Generate Schedule",
                   command=self.generate_schedule).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear Schedule",
                   command=self.clear_schedule).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Validate",
                   command=self.validate_schedule).pack(side=tk.LEFT, padx=5)

        # Schedule display
        schedule_label = ttk.Label(self.schedule_frame,
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

    def update_status(self, message):
        """Update status bar message."""
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    # Menu command implementations (placeholders)
    def new_project(self):
        self.update_status("New project created")
        self.persons = []
        self.defenses = []
        self.schedule = None

    def open_project(self):
        self.update_status("Open project - not implemented yet")

    def save_project(self):
        self.update_status("Save project - not implemented yet")

    def import_csv(self):
        self.update_status("Import CSV - not implemented yet")

    def export_schedule(self, format=None):
        self.update_status(f"Export to {format if format else 'file'} - not implemented yet")

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

    def edit_parameters(self):
        self.update_status("Edit parameters - not implemented yet")

    def generate_schedule(self):
        self.update_status("Generating schedule...")
        # Placeholder for schedule generation
        messagebox.showinfo("Schedule Generation",
                            "Schedule generation will be implemented in Task 7-8")

    def clear_schedule(self):
        self.update_status("Schedule cleared")
        self.schedule = None

    def validate_schedule(self):
        if not self.schedule:
            messagebox.showwarning("No Schedule",
                                   "No schedule to validate. Generate a schedule first.")
        else:
            self.update_status("Validating schedule...")

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