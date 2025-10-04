import os
import sys
import json
import glob
import logging
from io import BytesIO
from pathlib import Path

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, send_file, Blueprint, request
from flask_cors import CORS

# ---------- Existing app imports & setup (retained) ----------
from src.models.user import db
from src.routes.user import user_bp
from src.routes.chat import chat_bp
from src.routes.general_chat import general_chat_bp
from src.routes.course_creation import course_creation_bp

def load_config(config_file: str = "config.json") -> dict:
    """Load configuration from JSON file with validation (search anywhere)."""
    config_files = glob.glob(f"**/{config_file}", recursive=True)

    if config_files:
        # Pick the first match (or customize selection if needed)
        config_path = Path(config_files[0])
        print(f"Found config file at: {config_path}")
    else:
        print("Error: config.json not found anywhere in the project.")
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading config.json: {e}")
        sys.exit(1)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Optionally load and apply config values (if your config.json has a 'flask' section)
_config = load_config()
_flask_cfg = _config.get("flask", {})
app.config['SECRET_KEY'] = _flask_cfg.get('secret_key', app.config['SECRET_KEY'])
if 'SQLALCHEMY_DATABASE_URI' in _flask_cfg:
    app.config['SQLALCHEMY_DATABASE_URI'] = _flask_cfg['SQLALCHEMY_DATABASE_URI']

# Enable CORS for all routes (dev-friendly; scope as needed for prod)
CORS(app)

# Register existing blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api')
app.register_blueprint(general_chat_bp, url_prefix='/api')
app.register_blueprint(course_creation_bp, url_prefix='/api')

# Database defaults (SQLite fallback) and initialization
if 'SQLALCHEMY_DATABASE_URI' not in app.config:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

# ---------- Roles API (integrated from second main) ----------
# Try to import external roles data/generator (kept identical to your original)
import sys as _sys
_sys.path.append('/home/ubuntu/upload')

try:
    from pasted_file_nJPK7X_roles import ROLES_DATA, generate_pdf_for_role  # type: ignore
except Exception:
    # Fallback seed data if import fails (identical structure)
    ROLES_DATA = {
        "software-developer": {
            "role": "Software Developer",
            "summary": "Software developers design, build, and maintain applications and systems that power our digital world. They work across various platforms, from web and mobile applications to enterprise software and embedded systems. In Singapore's thriving tech ecosystem, developers collaborate with cross-functional teams to solve complex problems, implement new features, and ensure software quality. The role demands both technical expertise and creative problem-solving skills, as developers must translate business requirements into functional, scalable, and user-friendly solutions.",
            "facts": [
                "Singapore has over 200,000 tech professionals with software development being the most in-demand skill",
                "Average salary ranges from S$60,000 to S$150,000+ annually depending on experience and specialization",
                "Remote and hybrid work options are increasingly common, with 70% of companies offering flexible arrangements",
                "The demand for full-stack developers has grown by 35% year-over-year in Singapore's job market"
            ],
            "skills": [
                "JavaScript", "Python", "React", "Node.js", "SQL", "Git", "AWS", "Docker",
                "TypeScript", "API Development", "Testing", "Agile", "Problem Solving", "Debugging", "System Design"
            ],
            "imageQuery": "software developer coding programming"
        },
        "data-scientist": {
            "role": "Data Scientist",
            "summary": "Data scientists extract meaningful insights from complex datasets to drive business decisions and innovation. They combine statistical analysis, machine learning, and domain expertise to solve real-world problems across industries. In Singapore's data-driven economy, data scientists work with stakeholders to identify opportunities, build predictive models, and communicate findings through compelling visualizations. The role requires both technical proficiency in programming and analytics tools, as well as strong business acumen to translate data insights into actionable strategies.",
            "facts": [
                "Data science roles in Singapore have grown by 50% in the past two years across finance, healthcare, and e-commerce",
                "Average salary ranges from S$80,000 to S$180,000+ with senior roles commanding premium compensation",
                "Python and R are the most sought-after programming languages, with SQL being essential for data manipulation",
                "Machine learning and AI specializations can increase earning potential by 25-40% above base data science roles"
            ],
            "skills": [
                "Python", "R", "SQL", "Machine Learning", "Statistics", "Pandas", "Scikit-learn", "TensorFlow",
                "Data Visualization", "Jupyter", "A/B Testing", "Big Data", "Cloud Platforms", "Business Intelligence", "Communication"
            ],
            "imageQuery": "data science analytics machine learning"
        },
        "digital-marketing-specialist": {
            "role": "Digital Marketing Specialist",
            "summary": "Digital marketing specialists develop and execute comprehensive online marketing strategies to build brand awareness, engage customers, and drive business growth. They leverage various digital channels including social media, search engines, email, and content marketing to reach target audiences effectively. In Singapore's competitive digital landscape, specialists analyze market trends, create compelling campaigns, and optimize performance using data-driven insights. The role combines creativity with analytical thinking, requiring both strategic planning skills and hands-on execution capabilities.",
            "facts": [
                "Digital marketing spending in Singapore is projected to reach S$1.2 billion by 2025, driving job demand",
                "Average salary ranges from S$45,000 to S$120,000+ with specialization in areas like SEO, PPC, or social media",
                "E-commerce growth has increased demand for digital marketing specialists by 40% in the past year",
                "Multi-channel campaign management and marketing automation skills are highly valued by employers"
            ],
            "skills": [
                "SEO", "Google Ads", "Social Media Marketing", "Content Marketing", "Email Marketing", "Analytics", "PPC",
                "Marketing Automation", "A/B Testing", "Copywriting", "Brand Management", "Campaign Management", "CRM", "Conversion Optimization", "Data Analysis"
            ],
            "imageQuery": "digital marketing social media advertising"
        },
        "ux-ui-designer": {
            "role": "UX/UI Designer",
            "summary": "UX/UI designers create intuitive and engaging digital experiences by combining user research, interaction design, and visual aesthetics. They work closely with product teams to understand user needs, design wireframes and prototypes, and ensure seamless user journeys across web and mobile applications. In Singapore's design-conscious tech industry, designers conduct usability testing, iterate based on feedback, and collaborate with developers to bring designs to life. The role requires both creative vision and analytical thinking to balance user needs with business objectives.",
            "facts": [
                "Singapore's design industry has grown by 25% annually, with UX/UI roles being the fastest-growing segment",
                "Average salary ranges from S$55,000 to S$130,000+ with senior designers and design leads earning premium rates",
                "Mobile-first design and accessibility expertise are increasingly important as companies prioritize inclusive design",
                "Design systems and component libraries knowledge can increase earning potential by 20-30% above base UX/UI roles"
            ],
            "skills": [
                "Figma", "Sketch", "Adobe Creative Suite", "Prototyping", "User Research", "Wireframing", "Usability Testing",
                "Design Systems", "Interaction Design", "Visual Design", "Information Architecture", "Responsive Design", "Accessibility", "HTML/CSS", "Collaboration"
            ],
            "imageQuery": "ux ui design wireframe user experience"
        },
        "cybersecurity-analyst": {
            "role": "Cybersecurity Analyst",
            "summary": "Cybersecurity analysts protect organizations from digital threats by monitoring networks, investigating security incidents, and implementing protective measures. They analyze security logs, identify vulnerabilities, and respond to cyber attacks while ensuring compliance with security policies and regulations. In Singapore's digitally connected economy, analysts work with cutting-edge security tools, conduct risk assessments, and develop incident response procedures. The role demands both technical expertise in security technologies and strong analytical skills to stay ahead of evolving cyber threats.",
            "facts": [
                "Cybersecurity job demand in Singapore has increased by 60% as organizations prioritize digital security",
                "Average salary ranges from S$70,000 to S$160,000+ with specialized roles in threat hunting and forensics commanding higher pay",
                "Security certifications like CISSP, CEH, and CISM can increase earning potential by 25-35% above base analyst roles",
                "Cloud security and AI-powered threat detection skills are becoming essential as organizations migrate to hybrid environments"
            ],
            "skills": [
                "Network Security", "Incident Response", "SIEM Tools", "Penetration Testing", "Risk Assessment", "Compliance", "Forensics",
                "Threat Intelligence", "Vulnerability Assessment", "Security Monitoring", "Firewall Management", "Encryption", "Cloud Security", "Scripting", "Communication"
            ],
            "imageQuery": "cybersecurity security analyst monitoring"
        },
        "project-manager": {
            "role": "Project Manager",
            "summary": "Project managers orchestrate complex initiatives from conception to completion, ensuring projects are delivered on time, within budget, and meet quality standards. They coordinate cross-functional teams, manage stakeholder expectations, and navigate challenges while maintaining project momentum. In Singapore's fast-paced business environment, managers utilize various methodologies including Agile, Scrum, and traditional waterfall approaches to drive successful outcomes. The role requires strong leadership, communication, and organizational skills to balance competing priorities and deliver value to organizations.",
            "facts": [
                "Project management roles in Singapore span across industries with technology and construction showing highest demand",
                "Average salary ranges from S$65,000 to S$140,000+ with PMP certification adding 15-20% premium to compensation",
                "Agile and Scrum methodologies are used by 75% of Singapore companies, making these skills highly valuable",
                "Digital transformation projects have increased demand for technical project managers by 30% year-over-year"
            ],
            "skills": [
                "Project Planning", "Agile/Scrum", "Risk Management", "Stakeholder Management", "Budget Management", "Team Leadership", "Communication",
                "Problem Solving", "Quality Assurance", "Resource Allocation", "Timeline Management", "Reporting", "Change Management", "Negotiation", "Strategic Thinking"
            ],
            "imageQuery": "project manager team leadership meeting"
        }
    }

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/roles', methods=['GET'])
def get_all_roles():
    """Get all available roles"""
    roles_list = []
    for slug, data in ROLES_DATA.items():
        roles_list.append({
            'slug': slug,
            'role': data['role'],
            'summary': data['summary'][:100] + '...' if len(data['summary']) > 100 else data['summary']
        })
    return jsonify(roles_list)

@roles_bp.route('/roles/<slug>', methods=['GET'])
def get_role_data(slug):
    """Get detailed data for a specific role"""
    if slug not in ROLES_DATA:
        return jsonify({'error': 'Role not found'}), 404

    role_data = ROLES_DATA[slug].copy()
    role_data['pdfUrl'] = f'/api/roles/{slug}/pdf'
    return jsonify(role_data)

@roles_bp.route('/roles/<slug>/pdf', methods=['GET'])
def download_role_pdf(slug):
    """Generate and download PDF for a specific role"""
    if slug not in ROLES_DATA:
        return jsonify({'error': 'Role not found'}), 404

    try:
        # Prefer external generator if available
        if 'generate_pdf_for_role' in globals():
            pdf_content = generate_pdf_for_role(slug)  # type: ignore
            if pdf_content:
                return send_file(
                    BytesIO(pdf_content),
                    as_attachment=True,
                    download_name=f'{slug}-career-guide.pdf',
                    mimetype='application/pdf'
                )

        # Fallback: generate a simple PDF with reportlab
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        role_data = ROLES_DATA[slug]
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
        )
        story.append(Paragraph(role_data['role'], title_style))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Role Overview", styles['Heading2']))
        story.append(Paragraph(role_data['summary'], styles['Normal']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Key Facts", styles['Heading2']))
        for fact in role_data['facts']:
            story.append(Paragraph(f"• {fact}", styles['Normal']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Required Skills", styles['Heading2']))
        skills_text = ", ".join(role_data['skills'])
        story.append(Paragraph(skills_text, styles['Normal']))

        doc.build(story)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'{slug}-career-guide.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return jsonify({'error': 'Failed to generate PDF'}), 500

@roles_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Smart Career SG Backend API'})

# Register roles blueprint under /api
app.register_blueprint(roles_bp, url_prefix='/api')

# ---------- Static file serving (retained) ----------
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    target = os.path.join(static_folder_path, path)
    if path != "" and os.path.exists(target):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# ---------- Entrypoint ----------
if __name__ == '__main__':
    # Disable Werkzeug's default logger to prevent conflicts with custom logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    app.run(host='0.0.0.0', port=5000, debug=True)
