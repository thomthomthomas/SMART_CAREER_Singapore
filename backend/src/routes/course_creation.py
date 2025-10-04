"""
Course Creation API Routes
Handles the course creation workflow including skills tree generation and PDF creation.
"""

import os
import json
import logging
from io import BytesIO
from typing import Dict, List, Any
from flask import Blueprint, request, jsonify, send_file
import google.generativeai as genai
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor

# Initialize Gemini client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
_GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
_model = genai.GenerativeModel(model_name=_GEMINI_MODEL_NAME)

course_creation_bp = Blueprint('course_creation', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@course_creation_bp.route('/generate-skills-tree', methods=['POST'])
def generate_skills_tree():
    """
    Generate an interactive skills tree based on user input.
    
    Expected JSON payload:
    {
        "topic": "Data Science",
        "description": "Optional additional context"
    }
    
    Returns:
    {
        "success": true,
        "skills_tree": {
            "topic": "Data Science",
            "skills": [
                {
                    "id": "python_programming",
                    "name": "Python Programming",
                    "category": "Fundamentals",
                    "difficulty": "Beginner",
                    "description": "Learn Python syntax and basic programming concepts"
                },
                ...
            ]
        }
    }
    """
    try:
        data = request.get_json()
        if not data or 'topic' not in data:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400
        
        topic = data['topic'].strip()
        description = data.get('description', '')
        
        if not topic:
            return jsonify({'success': False, 'error': 'Topic cannot be empty'}), 400
        
        # Generate skills tree using Gemini API
        skills_tree = _generate_skills_with_openai(topic, description)
        
        return jsonify({
            'success': True,
            'skills_tree': skills_tree
        })
        
    except Exception as e:
        logger.error(f"Error generating skills tree: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to generate skills tree'}), 500

@course_creation_bp.route('/create-course', methods=['POST'])
def create_course():
    """
    Create a comprehensive learning course based on selected skills.
    
    Expected JSON payload:
    {
        "topic": "Data Science",
        "selected_skills": [
            {
                "id": "python_programming",
                "name": "Python Programming",
                "category": "Fundamentals"
            },
            {
                "id": "machine_learning",
                "name": "Machine Learning",
                "category": "Advanced"
            }
        ]
    }
    
    Returns PDF file download
    """
    try:
        data = request.get_json()
        if not data or 'topic' not in data or 'selected_skills' not in data:
            return jsonify({'success': False, 'error': 'Topic and selected_skills are required'}), 400
        
        topic = data['topic'].strip()
        selected_skills = data['selected_skills']
        
        if not topic or not selected_skills:
            return jsonify({'success': False, 'error': 'Topic and at least one skill must be provided'}), 400
        
        if len(selected_skills) > 10:
            return jsonify({'success': False, 'error': 'Maximum 10 skills can be selected'}), 400
        
        # Generate comprehensive course content
        pdf_content = _generate_course_pdf(topic, selected_skills)
        
        return send_file(
            BytesIO(pdf_content),
            as_attachment=True,
            download_name=f'{topic.lower().replace(" ", "_")}_learning_course.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error creating course: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to create course'}), 500

@course_creation_bp.route('/course-summary', methods=['POST'])
def get_course_summary():
    """
    Generate a summary of selected skills while the PDF is being created.
    
    Expected JSON payload:
    {
        "topic": "Data Science",
        "selected_skills": [...]
    }
    
    Returns:
    {
        "success": true,
        "summary": "Your personalized Data Science course covers...",
        "skill_count": 5,
        "estimated_duration": "8-12 weeks"
    }
    """
    try:
        data = request.get_json()
        if not data or 'topic' not in data or 'selected_skills' not in data:
            return jsonify({'success': False, 'error': 'Topic and selected_skills are required'}), 400
        
        topic = data['topic'].strip()
        selected_skills = data['selected_skills']
        
        if not topic or not selected_skills:
            return jsonify({'success': False, 'error': 'Topic and at least one skill must be provided'}), 400
        
        # Generate summary using Gemini API
        summary = _generate_course_summary(topic, selected_skills)
        
        return jsonify({
            'success': True,
            'summary': summary,
            'skill_count': len(selected_skills),
            'estimated_duration': _estimate_course_duration(len(selected_skills))
        })
        
    except Exception as e:
        logger.error(f"Error generating course summary: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to generate course summary'}), 500

def _generate_skills_with_openai(topic: str, description: str = "") -> Dict[str, Any]:
    """Generate skills tree using Gemini API."""
    try:
        prompt = f"""
        Generate a comprehensive skills tree for learning "{topic}".
        {f"Additional context: {description}" if description else ""}

        Create exactly 15 skills organized into different categories (Fundamentals, Intermediate, Advanced, Practical Application, Expert Level).
        Each skill should have:
        - id: snake_case identifier
        - name: Human-readable name
        - category: One of the categories mentioned above
        - difficulty: Beginner, Intermediate, or Advanced
        - description: Brief description of what this skill covers

        Return the response as a valid JSON object with this structure:
        {{
            "topic": "{topic}",
            "skills": [
                {{
                    "id": "skill_id",
                    "name": "Skill Name",
                    "category": "Fundamentals",
                    "difficulty": "Beginner",
                    "description": "Description of the skill"
                }}
            ]
        }}

        Make sure the skills are relevant, practical, and cover the full learning journey from beginner to expert level.
        Only output JSON. No extra commentary.
        """

        response = _model.generate_content(
            prompt,
            generation_config={"temperature": 0.7}
        )

        response_text = (response.text or "").strip()

        # Parse the JSON response
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
        
        skills_data = json.loads(response_text)
        
        # Validate the response structure
        if 'skills' not in skills_data or not isinstance(skills_data['skills'], list):
            raise ValueError("Invalid response structure from Gemini API")
        
        # Ensure we have exactly 15 skills
        if len(skills_data['skills']) != 15:
            skills_data['skills'] = skills_data['skills'][:15]  # Truncate if more than 15
        
        return skills_data
        
    except Exception as e:
        logger.error(f"Error with Gemini API: {str(e)}")
        # Fallback to predefined skills if Gemini fails
        return _get_fallback_skills(topic)

def _get_fallback_skills(topic: str) -> Dict[str, Any]:
    """Fallback skills tree if Gemini API fails."""
    fallback_skills = {
        "topic": topic,
        "skills": [
            {"id": "fundamentals_1", "name": "Basic Concepts", "category": "Fundamentals", "difficulty": "Beginner", "description": f"Introduction to {topic} fundamentals"},
            {"id": "fundamentals_2", "name": "Core Principles", "category": "Fundamentals", "difficulty": "Beginner", "description": f"Core principles of {topic}"},
            {"id": "fundamentals_3", "name": "Essential Tools", "category": "Fundamentals", "difficulty": "Beginner", "description": f"Essential tools for {topic}"},
            {"id": "intermediate_1", "name": "Practical Applications", "category": "Intermediate", "difficulty": "Intermediate", "description": f"Practical applications in {topic}"},
            {"id": "intermediate_2", "name": "Problem Solving", "category": "Intermediate", "difficulty": "Intermediate", "description": f"Problem solving techniques in {topic}"},
            {"id": "intermediate_3", "name": "Best Practices", "category": "Intermediate", "difficulty": "Intermediate", "description": f"Best practices for {topic}"},
            {"id": "intermediate_4", "name": "Advanced Concepts", "category": "Intermediate", "difficulty": "Intermediate", "description": f"Advanced concepts in {topic}"},
            {"id": "advanced_1", "name": "Specialized Techniques", "category": "Advanced", "difficulty": "Advanced", "description": f"Specialized techniques in {topic}"},
            {"id": "advanced_2", "name": "Optimization", "category": "Advanced", "difficulty": "Advanced", "description": f"Optimization strategies for {topic}"},
            {"id": "advanced_3", "name": "Integration", "category": "Advanced", "difficulty": "Advanced", "description": f"Integration with other systems in {topic}"},
            {"id": "practical_1", "name": "Real-world Projects", "category": "Practical Application", "difficulty": "Advanced", "description": f"Real-world projects in {topic}"},
            {"id": "practical_2", "name": "Case Studies", "category": "Practical Application", "difficulty": "Advanced", "description": f"Case studies in {topic}"},
            {"id": "expert_1", "name": "Research & Innovation", "category": "Expert Level", "difficulty": "Advanced", "description": f"Research and innovation in {topic}"},
            {"id": "expert_2", "name": "Leadership", "category": "Expert Level", "difficulty": "Advanced", "description": f"Leadership in {topic} projects"},
            {"id": "expert_3", "name": "Mentoring", "category": "Expert Level", "difficulty": "Advanced", "description": f"Mentoring others in {topic}"}
        ]
    }
    return fallback_skills

def _generate_course_summary(topic: str, selected_skills: List[Dict[str, Any]]) -> str:
    """Generate a course summary using Gemini API."""
    try:
        skill_names = [skill['name'] for skill in selected_skills]
        skills_text = ", ".join(skill_names)
        
        prompt = f"""
        Create a compelling and informative summary for a personalized learning course in "{topic}".
        
        The course will cover these selected skills: {skills_text}
        
        Write a 2-3 paragraph summary that:
        1. Explains what the learner will achieve by completing this course
        2. Highlights the practical value and real-world applications
        3. Mentions the progression from basic to advanced concepts
        4. Sounds engaging and motivational
        
        Keep it concise but inspiring, around 150-200 words.
        """
        
        response = _model.generate_content(
            prompt,
            generation_config={"temperature": 0.7}
        )
        
        return (response.text or "").strip()
        
    except Exception as e:
        logger.error(f"Error generating course summary: {str(e)}")
        return f"Your personalized {topic} course covers {len(selected_skills)} essential skills that will take you from beginner to advanced level. This comprehensive learning path is designed to provide practical, hands-on experience while building a strong theoretical foundation."

def _estimate_course_duration(skill_count: int) -> str:
    """Estimate course duration based on number of skills."""
    if skill_count <= 3:
        return "4-6 weeks"
    elif skill_count <= 6:
        return "8-12 weeks"
    elif skill_count <= 9:
        return "12-16 weeks"
    else:
        return "16-20 weeks"

def _generate_course_pdf(topic: str, selected_skills: List[Dict[str, Any]]) -> bytes:
    """Generate comprehensive course PDF focusing on top 2 skills."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=30,
        textColor=HexColor('#2E3440'),
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=20,
        textColor=HexColor('#5E81AC'),
        spaceBefore=20
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=15,
        textColor=HexColor('#81A1C1'),
        spaceBefore=15
    )
    
    story = []
    
    # Title page
    story.append(Paragraph(f"Comprehensive Learning Course", title_style))
    story.append(Paragraph(f"{topic}", title_style))
    story.append(Spacer(1, 50))
    
    # Course overview
    story.append(Paragraph("Course Overview", heading_style))
    overview_text = f"""
    This comprehensive course covers {len(selected_skills)} essential skills in {topic}. 
    The course is designed to take you from beginner to advanced level through practical, 
    hands-on learning experiences. Each module includes theoretical foundations, practical 
    exercises, and real-world applications.
    """
    story.append(Paragraph(overview_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Skills overview
    story.append(Paragraph("Skills Covered", heading_style))
    for i, skill in enumerate(selected_skills, 1):
        skill_text = f"{i}. <b>{skill['name']}</b> ({skill['category']}) - {skill.get('description', 'Essential skill for mastering ' + topic)}"
        story.append(Paragraph(skill_text, styles['Normal']))
    story.append(PageBreak())
    
    # Detailed modules for top 2 skills
    top_skills = selected_skills[:2]  # Focus on top 2 skills as requested
    
    for skill_index, skill in enumerate(top_skills, 1):
        story.append(Paragraph(f"Module {skill_index}: {skill['name']}", title_style))
        story.append(Spacer(1, 20))
        
        # Generate detailed content for this skill
        detailed_content = _generate_skill_content(skill['name'], topic)
        
        for section in detailed_content:
            story.append(Paragraph(section['title'], heading_style))
            story.append(Paragraph(section['content'], styles['Normal']))
            story.append(Spacer(1, 15))
            
            # Add practice exercises if available
            if 'exercises' in section:
                story.append(Paragraph("Practice Exercises", subheading_style))
                for exercise in section['exercises']:
                    story.append(Paragraph(f"• {exercise}", styles['Normal']))
                story.append(Spacer(1, 15))
        
        if skill_index < len(top_skills):
            story.append(PageBreak())
    
    # Learning pathway
    story.append(PageBreak())
    story.append(Paragraph("Recommended Learning Pathway", title_style))
    story.append(Spacer(1, 20))
    
    pathway_content = _generate_learning_pathway(topic, selected_skills)
    for step in pathway_content:
        story.append(Paragraph(step['title'], heading_style))
        story.append(Paragraph(step['description'], styles['Normal']))
        story.append(Spacer(1, 15))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def _generate_skill_content(skill_name: str, topic: str) -> List[Dict[str, Any]]:
    """Generate detailed content for a specific skill using Gemini."""
    try:
        prompt = f"""
        Create detailed learning content for the skill "{skill_name}" in the context of "{topic}".
        
        Structure the content as follows:
        1. Introduction - What is this skill and why is it important
        2. Fundamentals - Basic concepts and terminology
        3. Getting Started - Step-by-step beginner guide with examples
        4. Intermediate Concepts - More advanced topics
        5. Practical Applications - Real-world use cases and examples
        6. Best Practices - Tips and recommendations
        
        For each section, include:
        - Clear explanations
        - Practical examples (like "Hello World" for programming)
        - 2-3 practice exercises or questions
        
        Format as JSON with this structure:
        [
            {{
                "title": "Section Title",
                "content": "Detailed content...",
                "exercises": ["Exercise 1", "Exercise 2", "Exercise 3"]
            }}
        ]

        Only output JSON. No extra commentary.
        """
        
        response = _model.generate_content(
            prompt,
            generation_config={"temperature": 0.7}
        )
        
        response_text = (response.text or "").strip()
        
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
        
        content_data = json.loads(response_text)
        return content_data
        
    except Exception as e:
        logger.error(f"Error generating skill content: {str(e)}")
        # Fallback content
        return [
            {
                "title": "Introduction",
                "content": f"{skill_name} is a fundamental skill in {topic}. This module will guide you through the essential concepts and practical applications.",
                "exercises": [
                    "Research the basic concepts",
                    "Practice with simple examples",
                    "Apply to a small project"
                ]
            },
            {
                "title": "Getting Started",
                "content": f"Let's begin with the basics of {skill_name}. We'll start with simple examples and gradually build complexity.",
                "exercises": [
                    "Complete the introductory tutorial",
                    "Practice basic operations",
                    "Create your first simple project"
                ]
            },
            {
                "title": "Practical Applications",
                "content": f"Now that you understand the basics, let's explore how {skill_name} is used in real-world {topic} scenarios.",
                "exercises": [
                    "Analyze a real-world case study",
                    "Implement a practical solution",
                    "Optimize your approach"
                ]
            }
        ]

def _generate_learning_pathway(topic: str, selected_skills: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Generate a recommended learning pathway using Gemini."""
    try:
        skill_names = [skill['name'] for skill in selected_skills]
        skills_text = ", ".join(skill_names)
        
        prompt = f"""
        Create a recommended learning pathway for mastering "{topic}" with these skills: {skills_text}
        
        Provide 5-7 steps that outline the optimal learning sequence, including:
        - Which skills to learn first (prerequisites)
        - How to progress from beginner to advanced
        - When to apply practical projects
        - Milestones and checkpoints
        
        Format as JSON:
        [
            {{
                "title": "Step 1: Foundation Building",
                "description": "Start with fundamental concepts..."
            }}
        ]

        Only output JSON. No extra commentary.
        """
        
        response = _model.generate_content(
            prompt,
            generation_config={"temperature": 0.7}
        )
        
        response_text = (response.text or "").strip()
        
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
        
        pathway_data = json.loads(response_text)
        return pathway_data
        
    except Exception as e:
        logger.error(f"Error generating learning pathway: {str(e)}")
        # Fallback pathway
        return [
            {
                "title": "Step 1: Foundation Building",
                "description": f"Start with the fundamental concepts of {topic}. Focus on understanding core principles and terminology."
            },
            {
                "title": "Step 2: Practical Application",
                "description": "Apply your knowledge through hands-on exercises and small projects."
            },
            {
                "title": "Step 3: Skill Integration",
                "description": "Learn how different skills work together in real-world scenarios."
            },
            {
                "title": "Step 4: Advanced Techniques",
                "description": "Explore advanced concepts and specialized techniques."
            },
            {
                "title": "Step 5: Portfolio Development",
                "description": "Create comprehensive projects that demonstrate your mastery."
            }
        ]
