import tkinter as tk
from tkinter import ttk, messagebox
from db import (insert_user, get_all_users, search_users,
                update_user, delete_user, test_connection)


class UserManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("User Management System")
        self.root.geometry("900x600")

        # Check DB connection
        if not test_connection():
            messagebox.showerror("Database Error", "Cannot connect to MongoDB.")
            root.destroy()
            return

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.add_tab = ttk.Frame(self.notebook)
        self.view_tab = ttk.Frame(self.notebook)
        self.update_delete_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.add_tab, text="Add User")
        self.notebook.add(self.view_tab, text="View / Search Users")
        self.notebook.add(self.update_delete_tab, text="Update / Delete User")

        self.build_add_tab()
        self.build_view_tab()
        self.build_update_delete_tab()

    # ------------------ Add User Tab ------------------
    def build_add_tab(self):
        frame = ttk.LabelFrame(self.add_tab, text="New User Details", padding=20)
        frame.pack(padx=20, pady=20, fill='both', expand=True)

        labels = ["First Name", "Last Name", "Birth Date (YYYY-MM-DD)", "Birth Place", "Phone Number"]
        self.add_entries = {}
        for i, label in enumerate(labels):
            ttk.Label(frame, text=label + ":").grid(row=i, column=0, sticky='w', pady=5)
            entry = ttk.Entry(frame, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.add_entries[label] = entry

        ttk.Button(frame, text="Add User", command=self.add_user).grid(row=5, column=1, pady=20, sticky='e')
        self.add_status = ttk.Label(frame, text="", foreground="green")
        self.add_status.grid(row=6, column=1, sticky='w')

    def add_user(self):
        first = self.add_entries["First Name"].get().strip()
        last = self.add_entries["Last Name"].get().strip()
        bdate = self.add_entries["Birth Date (YYYY-MM-DD)"].get().strip()
        bplace = self.add_entries["Birth Place"].get().strip()
        phone = self.add_entries["Phone Number"].get().strip()

        success, message = insert_user(first, last, bdate, bplace, phone)
        if success:
            self.add_status.config(text=message, foreground="green")
            for entry in self.add_entries.values():
                entry.delete(0, tk.END)
        else:
            self.add_status.config(text=message, foreground="red")

    # ------------------ View / Search Tab ------------------
    def build_view_tab(self):
        search_frame = ttk.Frame(self.view_tab)
        search_frame.pack(pady=10, fill='x', padx=20)

        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side='left', padx=10)
        ttk.Button(search_frame, text="Search", command=self.refresh_view).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Show All",
                   command=lambda: [self.search_var.set(""), self.refresh_view()]).pack(side='left', padx=5)

        table_frame = ttk.Frame(self.view_tab)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ("First Name", "Last Name", "Birth Date", "Birth Place", "Phone")
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor='center')

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.refresh_view()

    def refresh_view(self):
        query = self.search_var.get().strip()
        users = search_users(query) if query else get_all_users()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for user in users:
            self.tree.insert("", "end", values=(
                user["first_name"], user["last_name"],
                user["birth_date"], user["birth_place"], user["phone"]
            ))

    # ------------------ Update / Delete Tab ------------------
    def build_update_delete_tab(self):
        select_frame = ttk.LabelFrame(self.update_delete_tab, text="Select User by Phone", padding=10)
        select_frame.pack(padx=20, pady=10, fill='x')

        ttk.Label(select_frame, text="Phone:").grid(row=0, column=0, padx=5)
        self.phone_to_fetch = ttk.Entry(select_frame, width=20)
        self.phone_to_fetch.grid(row=0, column=1, padx=5)
        ttk.Button(select_frame, text="Load User", command=self.load_user_for_edit).grid(row=0, column=2, padx=10)

        edit_frame = ttk.LabelFrame(self.update_delete_tab, text="Edit User Details", padding=10)
        edit_frame.pack(padx=20, pady=10, fill='both', expand=True)

        labels = ["First Name", "Last Name", "Birth Date (YYYY-MM-DD)", "Birth Place"]
        self.edit_entries = {}
        for i, label in enumerate(labels):
            ttk.Label(edit_frame, text=label + ":").grid(row=i, column=0, sticky='w', pady=5)
            entry = ttk.Entry(edit_frame, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.edit_entries[label] = entry

        ttk.Label(edit_frame, text="Phone (read-only):").grid(row=4, column=0, sticky='w', pady=5)
        self.phone_display = ttk.Label(edit_frame, text="", relief='sunken', width=37)
        self.phone_display.grid(row=4, column=1, padx=10, pady=5)

        btn_frame = ttk.Frame(edit_frame)
        btn_frame.grid(row=5, column=1, pady=20, sticky='e')

        ttk.Button(btn_frame, text="Update User", command=self.update_user_action).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete User", command=self.delete_user_action).pack(side='left', padx=5)

        self.edit_status = ttk.Label(edit_frame, text="", foreground="green")
        self.edit_status.grid(row=6, column=1, sticky='w')

    def load_user_for_edit(self):
        phone = self.phone_to_fetch.get().strip()
        if not phone:
            messagebox.showwarning("Input Required", "Please enter a phone number.")
            return

        users = search_users(phone)
        if not users:
            messagebox.showerror("Not Found", "No user with that phone number.")
            return

        user = users[0]
        self.edit_entries["First Name"].delete(0, tk.END)
        self.edit_entries["First Name"].insert(0, user["first_name"])
        self.edit_entries["Last Name"].delete(0, tk.END)
        self.edit_entries["Last Name"].insert(0, user["last_name"])
        self.edit_entries["Birth Date (YYYY-MM-DD)"].delete(0, tk.END)
        self.edit_entries["Birth Date (YYYY-MM-DD)"].insert(0, user["birth_date"])
        self.edit_entries["Birth Place"].delete(0, tk.END)
        self.edit_entries["Birth Place"].insert(0, user["birth_place"])
        self.phone_display.config(text=user["phone"])

    def update_user_action(self):
        phone = self.phone_display.cget("text")
        if not phone:
            messagebox.showwarning("No User", "Load a user first.")
            return

        first = self.edit_entries["First Name"].get().strip()
        last = self.edit_entries["Last Name"].get().strip()
        bdate = self.edit_entries["Birth Date (YYYY-MM-DD)"].get().strip()
        bplace = self.edit_entries["Birth Place"].get().strip()

        if not all([first, last, bdate, bplace]):
            messagebox.showwarning("Empty Fields", "All fields are required.")
            return

        success, message = update_user(phone, {
            "first_name": first,
            "last_name": last,
            "birth_date": bdate,
            "birth_place": bplace
        })
        self.edit_status.config(text=message, foreground="green" if success else "red")
        if success:
            for entry in self.edit_entries.values():
                entry.delete(0, tk.END)
            self.phone_display.config(text="")
            self.phone_to_fetch.delete(0, tk.END)

    def delete_user_action(self):
        phone = self.phone_display.cget("text")
        if not phone:
            messagebox.showwarning("No User", "Load a user first.")
            return

        if messagebox.askyesno("Confirm Delete", f"Delete user with phone {phone}?"):
            success, message = delete_user(phone)
            if success:
                self.edit_status.config(text=message, foreground="green")
                for entry in self.edit_entries.values():
                    entry.delete(0, tk.END)
                self.phone_display.config(text="")
                self.phone_to_fetch.delete(0, tk.END)
            else:
                self.edit_status.config(text=message, foreground="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = UserManagementApp(root)
    root.mainloop()