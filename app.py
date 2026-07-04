import streamlit as st
from datetime import datetime
import pandas as pd
import csv
import os

st.set_page_config(page_title="Clarity Hours Logger", layout="wide")
st.title("clarity.")
st.markdown("### Tech Hours Logger")

# User selection (simple for demo)
users = ["Manny Soto", "Admin", "Other"]
current_user = st.selectbox("Select User", users)

# Session state
if 'clock_in_time' not in st.session_state:
    st.session_state.clock_in_time = None
    st.session_state.active_job_site = None
    st.session_state.active_job_number = None
    st.session_state.active_job_type = None

# Form
col1, col2 = st.columns(2)
with col1:
    job_site = st.text_input("Job Site", value="Clarity" if current_user else "")
with col2:
    job_number = st.text_input("Job Number")

job_type = st.selectbox("Job Type", ["Installation", "Repair", "Maintenance", "Service Call", "Other"])

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
            current_user,
            end.strftime("%m/%d/%Y"),
            st.session_state.active_job_site,
            st.session_state.active_job_number,
            st.session_state.active_job_type,
            st.session_state.clock_in_time.strftime("%I:%M %p"),
            end.strftime("%I:%M %p"),
            f"{h} Hours and {m} Minutes"
        ]

        with open("hours_log.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        st.success(f"Clocked Out - {h} Hours and {m} Minutes")
        st.session_state.clock_in_time = None
    else:
        st.warning("Not clocked in")

if col3.button("Export CSV", use_container_width=True):
    if os.path.exists("hours_log.csv"):
        df = pd.read_csv("hours_log.csv")
        st.download_button("Download CSV", df.to_csv(index=False), "hours_log.csv", "text/csv")
    else:
        st.info("No records yet")

# Show current status
if st.session_state.clock_in_time:
    st.info(f"**ACTIVE**: {st.session_state.active_job_site} | {st.session_state.active_job_number}")

# Show history
if os.path.exists("hours_log.csv"):
    st.subheader("Hours History")
    df = pd.read_csv("hours_log.csv")
    st.dataframe(df, use_container_width=True)