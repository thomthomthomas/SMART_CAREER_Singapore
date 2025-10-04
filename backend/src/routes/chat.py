import os
import json
import threading
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from flask_cors import cross_origin
from src.agents.analysis_manager import AnalysisManager

# Import the PDF generator (add this to your existing imports)
from src.utils.pdf_report_generator import generate_pdf_report

# Global variables to track analysis status
analysis_status = {
    "status": "idle",      # idle, running, completed, error
    "progress": 0,
    "message": "",
    "result_file": None,
    "error": None,
    "start_time": None,
}

analysis_result = None
analysis_manager = AnalysisManager()

chat_bp = Blueprint("chat", __name__)

def update_analysis_status(status, progress=None, message="", result_file=None, error=None):
    """Update the global analysis status (called by AnalysisManager as well)."""
    global analysis_status
    analysis_status["status"] = status
    if progress is not None:
        analysis_status["progress"] = progress
    if message is not None:
        analysis_status["message"] = message
    if result_file is not None:
        analysis_status["result_file"] = result_file
    if error is not None:
        analysis_status["error"] = error

def run_analysis_workflow(skills):
    """Run the analysis workflow in a background thread."""
    global analysis_result
    try:
        # Ensure fresh state
        update_analysis_status("running", progress=5, message="Starting analysis...", result_file=None, error=None)

        # Delegate to your existing manager (it should call update_analysis_status during steps)
        result = analysis_manager.run_comprehensive_analysis(skills, update_analysis_status)
        analysis_result = result

        # Finalize status if manager didn't
        rf = analysis_status.get("result_file")
        if not rf and isinstance(result, dict):
            rf = result.get("file_path") or result.get("result_file")
            if rf:
                update_analysis_status(analysis_status["status"], result_file=rf)

        update_analysis_status("completed", progress=100, message="Analysis completed.")
    except Exception as e:
        update_analysis_status("error", progress=0, message="Analysis failed.", error=str(e))

@chat_bp.route("/chat", methods=["POST"])
@cross_origin()
def handle_chat():
    """Handle chat messages and determine appropriate responses."""
    try:
        data = request.get_json() or {}
        message = (data.get("message") or "").lower()

        analysis_keywords = ["analyze", "analysis", "career", "course", "skill", "job", "recommendation"]
        start_keywords = ["start", "begin", "go", "yes", "do it"]

        known_skills = [
            "data analyst", "software developer", "digital marketing specialist", "ux/ui designer",
            "finance", "money", "accounting", "marketing", "sales", "engineer", "doctor",
            "teacher", "nurse", "artist", "writer", "project manager", "business analyst",
            "cybersecurity", "machine learning", "artificial intelligence", "ai", "python",
            "javascript", "java", "cloud computing", "devops", "product management"
        ]

        detected_skill = next((s for s in known_skills if s in message), None)

        if detected_skill:
            response = {
                "message": (
                    f"Great! I'll start a comprehensive analysis for {detected_skill}. "
                    "This will include web scraping for courses, YouTube content analysis, "
                    "and personalized recommendations. Please wait while I process this for you..."
                ),
                "action": "start_analysis",
                "skills": [detected_skill.title()],
            }
        elif any(keyword in message for keyword in start_keywords):
            response = {
                "message": (
                    "Great! I'll start a comprehensive analysis that includes web scraping for courses, "
                    "YouTube content analysis, and personalized career insights. This may take a few minutes."
                ),
                "action": "start_analysis",
                "skills": ["Data Analyst"],
            }
        elif any(keyword in message for keyword in analysis_keywords):
            response = {
                "message": (
                    "I can help you with a comprehensive career analysis! "
                    "What specific career or skill would you like me to analyze?"
                ),
                "suggestions": [
                    "Data Analyst",
                    "Software Developer",
                    "Digital Marketing Specialist",
                    "UX/UI Designer",
                ],
            }
        elif any(keyword in message for keyword in ["help", "what", "how"]):
            response = {
                "message": (
                    "I'm your Smart Career SG assistant! I can help you with:\n\n"
                    "• Comprehensive career analysis\n"
                    "• Course recommendations from Coursera, edX, and Udemy\n"
                    "• YouTube learning content analysis\n"
                    "• Job market insights and salary information\n"
                    "• Skill development recommendations\n\n"
                    "Just tell me what career or skill you're interested in!"
                ),
                "suggestions": [
                    "Analyze Data Analyst career",
                    "Find courses for Python programming",
                    "What jobs are in demand?",
                ],
            }
        else:
            response = {
                "message": (
                    "I understand you're interested in career guidance. I can provide comprehensive analysis "
                    "including course recommendations, job market insights, and learning paths. "
                    "What specific career or skill would you like me to analyze?"
                ),
                "suggestions": [
                    "Data Analyst",
                    "Software Developer",
                    "Digital Marketing Specialist",
                    "UX/UI Designer",
                ],
            }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route("/start-analysis", methods=["POST"])
@cross_origin()
def start_analysis():
    """Start the comprehensive analysis workflow."""
    try:
        data = request.get_json() or {}
        skills = data.get("skills", ["Data Analyst"])

        if analysis_status["status"] == "running":
            return jsonify({"error": "Analysis is already running"}), 400

        # Reset previous result and status
        global analysis_result
        analysis_result = None
        update_analysis_status("running", progress=0, message="Starting analysis...", result_file=None, error=None)

        analysis_thread = threading.Thread(target=run_analysis_workflow, args=(skills,), daemon=True)
        analysis_thread.start()

        return jsonify({"status": "started", "message": f"Analysis started for: {', '.join(skills)}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route("/analysis-status", methods=["GET"])
@cross_origin()
def get_analysis_status():
    """Get current analysis status."""
    return jsonify(analysis_status)

@chat_bp.route("/analysis-result", methods=["GET"])
@cross_origin()
def get_analysis_result():
    """
    Return exactly what the frontend expects:
      { status: 'completed' | 'error' | 'running', data: <json or null>, file_path: <string or null> }
    """
    try:
        rf = analysis_status.get("result_file")
        status = analysis_status.get("status", "idle")

        # If we have a file path, load it and return
        if rf and os.path.exists(rf):
            with open(rf, "r", encoding="utf-8") as f:
                data = json.load(f)
            return jsonify({"status": "completed", "data": data, "file_path": rf})

        # Otherwise, if the manager returned data directly, wrap it
        if isinstance(analysis_result, dict) and ("data" in analysis_result or "skills_breakdown" in analysis_result):
            data = analysis_result.get("data", analysis_result)
            file_path = analysis_result.get("file_path") or rf
            return jsonify({"status": status, "data": data, "file_path": file_path})

        return jsonify({"status": status, "error": analysis_status.get("error"), "file_path": rf}), 400

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@chat_bp.route("/download-result/<path:filename>", methods=["GET"])
@cross_origin()
def download_result(filename):
    """Download the analysis result file."""
    try:
        if os.path.exists(filename):
            return send_file(filename, as_attachment=True)
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route("/download-pdf-report", methods=["GET"])
@cross_origin()
def download_latest_pdf_report():
    """
    Download the latest PDF report based on current analysis results.
    This endpoint uses the current analysis_result to generate a PDF.
    """
    try:
        global analysis_result, analysis_status
        
        # Check if we have analysis results
        if not analysis_result:
            # Try to load from file if available
            rf = analysis_status.get("result_file")
            if rf and os.path.exists(rf):
                with open(rf, "r", encoding="utf-8") as f:
                    analysis_result = json.load(f)
            else:
                return jsonify({"error": "No analysis results available"}), 404
        
        # Extract the data from analysis_result
        if isinstance(analysis_result, dict):
            analysis_data = analysis_result.get("data", analysis_result)
        else:
            analysis_data = analysis_result
        
        # Create reports directory
        reports_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate the PDF report
        pdf_path = generate_pdf_report(analysis_data, reports_dir)
        
        if not os.path.exists(pdf_path):
            return jsonify({"error": "Failed to generate PDF report"}), 500
        
        # Return the PDF file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"Smart_Career_SG_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({"error": f"Failed to generate PDF report: {str(e)}"}), 500

@chat_bp.route("/pdf-status", methods=["GET"])
@cross_origin()
def pdf_generation_status():
    """Check if PDF generation is available and working."""
    try:
        # Test if we can import the PDF generator
        from src.utils.pdf_report_generator import PDFReportGenerator
        
        return jsonify({
            "pdf_generation_available": True,
            "message": "PDF generation is ready"
        })
    except ImportError as e:
        return jsonify({
            "pdf_generation_available": False,
            "error": f"PDF generation not available: {str(e)}"
        }), 500



