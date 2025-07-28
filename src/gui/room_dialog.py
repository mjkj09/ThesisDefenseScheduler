import tkinter as tk
from tkinter import ttk, messagebox
from src.models import Room


class RoomDialog:
    """Dialog for adding/editing rooms."""

    def __init__(self, parent, room=None):
        self.result = None
        self.room = room

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Room" if not room else "Edit Room")
        self.dialog.geometry("350x200")
        self.dialog.resizable(False, False)

        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_widgets()
        self._load_data()

        self.dialog.wait_window()

    def _create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Room name
        ttk.Label(main_frame, text="Room Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=25).grid(row=0, column=1, pady=5)

        # Room number
        ttk.Label(main_frame, text="Room Number:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.number_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.number_var, width=25).grid(row=1, column=1, pady=5)

        # Capacity
        ttk.Label(main_frame, text="Capacity:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.capacity_var = tk.IntVar(value=20)
        ttk.Spinbox(main_frame, from_=5, to=100, textvariable=self.capacity_var,
                    width=23).grid(row=2, column=1, pady=5)

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)

    def _load_data(self):
        """Load existing room data if editing."""
        if self.room:
            self.name_var.set(self.room.name)
            self.number_var.set(self.room.number)
            self.capacity_var.set(self.room.capacity)

    def _ok_clicked(self):
        """Handle OK button click."""
        name = self.name_var.get().strip()
        number = self.number_var.get().strip()
        capacity = self.capacity_var.get()

        if not name:
            messagebox.showerror("Error", "Room name cannot be empty")
            return

        if not number:
            messagebox.showerror("Error", "Room number cannot be empty")
            return

        try:
            self.result = Room(name=name, number=number, capacity=capacity)
            self.dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))


class RoomManagementDialog:
    """Dialog for managing all rooms."""

    def __init__(self, parent, rooms):
        self.rooms = rooms.copy()  # Work with a copy
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Room Management")
        self.dialog.geometry("400x300")

        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_widgets()
        self._refresh_room_list()

        self.dialog.wait_window()

    def _create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Room list
        list_frame = ttk.LabelFrame(main_frame, text="Rooms", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Listbox with scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.room_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.room_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.room_listbox.yview)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Add", command=self._add_room).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Edit", command=self._edit_room).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Remove", command=self._remove_room).pack(side=tk.LEFT, padx=2)

        # Dialog buttons
        dialog_button_frame = ttk.Frame(self.dialog)
        dialog_button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(dialog_button_frame, text="OK", command=self._ok_clicked).pack(side=tk.RIGHT, padx=5)
        ttk.Button(dialog_button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)

    def _refresh_room_list(self):
        """Refresh the room list display."""
        self.room_listbox.delete(0, tk.END)
        for room in self.rooms:
            self.room_listbox.insert(tk.END, f"{room.name} ({room.number}) - Capacity: {room.capacity}")

    def _add_room(self):
        """Add new room."""
        dialog = RoomDialog(self.dialog)
        if dialog.result:
            self.rooms.append(dialog.result)
            self._refresh_room_list()

    def _edit_room(self):
        """Edit selected room."""
        selection = self.room_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a room to edit")
            return

        index = selection[0]
        room = self.rooms[index]

        dialog = RoomDialog(self.dialog, room)
        if dialog.result:
            self.rooms[index] = dialog.result
            self._refresh_room_list()

    def _remove_room(self):
        """Remove selected room."""
        selection = self.room_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a room to remove")
            return

        index = selection[0]
        room = self.rooms[index]

        if messagebox.askyesno("Confirm", f"Remove room {room.name}?"):
            del self.rooms[index]
            self._refresh_room_list()

    def _ok_clicked(self):
        """Save changes and close."""
        if not self.rooms:
            messagebox.showerror("Error", "At least one room is required")
            return

        self.result = self.rooms
        self.dialog.destroy()