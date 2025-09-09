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
        justify-content: center;
        text-align: center;
        padding: 20px;
        margin-top: 0px;  /* Changed from -100px */
    }
    .login-section {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 40px;
        margin-top: 0px;  /* Changed from -50px */
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
        margin: 10px 0 5px 0;  /* Reduced top and bottom margins */
    }
    .app-subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 10px;  /* Reduced from 20px */
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
        
        # App title and subtitle - properly centered with reduced spacing
        st.markdown("""
        <div style="text-align: center; margin-top: 10px;">  <!-- Reduced from 20px -->
            <h1 style="font-size: 3rem; font-weight: bold; color: #1f77b4; margin: 5px 0; line-height: 1.1;">SSK ACMS</h1>  <!-- Reduced margins and line-height -->
            <p style="font-size: 1.2rem; color: #666; margin: 5px 0 0 0;">Academic Course Management System</p>  <!-- Reduced margins -->
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
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
