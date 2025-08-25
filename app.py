import os
import math
import random
import pandas as pd
import streamlit as st
from collections import defaultdict

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# User credentials and display names
USERS = {
    "fahadhassan": {"password": "iobm1", "display_name": "Fahad Hassan"},
    "alihasnain": {"password": "iobm2", "display_name": "Ali Hasnain"},
    "habibullah": {"password": "iobm3", "display_name": "Habibullah"},
    "rabiyasabri": {"password": "iobm4", "display_name": "Rabiya Sabri"}
}

def login_page():
    st.set_page_config(page_title="🔐 Login - Semester Schedule Generator", layout="centered")
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🔐 Semester Schedule Generator</h1>
        <h3>Please Login to Continue</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown("### Login")
            username = st.text_input("Username", placeholder="Enter your username").lower()
            password = st.text_input("Password", type="password", placeholder="Enter your password").lower()
            
            if st.button("Login", use_container_width=True):
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid username or password!")

def how_to_use_section():
    st.markdown("## 📖 How to Use This Application")
    
    st.markdown("### Step 1: Prepare Your CSV File")
    st.markdown("Create a CSV file with the following **required columns** (column names should be exactly as shown):")
    
    # Required fields info
    st.markdown("""
    **Required Fields:**
    - `course_code` - Course code (e.g., ACS101)
    - `course_title` - Course title (e.g., Introduction to Financial Accounting)
    - `semester` - Semester (e.g., one, two, three, etc.)
    - `program` - Program name (e.g., BBA (Honors) 4Y)
    """)
    
    st.markdown("### Step 2: Sample Data Format")
    st.markdown("Your CSV should look like this:")
    
    # Sample data in a nice table format
    sample_data = {
        'course_code': ['ACS101', 'BCN101', 'MGT101', 'MAT102', 'SSC101', 'ECN101', 'CSP111', 'CSP111L', 'CSP121', 'CSP121L', 'PHY111', 'PHY111L', 'MAT110'],
        'course_title': [
            'Introduction to Financial Accounting',
            'Academic English',
            'Principles of Management',
            'Business Mathematics and Statistics',
            'Introduction To Psychology',
            'Principles of Microeconomics',
            'Intro to Info. & Comm. Technology [GER]',
            'Intro to Info. & Comm. Technology Lab',
            'Programming Fundamentals [CC]',
            'Programming Fundamentals Lab',
            'Applied Physics [GER]',
            'Applied Physics Lab',
            'Calculus and Analytical Geometry [GER]'
        ],
        'semester': ['one'] * 6 + ['one'] * 7,
        'program': ['BBA (Honors) 4Y'] * 6 + ['BS COMPUTER SCIENCE (BS CS)'] * 7
    }
    
    sample_df = pd.DataFrame(sample_data)
    st.dataframe(sample_df, use_container_width=True)
    
    st.markdown("### Step 3: Upload and Generate")
    st.markdown("""
    1. Upload your CSV file using the file uploader in the sidebar
    2. Select the Program and Semester from the dropdown menus
    3. Enter the number of students
    4. Click "Generate Report" to create the schedule
    5. Download the generated timetable as CSV
    """)
    
    st.markdown("---")

def main_app():
    # Page setup
    st.set_page_config(page_title="📊 Semester Schedule Generator", layout="wide")
    
    # Header with logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📊 Semester Schedule Generator")
    with col2:
        st.markdown(f"**Welcome, {USERS[st.session_state.username]['display_name']}!**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
    
    # How to use section
    with st.expander("📖 How to Use This Application", expanded=False):
        how_to_use_section()
    
    # Sidebar
    st.sidebar.header("Input Parameters")

    # Upload option only
    uploaded_file = st.sidebar.file_uploader("Upload Catalog File", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                catalog_df = pd.read_csv(uploaded_file)
            else:
                catalog_df = pd.read_excel(uploaded_file, engine="openpyxl")
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.stop()
    else:
        st.warning("Please upload a file to continue.")
        st.stop()

    # Normalize columns
    catalog_df.columns = catalog_df.columns.str.lower()

    # Required columns check
    required_columns = ["program", "semester", "course_code", "course_title"]
    missing_columns = [col for col in required_columns if col not in catalog_df.columns]

    if missing_columns:
        st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
        st.stop()

    # Dropdowns
    program_filter = st.sidebar.selectbox("Select Program", sorted(catalog_df["program"].unique()))
    semester_filter = st.sidebar.selectbox("Select Semester", sorted(catalog_df["semester"].unique()))
    student_count = st.sidebar.number_input("Enter Number of Students", min_value=1, step=1)

    # Time slots (AM/PM format)
    weekday_slots = [
        ("9:00 AM", "10:30 AM"),
        ("10:45 AM", "12:15 PM"),
        ("12:30 PM", "2:00 PM"),
        ("2:15 PM", "3:45 PM")
    ]

    weekend_slots = [
        ("9:00 AM", "12:00 PM"),
        ("2:00 PM", "5:00 PM")
    ]

    mba_slots = [
        ("9:00 AM", "12:00 PM"),  # Weekend morning
        ("2:00 PM", "5:00 PM"),   # Weekend afternoon
        ("6:30 PM", "9:30 PM")    # Weekday evening
    ]

    weekday_days = ["Monday", "Tuesday", "Wednesday", "Thursday"]
    weekend_days = ["Saturday", "Sunday"]

    def assign_schedule(df):
        """
        Improved scheduling function that avoids clashes and distributes weekend classes better
        """
        section_occupied_slots = defaultdict(set)  # section -> {(day, time)}
        course_slot_usage = defaultdict(lambda: defaultdict(int))  # course -> slot -> count
        
        schedule = []
        program_name = df["program"].iloc[0].lower() if not df.empty else ""
        is_mba = "mba" in program_name
        
        # Get all available slots
        if is_mba:
            all_slots = []
            for slot in mba_slots:
                if slot == ("6:30 PM", "9:30 PM"):
                    for day in weekday_days:
                        all_slots.append((day, slot))
                else:
                    for day in weekend_days:
                        all_slots.append((day, slot))
        else:
            all_slots = []
            for slot in weekday_slots:
                for day1, day2 in [("Monday", "Wednesday"), ("Tuesday", "Thursday")]:
                    all_slots.append((f"{day1} / {day2}", slot))
            for slot in weekend_slots:
                for day in weekend_days:
                    all_slots.append((day, slot))
        
        total_sections = df["required sections"].max() if not df.empty else 0
        
        if not is_mba:
            weekend_preference = {}
            for section in range(1, total_sections + 1):
                weekend_preference[section] = random.random() < 0.3
        
        for _, row in df.iterrows():
            course = row["course_title"]
            course_code = row["course_code"]
            sections = row["required sections"]
            
            for sec in range(1, sections + 1):
                slot_assigned = False
                
                if is_mba:
                    candidate_slots = all_slots.copy()
                else:
                    section_weekend_classes = sum(1 for (d, t) in section_occupied_slots[sec] 
                                                if any(wd in str(d) for wd in weekend_days))
                    section_weekday_classes = len(section_occupied_slots[sec]) - section_weekend_classes
                    prefer_weekend = weekend_preference.get(sec, False)
                    
                    if section_weekend_classes >= 2:
                        candidate_slots = [(d, s) for (d, s) in all_slots if "/" in str(d)]
                    elif section_weekday_classes >= 6:
                        weekend_slots_list = [(d, s) for (d, s) in all_slots if any(wd in str(d) for wd in weekend_days)]
                        weekday_slots_list = [(d, s) for (d, s) in all_slots if "/" in str(d)]
                        candidate_slots = weekend_slots_list + weekday_slots_list
                    else:
                        weekend_slots_list = [(d, s) for (d, s) in all_slots if any(wd in str(d) for wd in weekend_days)]
                        weekday_slots_list = [(d, s) for (d, s) in all_slots if "/" in str(d)]
                        candidate_slots = weekend_slots_list + weekday_slots_list if prefer_weekend else weekday_slots_list + weekend_slots_list
                
                candidate_slots.sort(key=lambda slot: course_slot_usage[course][slot])
                
                for slot_key in candidate_slots:
                    day, slot = slot_key
                    if slot_key in section_occupied_slots[sec]:
                        continue
                    if not is_mba and any(wd in str(day) for wd in weekend_days):
                        section_weekend_days = [d for (d, t) in section_occupied_slots[sec] 
                                              if any(wd in str(d) for wd in weekend_days)]
                        if section_weekend_days and day not in section_weekend_days:
                            existing_weekend_day = next(iter([d for d in section_weekend_days if d in weekend_days]), None)
                            if existing_weekend_day and (existing_weekend_day, slot) not in section_occupied_slots[sec]:
                                day = existing_weekend_day
                                slot_key = (day, slot)
                            else:
                                continue
                    max_usage_allowed = max(1, (sections // len(all_slots)) + 1)
                    if course_slot_usage[course][slot_key] >= max_usage_allowed:
                        continue
                    section_occupied_slots[sec].add(slot_key)
                    course_slot_usage[course][slot_key] += 1
                    schedule.append((sec, day, f"{slot[0]} - {slot[1]}"))
                    slot_assigned = True
                    break
                
                if not slot_assigned:
                    for slot_key in candidate_slots:
                        day, slot = slot_key
                        if slot_key not in section_occupied_slots[sec]:
                            section_occupied_slots[sec].add(slot_key)
                            course_slot_usage[course][slot_key] += 1
                            schedule.append((sec, day, f"{slot[0]} - {slot[1]}"))
                            slot_assigned = True
                            break
                
                if not slot_assigned:
                    st.warning(f"Could not find optimal slot for {course_code} Section {sec}. Using random assignment.")
                    slot_key = random.choice(all_slots)
                    day, slot = slot_key
                    section_occupied_slots[sec].add(slot_key)
                    course_slot_usage[course][slot_key] += 1
                    schedule.append((sec, day, f"{slot[0]} - {slot[1]}"))
        
        return schedule

    # Generate report
    if st.sidebar.button("Generate Report"):
        df = catalog_df[
            (catalog_df["program"] == program_filter) & 
            (catalog_df["semester"] == semester_filter)
        ][["program", "course_code", "course_title"]].copy()
        
        if df.empty:
            st.warning("No courses found for the selected Program and Semester.")
        else:
            df["failed/withdrawn students"] = 0
            df["active students"] = student_count
            df["total student strength"] = student_count
            df["required sections"] = df["total student strength"].apply(lambda x: math.ceil(x / 40))
            df["section"] = ""
            df["name"] = "Faculty Member"
            df["ids"] = ""
            df["type name"] = ""
            
            schedule = assign_schedule(df)
            
            expanded_df = []
            sched_idx = 0
            
            for _, row in df.iterrows():
                for sec in range(1, row["required sections"] + 1):
                    new_row = row.copy()
                    new_row["section"] = sec
                    new_row["days"] = schedule[sched_idx][1]
                    new_row["time's"] = schedule[sched_idx][2]
                    expanded_df.append(new_row)
                    sched_idx += 1
            
            df = pd.DataFrame(expanded_df)
            df = df.sort_values(by=["section", "course_code"]).reset_index(drop=True)
            df = df[[
                "program", "section", "course_code", "course_title", "name", "ids", 
                "type name", "days", "time's", "failed/withdrawn students", 
                "active students", "total student strength", "required sections"
            ]]
            
            st.success("Report generated with improved timetable!")
            st.dataframe(df)
            
            st.subheader("📋 Scheduling Summary")
            summary_data = []
            for section in df["section"].unique():
                section_data = df[df["section"] == section]
                weekend_count = sum(1 for day in section_data["days"] if any(wd in str(day) for wd in weekend_days))
                weekday_count = len(section_data) - weekend_count
                summary_data.append({
                    "Section": section,
                    "Weekend Classes": weekend_count,
                    "Weekday Classes": weekday_count,
                    "Total Classes": len(section_data)
                })
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"timetable_{program_filter}_{semester_filter}.csv",
                mime="text/csv",
            )

# Main application logic
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
