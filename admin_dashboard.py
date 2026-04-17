import tkinter as tk
import json

LOG_FILE = "logs.json"

def load_logs():
    log_box.delete(1.0, tk.END)

    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)

        for log in logs:
            log_box.insert(tk.END,
                f"{log['timestamp']} | {log['event']} | {log['description']}\n\n")

    except:
        log_box.insert(tk.END, "No logs found.")

root = tk.Tk()
root.title("Admin Dashboard - Security Logs")
root.geometry("600x400")

tk.Label(root, text="Log Monitoring Dashboard",
         font=("Arial", 16, "bold")).pack(pady=10)

tk.Button(root, text="Refresh Logs", command=load_logs).pack(pady=5)

log_box = tk.Text(root, height=20, width=70)
log_box.pack(pady=10)

load_logs()

root.mainloop()
