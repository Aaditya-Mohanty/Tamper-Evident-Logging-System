import tkinter as tk
from tkinter import messagebox
import json
from tamper_log import add_log, verify_logs

LOG_FILE = "logs.json"

# Add log function
def add_log_ui():
    event = entry_event.get()
    desc = entry_desc.get()

    if event == "" or desc == "":
        messagebox.showerror("Error", "All fields required")
        return

    add_log(event, desc)
    messagebox.showinfo("Success", "Log added successfully!")

    entry_event.delete(0, tk.END)
    entry_desc.delete(0, tk.END)

    load_logs()

# Verify logs
def verify_ui():
    try:
        verify_logs()
        messagebox.showinfo("Result", "Logs are secure ✅")
    except:
        messagebox.showerror("Warning", "⚠️ Tampering detected!")

# Load logs into box
def load_logs():
    log_box.delete(1.0, tk.END)

    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)

        for log in logs:
            log_box.insert(tk.END, f"{log['timestamp']} | {log['event']} | {log['description']}\n\n")

    except:
        log_box.insert(tk.END, "No logs found.")

# UI Setup
root = tk.Tk()
root.title("Tamper-Proof Logging Dashboard")
root.geometry("600x500")

# Title
tk.Label(root, text="Secure Logging System", font=("Arial", 16, "bold")).pack(pady=10)

# Inputs
tk.Label(root, text="Event").pack()
entry_event = tk.Entry(root, width=40)
entry_event.pack(pady=5)

tk.Label(root, text="Description").pack()
entry_desc = tk.Entry(root, width=40)
entry_desc.pack(pady=5)

# Buttons
tk.Button(root, text="Add Log", command=add_log_ui, bg="green", fg="white").pack(pady=5)
tk.Button(root, text="Verify Logs", command=verify_ui, bg="blue", fg="white").pack(pady=5)
tk.Button(root, text="Refresh Logs", command=load_logs).pack(pady=5)

# Log display
log_box = tk.Text(root, height=15, width=70)
log_box.pack(pady=10)

# Load logs initially
load_logs()

root.mainloop()
