from tamper_log import add_log

def fake_login():
    print("===== Secure Login =====")
    
    username = input("Enter Username: ")
    password = input("Enter Password: ")

    print("\n ALERT: Suspicious login attempt detected!")

    # Log this attempt securely
    add_log("LOGIN_ATTEMPT", f"Username: {username}, Password: {password}")

    print("This activity has been recorded.")

fake_login()
