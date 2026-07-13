import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import csv
import os

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="ClaritySync",
    layout="wide"
)

# ==========================
# TIMEZONE
# ==========================

def now():
    return datetime.now(ZoneInfo("America/Chicago"))

# ==========================
# USERS
# ==========================

USERS = {
    "Manny.Soto".lower(): "12345",
    "Admin": "admin",
}

# ==========================
# SESSION STATE
# ==========================

defaults = {
    "logged_in": False,
    "current_user": None,
    "clock_in_time": None,
    "active_job_site": None,
    "active_job_number": None,
    "active_job_type": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==========================
# HELPERS
# ==========================

def format_hours(hours_decimal):
    mins = int(round(hours_decimal * 60))
    return f"{mins // 60} Hours {mins % 60} Minutes"


def save_row(row):

    file_exists = os.path.exists("hours_log.csv")

    with open(
        "hours_log.csv",
        "a",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "Tech",
                "Date",
                "Site",
                "Job #",
                "Type",
                "Start",
                "End",
                "Hours"
            ])

        writer.writerow(row)
# ==========================
# TRANSFER DIALOG
# ==========================

@st.dialog("Transfer Job")
def transfer_dialog():

    new_site = st.selectbox(
        "New Site",
        ["Clarity"]
    )

    new_job = st.selectbox(
        "New Job #",
        [
            "Clarityadmin",
            "Clarity Drivetime"
        ]
    )

    new_type = st.selectbox(
        "New Job Type",
        [
            "Installation",
            "Preventative Maintanence",
            "Service Call",
            "Other"
        ]
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Submit Transfer", type="primary"):

            end = now()

            hours = round(
                (
                    end -
                    st.session_state.clock_in_time
                ).total_seconds() / 3600,
                2
            )

            row = [
                st.session_state.current_user,
                end.strftime("%m/%d/%Y"),
                st.session_state.active_job_site,
                st.session_state.active_job_number,
                st.session_state.active_job_type,
                st.session_state.clock_in_time.strftime("%I:%M %p"),
                end.strftime("%I:%M %p"),
                format_hours(hours)
            ]

            save_row(row)

            # immediately begin new job

            st.session_state.clock_in_time = now()
            st.session_state.active_job_site = new_site
            st.session_state.active_job_number = new_job
            st.session_state.active_job_type = new_type

            st.success("Transfer completed successfully")
            st.rerun()

    with col2:

        if st.button("Cancel"):
            st.rerun()
# ==========================
# LOGIN
# ==========================

if not st.session_state.logged_in:

    st.markdown(
        "<h1 style='color:#00E5FF'>claritysync.</h1>",
        unsafe_allow_html=True
    )

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", type="primary"):

        if username in USERS and USERS[username] == password:

            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.rerun()

        else:
            st.error("Incorrect username or password")

    st.stop()

# ==========================
# HEADER
# ==========================

st.markdown(
    "<h1 style='color:#00E5FF'>claritysync.</h1>",
    unsafe_allow_html=True
)

st.write(
    f"Logged in as **{st.session_state.current_user}**"
)

# ==========================
# ACTIVE JOB BANNER
# ==========================

if st.session_state.clock_in_time:

    st.markdown(
        f"""
        <div style="
            background:#111;
            color:#00E5FF;
            padding:15px;
            border-radius:10px;
            text-align:center;
            font-weight:bold;
            margin-bottom:20px;
        ">
        ACTIVE:
        {st.session_state.active_job_site}
        |
        {st.session_state.active_job_number}
        |
        {st.session_state.active_job_type}
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        """
        <div style="
            background:#111;
            color:#00E5FF;
            padding:15px;
            border-radius:10px;
            text-align:center;
            font-weight:bold;
            margin-bottom:20px;
        ">
        NO ACTIVE JOB
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================
# JOB FORM
# ==========================

col1, col2, col3 = st.columns(3)

with col1:
    job_site = st.selectbox(
        "Job Site",
        ["Clarity"]
    )

with col2:
    job_number = st.selectbox(
        "Job Number",
        [
            "Clarityadmin",
            "Clarity Drivetime"
        ]
    )

with col3:
    job_type = st.selectbox(
        "Job Type",
        [
            "Install",
            "Preventative Maintenance",
            "Service",
            "Other"
        ]
    )

# ==========================
# BUTTONS
# ==========================

b1, b2, b3, b4 = st.columns(4)

# CLOCK IN

if b1.button(
    "Clock In",
    type="primary",
    use_container_width=True
):

    if st.session_state.clock_in_time:

        st.error("Already clocked in")

    else:

        st.session_state.clock_in_time = now()

        st.session_state.active_job_site = job_site
        st.session_state.active_job_number = job_number
        st.session_state.active_job_type = job_type

        st.success(
            f"Clocked in at {st.session_state.clock_in_time.strftime('%I:%M %p')}"
        )

# CLOCK OUT

if b2.button(
    "Clock Out",
    use_container_width=True
):

    if not st.session_state.clock_in_time:

        st.error("Not clocked in")

    else:

        end = now()

        hours = round(
            (end - st.session_state.clock_in_time).total_seconds() / 3600,
            2
        )

        row = [
            st.session_state.current_user,
            end.strftime("%m/%d/%Y"),
            st.session_state.active_job_site,
            st.session_state.active_job_number,
            st.session_state.active_job_type,
            st.session_state.clock_in_time.strftime("%I:%M %p"),
            end.strftime("%I:%M %p"),
            format_hours(hours)
        ]

        save_row(row)

        st.session_state.clock_in_time = None
        st.session_state.active_job_site = None
        st.session_state.active_job_number = None
        st.session_state.active_job_type = None

        st.success("Clocked out successfully")

if b3.button(
    "Transfer",
    use_container_width=True
):

    if not st.session_state.clock_in_time:
        st.error("Not clocked in")
    else:
        transfer_dialog()
# EXPORT

with b4:

    if os.path.exists("hours_log.csv"):

        with open("hours_log.csv", "rb") as file:

            st.download_button(
                "Export CSV",
                file,
                file_name="hours_log.csv",
                mime="text/csv",
                use_container_width=True
            )




# ==========================
# ADMIN HISTORY ONLY
# ==========================

if st.session_state.current_user == "Admin":

    st.divider()
    st.subheader("Hours History")

    if os.path.exists("hours_log.csv"):

        df = pd.read_csv("hours_log.csv")

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.info("No logged hours yet.")

# ==========================
# LOGOUT
# ==========================

st.divider()

if st.button("Logout"):

    for key, value in defaults.items():
        st.session_state[key] = value

    st.rerun()
