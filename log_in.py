# login.py
import tkinter as tk
import subprocess
import sys

# Hardcoded users
USERS = {
    "Manny Soto": "1234",
    "Admin": "admin",
    # Add more users here
}

def login_success(username):
    root.destroy()
    try:
        subprocess.Popen([sys.executable, "main.py", username])
    except Exception as e:
        print("Error launching main.py:", e)

# ---------------- LOGIN WINDOW ----------------
root = tk.Tk()
root.title("Clarity - Login")
root.geometry("420x410")          # Slightly taller
root.configure(bg="#1e1e1e")
root.resizable(False, False)

# Title
tk.Label(root, text="clarity.", font=("Arial", 28, "bold"),
         bg="#1e1e1e", fg="#00E5FF").pack(pady=35)

tk.Label(root, text="Username", bg="#1e1e1e", fg="#ffffff", font=("Arial", 11)).pack(pady=(10,5))
username_entry = tk.Entry(root, bg="#2b2b2b", fg="#ffffff", insertbackground="white",
                          width=35, font=("Arial", 11), justify="center")
username_entry.pack(pady=5, ipady=8)

tk.Label(root, text="Password", bg="#1e1e1e", fg="#ffffff", font=("Arial", 11)).pack(pady=(15,5))
password_entry = tk.Entry(root, bg="#2b2b2b", fg="#ffffff", insertbackground="white",
                          width=35, font=("Arial", 11), show="•", justify="center")
password_entry.pack(pady=5, ipady=8)

status_label = tk.Label(root, text="", bg="#1e1e1e", fg="#ff6666", font=("Arial", 10))
status_label.pack(pady=15)

def attempt_login():
    user = username_entry.get().strip()
    pwd = password_entry.get().strip()

    if user in USERS and USERS[user] == pwd:
        login_success(user)
    else:
        status_label.config(text="❌ Incorrect username or password")

# Login Button - Larger height, but not too wide
login_btn = tk.Button(root, text="LOGIN", command=attempt_login,
                      bg="#00E5FF", fg="#1e1e1e", font=("Arial", 14, "bold"),
                      width=18, height=3)        # Adjusted size
login_btn.pack(pady=20)

# Press Enter to login
password_entry.bind("<Return>", lambda e: attempt_login())
username_entry.bind("<Return>", lambda e: password_entry.focus())

root.mainloop()