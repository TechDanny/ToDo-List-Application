import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["todo_app"]
users_collection = db["users"]
tasks_collection = db["tasks"]

class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List App")
        self.geometry("800x600")

        self.configure(bg="#f0f0f0")

        self.create_widgets()

    def create_widgets(self):
        self.task_entry = tk.Entry(self, width=50, bg="white", fg="black", font=("Helvetica", 12))
        self.task_entry.grid(row=0, column=0, padx=10, pady=10)

        self.add_button = tk.Button(self, text="Add Task", command=self.add_task, bg="#4CAF50", fg="white", font=("Helvetica", 12))
        self.add_button.grid(row=0, column=1, padx=5, pady=10)

        self.tasks_listbox = tk.Listbox(self, width=100, height=20, bg="white", fg="black", font=("Helvetica", 12))
        self.tasks_listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.edit_button = tk.Button(self, text="Edit Task", command=self.edit_task, bg="#008CBA", fg="white", font=("Helvetica", 12))
        self.edit_button.grid(row=2, column=0, padx=5, pady=10)

        self.delete_button = tk.Button(self, text="Delete Task", command=self.delete_task, bg="#f44336", fg="white", font=("Helvetica", 12))
        self.delete_button.grid(row=2, column=1, padx=5, pady=10)

        self.load_tasks()
        self.update_tasks_listbox()

    def add_task(self):
        task = self.task_entry.get().strip()
        if task:
            due_date = simpledialog.askstring("Due Date", "Enter Due Date (YYYY-MM-DD):")
            priority = simpledialog.askstring("Priority", "Enter Priority (Low, Medium, High):")
            task_data = {"task": task, "due_date": due_date, "priority": priority, "completed": False}
            tasks_collection.insert_one(task_data)
            self.load_tasks()
            self.update_tasks_listbox()
            self.task_entry.delete(0, tk.END)

    def load_tasks(self):
        self.tasks = list(tasks_collection.find())

    def update_tasks_listbox(self):
        self.tasks_listbox.delete(0, tk.END)
        for task in self.tasks:
            task_str = f"{task['task']} - Due: {task['due_date']} - Priority: {task['priority']}"
            if task["completed"]:
                task_str += " - Completed"
            self.tasks_listbox.insert(tk.END, task_str)

    def edit_task(self):
        selected_index = self.tasks_listbox.curselection()
        if selected_index:
            selected_task = self.tasks[selected_index[0]]
            new_task = simpledialog.askstring("Edit Task", "Edit Task:", initialvalue=selected_task['task'])
            if new_task:
                tasks_collection.update_one({"_id": selected_task["_id"]}, {"$set": {"task": new_task}})
                self.load_tasks()
                self.update_tasks_listbox()

    def delete_task(self):
        selected_index = self.tasks_listbox.curselection()
        if selected_index:
            selected_task = self.tasks[selected_index[0]]
            tasks_collection.delete_one({"_id": selected_task["_id"]})
            self.load_tasks()
            self.update_tasks_listbox()

class SignupPage(tk.Toplevel):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.title("Sign Up")
        self.geometry("300x200")

        self.username_label = tk.Label(self, text="Username:")
        self.username_label.grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self, text="Password:")
        self.password_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.signup_button = tk.Button(self, text="Sign Up", command=self.signup)
        self.signup_button.grid(row=2, column=0, padx=5, pady=5)

        self.login_button = tk.Button(self, text="Login Page", command=self.go_to_login)
        self.login_button.grid(row=2, column=1, padx=5, pady=5)

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not (username and password):
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        # Check if username already exists
        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            messagebox.showerror("Error", "Username already exists. Please choose a different username.")
            return

        # If username doesn't exist, proceed with signup
        user_data = {"username": username, "password": password}
        users_collection.insert_one(user_data)
        messagebox.showinfo("Success", "Account created successfully.")

        self.destroy()

        login_window = LoginPage(self.main_app)
        login_window.mainloop()

    def go_to_login(self):
        self.destroy()
        login_window = LoginPage(self.main_app)
        login_window.mainloop()

class LoginPage(tk.Toplevel):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.title("Log In")
        self.geometry("300x150")

        self.username_label = tk.Label(self, text="Username:")
        self.username_label.grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self, text="Password:")
        self.password_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = tk.Button(self, text="Log In", command=self.login)
        self.login_button.grid(row=2, columnspan=2, padx=5, pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not (username and password):
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        user_data = users_collection.find_one({"username": username, "password": password})

        if user_data:
            messagebox.showinfo("Success", "Login successful.")
            self.main_app.deiconify()
            self.destroy()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

if __name__ == "__main__":
    app = TodoApp()
    
    app.withdraw()

    signup_page = SignupPage(app)
    signup_page.mainloop()
