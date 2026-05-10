"""
Mobile Configuration for Android Deployment
Configures Streamlit for mobile compatibility and responsive design
"""

import streamlit as st

# Mobile-optimized configuration
MOBILE_CONFIG = {
    # Layout settings
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    
    # Mobile-friendly settings
    "page_title": "Resume AI",
    "page_icon": "📱",
    
    # Theme settings for mobile
    "theme": {
        "primaryColor": "#FF6B6B",
        "backgroundColor": "#FFFFFF",
        "secondaryBackgroundColor": "#F0F2F6",
        "textColor": "#262730",
        "font": "sans serif"
    }
}

def configure_mobile_app():
    """Configure Streamlit for mobile compatibility"""
    # Set page config for mobile
    st.set_page_config(
        page_title=MOBILE_CONFIG["page_title"],
        page_icon=MOBILE_CONFIG["page_icon"],
        layout=MOBILE_CONFIG["layout"],
        initial_sidebar_state=MOBILE_CONFIG["initial_sidebar_state"]
    )
    
    # Add mobile-specific CSS
    mobile_css = """
    <style>
    /* Mobile-specific styles */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 100%;
        }
        
        .stButton > button {
            width: 100%;
            margin-bottom: 0.5rem;
        }
        
        .stSelectbox > div > div > select {
            width: 100%;
        }
        
        .stTextInput > div > div > input {
            width: 100%;
        }
        
        .stFileUploader > div > div > button {
            width: 100%;
        }
        
        .sidebar .sidebar-content {
            padding: 0.5rem;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-size: clamp(1rem, 4vw, 2rem);
        }
        
        .streamlit-expanderHeader {
            font-size: 1rem;
        }
        
        .plotly-graph-div {
            width: 100% !important;
        }
    }
    
    /* Touch-friendly buttons */
    .stButton > button {
        min-height: 44px;
        touch-action: manipulation;
    }
    
    /* Better mobile form inputs */
    input, textarea, select {
        font-size: 16px; /* Prevents zoom on iOS */
    }
    
    /* Responsive containers */
    .element-container {
        width: 100%;
    }
    
    /* Mobile-friendly navigation */
    .css-1d391kg {
        flex-direction: column;
    }
    
    /* Hide desktop-only elements on mobile */
    @media (max-width: 768px) {
        .desktop-only {
            display: none !important;
        }
    }
    
    /* Show mobile-only elements on mobile */
    @media (min-width: 769px) {
        .mobile-only {
            display: none !important;
        }
    }
    </style>
    """
    
    st.markdown(mobile_css, unsafe_allow_html=True)

def is_mobile():
    """Detect if user is on mobile device"""
    user_agent = st.experimental_get_query_params().get("user_agent", "")
    mobile_indicators = ["mobile", "android", "iphone", "ipad", "tablet"]
    return any(indicator in user_agent.lower() for indicator in mobile_indicators)

def mobile_friendly_upload(label, key, help_text=None, types=None):
    """Mobile-friendly file uploader"""
    if types is None:
        types = ['pdf', 'docx', 'txt']
    
    return st.file_uploader(
        label=label,
        type=types,
        key=key,
        help=help_text,
        use_container_width=True
    )

def mobile_friendly_button(label, key=None, type="primary", disabled=False):
    """Mobile-friendly button"""
    return st.button(
        label=label,
        key=key,
        type=type,
        disabled=disabled,
        use_container_width=True
    )

def mobile_friendly_columns(n_cols):
    """Create mobile-friendly columns"""
    if is_mobile():
        # Stack columns vertically on mobile
        return [st.container() for _ in range(n_cols)]
    else:
        # Use normal columns on desktop
        return st.columns(n_cols)

def mobile_info_message():
    """Show mobile-specific information"""
    if is_mobile():
        st.info("📱 Mobile Mode: Optimized for touch interaction")
    else:
        st.info("💻 Desktop Mode: Full feature set available")
