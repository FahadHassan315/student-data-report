import os
import math
import random
import pandas as pd
import streamlit as st
from collections import defaultdict

# User credentials
VALID_USERS = {
    "Fahadhassan": "Iobm1",
    "Alihasnain": "Iobm2", 
    "Habibullah": "Iobm3",
    "Rabiyasabri": "Iobm4"
}

def check_login():
    """Display login form and handle authentication"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = ""
    
    if not st.session_state.authenticated:
        st.title("🔐 Login to Student Data Report System")
        
        with st.form("login_form"):
            st.subheader("Please enter your credentials")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if username in VALID_USERS and VALID_USERS[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success(f"Welcome, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password. Please try again.")
        
        with st.expander("ℹ️ Valid Users"):
            st.write("Valid usernames: Fahadhassan, Alihasnain, Habibullah, Rabiyasabri")
        
        return False
    
    return True

def logout():
    """Handle user logout"""
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.rerun()

def create_sample_data():
    """Create sample catalog data"""
    sample_data = {
        'program': [
            'Computer Science', 'Computer Science', 'Computer Science', 'Computer Science',
            'MBA', 'MBA', 'MBA', 'MBA',
            'Engineering', 'Engineering', 'Engineering', 'Engineering',
        ],
        'semester': [
            '1', '1', '2', '2',
            '1', '1', '2', '2', 
            '1', '1', '2', '2',
        ],
        'course_code': [
            'CS101', 'CS102', 'CS201', 'CS202',
            'MBA101', 'MBA102', 'MBA201', 'MBA202',
            'ENG101', 'ENG102', 'ENG201', 'ENG202',
        ],
        'course_title': [
            'Introduction to Programming', 'Data Structures', 'Database Systems', 'Web Development',
            'Business Management', 'Marketing Strategy', 'Financial Management', 'Operations Management',
            'Engineering Mathematics', 'Physics for Engineers', 'Circuit Analysis', 'Thermodynamics',
        ]
    }
    return pd.DataFrame(sample_data)

# Check authentication first
if not check_login():
    st.stop()

# Page setup
st.set_page_config(page_title="📊 Student Data Report", layout="wide")

# Header with logout button
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📊 Student Data Report")
with col2:
    st.write(f"👤 Welcome, {st.session_state.username}")
    if st.button("🚪 Logout"):
        logout()

# Sidebar
st.sidebar.header("📋 Input Parameters")

# Data source selection
data_source = st.sidebar.radio("Select Data Source", ["Upload File", "Use Sample Data"])

# Load data based on selection
catalog_df = None

if data_source == "Upload File":
    st.sidebar.markdown("### 📁 Upload Your Catalog File")
    uploaded_file = st.sidebar.file_uploader(
        "Choose catalog file", 
        type=["csv", "xlsx"],
        help="Upload CSV/Excel with: program, semester, course_code, course_title"
    )
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                catalog_df = pd.read_csv(uploaded_file)
            else:
                catalog_df = pd.read_excel(uploaded_file, engine="openpyxl")
            
            st.sidebar.success(f"✅ Loaded {len(catalog_df)} courses")
            
        except Exception as e:
            st.sidebar.error(f"❌ Error: {e}")
            st.stop()
    else:
        st.sidebar.info("👆 Please upload a file")

else:  # Use Sample Data
    catalog_df = create_sample_data()
    st.sidebar.success(f"✅ Using sample data ({len(catalog_df)} courses)")

# Only proceed if we have data
if catalog_df is not None:
    # Normalize column names
    catalog_df.columns = catalog_df.columns.str.lower().str.strip()
    
    # Required columns check
    required_columns = ["program", "semester", "course_code", "course_title"]
    missing_columns = [col for col in required_columns if col not in catalog_df.columns]
    
    if missing_columns:
        st.error(f"❌ Missing columns: {', '.join(missing_columns)}")
        st.stop()
    
    # Filter controls
    st.sidebar.markdown("### 🔍 Filters")
    program_filter = st.sidebar.selectbox("Select Program", sorted(catalog_df["program"].unique()))
    semester_filter = st.sidebar.selectbox("Select Semester", sorted(catalog_df["semester"].unique()))
    student_count = st.sidebar.number_input("Number of Students", min_value=1, value=40, step=1)
    
    # Generate report button
    if st.sidebar.button("🚀 Generate Report", type="primary"):
        # Filter the data
        filtered_df = catalog_df[
            (catalog_df["program"] == program_filter) & 
            (catalog_df["semester"] == semester_filter)
        ][["program", "course_code", "course_title"]].copy()
        
        if filtered_df.empty:
            st.warning("⚠️ No courses found for selected filters")
        else:
            # Add basic scheduling (simple version for demo)
            time_slots = [
                "9:00 AM - 10:30 AM",
                "10:45 AM - 12:15 PM", 
                "12:30 PM - 2:00 PM",
                "2:15 PM - 3:45 PM"
            ]
            
            days = ["Monday / Wednesday", "Tuesday / Thursday", "Saturday", "Sunday"]
            
            # Create final dataframe
            final_data = []
            for idx, (_, row) in enumerate(filtered_df.iterrows()):
                sections_needed = math.ceil(student_count / 40)
                
                for section in range(1, sections_needed + 1):
                    final_data.append({
                        "program": row["program"],
                        "section": section,
                        "course_code": row["course_code"],
                        "course_title": row["course_title"],
                        "faculty_name": "TBA",
                        "days": days[idx % len(days)],
                        "times": time_slots[idx % len(time_slots)],
                        "active_students": student_count // sections_needed,
                        "total_students": student_count,
                        "required_sections": sections_needed
                    })
            
            final_df = pd.DataFrame(final_data)
            
            # Display results
            st.success(f"🎉 Generated {len(final_df)} class sections!")
            
            # Show metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Courses", len(filtered_df))
            with col2:
                st.metric("Sections", len(final_df))
            with col3:
                st.metric("Students", student_count)
            with col4:
                st.metric("Program", program_filter)
            
            # Show timetable
            st.subheader("📅 Generated Timetable")
            st.dataframe(final_df, use_container_width=True)
            
            # Download option
            csv = final_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Report",
                data=csv,
                file_name=f"timetable_{program_filter}_{semester_filter}.csv",
                mime="text/csv",
                type="primary"
            )

else:
    # Show instructions
    st.info("👆 Select a data source from the sidebar to get started")
    
    st.markdown("""
    ## 🚀 How to use:
    
    1. **Login** with your credentials
    2. **Choose data source** (Upload file or Sample data)
    3. **Select filters** (Program, Semester, Students)
    4. **Generate report** 
    5. **Download CSV** file
    
    ### Valid Login Credentials:
    - Fahadhassan / Iobm1
    - Alihasnain / Iobm2  
    - Habibullah / Iobm3
    - Rabiyasabri / Iobm4
    """)
