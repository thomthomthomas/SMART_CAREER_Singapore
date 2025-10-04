"""
Fixed Main runner script for YouTube Skills Scraper
Includes better error handling and API validation with working PDF generation
"""
import asyncio
import json
import logging
import sys
import os
import glob
from pathlib import Path
from dataclasses import asdict
from .youtube import YouTubeSkillsScraper

# Configure logging with both file and console output
def setup_logging():
    """Setup logging configuration"""
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("logs/scraper.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Suppress noisy libraries
    logging.getLogger("pytube").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def load_config(config_file: str = "config.json") -> dict:
    """
    Load configuration with sane priority so it works when launched from the backend root:
      1) APP_CONFIG env var (absolute path)
      2) <this folder>/config.json  (src/youtube_agent/config.json)
      3) nearest config.json found by glob from project root
    """
    env_path = os.getenv("APP_CONFIG")
    if env_path and Path(env_path).is_file():
        path = Path(env_path)
    else:
        here = Path(__file__).resolve().parent / config_file
        if here.is_file():
            path = here
        else:
            project_root = Path(__file__).resolve().parents[2]
            matches = [
                Path(p).resolve()
                for p in glob.glob(str(project_root / "**" / config_file), recursive=True)
            ]
            if not matches:
                logger.error(f"Config file {config_file} not found anywhere.")
                logger.info("Set APP_CONFIG or place config.json in src/youtube_agent/")
                sys.exit(1)
            # prefer the one closest to project_root (stable order)
            matches.sort(key=lambda p: len(p.relative_to(project_root).parts))
            path = matches[0]

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
        sys.exit(1)

def validate_api_keys(config: dict) -> bool:
    """Validate that API keys are properly configured"""
    try:
        api_keys = config["api_keys"]
        gemini_key = api_keys.get("gemini_api_key", "")
        youtube_key = api_keys.get("youtube_api_key", "")
        supadata_key = api_keys.get("supadata_api_key", "")

        placeholder_values = [
            "YOUR_GEMINI_API_KEY_HERE",
            "YOUR_YOUTUBE_DATA_API_V3_KEY_HERE",
            "your-gemini-api-key-here",
            "your-youtube-api-key-here",
            "your_supadata_api_key_here",
            "",
        ]

        if gemini_key in placeholder_values:
            logger.error("Gemini API key not configured!")
            logger.info("Get your key from: https://aistudio.google.com/app/apikey")
            return False

        if youtube_key in placeholder_values:
            logger.error("YouTube API key not configured!")
            logger.info("Get your key from: https://console.cloud.google.com/")
            return False

        if supadata_key in placeholder_values:
            logger.error("Supadata API key not configured!")
            logger.info("Get your key from: https://dash.supadata.ai/organizations/api-key")
            return False

        if not gemini_key.startswith("AIzaSy") or len(gemini_key) < 35:
            logger.error("Gemini API key format appears invalid")
            return False

        if not youtube_key.startswith("AIzaSy") or len(youtube_key) < 35:
            logger.error("YouTube API key format appears invalid")
            return False

        if not supadata_key or len(supadata_key) < 10:
            logger.error("Supadata API key format appears invalid")
            return False

        logger.info("API keys configured and format validated")
        return True

    except KeyError as e:
        logger.error(f"Missing API key configuration: {e}")
        return False

def load_input_data(input_file: str = "input_skills.json") -> tuple[str, list]:
    """
    Load role and skills from the skills file located **next to this module**:
    backend/src/youtube_agent/input_skills.json

    If the file is missing or invalid, fall back to a small example.
    """
    skills_path = Path(__file__).resolve().parent / input_file

    if not skills_path.exists():
        logger.warning(f"Input file not found at {skills_path}, using example data")
        return "Data Scientist", [
            "Python Programming",
            "Machine Learning",
            "Data Visualization",
        ]

    try:
        data = json.loads(skills_path.read_text(encoding="utf-8"))

        role = (data.get("role") or "").strip()
        skills = data.get("skills", [])

        if not skills:
            logger.error("No skills found in input file; using example data")
            return "Data Scientist", [
                "Python Programming",
                "Machine Learning",
                "Data Visualization",
            ]

        # Clean and limit
        skills = [s.strip() for s in skills if s and s.strip()]
        if not skills:
            logger.error("No valid skills after cleanup; using example data")
            return "Data Scientist", [
                "Python Programming",
                "Machine Learning",
                "Data Visualization",
            ]

        if len(skills) > 5:
            logger.warning(f"Too many skills ({len(skills)}), limiting to 5")
            skills = skills[:5]

        # Leave role as-is; caller may override (e.g., with the user's role “Teacher”)
        role = role or "Unknown Role"
        logger.info(f"Loaded {len(skills)} skills from {skills_path}")
        return role, skills

    except Exception as e:
        logger.error(f"Error loading input data from {skills_path}: {e}")
        return "Data Scientist", [
            "Python Programming",
            "Machine Learning",
            "Data Visualization",
        ]

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "google.generativeai",
        "requests",
        "bs4",
        "aiohttp",
        "supadata",
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        logger.error(f"Missing required packages: {missing_packages}")
        logger.info("Run: pip install -r requirements.txt")
        return False

    return True

async def test_api_connectivity(config: dict):
    """Test API connectivity before starting main process"""
    import requests
    import google.generativeai as genai
    from supadata import Supadata, SupadataError

    logger.info("Testing API connectivity...")

    # Test YouTube API
    try:
        youtube_key = config["api_keys"]["youtube_api_key"]
        test_url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&q=test&type=video&maxResults=1&key={youtube_key}"
        )

        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            logger.info("YouTube API connectivity confirmed")
        else:
            logger.error(f"YouTube API test failed: HTTP {response.status_code}")
            if response.status_code == 403:
                logger.error("Check your API key and quota limits")
            return False

    except Exception as e:
        logger.error(f"YouTube API connectivity test failed: {e}")
        return False

    # Test Gemini API
    try:
        genai.configure(api_key=config["api_keys"]["gemini_api_key"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        _ = model.generate_content(
            "Hello",
            generation_config=genai.types.GenerationConfig(max_output_tokens=10),
        )
        logger.info("Gemini API connectivity confirmed")

    except Exception as e:
        logger.error(f"Gemini API connectivity test failed: {e}")
        return False

    # Test Supadata API
    try:
        supadata_key = config["api_keys"]["supadata_api_key"]
        supadata = Supadata(api_key=supadata_key)
        test_video_id = "dQw4w9WgXcQ"
        test_transcript = supadata.youtube.transcript(video_id=test_video_id, text=True)
        if test_transcript and test_transcript.content:
            logger.info("Supadata API connectivity confirmed")
        else:
            logger.error("Supadata API test failed: No content returned")
            return False
    except (SupadataError, Exception) as e:
        logger.error(f"Supadata API connectivity test failed: {e}")
        return False

    return True

def generate_markdown_report(data: dict) -> str:
    """Generates a Markdown formatted report from the analysis data."""
    report = f"# **{data['main_role'].upper()} - SKILLS ANALYSIS REPORT**\n\n"
    report += f"**Generated On**: {data['created_at']}\n\n"

    for skill_data in data["skills_breakdown"]:
        report += f"## Skill: {skill_data['skill']}\n\n"

        if skill_data["subskills"]:
            report += "### Subskills:\n"
            for subskill in skill_data["subskills"]:
                report += f"- {subskill}\n"
            report += "\n"

        if skill_data["key_takeaways"]:
            report += "### Key Takeaways:\n"
            for kt in skill_data["key_takeaways"]:
                report += f"- {kt}\n"
            report += "\n"

        if skill_data["important_info"]:
            report += "### Important Information:\n"
            for info in skill_data["important_info"]:
                report += f"- {info}\n"
            report += "\n"

        report += f"### Summary:\n{skill_data['summary']}\n\n"
        report += f"--- \n\n"

    if data["learning_path"]:
        report += "## Learning Path:\n"
        for i, step in enumerate(data["learning_path"], 1):
            report += f"{i}. {step}\n"
        report += "\n"

    if data["important_considerations"]:
        report += "## General Important Considerations:\n"
        for consideration in data["important_considerations"]:
            report += f"- {consideration}\n"
        report += "\n"

    return report

def generate_pdf_report(data: dict, config: dict, role: str) -> bool:
    """Generate PDF report with a clean and professional layout."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        report_filename_base = f"{role.replace(' ', '_')}_skills_report"
        pdf_path = Path(config["directories"]["json_output"]) / f"{report_filename_base}.pdf"
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=24,
            leading=28,
            alignment=1,
            spaceAfter=20,
            textColor=colors.HexColor("#2c3e50"),
        )
        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=12,
            alignment=1,
            spaceAfter=40,
            textColor=colors.gray,
        )
        h2_style = ParagraphStyle(
            "H2",
            parent=styles["Heading2"],
            fontSize=18,
            leading=22,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor("#34495e"),
        )
        h3_style = ParagraphStyle(
            "H3",
            parent=styles["Heading3"],
            fontSize=14,
            leading=18,
            spaceBefore=10,
            spaceAfter=5,
            textColor=colors.HexColor("#2980b9"),
        )
        body_style = styles["Normal"]
        bullet_style = ParagraphStyle(
            "Bullet",
            parent=styles["Normal"],
            firstLineIndent=0,
            leftIndent=18,
            spaceAfter=5,
        )

        story.append(Paragraph(f"<b>{data['main_role'].upper()}</b><br/>SKILLS ANALYSIS REPORT", title_style))
        story.append(Paragraph(f"Generated On: {data['created_at']}", subtitle_style))
        story.append(PageBreak())

        for skill_data in data["skills_breakdown"]:
            story.append(Paragraph(f"Skill: {skill_data['skill']}", h2_style))

            if skill_data["subskills"]:
                story.append(Paragraph("Subskills", h3_style))
                for subskill in skill_data["subskills"]:
                    story.append(Paragraph(f"• {subskill}", bullet_style))
                story.append(Spacer(1, 12))

            if skill_data["key_takeaways"]:
                story.append(Paragraph("Key Takeaways", h3_style))
                for kt in skill_data["key_takeaways"]:
                    story.append(Paragraph(f"• {kt}", bullet_style))
                story.append(Spacer(1, 12))

            if skill_data["important_info"]:
                story.append(Paragraph("Important Information", h3_style))
                for info in skill_data["important_info"]:
                    story.append(Paragraph(f"• {info}", bullet_style))
                story.append(Spacer(1, 12))

            story.append(Paragraph("Summary", h3_style))
            story.append(Paragraph(skill_data["summary"], body_style))
            story.append(PageBreak())

        if data["learning_path"]:
            story.append(Paragraph("Learning Path", h2_style))
            for i, step in enumerate(data["learning_path"], 1):
                story.append(Paragraph(f"{i}. {step}", body_style))
            story.append(Spacer(1, 12))

        if data["important_considerations"]:
            story.append(Paragraph("General Important Considerations", h2_style))
            for consideration in data["important_considerations"]:
                story.append(Paragraph(f"• {consideration}", bullet_style))

        doc.build(story)
        logger.info(f"PDF generated successfully with reportlab: {pdf_path}")
        return True

    except ImportError:
        logger.error("reportlab not installed. Run: pip install reportlab")
        return False
    except Exception as e:
        logger.error(f"Error generating PDF with reportlab: {e}")
        return False

async def run_scraper(role: str | None = None, skills: list[str] | None = None):
    """Run the YouTube scraper.

    If `role` is provided, it overrides the role read from input_skills.json
    (useful when the UI asked for e.g. 'Teacher'). If `skills` is None,
    we'll read them from input_skills.json next to this file.
    """
    print("YouTube Skills Learning Scraper")
    print("=" * 50)

    setup_logging()

    if not check_dependencies():
        return False

    config = load_config()

    if not validate_api_keys(config):
        return False

    if not await test_api_connectivity(config):
        logger.error("API connectivity test failed")
        return False

    # Load (role, skills) from file and then apply overrides
    file_role, file_skills = load_input_data()
    final_role = (role or file_role or "Unknown Role")
    final_skills = (skills or file_skills)

    print(f"Role: {final_role}")
    print(f"Skills to process: {len(final_skills)}")
    for i, s in enumerate(final_skills, 1):
        print(f"   {i}. {s}")

    expected_requests = len(final_skills) * config["settings"]["max_videos_per_skill"] * 2
    print(f"\nExpected API requests: ~{expected_requests}")
    print("YouTube API free tier limit: 100 requests/day")

    if expected_requests > 50:
        response = input("Continue? (y/n): ").lower().strip()
        if response != "y":
            print("Cancelled by user")
            return False

    print("\nInitializing scraper...")

    try:
        scraper = YouTubeSkillsScraper(
            gemini_api_key=config["api_keys"]["gemini_api_key"],
            youtube_api_key=config["api_keys"]["youtube_api_key"],
            supadata_api_key=config["api_keys"]["supadata_api_key"],
        )

        scraper.request_delay = config["settings"]["request_delay_seconds"]
        scraper.json_dir = Path(config["directories"]["json_output"])
        scraper.json_dir.mkdir(parents=True, exist_ok=True)

        print("Starting video analysis...")
        print("This may take several minutes depending on number of skills...")
        print("Progress will be saved to logs/scraper.log")

        comprehensive = await scraper.run_analysis(final_role, final_skills)

        result_file = scraper.json_dir / f"{final_role.replace(' ', '_')}_comprehensive_analysis.json"

        print("\nProcessing Complete!")
        print(f"Results saved to: {result_file}")

        display_summary(str(result_file))

        print("\nGenerating reports...")
        if generate_pdf_report(asdict(comprehensive), config, final_role):
            print("Reports generated successfully!")
        else:
            print("PDF generation failed, but JSON is available.")

        # Return the exact path so backend can expose it to the frontend
        return str(result_file)

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return False
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        logger.exception("Full error details:")
        return False

def display_summary(result_file: str):
    """Display summary of results with error handling"""
    try:
        if not Path(result_file).exists():
            logger.error(f"Result file not found: {result_file}")
            return

        with open(result_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"\nSUMMARY FOR {data['main_role'].upper()}")
        print("=" * 50)
        print(f"Skills analyzed: {len(data['skills_breakdown'])}")
        print(f"Learning path steps: {len(data['learning_path'])}")
        print(f"Important considerations: {len(data['important_considerations'])}")

        print(f"\nSKILLS BREAKDOWN:")
        total_videos = 0
        for skill_data in data["skills_breakdown"]:
            video_count = len(skill_data["videos"])
            total_videos += video_count
            print(f"   • {skill_data['skill']}: {video_count} videos")
            print(f"     Summary: {skill_data['summary']}")

        print(f"\nOUTPUT FOLDERS:")
        print(f"   • {Path(result_file).parent.as_posix()}/ - All analysis JSON files")
        print(f"   • ./logs/scraper.log - Detailed processing log")
        print(f"\nGenerated at: {data['created_at']}")

    except Exception as e:
        logger.error(f"Error displaying summary: {e}")
        logger.info(f"You can still check the result file: {result_file}")

def mainYTagent():
    """CLI entry point (kept for manual runs)"""
    try:
        # No override from CLI; backend should call run_scraper(role=...)
        success = asyncio.run(run_scraper())

        if success:
            print("\nAll done! Check the output folders for your results.")
            print("You can now run different roles or modify input_skills.json")
        else:
            print("\nProcessing failed. Check logs/scraper.log for details.")
            print("Common fixes:")
            print("   • Check your API keys in config.json")
            print("   • Verify internet connection")
            print("   • Check API quotas and limits")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Check logs/scraper.log for full details")
        sys.exit(1)

if __name__ == "__main__":
    mainYTagent()
