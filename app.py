import os
import math
import random
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import base64
from io import BytesIO

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
if 'student_counts' not in st.session_state:
    st.session_state.student_counts = {}
if 'section_capacities' not in st.session_state:
    st.session_state.section_capacities = {}

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

def create_upload_template():
    """Create a template CSV file for upload"""
    template_data = {
        'program': ['BBA', 'BBA', 'MBA'],
        'college': ['College of Business Management', 'College of Business Management', 'College of Business Management'],
        'semester': ['one', 'one', 'one'],
        'course_code': ['ACC101', 'MGT101', 'MBA501'],
        'course_title': ['Introduction to Accounting', 'Principles of Management', 'Strategic Management']
    }
    
    template_df = pd.DataFrame(template_data)
    return template_df

def show_upload_guidelines():
    """Display upload guidelines and template"""
    st.markdown("""
    <div style='background: rgba(255,255,255,0.9); padding: 20px; border-radius: 10px; margin: 20px 0;'>
        <h3 style='color: #1a1a1a; margin-top: 0;'>📋 Upload Guidelines</h3>
        
        <h4 style='color: #1a1a1a;'>Required Columns:</h4>
        <ul style='color: #1a1a1a;'>
            <li><strong>program</strong> - Name of the academic program (e.g., BBA, MBA, BCS)</li>
            <li><strong>college</strong> - Name of the college offering the course</li>
            <li><strong>semester</strong> - Semester number (one, two, three, etc. or 1, 2, 3, etc.)</li>
            <li><strong>course_code</strong> - Unique course identifier (e.g., ACC101, MGT201)</li>
            <li><strong>course_title</strong> - Full name of the course</li>
        </ul>
        
        <h4 style='color: #1a1a1a;'>Important Notes:</h4>
        <ul style='color: #1a1a1a;'>
            <li>All columns listed above are <strong>REQUIRED</strong></li>
            <li>Column names should be exactly as shown (case-insensitive)</li>
            <li>Semester values can be: one/1, two/2, three/3, four/4, five/5, six/6, seven/7, eight/8</li>
            <li>File format: CSV (.csv) or Excel (.xlsx)</li>
            <li>Make sure there are no empty rows in your data</li>
            <li>Course codes should be unique within each program and semester</li>
        </ul>
        
        <h4 style='color: #1a1a1a;'>Example Data:</h4>
        <table style='width: 100%; border-collapse: collapse; color: #1a1a1a;'>
            <tr style='background: #f0f0f0;'>
                <th style='padding: 8px; border: 1px solid #ddd;'>program</th>
                <th style='padding: 8px; border: 1px solid #ddd;'>college</th>
                <th style='padding: 8px; border: 1px solid #ddd;'>semester</th>
                <th style='padding: 8px; border: 1px solid #ddd;'>course_code</th>
                <th style='padding: 8px; border: 1px solid #ddd;'>course_title</th>
            </tr>
            <tr>
                <td style='padding: 8px; border: 1px solid #ddd;'>BBA</td>
                <td style='padding: 8px; border: 1px solid #ddd;'>College of Business Management</td>
                <td style='padding: 8px; border: 1px solid #ddd;'>one</td>
                <td style='padding: 8px; border: 1px solid #ddd;'>ACC101</td>
                <td style='padding: 8px; border: 1px solid #ddd;'>Introduction to Accounting</td>
            </tr>
            <tr style='background: #f9f9f9;'>
                <td style='padding: 8px; border: 1px solid #ddd;'>MBA</td>
                <td style='padding: 8px; border: 1px solid #ddd;'>College of Business Management</td>
                <td style='padding: 8px; border: 1px solid #ddd;'>one</td>
                <td style='padding: 8px; border: 1px solid #ddd;'>MBA501</td>
                <td style='padding: 8px; border: 1px solid #ddd;'>Strategic Management</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    # Download template button
    template_df = create_upload_template()
    csv_template = template_df.to_csv(index=False).encode('utf-8')
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="📥 Download Template CSV",
            data=csv_template,
            file_name="ssk_acms_upload_template.csv",
            mime="text/csv",
            use_container_width=True
        )

def generate_report_summary(final_df, program_filter, semester_filter, student_counts=None, section_capacities=None):
    """Generate a comprehensive summary of the generated report"""
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 25px; border-radius: 15px; margin: 20px 0; 
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);'>
        <h2 style='color: white; text-align: center; margin: 0 0 20px 0; 
                   text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>
            📊 Report Summary
        </h2>
    """, unsafe_allow_html=True)
    
    # Overall statistics
    total_courses = len(final_df)
    total_sections = final_df['section'].nunique() if 'section' in final_df.columns else len(final_df)
    total_students = final_df['total student strength'].sum() if 'total student strength' in final_df.columns else 0
    programs_included = final_df['program'].nunique()
    
    # Create 4 columns for key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.95); padding: 15px; border-radius: 10px; text-align: center;'>
            <h4 style='color: #667eea; margin: 0;'>Total Courses</h4>
            <h2 style='color: #1a1a1a; margin: 10px 0 0 0;'>{total_courses}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.95); padding: 15px; border-radius: 10px; text-align: center;'>
            <h4 style='color: #764ba2; margin: 0;'>Total Sections</h4>
            <h2 style='color: #1a1a1a; margin: 10px 0 0 0;'>{total_sections}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.95); padding: 15px; border-radius: 10px; text-align: center;'>
            <h4 style='color: #FF6B6B; margin: 0;'>Total Students</h4>
            <h2 style='color: #1a1a1a; margin: 10px 0 0 0;'>{total_students}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.95); padding: 15px; border-radius: 10px; text-align: center;'>
            <h4 style='color: #4ECDC4; margin: 0;'>Programs</h4>
            <h2 style='color: #1a1a1a; margin: 10px 0 0 0;'>{programs_included}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Program-wise breakdown
    if program_filter == "All Programs":
        st.markdown("""
        <div style='background: rgba(255,255,255,0.95); padding: 20px; border-radius: 10px; margin-top: 15px;'>
            <h3 style='color: #1a1a1a; margin-top: 0;'>📚 Program-wise Breakdown</h3>
        """, unsafe_allow_html=True)
        
        program_summary = final_df.groupby('program').agg({
            'course_code': 'count',
            'section': 'nunique',
            'total student strength': 'first'
        }).reset_index()
        program_summary.columns = ['Program', 'Courses', 'Sections', 'Students']
        
        # Add capacity information if available
        if section_capacities:
            capacity_list = []
            for prog in program_summary['Program']:
                capacity = section_capacities.get(prog, 40)
                capacity_list.append(capacity)
            program_summary['Section Capacity'] = capacity_list
        
        st.dataframe(program_summary, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Single program details
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.95); padding: 20px; border-radius: 10px; margin-top: 15px;'>
            <h3 style='color: #1a1a1a; margin-top: 0;'>📚 {program_filter} - Semester {semester_filter}</h3>
            <p style='color: #1a1a1a; font-size: 16px;'><strong>Courses:</strong> {total_courses} | <strong>Sections:</strong> {total_sections} | <strong>Students:</strong> {total_students}</p>
        """, unsafe_allow_html=True)
        
        if section_capacities and program_filter in section_capacities:
            capacity = section_capacities[program_filter]
            st.markdown(f"<p style='color: #1a1a1a;'><strong>Section Capacity:</strong> {capacity} students per section</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Day-wise distribution
    if 'days' in final_df.columns:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.95); padding: 20px; border-radius: 10px; margin-top: 15px;'>
            <h3 style='color: #1a1a1a; margin-top: 0;'>📅 Schedule Distribution</h3>
        """, unsafe_allow_html=True)
        
        day_counts = final_df['days'].value_counts().reset_index()
        day_counts.columns = ['Day', 'Number of Classes']
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(day_counts, use_container_width=True, hide_index=True)
        
        with col2:
            # Weekend vs Weekday breakdown
            weekend_classes = final_df[final_df['days'].str.contains('Saturday|Sunday', case=False, na=False)].shape[0]
            weekday_classes = total_courses - weekend_classes
            
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.95); padding: 15px; border-radius: 10px; text-align: center;'>
                <h4 style='color: #1a1a1a; margin: 0;'>Weekday Classes</h4>
                <h2 style='color: #4ECDC4; margin: 10px 0;'>{weekday_classes}</h2>
                <h4 style='color: #1a1a1a; margin: 15px 0 0 0;'>Weekend Classes</h4>
                <h2 style='color: #FF6B6B; margin: 10px 0 0 0;'>{weekend_classes}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

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
    bin_str = get_base64_of_bin_file('bg.jpg')
    
    if bin_str:
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
        
        .main .block-container {{
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 2rem;
            margin-top: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div {{
            background-color: rgba(30, 30, 30, 0.95) !important;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-right: 2px solid rgba(255, 255, 255, 0.2) !important;
        }}
        
        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3,
        section[data-testid="stSidebar"] .stMarkdown h4,
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] label {{
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8) !important;
            font-weight: bold !important;
        }}
        
        section[data-testid="stSidebar"] .stSelectbox > div > div > div,
        section[data-testid="stSidebar"] .stNumberInput > div > div > input,
        section[data-testid="stSidebar"] .stTextInput > div > div > input {{
            background-color: rgba(60, 60, 60, 0.9) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 5px !important;
        }}
        
        section[data-testid="stSidebar"] .stButton > button {{
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: bold !important;
        }}
        
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
        h1, h2, h3, h4, h5, h6, p {{
            color: white !important;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.8) !important;
        }}
        </style>
        """
    else:
        background_css = """
        <style>
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            background-attachment: fixed;
        }
        
        .main .block-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            padding: 2rem;
            margin-top: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div {
            background-color: rgba(30, 30, 30, 0.95) !important;
            backdrop-filter: blur(10px);
            border-right: 2px solid rgba(255, 255, 255, 0.2) !important;
        }
        
        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3,
        section[data-testid="stSidebar"] .stMarkdown h4,
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] label {
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8) !important;
            font-weight: bold !important;
        }
        
        section[data-testid="stSidebar"] .stSelectbox > div > div > div,
        section[data-testid="stSidebar"] .stNumberInput > div > div > input,
        section[data-testid="stSidebar"] .stTextInput > div > div > input {
            background-color: rgba(60, 60, 60, 0.9) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 5px !important;
        }
        
        section[data-testid="stSidebar"] .stButton > button {
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: bold !important;
        }
        
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
        h1, h2, h3, h4, h5, h6, p {
            color: white !important;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.8) !important;
        }
        </style>
        """
    
    st.markdown(background_css, unsafe_allow_html=True)

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
        catalog_df.columns = catalog_df.columns.str.lower().str.strip()
        catalog_df = catalog_df.dropna(subset=['semester'])
        catalog_df = catalog_df[catalog_df['semester'].astype(str).str.strip() != '']
        catalog_df['course_code'] = catalog_df['course_code'].fillna('')
        catalog_df['course_title'] = catalog_df['course_title'].fillna('Unknown Course')
        catalog_df['college'] = catalog_df.get('college', pd.Series(['Unknown College'] * len(catalog_df)))
        catalog_df['college'] = catalog_df['college'].fillna('Unknown College')
        catalog_df['semester'] = catalog_df['semester'].astype(str).str.lower().str.strip()
        
        return catalog_df, True
        
    except Exception as e:
        st.error(f"Error processing catalog file {filename}: {e}")
        return None, False

def create_catalog_charts(catalog_df, selected_catalog_year):
    """Create single pie chart showing college distribution by number of programs"""
    
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2 style='color: white !important; text-shadow: 3px 3px 6px rgba(0,0,0,0.8) !important; 
                   font-weight: bold !important; margin: 0 !important; font-size: 2.2rem !important;
                   font-family: Arial Black, sans-serif !important;'>
            📊 Catalog Insights - {selected_catalog_year}
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    college_program_counts = catalog_df.groupby('college')['program'].nunique().reset_index()
    college_program_counts.columns = ['college', 'program_count']
    college_program_counts = college_program_counts.sort_values('program_count', ascending=False)
    
    hover_text = []
    for college in college_program_counts['college']:
        programs_in_college = catalog_df[catalog_df['college'] == college]['program'].unique()
        programs_list = "<br>• ".join(sorted(programs_in_college))
        hover_text.append(f"<b>{college}</b><br>Programs: {len(programs_in_college)}<br><br>• {programs_list}")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        fig_college = px.pie(
            values=college_program_counts['program_count'],
            names=college_program_counts['college'],
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
        )
        
        fig_college.update_traces(
            hovertemplate=hover_text,
            textinfo="label+percent",
            textfont_size=14,
            textfont_color='white',
            textposition='inside'
        )
        
        fig_college.update_layout(
            height=300,
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
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
            margin=dict(l=20, r=150, t=5, b=5)
        )
        
        st.plotly_chart(fig_college, use_container_width=True)
    
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
    """Display horizontal login page"""
    set_background_image()
    
    st.markdown("""
    <style>
    .stApp > header {
        background-color: transparent;
    }
    
    .main .block-container {
        background: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
    }
    
    .element-container {
        background: transparent !important;
    }
    
    .app-title {
        font-size: 5rem;
        font-weight: bold;
        color: white !important; 
        margin: 10px 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
        font-family: 'Arial Black', sans-serif;
    }
    
    .app-subtitle {
        font-size: 3rem;
        color: white !important; 
        margin-bottom: 10px;
        font-weight: 600;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    }
    
    .login-title {
        font-size: 2rem;
