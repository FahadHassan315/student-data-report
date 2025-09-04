import os
import math
import random
import pandas as pd
import streamlit as st
from collections import defaultdict

# Page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="SSK ACMS", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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

def display_logo_login():
    """Display IOBM logo for login page - centered and smaller"""
    try:
        # Centered logo for login page
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image("iobm.png", width=150)
    except:
        # Fallback to centered text if logo is not found
        st.markdown("<div style='text-align: center;'><h2>IOBM</h2></div>", unsafe_allow_html=True)

def display_logo_main():
    """Display IOBM logo for main app - larger size for header"""
    try:
        # Larger logo for main app header
        st.image("iobm.png", width=200)
    except:
        # Fallback text if logo is not found
        st.markdown("<h2>IOBM</h2>", unsafe_allow_html=True)

def load_catalog_data(catalog_year):
    """Load catalog data from the repository CSV file"""
    filename = CATALOG_FILES[catalog_year]
    
    # Try different encodings to handle various file formats
    encodings_to_try = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings_to_try:
        try:
            catalog_df = pd.read_csv(filename, encoding=encoding)
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
        
        # Handle missing course_code - fill with empty string instead of dropping
        catalog_df['course_code'] = catalog_df['course_code'].fillna('')
        catalog_df['course_title'] = catalog_df['course_title'].fillna('Unknown Course')
        
        # Convert semester values to lowercase for consistency
        catalog_df['semester'] = catalog_df['semester'].astype(str).str.lower().str.strip()
        
        return catalog_df, True
        
    except Exception as e:
        st.error(f"Error processing catalog file {filename}: {e}")
        return None, False

def normalize_semester_name(semester):
    """Normalize semester names for consistent ordering"""
    semester_str = str(semester).lower().strip()
    
    # Handle various formats
    if semester_str in ['one', '1', 'first', 'semester 1', 'sem 1']:
        return 'one'
    elif semester_str in ['two', '2', 'second', 'semester 2', 'sem 2']:
        return 'two'
    elif semester_str in ['three', '3', 'third', 'semester 3', 'sem 3']:
        return 'three'
    elif semester_str in ['four', '4', 'fourth', 'semester 4', 'sem 4']:
        return 'four'
    elif semester_str in ['five', '5', 'fifth', 'semester 5', 'sem 5']:
        return 'five'
    elif semester_str in ['six', '6', 'sixth', 'semester 6', 'sem 6']:
        return 'six'
    elif semester_str in ['seven', '7', 'seventh', 'semester 7', 'sem 7']:
        return 'seven'
    elif semester_str in ['eight', '8', 'eighth', 'eights', 'semester 8', 'sem 8']:
        return 'eight'
    else:
        return semester_str

def get_semester_order():
    """Return the proper order for semesters"""
    return ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']

def create_catalog_charts(catalog_df, selected_catalog_year):
    """Create insightful bar chart from catalog data"""
    
    st.subheader(f"📊 Catalog Insights - {selected_catalog_year}")
    
    # Chart: Program-wise Course Distribution
    program_counts = catalog_df['program'].value_counts()
    
    # Create a DataFrame for the bar chart
    chart_data = pd.DataFrame({
        'Program': program_counts.index,
        'Course Count': program_counts.values
    })
    
    # Display the bar chart using Streamlit's built-in chart
    st.markdown("#### 🎯 Course Distribution by Program")
    st.bar_chart(chart_data.set_index('Program'))
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Programs", len(program_counts))
    
    with col2:
        st.metric("Total Courses", program_counts.sum())
    
    with col3:
        st.metric("Avg Courses/Program", round(program_counts.sum() / len(program_counts), 1))
    
    # Show detailed breakdown in an expandable section
    with st.expander("📊 Detailed Program Statistics"):
        total_courses = program_counts.sum()
        detailed_data = pd.DataFrame({
            'Program': program_counts.index,
            'Courses': program_counts.values,
            'Percentage': (program_counts.values / total_courses * 100).round(1)
        })
        st.dataframe(detailed_data, use_container_width=True)

def login_page():
    """Display login page"""
    # Center the logo and login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Display centered logo for login page
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        display_logo_login()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h1>SSK ACMS</h1>
            <p>Please Login to Continue</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("### Login")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            if st.button("Login", use_container_width=True):
                # Convert to lowercase for comparison
                username_lower = username.lower()
                password_lower = password.lower()
                
                if username_lower in USERS and USERS[username_lower]["password"] == password_lower:
                    st.session_state.logged_in = True
                    st.session_state.username = username_lower
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid username or password!")

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

def main_app():
    """Main application interface"""
    
    # Header with logo and logout - Left aligned logo with title
    col1, col2, col3 = st.columns([2, 4, 2])
    
    with col1:
        # Logo and title together on the left
        display_logo_main()
    
    with col2:
        st.markdown("""
        <div style="padding-top: 40px;">
            <h1>SSK ACMS</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"**Welcome, {USERS[st.session_state.username]['display_name']}!**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
    
    # Sidebar
    st.sidebar.header("Input Parameters")

    # Data source selection
    data_source = st.sidebar.radio(
        "Choose Data Source:",
        ["📊 Institutional Catalog", "📁 Upload Your Own File"],
        index=0
    )
    
    catalog_df = None
    selected_catalog_year = None
    
    if data_source == "📊 Institutional Catalog":
        # Catalog year selection - default to 2024-2025
        default_index = list(CATALOG_FILES.keys()).index("2024-2025")
        selected_catalog_year = st.sidebar.selectbox(
            "Select Academic Year:",
            list(CATALOG_FILES.keys()),
            index=default_index
        )
        
        # Load selected catalog
        catalog_df, success = load_catalog_data(selected_catalog_year)
        if not success:
            st.error(f"Failed to load the {selected_catalog_year} catalog. Please try uploading your own file.")
            st.stop()
        
        # Show catalog charts
        create_catalog_charts(catalog_df, selected_catalog_year)
            
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
                
                # Handle missing course_code
                catalog_df['course_code'] = catalog_df['course_code'].fillna('')
                catalog_df['course_title'] = catalog_df['course_title'].fillna('Unknown Course')
                
                # Show charts for uploaded file too
                selected_catalog_year = "Custom Upload"
                create_catalog_charts(catalog_df, selected_catalog_year)
                
            except Exception as e:
                st.error(f"Error reading file: {e}")
                st.stop()
        else:
            st.warning("Please upload a file to continue.")
            st.stop()

    # Check if catalog_df is loaded
    if catalog_df is None:
        st.error("No data loaded. Please select a catalog or upload a file.")
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
    
    # Get available semesters, normalize them, and sort them properly
    raw_semesters = catalog_df["semester"].unique()
    normalized_semesters = []
    
    for sem in raw_semesters:
        if sem and str(sem).strip():
            normalized = normalize_semester_name(sem)
            normalized_semesters.append((normalized, sem))  # (normalized, original)
    
    # Sort by the normalized order
    semester_order = get_semester_order()
    normalized_semesters.sort(key=lambda x: semester_order.index(x[0]) if x[0] in semester_order else 999)
    
    # Create display list and mapping
    semester_display_list = [original for normalized, original in normalized_semesters]
    semester_filter = st.sidebar.selectbox("Select Semester", semester_display_list)
    
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
    
    # Student count input - improved UI for "All Programs"
    if program_filter == "All Programs":
        # Initialize session state for student counts if not exists
        if 'student_counts' not in st.session_state:
            st.session_state.student_counts = {program: 1 for program in programs_list}
        
        # Expandable section for student counts
        with st.sidebar.expander("👥 Program-wise Student Counts", expanded=False):
            st.markdown("**Enter number of students for each program:**")
            for i, program in enumerate(programs_list):
                st.session_state.student_counts[program] = st.number_input(
                    f"{program}",
                    min_value=1,
                    value=st.session_state.student_counts.get(program, 1),
                    step=1,
                    key=f"students_{i}_{program.replace(' ', '_').replace('(', '').replace(')', '')}"
                )
        
        student_counts = st.session_state.student_counts
        
    else:
        student_count = st.sidebar.number_input("Enter Number of Students", min_value=1, step=1)

    # Generate report
    if st.sidebar.button("Generate Report"):
        # Determine catalog name for display
        catalog_name = selected_catalog_year if selected_catalog_year else "Custom_Upload"
        weekend_days = ["Saturday", "Sunday"]
        
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
                        # Add new columns
                        program_df["semester_selected"] = semester_filter
                        program_df["catalog_year"] = catalog_name
                        
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
                        "active students", "total student strength", "required sections",
                        "semester_selected", "catalog_year"
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
                    
                    # Enhanced filename for all programs
                    clean_semester = semester_filter.replace(" ", "_").replace("/", "_")
                    clean_catalog = catalog_name.replace(" ", "_").replace("-", "_")
                    filename = f"timetable_AllPrograms_{clean_semester}_{clean_catalog}.csv"
                    
                    csv = final_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Complete Schedule CSV",
                        data=csv,
                        file_name=filename,
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
                # Add new columns
                df["semester_selected"] = semester_filter
                df["catalog_year"] = catalog_name
                
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
                    "active students", "total student strength", "required sections",
                    "semester_selected", "catalog_year"
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
                
                # Enhanced filename for single program
                clean_program = program_filter.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
                clean_semester = semester_filter.replace(" ", "_").replace("/", "_")
                clean_catalog = catalog_name.replace(" ", "_").replace("-", "_")
                filename = f"timetable_{clean_program}_{clean_semester}_{clean_catalog}.csv"
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv",
                )

    # Add Room Allocation System button at the bottom
    st.markdown("---")
    st.subheader("🏢 Additional Tools")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏫 Go to Room Allocation System", use_container_width=True, type="primary"):
            st.info("Opening Room Allocation System...")
            st.markdown("[🏫 **Click here to access Room Allocation System**](https://iobm-room-allocation-system.streamlit.app/)")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 12px; margin-top: 30px;'>
            <p><strong>Development Team:</strong> Fahad Hassan, Ali Hasnain Abro | <strong>Supervisor:</strong> Dr. Rabiya Sabri | <strong>Designer:</strong> Habibullah Rajpar</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Main application logic
def main():
    """Main function to run the application"""
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()

# Run the application
if __name__ == "__main__":
    main()
