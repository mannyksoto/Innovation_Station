import streamlit as st
from datetime import datetime
import pandas as pd
import csv
import os
from main import run_app 

run_app()
st.set_page_config(page_title="Clarity Hours Logger", layout="wide")

# Users
USERS = {
    "Manny Soto": "1234",
    "Admin": "admin",
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.clock_in_time = None
    st.session_state.active_job_site = None
    st.session_state.active_job_number = None
    st.session_state.active_job_type = None

# LOGIN
if not st.session_state.logged_in:
    st.title("clarity.")
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login", type="primary"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

# MAIN APP
st.title("clarity.")
st.write(f"Logged in as: **{st.session_state.current_user}**")

# Dynamic Job Number options
def get_job_numbers(site):
    if site == "Clarity":
        return ["Clarityadmin", "Clarity Drivetime"]
    return ["Clarityadmin", "Clarity Drivetime"]

# Form
col1, col2, col3 = st.columns(3)
with col1:
    job_site = st.text_input("Job Site", key="job_site")
with col2:
    job_number = st.selectbox("Job Number", options=get_job_numbers(job_site), key="job_number")
with col3:
    job_type = st.selectbox("Job Type", 
                           ["Installation", "Repair", "Maintenance", "Service Call", "Other"], 
                           key="job_type")

# Buttons
col1, col2, col3, col4 = st.columns(4)

if col1.button("Clock In", type="primary", use_container_width=True):
    if job_site and job_number:
        st.session_state.clock_in_time = datetime.now()
        st.session_state.active_job_site = job_site
        st.session_state.active_job_number = job_number
        st.session_state.active_job_type = job_type
        st.success(f"Clocked In at {st.session_state.clock_in_time.strftime('%I:%M %p')}")
    else:
        st.error("Job Site and Job Number required")

if col2.button("Clock Out", type="secondary", use_container_width=True):
    if st.session_state.clock_in_time:
        end = datetime.now()
        hours = round((end - st.session_state.clock_in_time).total_seconds() / 3600, 2)
        total_min = int(hours * 60)
        h = total_min // 60
        m = total_min % 60

        row = [
            st.session_state.current_user,
            end.strftime("%m/%d/%Y"),
            st.session_state.active_job_site,
            st.session_state.active_job_number,
            st.session_state.active_job_type,
            st.session_state.clock_in_time.strftime("%I:%M %p"),
            end.strftime("%I:%M %p"),
            f"{h} Hours and {m} Minutes"
        ]

        with open("hours_log.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        st.success(f"Clocked Out - {h} Hours and {m} Minutes")
        st.session_state.clock_in_time = None
    else:
        st.warning("Not clocked in")

if col3.button("Transfer", use_container_width=True):
    st.info("Transfer function coming soon - let me know what you want here")

if col4.button("Export CSV", use_container_width=True):
    if os.path.exists("hours_log.csv"):
        df = pd.read_csv("hours_log.csv")
        st.download_button("Download CSV", df.to_csv(index=False), "hours_log.csv", "text/csv")
    else:
        st.info("No records yet")

# Active Status
if st.session_state.clock_in_time:
    st.info(f"**ACTIVE**: {st.session_state.active_job_site} | #{st.session_state.active_job_number} | {st.session_state.active_job_type}")

# History
st.subheader("History")
if os.path.exists("hours_log.csv"):
    df = pd.read_csv("hours_log.csv")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No hours logged yet.")

if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
