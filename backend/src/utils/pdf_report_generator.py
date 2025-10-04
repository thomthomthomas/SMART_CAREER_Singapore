"""
PDF Report Generator for Smart Career SG Analysis Results
Converts JSON analysis data into professional PDF reports
"""

import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import logging

class PDFReportGenerator:
    """Generate professional PDF reports from analysis data."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for the PDF report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#2563eb'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#1e40af'),
            fontName='Helvetica-Bold'
        ))
        
        # Subheading style
        self.styles.add(ParagraphStyle(
            name='CustomSubheading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=HexColor('#374151'),
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=HexColor('#374151'),
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Summary box style
        self.styles.add(ParagraphStyle(
            name='SummaryBox',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            spaceBefore=12,
            textColor=HexColor('#1f2937'),
            alignment=TA_LEFT,
            fontName='Helvetica',
            backColor=HexColor('#f3f4f6'),
            borderColor=HexColor('#d1d5db'),
            borderWidth=1,
            borderPadding=10
        ))
    
    def generate_report(self, analysis_data: dict, output_path: str) -> str:
        """
        Generate a PDF report from analysis data.
        
        Args:
            analysis_data (dict): The analysis results data
            output_path (str): Path where the PDF should be saved
            
        Returns:
            str: Path to the generated PDF file
        """
        try:
            # Create the PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build the story (content)
            story = []
            
            # Add title page
            story.extend(self._create_title_page(analysis_data))
            
            # Add executive summary
            story.extend(self._create_executive_summary(analysis_data))
            
            # Add course recommendations
            if 'course_recommendations' in analysis_data:
                story.extend(self._create_course_recommendations(analysis_data['course_recommendations']))
            
            # Add job market analysis
            if 'job_market_analysis' in analysis_data:
                story.extend(self._create_job_market_analysis(analysis_data['job_market_analysis']))
            
            # Add skills breakdown
            if 'skills_breakdown' in analysis_data:
                story.extend(self._create_skills_breakdown(analysis_data['skills_breakdown']))
            
            # Add learning path
            if 'learning_path' in analysis_data:
                story.extend(self._create_learning_path(analysis_data['learning_path']))
            
            # Add important considerations
            if 'important_considerations' in analysis_data:
                story.extend(self._create_important_considerations(analysis_data['important_considerations']))
            
            # Build the PDF
            doc.build(story)
            
            self.logger.info(f"PDF report generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generating PDF report: {str(e)}")
            raise
    
    def _create_title_page(self, analysis_data: dict) -> list:
        """Create the title page content."""
        story = []
        
        # Main title
        story.append(Paragraph("Smart Career SG", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Subtitle
        story.append(Paragraph("Comprehensive Career Analysis Report", self.styles['Heading1']))
        story.append(Spacer(1, 20))
        
        # Analysis details
        analysis_info = [
            f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            f"<b>Analysis Type:</b> Career Path and Course Recommendations",
        ]
        
        # Add skills if available
        if 'skills_breakdown' in analysis_data and analysis_data['skills_breakdown']:
            skills = [skill.get('skill', 'Unknown') for skill in analysis_data['skills_breakdown'][:3]]
            analysis_info.append(f"<b>Focus Areas:</b> {', '.join(skills)}")
        
        for info in analysis_info:
            story.append(Paragraph(info, self.styles['CustomBody']))
            story.append(Spacer(1, 8))
        
        story.append(PageBreak())
        return story
    
    def _create_executive_summary(self, analysis_data: dict) -> list:
        """Create executive summary section."""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['CustomHeading']))
        
        # Generate summary based on available data
        summary_text = self._generate_summary_text(analysis_data)
        story.append(Paragraph(summary_text, self.styles['SummaryBox']))
        
        story.append(Spacer(1, 20))
        return story
    
    def _generate_summary_text(self, analysis_data: dict) -> str:
        """Generate executive summary text based on analysis data."""
        summary_parts = []
        
        # Course recommendations summary
        if 'course_recommendations' in analysis_data:
            courses = analysis_data['course_recommendations']
            if courses:
                summary_parts.append(f"We found {len(courses)} relevant courses to help advance your career.")
        
        # Job market summary
        if 'job_market_analysis' in analysis_data:
            job_market = analysis_data['job_market_analysis']
            if 'demand_level' in job_market:
                summary_parts.append(f"The job market shows {job_market['demand_level']} demand for your target skills.")
        
        # Skills summary
        if 'skills_breakdown' in analysis_data:
            skills = analysis_data['skills_breakdown']
            if skills:
                summary_parts.append(f"Your learning path focuses on {len(skills)} key skill areas.")
        
        # Learning path summary
        if 'learning_path' in analysis_data:
            path = analysis_data['learning_path']
            if path:
                summary_parts.append(f"We've outlined a {len(path)}-step learning path for your career development.")
        
        if not summary_parts:
            summary_parts.append("This comprehensive analysis provides personalized career insights and recommendations.")
        
        return " ".join(summary_parts)
    
    def _create_course_recommendations(self, courses: list) -> list:
        """Create course recommendations section."""
        story = []
        
        story.append(Paragraph("Course Recommendations", self.styles['CustomHeading']))
        story.append(Paragraph("Based on your career goals, we recommend the following courses:", self.styles['CustomBody']))
        story.append(Spacer(1, 12))
        
        # Create table data
        table_data = [['Course Title', 'Provider', 'Rating', 'Level']]
        
        for course in courses[:10]:  # Limit to top 10 courses
            title = course.get('title', 'N/A')[:50] + ('...' if len(course.get('title', '')) > 50 else '')
            provider = course.get('provider', 'N/A')
            rating = f"{course.get('rating', 'N/A')}⭐" if course.get('rating') else 'N/A'
            level = course.get('level', 'N/A')
            
            table_data.append([title, provider, rating, level])
        
        # Create and style the table
        table = Table(table_data, colWidths=[3*inch, 1.5*inch, 0.8*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#f8fafc')])
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        return story
    
    def _create_job_market_analysis(self, job_market: dict) -> list:
        """Create job market analysis section."""
        story = []
        
        story.append(Paragraph("Job Market Analysis", self.styles['CustomHeading']))
        
        # Demand level
        if 'demand_level' in job_market:
            story.append(Paragraph(f"<b>Market Demand:</b> {job_market['demand_level']}", self.styles['CustomBody']))
        
        # Growth rate
        if 'growth_rate' in job_market:
            story.append(Paragraph(f"<b>Growth Rate:</b> {job_market['growth_rate']}", self.styles['CustomBody']))
        
        # Salary information
        if 'salary_range' in job_market:
            salary = job_market['salary_range']
            if isinstance(salary, dict):
                entry_level = salary.get('entry_level', 'N/A')
                senior_level = salary.get('senior_level', 'N/A')
                story.append(Paragraph(f"<b>Salary Range:</b> {entry_level} - {senior_level}", self.styles['CustomBody']))
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_skills_breakdown(self, skills: list) -> list:
        """Create skills breakdown section."""
        story = []
        
        story.append(Paragraph("Skills Breakdown", self.styles['CustomHeading']))
        story.append(Paragraph("Key skills and competencies for your career path:", self.styles['CustomBody']))
        story.append(Spacer(1, 12))
        
        for skill in skills:
            skill_name = skill.get('skill', 'Unknown Skill')
            story.append(Paragraph(f"<b>{skill_name}</b>", self.styles['CustomSubheading']))
            
            # Add subskills if available
            if 'subskills' in skill and skill['subskills']:
                subskills_text = ", ".join(skill['subskills'][:8])  # Limit to 8 subskills
                story.append(Paragraph(f"Key areas: {subskills_text}", self.styles['CustomBody']))
            
            story.append(Spacer(1, 8))
        
        story.append(Spacer(1, 12))
        return story
    
    def _create_learning_path(self, learning_path: list) -> list:
        """Create learning path section."""
        story = []
        
        story.append(Paragraph("Recommended Learning Path", self.styles['CustomHeading']))
        story.append(Paragraph("Follow this step-by-step path to achieve your career goals:", self.styles['CustomBody']))
        story.append(Spacer(1, 12))
        
        for i, step in enumerate(learning_path, 1):
            story.append(Paragraph(f"<b>Step {i}:</b> {step}", self.styles['CustomBody']))
            story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_important_considerations(self, considerations: list) -> list:
        """Create important considerations section."""
        story = []
        
        story.append(Paragraph("Important Considerations", self.styles['CustomHeading']))
        story.append(Paragraph("Keep these key points in mind as you pursue your career goals:", self.styles['CustomBody']))
        story.append(Spacer(1, 12))
        
        for consideration in considerations:
            story.append(Paragraph(f"• {consideration}", self.styles['CustomBody']))
            story.append(Spacer(1, 4))
        
        story.append(Spacer(1, 20))
        return story


def generate_pdf_report(analysis_data: dict, output_dir: str = "reports") -> str:
    """
    Convenience function to generate a PDF report.
    
    Args:
        analysis_data (dict): Analysis results data
        output_dir (str): Directory to save the PDF
        
    Returns:
        str: Path to the generated PDF file
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"career_analysis_report_{timestamp}.pdf"
    output_path = os.path.join(output_dir, filename)
    
    # Generate the report
    generator = PDFReportGenerator()
    return generator.generate_report(analysis_data, output_path)


# Example usage
if __name__ == "__main__":
    # Sample data for testing
    sample_data = {
        "course_recommendations": [
            {
                "title": "Python for Data Science",
                "provider": "Coursera",
                "rating": 4.8,
                "level": "Beginner"
            },
            {
                "title": "Machine Learning Fundamentals",
                "provider": "edX",
                "rating": 4.6,
                "level": "Intermediate"
            }
        ],
        "job_market_analysis": {
            "demand_level": "High",
            "growth_rate": "15% annually",
            "salary_range": {
                "entry_level": "$60,000",
                "senior_level": "$120,000"
            }
        },
        "skills_breakdown": [
            {
                "skill": "Data Analysis",
                "subskills": ["Python", "SQL", "Excel", "Statistics"]
            },
            {
                "skill": "Machine Learning",
                "subskills": ["Scikit-learn", "TensorFlow", "Model Evaluation"]
            }
        ],
        "learning_path": [
            "Master Python programming fundamentals",
            "Learn data manipulation with Pandas",
            "Understand statistical concepts",
            "Practice with real datasets",
            "Build a portfolio of projects"
        ],
        "important_considerations": [
            "Focus on practical projects to build your portfolio",
            "Network with professionals in the data science community",
            "Stay updated with the latest tools and technologies"
        ]
    }
    
    # Generate test report
    pdf_path = generate_pdf_report(sample_data)
    print(f"Test PDF report generated: {pdf_path}")