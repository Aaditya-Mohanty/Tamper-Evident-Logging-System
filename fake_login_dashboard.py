import tkinter as tk
from tkinter import messagebox
from tamper_log import add_log

def login_action():
    username = entry_user.get()
    password = entry_pass.get()

    messagebox.showwarning("Alert", "⚠️ Unauthorized access detected!")

    add_log("LOGIN_ATTEMPT", f"Username: {username}, Password: {password}")

    entry_user.delete(0, tk.END)
    entry_pass.delete(0, tk.END)

root = tk.Tk()
root.title("Bank Login")
root.geometry("300x200")

tk.Label(root, text="Bank Login", font=("Arial", 14)).pack(pady=10)

tk.Label(root, text="Username").pack()
entry_user = tk.Entry(root)
entry_user.pack()

tk.Label(root, text="Password").pack()
entry_pass = tk.Entry(root, show="*")
entry_pass.pack()

tk.Button(root, text="Login", command=login_action, bg="red", fg="white").pack(pady=15)

root.mainloop()
