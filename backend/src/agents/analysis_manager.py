"""
Analysis Manager - Integrates the Main_1.py workflow into the Flask backend
"""
import os
import sys
import json
import asyncio
from datetime import datetime

from TavilyScp.tavily_web_s import run_scraper  # web course scraper
# OLD: from youtube_agent.main import mainYTagent
from youtube_agent.main import run_scraper as run_youtube_scraper  # async YouTube agent

from json_finder.jsonF import (
    process_json_file,
    update_skills_from_modules,
    find_json_files,
)


class AnalysisManager:
    def __init__(self):
        self.current_directory = os.getcwd()
        self.results_directory = os.path.join(self.current_directory, "results")
        os.makedirs(self.results_directory, exist_ok=True)

    def run_comprehensive_analysis(self, skills, progress_callback=None):
        """
        Run the comprehensive analysis workflow from Main_1.py

        Args:
            skills (list): List of skills to analyze (first item is used as the role)
            progress_callback (function): Callback to update progress/status

        Returns:
            dict: Analysis results
        """
        try:
            if progress_callback:
                progress_callback("running", 0, "Initializing analysis.")

            # ---------------------------
            # 1) Web scraper (Coursera/edX/Udemy)
            # ---------------------------
            test_websites = [
                "https://www.coursera.org",
                "https://www.edx.org",
                "https://www.udemy.com/",
            ]

            if progress_callback:
                progress_callback("running", 20, "Running web scraper.")

            run_scraper(skills, test_websites, search_all=True, rank_modules=True)

            # ---------------------------
            # 2) Update YouTube input skills from scraped modules
            # ---------------------------
            if progress_callback:
                progress_callback("running", 50, "Updating skills from modules.")

            update_skills_from_modules(self.current_directory)

            # ---------------------------
            # 3) Run YouTube agent with role override
            # ---------------------------
            if progress_callback:
                progress_callback("running", 80, "Running YouTube agent...")

            # Role override ensures filenames match user request (e.g., Teacher)
            user_role = (skills[0] if skills else "Data Analyst").title()

            # New async runner returns the exact JSON path it wrote
            yt_result_path = asyncio.run(run_youtube_scraper(role=user_role))

            # ---------------------------
            # 4) Locate the final result file
            # ---------------------------
            if progress_callback:
                progress_callback("running", 95, "Finding results...")

            result_file = None
            if yt_result_path and os.path.exists(yt_result_path):
                result_file = yt_result_path
            else:
                # Fallback: search by expected filename pattern
                # OLD code guessed using skills[0] which caused mismatches when
                # YouTube runner used a different role; now we search by user_role.
                result_file = find_json_files(
                    self.current_directory,
                    f"{user_role}_comprehensive_analysis.json",
                )

            if progress_callback:
                progress_callback("completed", 100, "Analysis completed!", result_file)

            # ---------------------------
            # 5) Load and return results
            # ---------------------------
            with open(result_file, "r", encoding="utf-8") as f:
                analysis_data = json.load(f)

            return {
                "status": "success",
                "data": analysis_data,
                "file_path": result_file,
            }

        except Exception as e:
            if progress_callback:
                progress_callback("error", 0, "", None, str(e))
            raise e

    def _generate_mock_analysis(self, skills):
        """Generate a comprehensive mock analysis result (unused)"""
        return {
            "analysis_metadata": {
                "analysis_date": datetime.now().isoformat(),
                "skills_analyzed": skills,
                "analysis_version": "1.0",
                "data_sources": ["Coursera", "edX", "Udemy", "YouTube"],
            },
            "course_recommendations": [
                {
                    "title": f"{skills[0]} Fundamentals",
                    "provider": "Coursera",
                    "rating": 4.8,
                    "duration": "6 weeks",
                    "level": "Beginner",
                    "price": "Free",
                    "url": "https://coursera.org/learn/data-analysis-fundamentals",
                    "skills_covered": [
                        "Python",
                        "Statistics",
                        "Data Visualization",
                    ],
                    "enrollment_count": 50000,
                },
                {
                    "title": f"{skills[0]} Bootcamp",
                    "provider": "Udemy",
                    "rating": 4.5,
                    "duration": "40 hours",
                    "level": "All Levels",
                    "price": "$89.99",
                    "url": "https://udemy.com/course/data-analyst-bootcamp",
                    "skills_covered": ["Excel", "Tableau", "Power BI"],
                    "enrollment_count": 75000,
                },
            ],
            "youtube_insights": {
                "top_channels": [
                    {
                        "channel_name": f"{skills[0]} Academy",
                        "subscriber_count": 500000,
                        "video_count": 150,
                        "avg_views_per_video": 45000,
                        "content_focus": [
                            "Tutorials",
                            "Case Studies",
                            "Industry Insights",
                        ],
                    },
                    {
                        "channel_name": "Data Science Central",
                        "subscriber_count": 300000,
                        "video_count": 200,
                        "avg_views_per_video": 30000,
                        "content_focus": [
                            "Tools",
                            "Techniques",
                            "Career Advice",
                        ],
                    },
                ],
                "trending_topics": [
                    "Python for Data Analysis",
                    "SQL Fundamentals",
                    "Data Visualization Best Practices",
                    "Machine Learning Basics",
                    "Career Transition Tips",
                ],
                "learning_paths": [
                    {
                        "path_name": "Beginner to Professional",
                        "estimated_duration": "6 months",
                        "video_count": 45,
                        "topics": ["Basics", "Tools", "Projects", "Portfolio"],
                    }
                ],
            },
            "job_market_analysis": {
                "demand_level": "High",
                "growth_rate": "22% (Much faster than average )",
                "salary_range": {
                    "entry_level": "$45,000 - $65,000",
                    "mid_level": "$65,000 - $95,000",
                    "senior_level": "$95,000 - $130,000",
                },
                "top_hiring_companies": [
                    "Google",
                    "Microsoft",
                    "Amazon",
                    "Meta",
                    "Apple",
                ],
                "required_skills": [
                    "Python",
                    "SQL",
                    "Excel",
                    "Statistics",
                    "Data Visualization",
                    "Machine Learning",
                    "Critical Thinking",
                    "Communication",
                ],
                "job_locations": [
                    {
                        "city": "San Francisco",
                        "avg_salary": "$120,000",
                        "job_count": 1500,
                    },
                    {
                        "city": "New York",
                        "avg_salary": "$110,000",
                        "job_count": 1200,
                    },
                    {
                        "city": "Seattle",
                        "avg_salary": "$105,000",
                        "job_count": 800,
                    },
                    {
                        "city": "Austin",
                        "avg_salary": "$95,000",
                        "job_count": 600,
                    },
                ],
            },
            "skill_development_roadmap": {
                "phase_1": {
                    "title": "Foundation Building (Months 1-2)",
                    "skills": ["Excel", "Basic Statistics", "SQL Basics"],
                    "resources": [
                        "Online courses",
                        "Practice datasets",
                        "Tutorials",
                    ],
                },
                "phase_2": {
                    "title": "Technical Skills (Months 3-4)",
                    "skills": ["Python", "Data Visualization", "Advanced SQL"],
                    "resources": ["Coding bootcamps", "Projects", "Certifications"],
                },
                "phase_3": {
                    "title": "Advanced Analytics (Months 5-6)",
                    "skills": [
                        "Machine Learning",
                        "Statistical Analysis",
                        "Business Intelligence",
                    ],
                    "resources": [
                        "Specialized courses",
                        "Real projects",
                        "Industry mentorship",
                    ],
                },
            },
            "recommendations": {
                "immediate_actions": [
                    "Start with Python fundamentals course",
                    "Practice SQL on real datasets",
                    "Build a portfolio on GitHub",
                ],
                "long_term_goals": [
                    "Complete a data analysis certification",
                    "Contribute to open-source projects",
                    "Network with industry professionals",
                ],
                "tools_to_learn": [
                    {"tool": "Python", "priority": "High", "time_investment": "3-4 weeks"},
                    {"tool": "SQL", "priority": "High", "time_investment": "2-3 weeks"},
                    {"tool": "Tableau", "priority": "Medium", "time_investment": "2 weeks"},
                    {"tool": "Excel", "priority": "Medium", "time_investment": "1 week"},
                ],
            },
        }
