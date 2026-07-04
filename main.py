# main.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import csv
import re
import sys
import os
# ================== GET USER FROM LOGIN ==================
if len(sys.argv) > 1:
    current_user = sys.argv[1]
else:
    current_user = "Manny Soto"  # fallback if run directly

print(f"Logged in as: {current_user}")

# ---------------- THEME ----------------
BG = "#1e1e1e"
CARD = "#2a2a2a"
FG = "#ffffff"
BTN = "#3a3a3a"
ELECTRIC_BLUE = "#00E5FF"

# ---------------- STATE ----------------
clock_in_time = None
active_job_site = None
active_job_number = None
active_job_type = None

# ---------------- TIME HELPERS ----------------
def now():
    return datetime.now()

def calc_hours(start, end):
    return round((end - start).total_seconds() / 3600, 2)

def format_hours_minutes(hours_decimal):
    total_minutes = int(round(hours_decimal * 60))
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours} Hours and {minutes} Minutes"

# ---------------- JOB NUMBER VALIDATION ----------------
def validate_job_number(job_num):
    pattern = r"^\d{2}-\d{3}$"
    return re.match(pattern, job_num.strip()) is not None

# ---------------- UPDATE JOB NUMBER OPTIONS ----------------
def update_job_number_options(event=None):
    site = job_site.get().strip()
    if site == "Clarity":
        job_number['values'] = ["Clarityadmin", "Clarity Drivetime"]
    else:
        job_number['values'] = ["Clarityadmin", "Clarity Drivetime"]

# ---------------- SAVE ----------------
def save_row(row):
    with open("hours_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    tag = ()
    if str(row[3]).strip().lower() == "idk":
        tag = ("idk",)

    tree.insert("", "end", values=row, tags=tag)

# ---------------- VALIDATION ----------------
def validate_inputs():
    if not job_site.get().strip():
        status.config(text="❌ Job Site required")
        return False

    job_num = job_number.get().strip()
    if not job_num:
        status.config(text="❌ Job Number required")
        return False

    return True

# ---------------- CLOCK IN ----------------
def clock_in():
    global clock_in_time, active_job_site, active_job_number, active_job_type

    if clock_in_time:
        status.config(text="❌ Already clocked in")
        return

    if not validate_inputs():
        return

    clock_in_time = now()
    active_job_site = job_site.get().strip()
    active_job_number = job_number.get().strip()
    active_job_type = job_type.get().strip()

    active_banner.config(
        text=f"ACTIVE JOB: {active_job_site} | #{active_job_number} | {active_job_type}"
    )

    status.config(text=f"Clocked In @ {clock_in_time.strftime('%I:%M %p')}")

# ---------------- CLOCK OUT ----------------
def clock_out():
    global clock_in_time, active_job_site, active_job_number, active_job_type

    if not clock_in_time:
        status.config(text="❌ Not clocked in")
        return

    end = now()
    hrs_decimal = calc_hours(clock_in_time, end)
    hours_display = format_hours_minutes(hrs_decimal)
    date_str = end.strftime("%m/%d/%Y")

    row = [
        current_user,
        date_str,
        active_job_site,
        active_job_number,
        active_job_type,
        clock_in_time.strftime("%I:%M %p"),
        end.strftime("%I:%M %p"),
        hours_display
    ]

    save_row(row)

    clock_in_time = None
    active_job_site = None
    active_job_number = None
    active_job_type = None

    active_banner.config(text="NO ACTIVE JOB")
    status.config(text="Clocked Out")

# ---------------- TRANSFER POPUP ----------------
def open_transfer_popup():
    global clock_in_time, active_job_site, active_job_number, active_job_type

    if not clock_in_time:
        status.config(text="❌ Not clocked in")
        return

    popup = tk.Toplevel(root)
    popup.title("Transfer Job")
    popup.geometry("380x340")
    popup.configure(bg=BG)

    tk.Label(popup, text="New Job Site", bg=BG, fg=FG).pack(pady=5)
    new_site = ttk.Combobox(popup, values=["Clarity"], state="normal")
    new_site.set(" ")
    new_site.pack(pady=5)

    tk.Label(popup, text="New Job Number", bg=BG, fg=FG).pack(pady=5)
    new_job = ttk.Combobox(popup,
                           values=["Clarityadmin", "Clarity Drivetime"],
                           state="normal")
    new_job.pack(pady=5)

    tk.Label(popup, text="New Job Type", bg=BG, fg=FG).pack(pady=5)
    new_type = ttk.Combobox(popup,
                            values=["Installation", "Repair", "Maintenance", "Service Call", "Other"],
                            state="normal")
    new_type.pack(pady=5)

    def submit():
        global clock_in_time, active_job_site, active_job_number, active_job_type

        site = new_site.get().strip()
        job = new_job.get().strip()
        jtype = new_type.get().strip()

        if not site or not job or not jtype:
            status.config(text="❌ All fields required")
            return

        # Save current job
        end = now()
        hrs_decimal = calc_hours(clock_in_time, end)
        hours_display = format_hours_minutes(hrs_decimal)
        date_str = end.strftime("%m/%d/%Y")

        row = [
            current_user,
            date_str,
            active_job_site,
            active_job_number,
            active_job_type,
            clock_in_time.strftime("%I:%M %p"),
            end.strftime("%I:%M %p"),
            hours_display
        ]

        save_row(row)

        # Switch to new job
        clock_in_time = end
        active_job_site = site
        active_job_number = job
        active_job_type = jtype

        job_site.set(site)
        job_number.set(job)
        job_type.set(jtype)

        active_banner.config(
            text=f"ACTIVE JOB: {active_job_site} | #{active_job_number} | {active_job_type}"
        )

        status.config(
            text=f"Transferred & Clocked In @ {end.strftime('%I:%M %p')}"
        )

        popup.destroy()

    tk.Button(popup, text="Submit Transfer", command=submit,
              bg=BTN, fg=FG, width=20).pack(pady=20)


# ---------------- EXPORT CSV ----------------
import os


def export_csv():
    try:
        with open("hours_log.csv", "r", newline="") as infile:
            content = infile.read()

        export_filename = "hours_export.csv"

        with open(export_filename, "w", newline="") as outfile:
            outfile.write(content)

        status.config(text=f"✅ Exported successfully to {export_filename}")

        # Open the folder containing the file
        folder = os.path.dirname(os.path.abspath(export_filename))
        if os.name == "nt":  # Windows
            os.startfile(folder)
        elif os.name == "posix":  # macOS / Linux
            os.system(f'open "{folder}"' if sys.platform == "darwin" else f'xdg-open "{folder}"')

    except FileNotFoundError:
        status.config(text="❌ No log file found yet")
    except Exception as e:
        status.config(text="❌ Export failed")
        print(e)

# ---------------- UI ----------------
root = tk.Tk()
root.title("Tech Hours Logger")
root.geometry("1050x720")
root.configure(bg=BG)

main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=20, pady=20)

# Top Left "clarity."
tk.Label(root, text="clarity.", bg=BG, fg=ELECTRIC_BLUE, font=("Arial", 16, "bold")).place(x=20, y=10)

# ACTIVE JOB BANNER
active_banner = tk.Label(main, text="NO ACTIVE JOB", bg="#111111", fg=ELECTRIC_BLUE,
                         font=("Arial", 14, "bold"), pady=10)
active_banner.pack(fill="x", pady=10)

# FORM
form = tk.Frame(main, bg=CARD)
form.pack(fill="x", pady=10)

tk.Label(form, text="Tech Name", bg=CARD, fg=FG).grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Label(form, text=current_user, bg=CARD, fg=FG).grid(row=0, column=1, sticky="w")

tk.Label(form, text="Job Site", bg=CARD, fg=FG).grid(row=1, column=0, padx=10, pady=5, sticky="e")
job_site = ttk.Combobox(form, values=["Clarity"], state="normal", width=30)
job_site.set("")
job_site.grid(row=1, column=1, padx=5, pady=5)
job_site.bind("<<ComboboxSelected>>", update_job_number_options)
job_site.bind("<KeyRelease>", update_job_number_options)

tk.Label(form, text="Job Number", bg=CARD, fg=FG).grid(row=2, column=0, padx=10, pady=5, sticky="e")
job_number = ttk.Combobox(form, state="normal", width=30)
job_number.grid(row=2, column=1, padx=5, pady=5)

tk.Label(form, text="Job Type", bg=CARD, fg=FG).grid(row=3, column=0, padx=10, pady=5, sticky="e")
job_type = ttk.Combobox(form, values=["Installation", "Repair", "Maintenance", "Service Call", "Other"],
                        state="normal", width=30)
job_type.grid(row=3, column=1, padx=5, pady=5)

# BUTTONS
btns = tk.Frame(main, bg=BG)
btns.pack(fill="x", pady=10)

tk.Button(btns, text="Clock In", command=clock_in, bg=BTN, fg=FG, width=12).pack(side="left", padx=5)
tk.Button(btns, text="Clock Out", command=clock_out, bg=BTN, fg=FG, width=12).pack(side="left", padx=5)
tk.Button(btns, text="Transfer", command=open_transfer_popup, bg=BTN, fg=FG, width=12).pack(side="left", padx=5)

# New Export Button
tk.Button(btns, text="Export CSV", command=export_csv, bg="#00cc88", fg="#ffffff", width=12).pack(side="left", padx=5)
# STATUS
status = tk.Label(main, text="Ready", bg=BG, fg=ELECTRIC_BLUE, font=("Arial", 12, "bold"))
status.pack(pady=5)

# TABLE
table_frame = tk.Frame(main)
table_frame.pack(fill="both", expand=True)

columns = ("Tech", "Date", "Site", "Job #", "Job Type", "Start", "End", "Hours")

tree = ttk.Treeview(table_frame, columns=columns, show="headings")

for c in columns:
    tree.heading(c, text=c)
    tree.column(c, width=110 if c in ["Date", "Job #"] else 130)

tree.tag_configure("idk", foreground="red")
tree.pack(fill="both", expand=True)

root.mainloop()