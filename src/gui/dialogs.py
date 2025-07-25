import tkinter as tk
from tkinter import ttk, messagebox
from src.models.person import Person
from src.models.defense import Defense
from src.models.__init__ import Role
from src.utils.validators import Validator

class PersonDialog:
    def __init__(self, parent, person=None):
        self.result = None
        self.person = person

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Person" if not person else "Edit Person")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_widgets()
        self._load_data()

        self.dialog.wait_window()

    def _create_widgets(self):
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky=tk.W)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(frame, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=0, column=1)

        ttk.Label(frame, text="Email:").grid(row=1, column=0, sticky=tk.W)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(frame, textvariable=self.email_var, width=30)
        self.email_entry.grid(row=1, column=1)

        ttk.Label(frame, text="Roles:").grid(row=2, column=0, sticky=tk.NW)
        self.role_vars = {}
        role_frame = ttk.Frame(frame)
        role_frame.grid(row=2, column=1, sticky=tk.W)
        for i, role in enumerate(Role):
            var = tk.BooleanVar()
            self.role_vars[role] = var
            ttk.Checkbutton(role_frame, text=role.name.capitalize(), variable=var).pack(anchor=tk.W)

        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)

    def _load_data(self):
        if self.person:
            self.name_var.set(self.person.name)
            self.email_var.set(self.person.email)
            for role in self.person.roles:
                self.role_vars[role].set(True)

    def _ok_clicked(self):
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        if not name or not email:
            messagebox.showerror("Error", "Name and email are required")
            return
        if not Validator.validate_email(email):
            messagebox.showerror("Error", "Invalid email format")
            return
        roles = {role for role, var in self.role_vars.items() if var.get()}
        if not roles:
            messagebox.showerror("Error", "At least one role must be selected")
            return
        self.result = Person(name=name, email=email, roles=roles)
        self.dialog.destroy()

class DefenseDialog:
    def __init__(self, parent, persons, defense=None):
        self.result = None
        self.persons = persons
        self.defense = defense
        self.supervisors = [p for p in persons if Role.SUPERVISOR in p.roles]
        self.reviewers = [p for p in persons if Role.REVIEWER in p.roles]

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Defense" if not defense else "Edit Defense")
        self.dialog.geometry("450x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_widgets()
        self._load_data()

        self.dialog.wait_window()

    def _create_widgets(self):
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Student Name:").grid(row=0, column=0, sticky=tk.W)
        self.student_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.student_var, width=40).grid(row=0, column=1)

        ttk.Label(frame, text="Thesis Title:").grid(row=1, column=0, sticky=tk.W)
        self.title_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.title_var, width=40).grid(row=1, column=1)

        ttk.Label(frame, text="Supervisor:").grid(row=2, column=0, sticky=tk.W)
        self.supervisor_var = tk.StringVar()
        self.supervisor_combo = ttk.Combobox(frame, textvariable=self.supervisor_var,
                                             values=[p.name for p in self.supervisors], state="readonly")
        self.supervisor_combo.grid(row=2, column=1)

        ttk.Label(frame, text="Reviewer:").grid(row=3, column=0, sticky=tk.W)
        self.reviewer_var = tk.StringVar()
        self.reviewer_combo = ttk.Combobox(frame, textvariable=self.reviewer_var,
                                           values=[p.name for p in self.reviewers], state="readonly")
        self.reviewer_combo.grid(row=3, column=1)

        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)

    def _load_data(self):
        if self.defense:
            self.student_var.set(self.defense.student_name)
            self.title_var.set(self.defense.thesis_title)
            self.supervisor_var.set(self.defense.supervisor.name)
            self.reviewer_var.set(self.defense.reviewer.name)

    def _ok_clicked(self):
        student = self.student_var.get().strip()
        title = self.title_var.get().strip()
        supervisor_name = self.supervisor_var.get()
        reviewer_name = self.reviewer_var.get()

        if not student or not title or not supervisor_name or not reviewer_name:
            messagebox.showerror("Error", "All fields are required")
            return
        if supervisor_name == reviewer_name:
            messagebox.showerror("Error", "Supervisor and reviewer must be different")
            return

        supervisor = next(p for p in self.supervisors if p.name == supervisor_name)
        reviewer = next(p for p in self.reviewers if p.name == reviewer_name)
        self.result = Defense(student_name=student, thesis_title=title,
                              supervisor=supervisor, reviewer=reviewer)
        self.dialog.destroy()
