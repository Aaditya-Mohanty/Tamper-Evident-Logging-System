import hashlib
import json
from datetime import datetime

log_file = "logs.json"

def create_first_log():
    first_log = {
        "timestamp": str(datetime.now()),
        "event": "GENESIS",
        "description": "First log entry",
        "previous_hash": "0",
    }
    first_log["hash"] = generate_hash(first_log)
    
    with open(log_file, "w") as f:
        json.dump([first_log], f, indent=4)

def generate_hash(log):
    temp_log = {
        "timestamp": log["timestamp"],
        "event": log["event"],
        "description": log["description"],
        "previous_hash": log["previous_hash"]
    }
    
    log_string = json.dumps(temp_log, sort_keys=True)
    return hashlib.sha256(log_string.encode()).hexdigest()

def add_log(event, description):
    with open(log_file, "r") as f:
        logs = json.load(f)

    last_log = logs[-1]

    new_log = {
        "timestamp": str(datetime.now()),
        "event": event,
        "description": description,
        "previous_hash": last_log["hash"]
    }

    new_log["hash"] = generate_hash(new_log)

    logs.append(new_log)

    with open(log_file, "w") as f:
        json.dump(logs, f, indent=4)

    print("Log added successfully!")

def verify_logs():
    with open(log_file, "r") as f:
        logs = json.load(f)

    for i in range(1, len(logs)):
        current = logs[i]
        previous = logs[i-1]

        if current["previous_hash"] != previous["hash"]:
            print("⚠️ Tampering detected at log", i)
            return

        if generate_hash(current) != current["hash"]:
            print("⚠️ Log modified at", i)
            return

    print("✅ Logs are secure. No tampering found.")

def menu():
    while True:
        print("\n1. Add Log")
        print("2. Verify Logs")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            event = input("Enter event: ")
            desc = input("Enter description: ")
            add_log(event, desc)

        elif choice == "2":
            verify_logs()

        elif choice == "3":
            break

        else:
            print("Invalid choice")

try:
    open(log_file)
except:
    create_first_log()

if __name__ == "__main__":
    menu()
