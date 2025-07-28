import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os


class ImportCSVDialog:
    """Dialog for importing CSV files."""

    def __init__(self, parent):
        self.result = None  # Will be (type, filepath) tuple

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Import CSV")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)

        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_widgets()

        # Center dialog
        self.dialog.update_idletasks()
        x = (parent.winfo_x() + parent.winfo_width() // 2 -
             self.dialog.winfo_width() // 2)
        y = (parent.winfo_y() + parent.winfo_height() // 2 -
             self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Instructions
        ttk.Label(main_frame, text="Choose what to import:",
                  font=('Arial', 10, 'bold')).pack(pady=(0, 15))

        # Radio buttons for import type
        self.import_type = tk.StringVar(value="persons")

        ttk.Radiobutton(main_frame, text="Import Persons (Faculty Members)",
                        variable=self.import_type, value="persons").pack(anchor=tk.W, pady=5)

        ttk.Radiobutton(main_frame, text="Import Defenses",
                        variable=self.import_type, value="defenses").pack(anchor=tk.W, pady=5)

        # File selection
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Label(file_frame, text="File:").pack(side=tk.LEFT, padx=(0, 10))
        self.filepath_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.filepath_var,
                  state="readonly", width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse...",
                   command=self._browse_file).pack(side=tk.LEFT, padx=(10, 0))

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, pady=10, padx=20)

        ttk.Button(button_frame, text="Import",
                   command=self._import_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel",
                   command=self.dialog.destroy).pack(side=tk.RIGHT)

        # Sample files button
        ttk.Button(button_frame, text="Create Sample Files",
                   command=self._create_samples).pack(side=tk.LEFT)

    def _browse_file(self):
        """Open file browser to select CSV file."""
        filepath = filedialog.askopenfilename(
            parent=self.dialog,
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filepath:
            self.filepath_var.set(filepath)

    def _import_clicked(self):
        """Handle import button click."""
        filepath = self.filepath_var.get()

        if not filepath:
            messagebox.showerror("Error", "Please select a file to import")
            return

        if not os.path.exists(filepath):
            messagebox.showerror("Error", "Selected file does not exist")
            return

        self.result = (self.import_type.get(), filepath)
        self.dialog.destroy()

    def _create_samples(self):
        """Create sample CSV files."""
        from src.utils.csv_handler import CSVHandler

        # Ask where to save samples
        directory = filedialog.askdirectory(
            parent=self.dialog,
            title="Choose directory for sample files"
        )

        if directory:
            try:
                # Create sample files
                persons_file = os.path.join(directory, "sample_persons.csv")
                defenses_file = os.path.join(directory, "sample_defenses.csv")

                CSVHandler.create_sample_persons_csv(persons_file)
                CSVHandler.create_sample_defenses_csv(defenses_file)

                messagebox.showinfo("Success",
                                    f"Sample files created:\n"
                                    f"- sample_persons.csv\n"
                                    f"- sample_defenses.csv\n\n"
                                    f"Location: {directory}")

            except Exception as e:
                messagebox.showerror("Error", f"Error creating samples: {str(e)}")