import os
import math
import random
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict

# Page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="SSK ACMS - IOBM",
    page_icon="https://raw.githubusercontent.com/FahadHassan315/room-allocation-system/main/iobm.png",
    layout="wide"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'selected_college' not in st.session_state:
    st.session_state.selected_college = None
if 'selected_program' not in st.session_state:
    st.session_state.selected_program = None

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

def display_logo_main():
    """Display IOBM logo for main app - larger size for header"""
    try:
        st.image("iobm.png", width=200)
    except:
        st.markdown("<h2>IOBM</h2>", unsafe_allow_html=True)

def load_catalog_data(catalog_year):
    """Load catalog data from the repository CSV file"""
    filename = CATALOG_FILES[catalog_year]
    
    encodings_to_try = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings_to_try:
        try:
            catalog_df = pd.read_csv(filename, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            if encoding == encodings_to_try[-1]:
                st.error(f"Error loading catalog file {filename}: {e}")
                return None, False
            continue
    else:
        st.error(f"Could not decode {filename} with any of the attempted encodings")
        return None, False
    
    try:
        # Normalize column names
        catalog_df.columns = catalog_df.columns.str.lower().str.strip()
        
        # Handle missing values
        catalog_df = catalog_df.dropna(subset=['semester'])
        catalog_df = catalog_df[catalog_df['semester'].astype(str).str.strip() != '']
        catalog_df['course_code'] = catalog_df['course_code'].fillna('')
        catalog_df['course_title'] = catalog_df['course_title'].fillna('Unknown Course')
        catalog_df['college'] = catalog_df.get('college', pd.Series(['Unknown College'] * len(catalog_df)))
        catalog_df['college'] = catalog_df['college'].fillna('Unknown College')
        
        # Convert semester values to lowercase for consistency
        catalog_df['semester'] = catalog_df['semester'].astype(str).str.lower().str.strip()
        
        return catalog_df, True
        
    except Exception as e:
        st.error(f"Error processing catalog file {filename}: {e}")
        return None, False

def create_catalog_charts(catalog_df, selected_catalog_year):
    """Create single pie chart showing college distribution by number of programs"""
    
    st.subheader(f"📊 Catalog Insights - {selected_catalog_year}")
    
    # Create college-wise program distribution (count unique programs per college)
    college_program_counts = catalog_df.groupby('college')['program'].nunique().reset_index()
    college_program_counts.columns = ['college', 'program_count']
    college_program_counts = college_program_counts.sort_values('program_count', ascending=False)
    
    # Create a detailed hover text showing all programs in each college
    hover_text = []
    for college in college_program_counts['college']:
        programs_in_college = catalog_df[catalog_df['college'] == college]['program'].unique()
        programs_list = "<br>• ".join(sorted(programs_in_college))
        hover_text.append(f"<b>{college}</b><br>Programs: {len(programs_in_college)}<br><br>• {programs_list}")
    
    # Center the pie chart
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # College pie chart based on number of programs
        fig_college = px.pie(
            values=college_program_counts['program_count'],
            names=college_program_counts['college'],
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        # Update hover template to show programs
        fig_college.update_traces(
            hovertemplate=hover_text,
            textinfo="label+percent"
        )
        fig_college.update_layout(height=500, showlegend=True)
        
        st.plotly_chart(fig_college, use_container_width=True)
    
    # Summary statistics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Colleges", len(catalog_df['college'].unique()))
    
    with col2:
        st.metric("Total Programs", len(catalog_df['program'].unique()))
    
    with col3:
        st.metric("Total Courses", len(catalog_df))

def login_page():
    """Display horizontal login page with logo/name on left, login on right, credits at bottom"""
    
    # Add custom CSS for full height layout and styling
    st.markdown("""
    <style>
    /* Hide the default Streamlit header and menu */
    .stApp > header {
        background-color: transparent;
    }
    
    .main-container {
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 20px;
    }
    .login-content {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 40px;
        margin: 20px 0;
    }
    .logo-section {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        text-align: center;
        padding: 20px;
        margin-top: -100px;
    }
    .login-section {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 40px;
        margin-top: -50px;
    }
    .credits-section {
        text-align: center;
        padding: 20px;
        border-top: 1px solid #e0e0e0;
        margin-top: auto;
    }
    .app-title {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        margin: 20px 0 10px 0;
    }
    .app-subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 20px;
    }
    .login-title {
        font-size: 1.8rem;
        color: #333;
        margin-bottom: 30px;
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create two main columns for horizontal layout
    col_left, col_right = st.columns([1, 1], gap="large")
    
    # Left side - Logo and App Name
    with col_left:
        st.markdown('<div class="logo-section">', unsafe_allow_html=True)
        
        # Display logo - centered
        col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
        with col_logo2:
            try:
                st.image("iobm.png", width=250)
            except:
                st.markdown('<div style="width: 250px; height: 150px; background: #ddd; display: flex; align-items: center; justify-content: center; border-radius: 10px; margin: 0 auto;"><h2>IOBM</h2></div>', unsafe_allow_html=True)
        
        # App title and subtitle - properly centered
       st.markdown(
    """
    <div style="text-align: center; margin-top: 0; padding-top: 0;">
        <img src="data:image/png;base64,..." style="max-width:150px; margin-bottom:5px;"/>
        <h1 style="font-size: 3rem; font-weight: bold; color: #1f77b4; margin: 0; line-height: 1.2;">
            SSK ACMS
        </h1>
        <p style="font-size: 1.2rem; color: #666; margin: 0;">
            Academic Course Management System
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

    
    # Right side - Login Form
    with col_right:
        st.markdown('<div class="login-section">', unsafe_allow_html=True)
        
        st.markdown('<h2 class="login-title">🔐 Login</h2>', unsafe_allow_html=True)
        
        # Login form
        username = st.text_input("👤 Username", placeholder="Enter your username", key="username_input", label_visibility="collapsed")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="password_input", label_visibility="collapsed")
        
        # Add some spacing
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Login button
        if st.button("🚀 Login", use_container_width=True, type="primary"):
            username_lower = username.lower()
            password_lower = password.lower()
            
            if username_lower in USERS and USERS[username_lower]["password"] == password_lower:
                st.session_state.logged_in = True
                st.session_state.username = username_lower
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Bottom - Credits section (full width)
    st.markdown('<div class="credits-section">', unsafe_allow_html=True)
    st.markdown("""
    <div style='color: #666; font-size: 14px;'>
        <p><strong>Development Team:</strong> Fahad Hassan, Ali Hasnain Abro | <strong>Supervisor:</strong> Dr. Rabiya Sabri | <strong>Designer:</strong> Habibullah Rajpar</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def normalize_semester_name(semester):
    """Normalize semester names for consistent ordering"""
    semester_str = str(semester).lower().strip()
    
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

def assign_schedule(df, allow_weekend_courses=True):
    """Improved scheduling function"""
    section_occupied_slots = defaultdict(set)
    course_slot_usage = defaultdict(lambda: defaultdict(int))
    course_section_slots = defaultdict(set)
    
    schedule = []
    program_name = df["program"].iloc[0].lower() if not df.empty else ""
    is_mba = "mba" in program_name
    
    # Time slots
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
        ("9:00 AM", "12:00 PM"),
        ("2:00 PM", "5:00 PM"),
        ("6:30 PM", "9:30 PM")
    ]

    weekday_days = ["Monday", "Tuesday", "Wednesday", "Thursday"]
    weekend_days = ["Saturday", "Sunday"]
    
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
        
        if allow_weekend_courses:
            for slot in weekend_slots:
                for day in weekend_days:
                    all_slots.append((day, slot))
    
    total_sections = df["required sections"].max() if not df.empty else 0
    
    for _, row in df.iterrows():
        course = row["course_title"]
        course_code = row["course_code"]
        sections = row["required sections"]
        
        for sec in range(1, sections + 1):
            slot_assigned = False
            candidate_slots = all_slots.copy()
            candidate_slots.sort(key=lambda slot: course_slot_usage[course][slot])
            
            for slot_key in candidate_slots:
                day, slot = slot_key
                
                if slot_key in section_occupied_slots[sec]:
                    continue
                
                if slot_key in course_section_slots[course]:
                    continue
                
                section_occupied_slots[sec].add(slot_key)
                course_slot_usage[course][slot_key] += 1
                course_section_slots[course].add(slot_key)
                schedule.append((sec, day, f"{slot[0]} - {slot[1]}"))
                slot_assigned = True
                break
            
            if not slot_assigned:
                for slot_key in candidate_slots:
                    day, slot = slot_key
                    
                    if slot_key in section_occupied_slots[sec]:
                        continue
                    
                    section_occupied_slots[sec].add(slot_key)
                    course_slot_usage[course][slot_key] += 1
                    course_section_slots[course].add(slot_key)
                    schedule.append((sec, day, f"{slot[0]} - {slot[1]}"))
                    slot_assigned = True
                    break
            
            if not slot_assigned:
                slot_key = random.choice(all_slots)
                day, slot = slot_key
                section_occupied_slots[sec].add(slot_key)
                course_slot_usage[course][slot_key] += 1
                course_section_slots[course].add(slot_key)
                schedule.append((sec, day, f"{slot[0]} - {slot[1]}"))
    
    return schedule

def main_app():
    """Main application interface"""
    
    # Header
    col1, col2, col3 = st.columns([2, 4, 2])
    
    with col1:
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
            st.session_state.selected_college = None
            st.session_state.selected_program = None
            st.rerun()
    
    # Sidebar
    st.sidebar.header("Input Parameters")

    data_source = st.sidebar.radio(
        "Choose Data Source:",
        ["📊 Institutional Catalog", "📁 Upload Your Own File"],
        index=0
    )
    
    catalog_df = None
    selected_catalog_year = None
    
    if data_source == "📊 Institutional Catalog":
        default_index = list(CATALOG_FILES.keys()).index("2023-2024")
        selected_catalog_year = st.sidebar.selectbox(
            "Select Academic Year:",
            list(CATALOG_FILES.keys()),
            index=default_index
        )
        
        catalog_df, success = load_catalog_data(selected_catalog_year)
        if not success:
            st.error(f"Failed to load the {selected_catalog_year} catalog.")
            st.stop()
        
        create_catalog_charts(catalog_df, selected_catalog_year)
            
    else:
        uploaded_file = st.sidebar.file_uploader("Upload Catalog File", type=["csv", "xlsx"])
        if uploaded_file:
            try:
                if uploaded_file.name.endswith(".csv"):
                    catalog_df = pd.read_csv(uploaded_file)
                else:
                    catalog_df = pd.read_excel(uploaded_file)
                
                catalog_df.columns = catalog_df.columns.str.lower().str.strip()
                catalog_df = catalog_df.dropna(subset=['semester'])
                catalog_df['course_code'] = catalog_df['course_code'].fillna('')
                catalog_df['course_title'] = catalog_df['course_title'].fillna('Unknown Course')
                catalog_df['college'] = catalog_df.get('college', pd.Series(['Unknown College'] * len(catalog_df)))
                
                selected_catalog_year = "Custom Upload"
                create_catalog_charts(catalog_df, selected_catalog_year)
                
            except Exception as e:
                st.error(f"Error reading file: {e}")
                st.stop()
        else:
            st.warning("Please upload a file to continue.")
            st.stop()

    if catalog_df is None:
        st.error("No data loaded.")
        st.stop()

    # Rest of the main functionality continues here...
    programs_list = sorted(catalog_df["program"].unique())
    programs_with_all = ["All Programs"] + programs_list
    program_filter = st.sidebar.selectbox("Select Program", programs_with_all)
    
    # Get semesters
    raw_semesters = catalog_df["semester"].unique()
    normalized_semesters = []
    
    for sem in raw_semesters:
        if sem and str(sem).strip():
            normalized = normalize_semester_name(sem)
            normalized_semesters.append((normalized, sem))
    
    semester_order = get_semester_order()
    normalized_semesters.sort(key=lambda x: semester_order.index(x[0]) if x[0] in semester_order else 999)
    
    semester_display_list = [original for normalized, original in normalized_semesters]
    semester_filter = st.sidebar.selectbox("Select Semester", semester_display_list)
    
    selected_programs = [program_filter] if program_filter != "All Programs" else programs_list
    has_bachelor_programs = any("mba" not in prog.lower() for prog in selected_programs)
    
    include_weekend_courses = True
    if has_bachelor_programs:
        st.sidebar.markdown("### Weekend Course Settings")
        include_weekend_courses = st.sidebar.checkbox(
            "Include Weekend Courses",
            value=True,
            help="Uncheck to avoid weekend classes"
        )
    
    # Student count input
    if program_filter == "All Programs":
        if 'student_counts' not in st.session_state:
            st.session_state.student_counts = {program: 1 for program in programs_list}
        
        with st.sidebar.expander("👥 Program-wise Student Counts", expanded=False):
            st.markdown("**Enter number of students for each program:**")
            for program in programs_list:
                st.session_state.student_counts[program] = st.number_input(
                    f"{program}",
                    min_value=1,
                    value=st.session_state.student_counts.get(program, 1),
                    step=1,
                    key=f"students_{program}"
                )
        
        student_counts = st.session_state.student_counts
        
    else:
        student_count = st.sidebar.number_input("Enter Number of Students", min_value=1, step=1)

    # Generate report
    if st.sidebar.button("Generate Report"):
        catalog_name = selected_catalog_year if selected_catalog_year else "Custom_Upload"
        
        if program_filter == "All Programs":
            all_programs_df = catalog_df[
                catalog_df["semester"] == semester_filter
            ][["program", "course_code", "course_title", "college"]].copy()
            
            if all_programs_df.empty:
                st.warning("No courses found for the selected Semester.")
            else:
                all_results = []
                
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
                
                if all_results:
                    final_df = pd.concat(all_results, ignore_index=True)
                    final_df = final_df[[
                        "program", "college", "section", "course_code", "course_title", "name", "ids", 
                        "type name", "days", "time's", "failed/withdrawn students", 
                        "active students", "total student strength", "required sections",
                        "semester_selected", "catalog_year"
                    ]]
                    
                    st.success("Report generated for all programs!")
                    
                    for program in programs_list:
                        program_data = final_df[final_df["program"] == program]
                        if not program_data.empty:
                            st.subheader(f"📚 {program}")
                            st.dataframe(program_data)
                    
                    csv = final_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Complete Schedule CSV",
                        data=csv,
                        file_name=f"timetable_AllPrograms_{semester_filter}_{catalog_name}.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("No data found for any programs in the selected semester.")
        
        else:
            # Single program logic
            df = catalog_df[
                (catalog_df["program"] == program_filter) & 
                (catalog_df["semester"] == semester_filter)
            ][["program", "course_code", "course_title", "college"]].copy()
            
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
                    "program", "college", "section", "course_code", "course_title", "name", "ids", 
                    "type name", "days", "time's", "failed/withdrawn students", 
                    "active students", "total student strength", "required sections",
                    "semester_selected", "catalog_year"
                ]]
                
                st.success("Report generated!")
                st.dataframe(df)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"timetable_{program_filter}_{semester_filter}_{catalog_name}.csv",
                    mime="text/csv",
                )

    # Add Room Allocation System button at the bottom
    st.markdown("---")
    st.subheader("🏢 Additional Tools")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏫 Go to Room Allocation System", use_container_width=True, type="primary"):
            st.info("Opening Room Allocation System...")
            st.markdown("[🏫 Click here to access Room Allocation System](https://iobm-room-allocation-system.streamlit.app)")
    
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
