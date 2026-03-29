import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
import base64
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
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1e1e2e !important;
        color: #ffffff !important;
        border: 2px solid #40414f !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-size: 14px;
    }
    
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
    
    .preview-container {
        background: white !important;
        border-radius: 16px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3) !important;
        overflow: hidden !important;
        height: 80vh !important;
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def generate_preview(data, theme, profile_image):
    return create_pdf_resume(data, theme, profile_image)

def calculate_ats_score(resume_data):
    score = 100
    issues = []
    
    if len(resume_data.get('skills', [])) < 5:
        score -= 15
        issues.append("Add 5+ relevant skills")
    
    if not resume_data.get('email') or not re.match(r"[^@]+@[^@]+\.[^@]+", resume_data['email']):
        score -= 20
        issues.append("Valid email required")
    
    if len(resume_data.get('experience', [])) == 0:
        score -= 25
        issues.append("Add work experience")
    
    if len(resume_data.get('education', [])) == 0:
        score -= 15
        issues.append("Add education")
    
    summary = resume_data.get('summary', [])
    if len(' '.join(summary).split()) < 20:
        score -= 10
        issues.append("Summary too short (aim for 3-5 sentences)")
    
    return max(0, score), issues

def create_pdf_resume(data, theme="blue", profile_image=None):
    """Fixed PDF generation function - handles all data formats safely"""
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
    
    color = theme_colors.get(theme, theme_colors["blue"])
    
    # Custom styles
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
    
    # Name and Title
    story.append(Paragraph(data.get('name', 'Your Name'), name_style))
    if data.get('title'):
        story.append(Paragraph(data['title'], title_style))
    
    # Contact Info
    contact_parts = []
    if data.get('email'): contact_parts.append(data['email'])
    if data.get('phone'): contact_parts.append(data['phone'])
    if data.get('linkedin'): contact_parts.append(data['linkedin'])
    if data.get('location'): contact_parts.append(data['location'])
    
    if contact_parts:
        contact_text = " | ".join(contact_parts)
        story.append(Paragraph(f"<font size=10>{contact_text}</font>", body_style))
        story.append(Spacer(1, 20))
    
    # Process sections
    sections = [
        ('summary', 'PROFESSIONAL SUMMARY'),
        ('education', 'EDUCATION'),
        ('experience', 'EXPERIENCE'),
        ('projects', 'PROJECTS')
    ]
    
    for key, title in sections:
        content = data.get(key, [])
        
        # Handle string input (split by lines)
        if isinstance(content, str):
            content = [line.strip() for line in content.split('\n') if line.strip()]
        
        if content:
            story.append(Paragraph(title, heading_style))
            for item in content:
                item_text = str(item) if item else ""
                if item_text:
                    story.append(Paragraph(item_text, body_style))
            story.append(Spacer(1, 12))
    
    # Skills section
    skills = data.get('skills', [])
    if isinstance(skills, str):
        skills = [skill.strip() for skill in skills.split('\n') if skill.strip()]
    
    if skills:
        story.append(Paragraph("SKILLS", heading_style))
        if skills:
            table_data = [['SKILL']] + [[skill] for skill in skills[:12]]
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
        story.append(Spacer(1, 12))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def main():
    st.markdown('<h1 class="main-header">🎯 AI Resume Builder Pro</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚙️ Settings")
    theme = st.sidebar.selectbox("Resume Theme", ["blue", "green", "purple", "orange"])
    
    profile_image = None
    uploaded_file = st.sidebar.file_uploader("📸 Profile Photo (optional)", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        profile_image = uploaded_file
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**💡 Pro Tips:**")
    st.sidebar.markdown("• Use action verbs (Led, Built, Improved)")
    st.sidebar.markdown("• Quantify results (Increased sales 30%)")
    st.sidebar.markdown("• Include job keywords")
    
    # Main tabs
    tab1, tab2 = st.tabs(["📝 Builder", "📊 ATS Analyzer"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
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
                                     placeholder="Dynamic software engineer with 5+ years experience in full-stack development. Specialized in React, Node.js, and cloud architecture. Proven track record of delivering scalable applications...")
                
                st.markdown('<h2 class="section-header">🎓 Education</h2>', unsafe_allow_html=True)
                education = st.text_area("Education (one per line)", height=80,
                                       placeholder="B.S. Computer Science | Stanford University | 2020\nHigh School Diploma | Local High School | 2016")
                
                st.markdown('<h2 class="section-header">💼 Experience</h2>', unsafe_allow_html=True)
                experience = st.text_area("Experience (one per line)", height=120,
                                        placeholder="Software Engineer | Google | 2021-Present | Led team of 5 developers\nJunior Developer | Startup Inc | 2019-2021 | Built core features")
                
                st.markdown('<h2 class="section-header">🛠️ Skills</h2>', unsafe_allow_html=True)
                skills_input = st.text_area("Skills (one per line)", height=100,
                                          placeholder="Python\nJavaScript\nReact\nNode.js\nDocker\nAWS\nPostgreSQL\nGit")
                skills = [skill.strip() for skill in skills_input.split('\n') if skill.strip()]
                
                st.markdown('<h2 class="section-header">📂 Projects</h2>', unsafe_allow_html=True)
                projects = st.text_area("Projects (one per line)", height=80,
                                      placeholder="AI Chatbot | Built with GPT-3 & React | 10k users\nE-commerce Platform | Full-stack app | Deployed on AWS")
                
                generate = st.form_submit_button("✨ Update Preview & Generate PDF", use_container_width=True)
        
        with col2:
            st.markdown('<div class="preview-container">', unsafe_allow_html=True)
            resume_data = None
            
            if name:
                # FIXED: Prepare data correctly
                resume_data = {
                    "name": name,
                    "title": title or "",
                    "email": email or "",
                    "phone": phone or "",
                    "linkedin": linkedin or "",
                    "location": location or "",
                    "summary": [summary.strip()] if summary and summary.strip() else [],
                    "education": [line.strip() for line in (education or "").split('\n') if line.strip()],
                    "experience": [line.strip() for line in (experience or "").split('\n') if line.strip()],
                    "skills": skills,
                    "projects": [line.strip() for line in (projects or "").split('\n') if line.strip()]
                }
                
                with st.spinner("Rendering live preview..."):
                    preview_pdf = generate_preview(resume_data, theme, profile_image)
                
                st.components.v1.html(
                    f"""
                    <iframe src="data:application/pdf;base64,{base64.b64encode(preview_pdf).decode()}" 
                            width="100%" height="100%" style="border: none; border-radius: 12px;"></iframe>
                    """,
                    height=700
                )
                
                st.download_button(
                    label="📥 Download PDF Resume",
                    data=preview_pdf,
                    file_name=f"{name.replace(' ', '_')}_{theme}_Resume.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.info("👆 **Fill out the form on the left** to see your live resume preview!")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<h2 class="section-header">🤖 ATS Score Analyzer</h2>', unsafe_allow_html=True)
        
        if resume_data:
            ats_score, issues = calculate_ats_score(resume_data)
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("ATS Score", f"{ats_score}/100")
            
            st.progress(ats_score / 100)
            
            if issues:
                st.markdown("**🔧 Issues to Fix:**")
                for issue in issues:
                    st.error(f"• {issue}")
            else:
                st.success("✅ **Perfect!** Your resume is ATS-optimized!")
        else:
            st.warning("👆 Build your resume first to analyze ATS score")
        
        st.markdown("---")
        st.markdown("""
        **🤖 ATS Best Practices:**
        - Use standard headers (EXPERIENCE, EDUCATION)
        - Include job description keywords
        - Avoid tables/images in main content
        - Use common fonts (Arial, Helvetica)
        - Spell out acronyms first
        """)

if __name__ == "__main__":
    main()