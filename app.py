import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
import base64
import io
import re
from PIL import Image as PILImage

# Page config
st.set_page_config(
    page_title="AI Resume Builder Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1e1e2e !important;
        color: #ffffff !important;
        border: 2px solid #40414f !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-size: 14px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 600 !important;
        height: 44px !important;
        font-size: 16px !important;
        box-shadow: 0 4px 14px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Header */
    .main-header {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .section-header {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        background: linear-gradient(45deg, #4fc3f7, #29b6f6) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin: 2rem 0 1rem 0 !important;
        border-bottom: 3px solid #40414f !important;
        padding-bottom: 0.5rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(145deg, #1e1e2e, #2a2a3e) !important;
        border: 1px solid #40414f !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3) !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    
    /* Preview */
    .preview-container {
        background: white !important;
        border-radius: 16px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3) !important;
        overflow: hidden !important;
        height: 80vh !important;
        position: relative !important;
    }
</style>
""", unsafe_allow_html=True)

# ATS Score Calculator
def calculate_ats_score(resume_data):
    score = 100
    issues = []
    
    # Check keyword density
    if len(resume_data.get('skills', [])) < 5:
        score -= 15
        issues.append("Add 5+ relevant skills")
    
    # Check contact info
    if not resume_data.get('email') or not re.match(r"[^@]+@[^@]+\.[^@]+", resume_data['email']):
        score -= 20
        issues.append("Valid email required")
    
    # Check experience
    if len(resume_data.get('experience', [])) == 0:
        score -= 25
        issues.append("Add work experience")
    
    # Check education
    if len(resume_data.get('education', [])) == 0:
        score -= 15
        issues.append("Add education")
    
    # Check summary length
    summary = resume_data.get('summary', '')
    if len(summary.split()) < 20:
        score -= 10
        issues.append("Summary too short (aim for 3-5 sentences)")
    
    return max(0, score), issues

def create_pdf_resume(data, theme="blue", profile_image=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=60, leftMargin=60, topMargin=60, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    # Theme colors
    theme_colors = {
        "blue": {"primary": "#2563eb", "secondary": "#1e40af", "accent": "#3b82f6"},
        "green": {"primary": "#059669", "secondary": "#047857", "accent": "#10b981"},
        "purple": {"primary": "#7c3aed", "secondary": "#6d28d9", "accent": "#8b5cf6"},
        "orange": {"primary": "#ea580c", "secondary": "#c2410c", "accent": "#f97316"}
    }
    
    color = theme_colors[theme]
    
    # Custom styles with theme
    name_style = ParagraphStyle('Name', fontSize=28, spaceAfter=10, alignment=TA_CENTER,
                               textColor=colors.HexColor(color['primary']), fontName='Helvetica-Bold')
    title_style = ParagraphStyle('Title', fontSize=18, spaceAfter=20, alignment=TA_CENTER,
                                textColor=colors.HexColor(color['secondary']), fontName='Helvetica-Bold')
    
    heading_style = ParagraphStyle('Heading', fontSize=14, spaceAfter=8, spaceBefore=12,
                                  textColor=colors.HexColor(color['primary']), fontName='Helvetica-Bold')
    body_style = ParagraphStyle('Body', fontSize=11, spaceAfter=6, leftIndent=15,
                               textColor=colors.black, fontName='Helvetica')
    
    story = []
    
    # Profile image
    if profile_image:
        try:
            img = PILImage.open(profile_image)
            img_buffer = BytesIO()
            img.resize((80, 100)).save(img_buffer, format='PNG')
            img_data = img_buffer.getvalue()
            story.append(Image(img_data, width=1.2*inch, height=1.5*inch))
            story.append(Spacer(1, 10))
        except:
            pass
    
    # Name
    story.append(Paragraph(data['name'], name_style))
    story.append(Paragraph(data.get('title', ''), title_style))
    
    # Contact
    contact_text = f"<font size=10>{data['email']} | {data['phone']} | {data.get('linkedin', '')} | {data.get('location', '')}</font>"
    story.append(Paragraph(contact_text, body_style))
    story.append(Spacer(1, 20))
    
    # Sections
    sections = [
        ('summary', 'PROFESSIONAL SUMMARY'),
        ('education', 'EDUCATION'),
        ('experience', 'EXPERIENCE'),
        ('skills', 'SKILLS'),
        ('projects', 'PROJECTS')
    ]
    
    for key, title in sections:
        content = data.get(key, [])
        if content:
            story.append(Paragraph(title, heading_style))
            if key == 'skills':
                table_data = [['Skill']]
                for skill in content:
                    table_data.append([skill])
                table = Table(table_data, colWidths=[4*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f3f4f6')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor(color['secondary'])),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 11),
                    ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9fafb')])
                ]))
                story.append(table)
            else:
                for item in content:
                    text = item.get('text', str(item))
                    story.append(Paragraph(text, body_style))
            story.append(Spacer(1, 12))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Live Preview Function
@st.cache_data
def generate_preview(data, theme, profile_image):
    pdf_bytes = create_pdf_resume(data, theme, profile_image)
    return pdf_bytes

def main():
    st.markdown('<h1 class="main-header">🎯 AI Resume Builder Pro</h1>', unsafe_allow_html=True)
    
    # Sidebar Navigation
    st.sidebar.title("⚙️ Settings")
    
    # Theme selector
    theme = st.sidebar.selectbox("Resume Theme", ["blue", "green", "purple", "orange"])
    
    # Profile photo
    profile_image = None
    uploaded_file = st.sidebar.file_uploader("📸 Profile Photo (optional)", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        profile_image = uploaded_file
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**💡 Pro Tips:**")
    st.sidebar.markdown("• Use action verbs")
    st.sidebar.markdown("• Quantify achievements")
    st.sidebar.markdown("• Tailor to job description")
    
    # Main content with tabs
    tab1, tab2 = st.tabs(["📝 Builder", "📊 ATS Analyzer"])
    
    with tab1:
        # 2-column layout: Form | Preview
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Form data
            with st.form("resume_form"):
                st.markdown('<h2 class="section-header">👤 Personal Info</h2>', unsafe_allow_html=True)
                
                name = st.text_input("Full Name", placeholder="John Doe")
                title = st.text_input("Job Title", placeholder="Senior Software Engineer")
                email = st.text_input("Email", placeholder="john@example.com")
                phone = st.text_input("Phone", placeholder="+1 (555) 123-4567")
                linkedin = st.text_input("LinkedIn", placeholder="linkedin.com/in/johndoe")
                location = st.text_input("Location", placeholder="San Francisco, CA")
                
                st.markdown('<h2 class="section-header">📄 Summary</h2>', unsafe_allow_html=True)
                summary = st.text_area("Professional Summary", height=100,
                                     placeholder="Dynamic software engineer with 5+ years experience...")
                
                # Quick sections
                st.markdown('<h2 class="section-header">🎓 Education</h2>', unsafe_allow_html=True)
                education = st.text_area("Education (one per line)", height=80,
                                       placeholder="B.S. Computer Science | Stanford University | 2020")
                
                st.markdown('<h2 class="section-header">💼 Experience</h2>', unsafe_allow_html=True)
                experience = st.text_area("Experience (one per line)", height=120,
                                        placeholder="Software Engineer | Google | 2021-Present | Led team...")
                
                st.markdown('<h2 class="section-header">🛠️ Skills</h2>', unsafe_allow_html=True)
                skills = st.text_area("Skills (one per line)", height=100,
                                    placeholder="Python\nJavaScript\nReact\nDocker\nAWS")
                
                st.markdown('<h2 class="section-header">📂 Projects</h2>', unsafe_allow_html=True)
                projects = st.text_area("Projects (one per line)", height=80,
                                      placeholder="AI Chatbot | Built with GPT-3 | 10k users")
                
                generate = st.form_submit_button("✨ Update Preview & Generate PDF", use_container_width=True)
        
        with col2:
            st.markdown('<div class="preview-container">', unsafe_allow_html=True)
            if name:
                # Prepare data for preview
                resume_data = {
                    "name": name,
                    "title": title,
                    "email": email,
                    "phone": phone,
                    "linkedin": linkedin,
                    "location": location,
                    "summary": [summary] if summary else [],
                    "education": [line.strip() for line in education.split('\n') if line.strip()],
                    "experience": [line.strip() for line in experience.split('\n') if line.strip()],
                    "skills": [line.strip() for line in skills.split('\n') if line.strip()],
                    "projects": [line.strip() for line in projects.split('\n') if line.strip()]
                }
                
                # Generate live preview
                with st.spinner("Rendering live preview..."):
                    preview_pdf = generate_preview(resume_data, theme, profile_image)
                
                # PDF Preview
                st.components.v1.html(
                    f"""
                    <iframe src="data:application/pdf;base64,{base64.b64encode(preview_pdf).decode()}" 
                            width="100%" height="100%" style="border: none; border-radius: 12px;"></iframe>
                    """,
                    height=600
                )
                
                # Download button
                st.download_button(
                    label="📥 Download PDF Resume",
                    data=preview_pdf,
                    file_name=f"{name.replace(' ', '_')}_{theme}_Resume.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.info("👆 Fill out the form on the left to see live preview")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        # ATS Analyzer
        st.markdown('<h2 class="section-header">🤖 ATS Score Analyzer</h2>', unsafe_allow_html=True)
        
        if name:
            ats_score, issues = calculate_ats_score(resume_data)
            
            # Score metric
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("ATS Score", f"{ats_score}/100", delta=None)
            
            # Score visualization
            st.progress(ats_score / 100)
            
            # Issues list
            if issues:
                st.markdown("**🔧 Issues to Fix:**")
                for issue in issues:
                    st.error(f"• {issue}")
            else:
                st.success("✅ Perfect! Your resume is ATS-ready!")
        
        st.markdown("---")
        st.markdown("""
        **ATS Best Practices:**
        - Use standard section headers
        - Include job-specific keywords  
        - Avoid tables/graphics in critical sections
        - Use standard fonts (Arial, Times)
        - Save as PDF or Word format
        """)

if __name__ == "__main__":
    main()