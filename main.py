import tkinter as tk
from tkinter import ttk
from datetime import datetime
import csv
import re
import sys
import os
def run_app(): 
    
# ================== USER ==================
current_user = sys.argv[1] if len(sys.argv) > 1 else "Manny Soto"

# ================== THEME ==================
BG = "#1e1e1e"
CARD = "#2a2a2a"
FG = "#ffffff"
BTN = "#3a3a3a"
ACCENT = "#00E5FF"
SUCCESS = "#00cc88"
DANGER = "#ff4d4d"

# ================== STATE ==================
clock_in_time = None
active_job = {
    "site": None,
    "number": None,
    "type": None
}

# ================== HELPERS ==================
def now():
    return datetime.now()

def calc_hours(start, end):
    return round((end - start).total_seconds() / 3600, 2)

def format_hours(hours_decimal):
    mins = int(round(hours_decimal * 60))
    return f"{mins // 60} Hours {mins % 60} Minutes"

def validate_job_number(job_num):
    return re.match(r"^\d{2}-\d{3}$", job_num.strip()) is not None

# ================== FILE ==================
def save_row(row):
    file_exists = os.path.isfile("hours_log.csv")
    with open("hours_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Tech", "Date", "Site", "Job #", "Type", "Start", "End", "Hours"])
        writer.writerow(row)

    tree.insert("", "end", values=row)

# ================== UI STATE ==================
def update_banner(text):
    active_banner.config(text=text)

def update_status(text, color=ACCENT):
    status.config(text=text, fg=color)

# ================== JOB VALIDATION ==================
def validate_inputs():
    if not job_site.get().strip():
        update_status("Job Site required", DANGER)
        return False

    if not job_number.get().strip():
        update_status("Job Number required", DANGER)
        return False

    if not job_type.get().strip():
        update_status("Job Type required", DANGER)
        return False

    return True

# ================== CLOCK IN ==================
def clock_in():
    global clock_in_time, active_job

    if clock_in_time:
        update_status("Already clocked in", DANGER)
        return

    if not validate_inputs():
        return

    clock_in_time = now()

    active_job = {
        "site": job_site.get().strip(),
        "number": job_number.get().strip(),
        "type": job_type.get().strip()
    }

    update_banner(f"ACTIVE: {active_job['site']} | #{active_job['number']} | {active_job['type']}")
    update_status(f"Clocked in at {clock_in_time.strftime('%I:%M %p')}")

# ================== CLOCK OUT ==================
def clock_out():
    global clock_in_time, active_job

    if not clock_in_time:
        update_status("Not clocked in", DANGER)
        return

    end = now()
    hours = calc_hours(clock_in_time, end)

    row = [
        current_user,
        end.strftime("%m/%d/%Y"),
        active_job["site"],
        active_job["number"],
        active_job["type"],
        clock_in_time.strftime("%I:%M %p"),
        end.strftime("%I:%M %p"),
        format_hours(hours)
    ]

    save_row(row)

    clock_in_time = None
    active_job = {"site": None, "number": None, "type": None}

    update_banner("NO ACTIVE JOB")
    update_status("Clocked out successfully", SUCCESS)

# ================== TRANSFER ==================
def open_transfer():
    global clock_in_time, active_job

    if not clock_in_time:
        update_status("Not clocked in", DANGER)
        return

    popup = tk.Toplevel(root)
    popup.title("Transfer Job")
    popup.geometry("400x350")
    popup.configure(bg=BG)

    tk.Label(popup, text="New Site", bg=BG, fg=FG).pack(pady=5)
    new_site = ttk.Combobox(popup, values=["Clarity"])
    new_site.pack()

    tk.Label(popup, text="New Job #", bg=BG, fg=FG).pack(pady=5)
    new_job = ttk.Combobox(popup, values=["Clarityadmin", "Clarity Drivetime"])
    new_job.pack()

    tk.Label(popup, text="New Type", bg=BG, fg=FG).pack(pady=5)
    new_type = ttk.Combobox(
        popup,
        values=["Installation", "Repair", "Maintenance", "Service Call", "Other"]
    )
    new_type.pack()

    def submit():
        global clock_in_time, active_job

        if not new_site.get() or not new_job.get() or not new_type.get():
            update_status("All fields required", DANGER)
            return

        end = now()
        hours = calc_hours(clock_in_time, end)

        # close old job
        row = [
            current_user,
            end.strftime("%m/%d/%Y"),
            active_job["site"],
            active_job["number"],
            active_job["type"],
            clock_in_time.strftime("%I:%M %p"),
            end.strftime("%I:%M %p"),
            format_hours(hours)
        ]

        save_row(row)

        # start new job
        clock_in_time = end
        active_job = {
            "site": new_site.get(),
            "number": new_job.get(),
            "type": new_type.get()
        }

        job_site.set(active_job["site"])
        job_number.set(active_job["number"])
        job_type.set(active_job["type"])

        update_banner(f"ACTIVE: {active_job['site']} | #{active_job['number']} | {active_job['type']}")
        update_status("Transfer complete", SUCCESS)

        popup.destroy()

    tk.Button(popup, text="Submit", command=submit, bg=BTN, fg=FG).pack(pady=20)

# ================== EXPORT ==================
def export_csv():
    try:
        src = "hours_log.csv"
        dst = "hours_export.csv"

        with open(src, "r") as f:
            data = f.read()

        with open(dst, "w") as f:
            f.write(data)

        update_status(f"Exported to {dst}", SUCCESS)

        folder = os.path.abspath(dst)
        if os.name == "nt":
            os.startfile(os.path.dirname(folder))
        else:
            os.system(f'open "{os.path.dirname(folder)}"' if sys.platform == "darwin"
                      else f'xdg-open "{os.path.dirname(folder)}"')

    except FileNotFoundError:
        update_status("No log file found", DANGER)

# ================== UI ==================
root = tk.Tk()
root.title("Clarity Time Tracker")
root.geometry("1050x720")
root.configure(bg=BG)

# HEADER
header = tk.Frame(root, bg=BG)
header.pack(fill="x", pady=10)

tk.Label(
    header,
    text="clarity.",
    font=("Arial", 18, "bold"),
    fg=ACCENT,
    bg=BG
).pack(side="left", padx=20)

tk.Label(
    header,
    text=f"Logged in as {current_user}",
    fg=FG,
    bg=BG
).pack(side="right", padx=20)

# ACTIVE BANNER
active_banner = tk.Label(
    root,
    text="NO ACTIVE JOB",
    bg="#111",
    fg=ACCENT,
    font=("Arial", 14, "bold"),
    pady=10
)
active_banner.pack(fill="x", padx=20)

# FORM
form = tk.Frame(root, bg=CARD)
form.pack(fill="x", padx=20, pady=10)

tk.Label(form, text="Job Site", bg=CARD, fg=FG).grid(row=0, column=0)
job_site = ttk.Combobox(form, values=["Clarity"], width=30)
job_site.grid(row=0, column=1, padx=5)

tk.Label(form, text="Job #", bg=CARD, fg=FG).grid(row=1, column=0)
job_number = ttk.Combobox(form, values=["Clarityadmin", "Clarity Drivetime"], width=30)
job_number.grid(row=1, column=1, padx=5)

tk.Label(form, text="Job Type", bg=CARD, fg=FG).grid(row=2, column=0)
job_type = ttk.Combobox(
    form,
    values=["Installation", "Repair", "Maintenance", "Service Call", "Other"],
    width=30
)
job_type.grid(row=2, column=1, padx=5)

# BUTTONS
btns = tk.Frame(root, bg=BG)
btns.pack(fill="x", padx=20, pady=10)

tk.Button(btns, text="Clock In", command=clock_in, bg=BTN, fg=FG, width=12).pack(side="left")
tk.Button(btns, text="Clock Out", command=clock_out, bg=BTN, fg=FG, width=12).pack(side="left", padx=5)
tk.Button(btns, text="Transfer", command=open_transfer, bg=BTN, fg=FG, width=12).pack(side="left", padx=5)
tk.Button(btns, text="Export CSV", command=export_csv, bg=SUCCESS, fg=FG, width=12).pack(side="left", padx=5)

# STATUS
status = tk.Label(root, text="Ready", bg=BG, fg=ACCENT, font=("Arial", 12, "bold"))
status.pack(pady=5)

# TABLE
columns = ("Tech", "Date", "Site", "Job #", "Type", "Start", "End", "Hours")

tree = ttk.Treeview(root, columns=columns, show="headings")
for c in columns:
    tree.heading(c, text=c)
    tree.column(c, width=130)

tree.pack(fill="both", expand=True, padx=20, pady=10)
run_app()

root.mainloop()
