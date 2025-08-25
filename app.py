import math
import random
import pandas as pd
import streamlit as st
from collections import defaultdict

# -----------------------------
# Login system
# -----------------------------
VALID_USERS = {
    "Fahadhassan": {"password": "Iobm1", "name": "Fahad Hassan"},
    "Alihasnain": {"password": "Iobm2", "name": "Ali Hasnain"},
    "Habibullah": {"password": "Iobm3", "name": "Habibullah"},
    "Rabiyasabri": {"password": "Iobm4", "name": "Rabiya Sabri"},
}

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def login():
    st.title("🔐 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in VALID_USERS and VALID_USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome {VALID_USERS[username]['name']} 👋")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.experimental_rerun()

# -----------------------------
# Main App (only if logged in)
# -----------------------------
if not st.session_state.logged_in:
    login()
else:
    user_fullname = VALID_USERS[st.session_state.username]["name"]

    # Page setup
    st.set_page_config(page_title="📊 Semester Schedule Generator", layout="wide")
    st.title("📊 Semester Schedule Generator")

    # Sidebar
    st.sidebar.write(f"👤 Logged in as **{user_fullname}**")
    if st.sidebar.button("Logout"):
        logout()

    st.sidebar.header("📖 How to Use")
    st.sidebar.markdown("""
    1. Upload the **Catalog file** in CSV or Excel format.  
    2. Ensure the following columns are present:  
       - `course_code`  
       - `course_title`  
       - `Semester`  
       - `Program`  
       - `Pre-Req`  
       - `Elective`  
       - `Catalog code`  
    3. Example format:
    """)
    
    # Sample CSV styled like Excel
    sample_data = {
        "course_code": ["ACS101", "BCN101", "MGT101", "MAT102", "SSC101", "ECN101", 
                        "CSP111", "CSP111L", "CSP121", "CSP121L", "BCN101", "PHY111", 
                        "PHY111L", "MAT110"],
        "course_title": [
            "Introduction to Financial Accounting", "Academic English", "Principles of Management", 
            "Business Mathematics and Statistics", "Introduction To Psychology", "Principles of Microeconomics",
            "Intro to Info. & Comm. Technology [GER]", "Intro to Info. & Comm. Technology Lab", 
            "Programming Fundamentals [CC]", "Programming Fundamentals Lab", "Academic English [GER]", 
            "Applied Physics [GER]", "Applied Physics Lab", "Calculus and Analytical Geometry [GER]"
        ],
        "Semester": ["one"] * 14,
        "Program": [
            "BBA (Honors) 4Y", "BBA (Honors) 4Y", "BBA (Honors) 4Y", "BBA (Honors) 4Y", 
            "BBA (Honors) 4Y", "BBA (Honors) 4Y", 
            "BS COMPUTER SCIENCE (BS CS)", "BS COMPUTER SCIENCE (BS CS)", "BS COMPUTER SCIENCE (BS CS)", 
            "BS COMPUTER SCIENCE (BS CS)", "BS COMPUTER SCIENCE (BS CS)", "BS COMPUTER SCIENCE (BS CS)", 
            "BS COMPUTER SCIENCE (BS CS)", "BS COMPUTER SCIENCE (BS CS)"
        ],
        "Pre-Req": ["" for _ in range(14)],
        "Elective": ["" for _ in range(14)],
        "Catalog code": ["" for _ in range(14)],
    }
    st.sidebar.dataframe(pd.DataFrame(sample_data))

    # -----------------------------
    # Keep rest of your functionalities (upload, timetable generation, etc.)
    # -----------------------------
    # (Paste your existing functionality code here without changes)
