"""
Mobile-Optimized Resume Analyzer for Android Deployment
Streamlit app optimized for mobile devices and WebView embedding
"""
import streamlit as st
from pathlib import Path

# Mobile-optimized page config
st.set_page_config(
    page_title="Resume AI - Mobile",
    page_icon="",
    layout="centered",  # Better for mobile
    initial_sidebar_state="collapsed"
)

# Mobile CSS optimizations
MOBILE_CSS = """
<style>
/* Mobile-specific optimizations */
@media (max-width: 768px) {
    .stSelectbox > div > div {
        font-size: 16px !important;
    }
    
    .stButton > button {
        width: 100% !important;
        margin: 5px 0;
        font-size: 16px !important;
    }
    
    .stFileUploader {
        width: 100% !important;
    }
    
    .stTextArea textarea {
        font-size: 16px !important;
    }
    
    .stMetric {
        margin: 5px 0;
    }
    
    .stColumns {
        gap: 10px;
    }
    
    .stExpander {
        margin: 10px 0;
    }
}

/* Hide Streamlit branding for app-like feel */
footer {
    visibility: hidden;
}

/* Custom mobile header */
.mobile-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
    text-align: center;
    color: white;
}

/* Mobile navigation */
.mobile-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #1a1a1a;
    padding: 10px;
    display: flex;
    justify-content: space-around;
    z-index: 999;
}

.mobile-nav button {
    background: none;
    border: none;
    color: white;
    padding: 10px;
    border-radius: 5px;
    cursor: pointer;
}

.mobile-nav button:hover {
    background: #333;
}

/* Mobile upload area */
.mobile-upload {
    border: 2px dashed #667eea;
    border-radius: 10px;
    padding: 30px;
    text-align: center;
    margin: 20px 0;
    background: #f8f9fa;
}

/* Mobile cards */
.mobile-card {
    background: white;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

/* Mobile metrics */
.mobile-metrics {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin: 20px 0;
}

.mobile-metric {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}

.mobile-metric-value {
    font-size: 24px;
    font-weight: bold;
}

.mobile-metric-label {
    font-size: 12px;
    opacity: 0.8;
}
</style>
"""

# Apply mobile CSS
st.markdown(MOBILE_CSS, unsafe_allow_html=True)

# Mobile-optimized components
def mobile_header(title, subtitle=""):
    """Mobile-optimized header"""
    st.markdown(f"""
    <div class="mobile-header">
        <h1 style="margin: 0; font-size: 24px;">{title}</h1>
        {f'<p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def mobile_upload_area(label, help_text=""):
    """Mobile-optimized file upload"""
    st.markdown(f"""
    <div class="mobile-upload">
        <h3 style="margin: 0 0 10px 0;">{label}</h3>
        <p style="margin: 0; color: #666; font-size: 14px;">{help_text}</p>
    </div>
    """, unsafe_allow_html=True)

def mobile_metrics(metrics_data):
    """Mobile-optimized metrics display"""
    st.markdown('<div class="mobile-metrics">', unsafe_allow_html=True)
    
    for label, value in metrics_data.items():
        st.markdown(f"""
        <div class="mobile-metric">
            <div class="mobile-metric-value">{value}</div>
            <div class="mobile-metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def mobile_card(title, content, icon=""):
    """Mobile-optimized card"""
    st.markdown(f"""
    <div class="mobile-card">
        <h3 style="margin: 0 0 10px 0; color: #333;">
            {icon} {title}
        </h3>
        <div style="color: #666; font-size: 14px;">{content}</div>
    </div>
    """, unsafe_allow_html=True)

def mobile_navigation(current_page="home"):
    """Mobile bottom navigation"""
    nav_items = {
        "home": ("", "Home"),
        "analyzer": ("", "Analyze"),
        "interview": ("", "Interview"),
        "roadmap": ("", "Roadmap")
    }
    
    st.markdown('<div class="mobile-nav">', unsafe_allow_html=True)
    
    for key, (icon, label) in nav_items.items():
        active = "background: #333;" if key == current_page else ""
        st.markdown(f"""
        <button style="{active}" onclick="navigateTo('{key}')">
            {icon}<br>{label}
        </button>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Mobile-optimized main app
def main():
    """Mobile-optimized main application"""
    
    # Mobile header
    mobile_header("Resume AI", "Your Career Assistant")
    
    # Mobile navigation
    mobile_navigation()
    
    # Page content
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    # Home page
    if st.session_state.page == 'home':
        mobile_card("Welcome to Resume AI", 
                    "Upload your resume to get instant AI-powered analysis and career guidance.")
        
        mobile_upload_area("Upload Resume", "Tap to select PDF or DOCX file")
        
        uploaded_file = st.file_uploader("", type=['pdf', 'docx'], label_visibility="collapsed")
        
        if uploaded_file:
            st.success("File uploaded successfully!")
            if st.button("Analyze Resume", type="primary", use_container_width=True):
                st.session_state.page = 'analyzer'
                st.rerun()
    
    # Analyzer page
    elif st.session_state.page == 'analyzer':
        mobile_header("Resume Analysis")
        
        # Simulated analysis results
        mobile_metrics({
            "ATS Score": "85/100",
            "Skills Match": "78%",
            "Grade": "B+",
            "Improvement": "+15%"
        })
        
        mobile_card("Key Skills", 
                   "Python, JavaScript, React, SQL, Machine Learning")
        
        mobile_card("Recommendations", 
                   "Add more technical skills, include project descriptions, optimize for keywords")
        
        if st.button("View Full Report", use_container_width=True):
            st.info("Full report feature coming soon!")
        
        if st.button("Back to Home", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()
    
    # Interview page
    elif st.session_state.page == 'interview':
        mobile_header("Interview Coach")
        
        mobile_card("Practice Interview", 
                   "Get AI-powered interview questions and feedback")
        
        role = st.selectbox("Target Role", 
                          ["Software Engineer", "Web Developer", "Data Analyst"])
        
        if st.button("Start Interview", type="primary", use_container_width=True):
            st.info("Interview feature coming soon!")
        
        if st.button("Back to Home", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()
    
    # Roadmap page
    elif st.session_state.page == 'roadmap':
        mobile_header("Learning Roadmap")
        
        mobile_card("Skill Development", 
                   "Get personalized learning paths based on your career goals")
        
        target_role = st.selectbox("Career Goal", 
                                 ["Software Engineer", "Web Developer", "Data Analyst"])
        
        time_commitment = st.selectbox("Time Commitment", 
                                     ["Casual", "Part-time", "Full-time"])
        
        if st.button("Generate Roadmap", type="primary", use_container_width=True):
            st.info("Roadmap generation coming soon!")
        
        if st.button("Back to Home", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()

if __name__ == "__main__":
    main()
