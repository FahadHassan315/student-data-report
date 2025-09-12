import os
import math
import random
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import base64

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

def get_base64_of_bin_file(bin_file):
    """Convert image to base64 string"""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

def set_background_image():
    """Set background image for the app"""
    # Try to get the image as base64
    bin_str = get_base64_of_bin_file('bg.jpg')
    
    if bin_str:
        # If local image exists, use it
        background_css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        .stApp > div:first-child {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }}
        
        /* Make main content area semi-transparent */
        .main .block-container {{
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 1rem;
            margin-top: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        /* Keep sidebar opaque */
        .css-1d391kg, .css-1544g2n {{
            background-color: rgba(255, 255, 255, 0.95) !important;
        }}
        
        /* Make charts blend better - remove white background completely */
        .js-plotly-plot {{
            background: transparent !important;
            border-radius: 10px;
            padding: 10px;
        }}
        
        .js-plotly-plot .plotly {{
            background: transparent !important;
        }}
        
        /* Improve text visibility */
        .stMarkdown, .stDataFrame, .stSelectbox, .stText {{
            color: #1a1a1a !important;
        }}
        
        h1, h2, h3, h4, h5, h6, p, .stMetric {{
            color: #1a1a1a !important;
            text-shadow: 0 0 5px rgba(255, 255, 255, 0.8);
        }}
        </style>
        """
    else:
        # Fallback: use a gradient background
        background_css = """
        <style>
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            background-attachment: fixed;
        }
        
        .main .block-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            padding: 1rem;
            margin-top: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Keep sidebar opaque */
        .css-1d391kg, .css-1544g2n {
            background-color: rgba(255, 255, 255, 0.95) !important;
        }
        
        /* Make charts blend better - remove white background completely */
        .js-plotly-plot {
            background: transparent !important;
            border-radius: 10px;
            padding: 10px;
        }
        
        .js-plotly-plot .plotly {
            background: transparent !important;
        }
        </style>
        """
    
    st.markdown(background_css, unsafe_allow_html=True)

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
    
    st.markdown(f"<h2 style='color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); font-weight: bold; margin-bottom: 20px; margin-top: 0px;'>📊 Catalog Insights - {selected_catalog_year}</h2>", unsafe_allow_html=True)
    
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
    
    # Center the pie chart with better styling
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # College pie chart based on number of programs
        fig_college = px.pie(
            values=college_program_counts['program_count'],
            names=college_program_counts['college'],
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
        )
        
        # Update hover template to show programs
        fig_college.update_traces(
            hovertemplate=hover_text,
            textinfo="label+percent",
            textfont_size=14,
            textfont_color='white',
            textposition='inside'
        )
        
        # Improve chart styling with transparent background
        fig_college.update_layout(
            height=400, 
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',  # Changed to transparent
            font=dict(color='#1a1a1a', size=14, family="Arial Black"),
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05,
                font=dict(size=12, color='#1a1a1a'),
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='#1a1a1a',
                borderwidth=1
            ),
            margin=dict(l=20, r=150, t=20, b=20)
        )
        
        st.plotly_chart(fig_college, use_container_width=True)
    
    # Summary statistics with increased opacity for background blending
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.7); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.5); text-align: center; backdrop-filter: blur(5px);'>
            <h3 style='color: #1a1a1a; margin: 0; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>Total Colleges</h3>
            <h1 style='color: #FF6B6B; margin: 10px 0 0 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>{}</h1>
        </div>
        """.format(len(catalog_df['college'].unique())), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.7); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.5); text-align: center; backdrop-filter: blur(5px);'>
            <h3 style='color: #1a1a1a; margin: 0; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>Total Programs</h3>
            <h1 style='color: #4ECDC4; margin: 10px 0 0 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>{}</h1>
        </div>
        """.format(len(catalog_df['program'].unique())), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.7); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.5); text-align: center; backdrop-filter: blur(5px);'>
            <h3 style='color: #1a1a1a; margin: 0; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>Total Courses</h3>
            <h1 style='color: #45B7D1; margin: 10px 0 0 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>{}</h1>
        </div>
        """.format(len(catalog_df)), unsafe_allow_html=True)

def login_page():
    """Display horizontal login page with NO white boxes and proper viewport sizing"""
    
    # Set background image
    set_background_image()
    
    # Add custom CSS to completely remove white containers and fix viewport
    st.markdown("""
    <style>
    /* Hide the default Streamlit header and menu */
    .stApp > header {
        background-color: transparent;
        height: 0px;
    }
    
    /* Force full height usage */
    html, body, [data-testid="stAppViewContainer"] {
        height: 100vh !important;
        overflow: hidden !important;
    }
    
    [data-testid="stAppViewContainer"] > .main {
        height: 100vh !important;
        overflow-y: auto !important;
        padding-top: 0 !important;
    }
    
    /* Remove ALL white backgrounds and containers */
    .main .block-container {
        background: transparent !important;
        padding: 1rem 2rem !important;
        margin: 0 !important;
        box-shadow: none !important;
        max-width: 100% !important;
        height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    
    /* Remove any element containers */
    .element-container {
        background: transparent !important;
    }
    
    /* Hide Streamlit's image container styling */
    .stImage {
        background: transparent !important;
    }
    
    .stImage > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Custom login sections with NO background boxes */
    .logo-section {
        text-align: center;
        margin: 10px 0;
        padding: 20px;
        flex-shrink: 0;
    }
    
    .login-section {
        margin: 10px 0;
        padding: 20px;
        flex-shrink: 0;
    }
    
    .credits-section {
        text-align: center;
        margin-top: 20px;
        padding: 10px;
        border-top: 2px solid rgba(255,255,255,0.3);
        flex-shrink: 0;
    }
    
    .app-title {
        font-size: 5rem;
        font-weight: bold;
        color: white !important; 
        margin: 5px 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
        font-family: 'Arial Black', sans-serif;
        line-height: 1.1;
    }
    
    .app-subtitle {
        font-size: 3rem;
        color: white !important; 
        margin-bottom: 5px;
        font-weight: 600;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
        line-height: 1.2;
    }
    
    .login-title {
        font-size: 2rem;
        color: white;
        margin-bottom: 20px;
        text-align: center;
        font-weight: bold;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
    }
    
    .credits-text {
        color: white !important;
        font-size: 14px;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    }
    
    .credits-text p {
        color: white !important;
        margin: 5px 0 !important;
    }
    
    .credits-text strong {
        color: white !important;
    }
    
    /* Make form inputs more visible */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-size: 16px !important;
        color: #1a1a1a !important;
        font-weight: 500 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4ECDC4 !important;
        box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.3) !important;
    }
    
    .stTextInput > label {
        color: white !important;
        font-weight: bold !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7) !important;
        font-size: 16px !important;
    }
    
    /* Style buttons */
    .stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 25px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4) !important;
    }
    
    /* Adjust column spacing */
    .block-container [data-testid="column"] {
        padding: 0 1rem !important;
    }
    
    /* Fix main content container */
    .main-content-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100vh;
        max-height: 100vh;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Wrap everything in a container to control layout
    st.markdown('<div class="main-content-container">', unsafe_allow_html=True)
    
    # Main content - two columns
    col_left, col_right = st.columns([1, 1], gap="large")
    
    # Left side - Logo and App Name
    with col_left:
        st.markdown('<div class="logo-section">', unsafe_allow_html=True)

        # Show logo FIRST - above everything
        try:
            # Force the logo to display with centered alignment
            col1, col2, col3 = st.columns([0.5, 1, 0.5])
            with col2:
                st.image("iobm.png", width=250)
        except Exception as e:
            # Fallback if image doesn't load
            st.markdown('''
            <div style="display: flex; justify-content: center; margin-bottom: 15px;">
                <div style="width: 250px; height: 150px; background: rgba(255,255,255,0.2); 
                           display: flex; align-items: center; justify-content: center; 
                           border-radius: 10px;">
                    <h1 style="color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.7); margin: 0;">IOBM</h1>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        # Title + subtitle (AFTER logo, with some spacing)
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <h1 class="app-title">SSK ACMS</h1>
            <p class="app-subtitle">Academic Course Management System</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    
    # Right side - Login Form
    with col_right:
        st.markdown('<div class="login-section">', unsafe_allow_html=True)
        
        st.markdown('<h2 class="login-title">🔐 Login</h2>', unsafe_allow_html=True)
        
        # Login form with better spacing
        username = st.text_input("👤 Username", placeholder="Enter your username", key="username_input")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="password_input")
        
        # Add spacing
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
    
    # Bottom - Credits section with thin line separator
    st.markdown('<div class="credits-section">', unsafe_allow_html=True)
    st.markdown("""
    <div class="credits-text">
        <p><strong>Development Team:</strong> Fahad Hassan, Ali Hasnain Abro | <strong>Supervisor:</strong> Dr. Rabiya Sabri | <strong>Designer:</strong> Habibullah Rajpar</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Close main container
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
    """Main application interface with improved design and proper spacing"""
    
    # Set background image for main app
    set_background_image()
    
    # Add CSS for white text in header and footer
    st.markdown("""
    <style>
    /* Main app container adjustments */
    .main .block-container {
        padding-top: 1rem !important;
        margin-top: 0 !important;
    }
    
    /* White text for headers and important elements */
    .main-header h1, .main-header p {
        color: white !important;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.8) !important;
    }
    
    .main-footer p, .main-footer strong {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7) !important;
    }
    
    /* Reduce spacing and margins */
    .chart-container {
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    
    /* Compact layout adjustments */
    div[data-testid="stMarkdownContainer"] {
        margin-bottom: 0.5rem !important;
    }
    
    .stPlotlyChart {
        margin-top: 0 !important;
        margin-bottom: 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with white text and better alignment
    st.markdown(f"""
    <div class="main-header" style='display: flex; align-items: center; justify-content: space-between; padding:
