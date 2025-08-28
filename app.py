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

# Available catalog files
CATALOG_FILES = {
    "2020-2021": "2020-21.csv",
    "2021-2022": "2021-22.csv", 
    "2022-2023": "2022-23.csv",
    "2023-2024": "2023-24.csv",
    "2024-2025": "2024-2025.csv",
    "2025-2026": "csvcatalog 2025-26 timetables.csv"
}

def load_catalog_data(catalog_year):
    """Load catalog data from the repository CSV file"""
    filename = CATALOG_FILES[catalog_year]
    
    # Try different encodings to handle various file formats
    encodings_to_try = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings_to_try:
        try:
            catalog_df = pd.read_csv(filename, encoding=encoding)
            st.info(f"Successfully loaded {filename} using {encoding} encoding")
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            if encoding == encodings_to_try[-1]:  # Last encoding attempt
                st.error(f"Error loading catalog file {filename}: {e}")
                return None, False
            continue
    else:
        st.error(f"Could not decode {filename} with any of the attempted encodings: {', '.join(encodings_to_try)}")
        return None, False
    
    try:
        # Normalize column names - handle both old and new format
        catalog_df.columns = catalog_df.columns.str.lower().str.strip()
        
        # Map old column names to new standard names if needed
        column_mapping = {
            'semester': 'semester',
            'program': 'program',
            'course_code': 'course_code',
            'course_title': 'course_title'
        }
        
        # Rename columns to standard format
        catalog_df = catalog_df.rename(columns=column_mapping)
        
        # Filter out rows where semester is missing (NaN or empty)
        initial_count = len(catalog_df)
        catalog_df = catalog_df.dropna(subset=['semester'])
        catalog_df = catalog_df[catalog_df['semester'].astype(str).str.strip() != '']
        final_count = len(catalog_df)
        
        if initial_count != final_count:
            st.info(f"Filtered out {initial_count - final_count} rows with missing semester data")
        
        # Handle missing course_code - fill with empty string instead of dropping
        catalog_df['course_code'] = catalog_df['course_code'].fillna('')
        catalog_df['course_title'] = catalog_df['course_title'].fillna('Unknown Course')
        
        # Convert semester values to lowercase for consistency
        catalog_df['semester'] = catalog_df['semester'].astype(str).str.lower().str.strip()
        
        return catalog_df, True
        
    except Exception as e:
        st.error(f"Error processing catalog file {filename}: {e}")
        return None, False

def login_page():
    st.set_page_config(page_title="🔐 Login - Hafali Smart Solutions", layout="centered")
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🔐 Hafali Smart Solutions</h1>
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
    
    st.markdown("### Step 1: Choose Your Data Source")
    st.markdown("""
    **Option 1: Use Institutional Catalogs** 📊
    - Select from available academic years (2020-21 to 2025-26)
    - Uses the institutional catalog directly from the system
    - No file upload needed
    
    **Option 2: Upload Your Own File** 📁
    - Select "Upload Your Own File" 
    - Upload your custom CSV with the required columns
    """)
    
    st.markdown("### Step 2: Required Fields for Custom Upload")
    st.markdown("If uploading your own file, ensure these **required columns** exist:")
    
    # Required fields info
    st.markdown("""
    **Required Fields:**
    - `course_code` - Course code (e.g., ACS101) - can be blank
    - `course_title` - Course title (e.g., Introduction to Financial Accounting)
    - `semester` - Semester (e.g., one, two, three, etc.) - **must not be blank**
    - `program` - Program name (e.g., BBA (Honors) 4Y)
    """)
    
    st.markdown("### Step 3: Sample Data Format")
    st.markdown("Your CSV should look like this:")
    
    # Sample data in a nice table format
    sample_data = {
        'course_code': ['ACS101', 'BCN101', '', 'MAT102', 'SSC101', 'ECN101'],
        'course_title': [
            'Introduction to Financial Accounting',
            'Academic English',
            'Special Topics in Management',
            'Business Mathematics and Statistics',
            'Introduction To Psychology',
            'Principles of Microeconomics'
        ],
        'semester': ['one', 'one', 'one', 'one', 'one', 'one'],
        'program': ['BBA (Honors) 4Y', 'BBA (Honors) 4Y', 'BBA (Honors) 4Y', 'BBA (Honors) 4Y', 'BBA (Honors) 4Y', 'BBA (Honors) 4Y']
    }
    
    sample_df = pd.DataFrame(sample_data)
    st.dataframe(sample_df, use_container_width=True)
    
    st.markdown("### Step 4: Generate Schedule")
    st.markdown("""
    1. Choose your data source (Catalog Year or Upload File)
    2. Select the Program and Semester from the dropdown menus
    3. Enter the number of students (for individual programs) or student counts for each program (for "All Programs")
    4. Click "Generate Report" to create the schedule
    5. Download the generated timetable as CSV
    """)
    
    st.markdown("---")

def main_app():
    # Page setup
    st.set_page_config(page_title="📊 Hafali Smart Solutions", layout="wide")
    
    # Header with logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📊 Hafali Smart Solutions")
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

    # Data source selection
    data_source = st.sidebar.radio(
        "Choose Data Source:",
        ["📊 Institutional Catalog", "📁 Upload Your Own File"],
        index=0
    )
    
    if data_source == "📊 Institutional Catalog":
        # Catalog year selection
        catalog_year = st.sidebar.selectbox(
            "Select Academic Year:",
            list(CATALOG_FILES.keys()),
            index=len(CATALOG_FILES)-1  # Default to latest year
        )
        
        # Load selected catalog
        catalog_df, success = load_catalog_data(catalog_year)
        if not success:
            st.error(f"Failed to load the {catalog_year} catalog. Please try uploading your own file.")
            st.stop()
        
        st.sidebar.success(f"✅ {catalog_year} Catalog loaded ({len(catalog_df)} courses)")
        
        # Show catalog info
        with st.sidebar.expander("📋 Catalog Info"):
            st.write(f"**Academic Year:** {catalog_year}")
            st.write(f"**Total Courses:** {len(catalog_df)}")
            st.write(f"**Programs:** {len(catalog_df['program'].unique())}")
            st.write(f"**Semesters:** {', '.join(sorted(catalog_df['semester'].unique()))}")
            
            # Show courses without course codes
            missing_codes = len(catalog_df[catalog_df['course_code'] == ''])
            if missing_codes > 0:
                st.write(f"**Courses without codes:** {missing_codes}")
            
    else:
        # Upload option
        uploaded_file = st.sidebar.file_uploader("Upload Catalog File", type=["csv", "xlsx"])
        if uploaded_file:
            try:
                if uploaded_file.name.endswith(".csv"):
                    # Try different encodings for CSV files
                    encodings_to_try = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1', 'cp1252']
                    
                    for encoding in encodings_to_try:
                        try:
                            catalog_df = pd.read_csv(uploaded_file, encoding=encoding)
                            st.info(f"Successfully loaded {uploaded_file.name} using {encoding} encoding")
                            break
                        except UnicodeDecodeError:
                            uploaded_file.seek(0)  # Reset file pointer for next attempt
                            continue
                        except Exception as e:
                            if encoding == encodings_to_try[-1]:
                                raise e
                            uploaded_file.seek(0)
                            continue
                    else:
                        st.error(f"Could not decode {uploaded_file.name} with any of the attempted encodings")
                        st.stop()
                else:
                    catalog_df = pd.read_excel(uploaded_file, engine="openpyxl")
                
                # Normalize columns
                catalog_df.columns = catalog_df.columns.str.lower().str.strip()
                
                # Filter out rows where semester is missing
                initial_count = len(catalog_df)
                catalog_df = catalog_df.dropna(subset=['semester'])
                catalog_df = catalog_df[catalog_df['semester'].astype(str).str.strip() != '']
                final_count = len(catalog_df)
                
                if initial_count != final_count:
                    st.info(f"Filtered out {initial_count - final_count} rows with missing semester data")
                
                # Handle missing course_code
                catalog_df['course_code'] = catalog_df['course_code'].fillna('')
                catalog_df['course_title'] = catalog_df['course_title'].fillna('Unknown Course')
                
                st.sidebar.success(f"✅ File uploaded ({len(catalog_df)} courses)")
            except Exception as e:
                st.error(f"Error reading file: {e}")
                st.stop()
        else:
            st.warning("Please upload a file to continue.")
            st.stop()

    # Required columns check (only for uploaded files)
    if data_source == "📁 Upload Your Own File":
        required_columns = ["program", "semester", "course_code", "course_title"]
        missing_columns = [col for col in required_columns if col not in catalog_df.columns]

        if missing_columns:
            st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
            st.stop()

    # Dropdowns
    programs_list = sorted(catalog_df["program"].unique())
    programs_with_all = ["All Programs"] + programs_list
    program_filter = st.sidebar.selectbox("Select Program", programs_with_all)
    
    # Get available semesters and clean them up
    available_semesters = sorted([s for s in catalog_df["semester"].unique() if s and str(s).strip()])
    semester_filter = st.sidebar.selectbox("Select Semester", available_semesters)
    
    # Check if any selected programs are Bachelor's (not MBA)
    selected_programs = [program_filter] if program_filter != "All Programs" else programs_list
    has_bachelor_programs = any("mba" not in prog.lower() for prog in selected_programs)
    
    # Weekend course option (only for Bachelor's programs)
    include_weekend_courses = True  # Default for MBA programs
    if has_bachelor_programs:
        st.sidebar.markdown("### Weekend Course Settings")
        include_weekend_courses = st.sidebar.checkbox(
            "Include Weekend Courses",
            value=True,
            help="Uncheck to avoid weekend classes (may cause some course time clashes)"
        )
        
        if not include_weekend_courses:
            st.sidebar.warning("⚠️ Disabling weekend courses may result in time clashes for different sections of the same course")
    
    # Student count input - different behavior for "All Programs"
    if program_filter == "All Programs":
        st.sidebar.markdown("### Student Count for Each Program")
        student_counts = {}
        for program in programs_list:
            student_counts[program] = st.sidebar.number_input(
                f"Students for {program}", 
                min_value=1, 
                step=1, 
                key=f"students_{program.replace(' ', '_').replace('(', '').replace(')', '')}"
            )
    else:
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

    def assign_schedule(df, allow_weekend_courses=True):
        """
        Improved scheduling function that avoids clashes and distributes weekend classes better
        For Bachelor's programs, can optionally disable weekend courses
        """
        section_occupied_slots = defaultdict(set)  # section -> {(day, time)}
        course_slot_usage = defaultdict(lambda: defaultdict(int))  # course -> slot -> count
        course_section_slots = defaultdict(set)  # course -> {(day, time)} used by any section
        
        schedule = []
        program_name = df["program"].iloc[0].lower() if not df.empty else ""
        is_mba = "mba" in program_name
        
        # Get all available slots
        if is_mba:
            # MBA programs always use their specific slots (no weekend restriction)
            all_slots = []
            for slot in mba_slots:
                if slot == ("6:30 PM", "9:30 PM"):
                    for day in weekday_days:
                        all_slots.append((day, slot))
                else:
                    for day in weekend_days:
                        all_slots.append((day, slot))
        else:
            # Bachelor's programs - can optionally exclude weekend slots
            all_slots = []
            for slot in weekday_slots:
                for day1, day2 in [("Monday", "Wednesday"), ("Tuesday", "Thursday")]:
                    all_slots.append((f"{day1} / {day2}", slot))
            
            # Add weekend slots only if allowed for Bachelor's programs
            if allow_weekend_courses:
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
                    prefer_weekend = weekend_preference.get(sec, False) and allow_weekend_courses
                    
                    if not allow_weekend_courses or section_weekend_classes >= 2:
                        # Prioritize weekday slots
                        candidate_slots = [(d, s) for (d, s) in all_slots if "/" in str(d)]
                        if allow_weekend_courses:
                            candidate_slots += [(d, s) for (d, s) in all_slots if any(wd in str(d) for wd in weekend_days)]
                    elif section_weekday_classes >= 6:
                        weekend_slots_list = [(d, s) for (d, s) in all_slots if any(wd in str(d) for wd in weekend_days)]
                        weekday_slots_list = [(d, s) for (d, s) in all_slots if "/" in str(d)]
                        candidate_slots = weekend_slots_list + weekday_slots_list
                    else:
                        weekend_slots_list = [(d, s) for (d, s) in all_slots if any(wd in str(d) for wd in weekend_days)]
                        weekday_slots_list = [(d, s) for (d, s) in all_slots if "/" in str(d)]
                        candidate_slots = weekend_slots_list + weekday_slots_list if prefer_weekend else weekday_slots_list + weekend_slots_list
                
                candidate_slots.sort(key=lambda slot: course_slot_usage[course][slot])
                
                # First pass: Try to avoid section clashes and course clashes
                for slot_key in candidate_slots:
                    day, slot = slot_key
                    
                    # Check for section clash (always avoid)
                    if slot_key in section_occupied_slots[sec]:
                        continue
                    
                    # Check for course clash (avoid if possible, but allow as last resort)
                    if slot_key in course_section_slots[course]:
                        continue
                        
                    # Handle weekend day consistency for non-MBA programs
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
                    
                    # Assign the slot
                    section_occupied_slots[sec].add(slot_key)
                    course_slot_usage[course][slot_key] += 1
                    course_section_slots[course].add(slot_key)
                    schedule.append((sec, day, f"{slot[0]} - {slot[1]}"))
                    slot_assigned = True
                    break
                
                # Second pass: Allow course clashes if no other option (but still avoid section clashes)
                if not slot_assigned:
                    for slot_key in candidate_slots:
                        day, slot = slot_key
                        
                        # Still avoid section clashes
                        if slot_key in section_occupied_slots[sec]:
                            continue
                        
                        # Allow course clashes as last resort
                        section_occupied_slots[sec].add(slot_key)
                        course_slot_usage[course][slot_key] += 1
                        course_section_slots[course].add(slot_key)
                        schedule.append((sec, day, f"{slot[0]} - {slot[1]}"))
                        slot_assigned = True
                        break
                
                # Final fallback: Random assignment with warning
                if not slot_assigned:
                    st.warning(f"Could not find optimal slot for {course_code if course_code else 'Unknown Course'} Section {sec}. Using random assignment.")
                    slot_key = random.choice(all_slots)
                    day, slot = slot_key
                    section_occupied_slots[sec].add(slot_key)
                    course_slot_usage[course][slot_key] += 1
                    course_section_slots[course].add(slot_key)
                    schedule.append((sec, day, f"{slot[0]} - {slot[1]}"))
        
        return schedule

    # Generate report
    if st.sidebar.button("Generate Report"):
        if program_filter == "All Programs":
            # Handle all programs at once
            all_programs_df = catalog_df[
                catalog_df["semester"] == semester_filter
            ][["program", "course_code", "course_title"]].copy()
            
            if all_programs_df.empty:
                st.warning("No courses found for the selected Semester.")
            else:
                all_results = []
                all_summaries = []
                
                for program in programs_list:
                    program_df = all_programs_df[all_programs_df["program"] == program].copy()
                    
                    if not program_df.empty:
                        current_student_count = student_counts[program]
                        
                        program_df["failed/withdrawn students"] = 0
                        program_df["active students"] = current_student_count
                        program_df["total student strength"] = current_student_count
                        program_df["required sections"] = program_df["total student strength"].apply(lambda x: math.ceil(x / 40))
                        program_df["section"] = ""
                        program_df["name"] = "Faculty Member"
                        program_df["ids"] = ""
                        program_df["type name"] = ""
                        
                        schedule = assign_schedule(program_df, include_weekend_courses)
                        
                        expanded_df = []
                        sched_idx = 0
                        
                        for _, row in program_df.iterrows():
                            for sec in range(1, row["required sections"] + 1):
                                new_row = row.copy()
                                new_row["section"] = sec
                                new_row["days"] = schedule[sched_idx][1]
                                new_row["time's"] = schedule[sched_idx][2]
                                expanded_df.append(new_row)
                                sched_idx += 1
                        
                        program_result_df = pd.DataFrame(expanded_df)
                        program_result_df = program_result_df.sort_values(by=["section", "course_code"]).reset_index(drop=True)
                        all_results.append(program_result_df)
                        
                        # Create summary for this program
                        for section in program_result_df["section"].unique():
                            section_data = program_result_df[program_result_df["section"] == section]
                            weekend_count = sum(1 for day in section_data["days"] if any(wd in str(day) for wd in weekend_days))
                            weekday_count = len(section_data) - weekend_count
                            all_summaries.append({
                                "Program": program,
                                "Section": section,
                                "Weekend Classes": weekend_count,
                                "Weekday Classes": weekday_count,
                                "Total Classes": len(section_data)
                            })
                
                if all_results:
                    # Combine all program results
                    final_df = pd.concat(all_results, ignore_index=True)
                    final_df = final_df[[
                        "program", "section", "course_code", "course_title", "name", "ids", 
                        "type name", "days", "time's", "failed/withdrawn students", 
                        "active students", "total student strength", "required sections"
                    ]]
                    
                    st.success("Report generated for all programs with improved timetable!")
                    
                    # Show results by program
                    for program in programs_list:
                        program_data = final_df[final_df["program"] == program]
                        if not program_data.empty:
                            st.subheader(f"📚 {program}")
                            st.dataframe(program_data)
                    
                    st.subheader("📋 Overall Scheduling Summary")
                    summary_df = pd.DataFrame(all_summaries)
                    st.dataframe(summary_df)
                    
                    csv = final_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Complete Schedule CSV",
                        data=csv,
                        file_name=f"complete_timetable_all_programs_{semester_filter}.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("No data found for any programs in the selected semester.")
        
        else:
            # Handle single program (original functionality)
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
                
                schedule = assign_schedule(df, include_weekend_courses)
                
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
