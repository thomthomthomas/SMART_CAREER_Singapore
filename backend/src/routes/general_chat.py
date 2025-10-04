"""
General Chat Routes for Smart Career SG
Simple Strands + Bedrock implementation with a pre-prompt.
"""

from flask import Blueprint, request, jsonify
import os
import logging
from datetime import datetime

# Strands
from strands import Agent
from strands.models import BedrockModel

general_chat_bp = Blueprint("general_chat", __name__)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Config (env-driven) ---
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
# Use a region-prefixed Bedrock modelId that your account has access to.
# Example: "us.anthropic.claude-sonnet-4-20250514-v1:0" or an approved Claude 3.5 Sonnet variant.
BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "us.anthropic.claude-sonnet-4-20250514-v1:0",
)

SYSTEM_PROMPT = (
    "You are a friendly, pragmatic assistant for workplace questions, "
    "career development, and professional growth. Give concise, useful answers, "
    "with optional bullet points and actionable next steps when helpful."
)

# Build a Bedrock model + agent once (Strands will use the Converse API under the hood)
bedrock_model = BedrockModel(
    model_id=BEDROCK_MODEL_ID,
    region_name=AWS_REGION,
    temperature=0.3,
    top_p=0.9,
)
agent = Agent(model=bedrock_model, system_prompt=SYSTEM_PROMPT)

@general_chat_bp.route("/general-chat", methods=["POST"])
def general_chat():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON", "success": False}), 400

        data = request.get_json()
        msg = (data.get("message") or "").strip()
        if not msg:
            return jsonify({"error": "Message is required", "success": False}), 400

        session_id = (data.get("user_context") or {}).get("session_id") or "default"
        logger.info("[general-chat] session=%s msg=%r", session_id, msg[:100])

        # Simple single-turn invoke (Strands handles role formatting + system prompt)
        reply = str(agent(msg)).strip()

        return jsonify({
            "message": reply,
            "suggestions": [
                "How can I prepare for a performance review?",
                "Tips to negotiate a raise?",
                "Plan a 90-day growth roadmap"
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": True
        }), 200

    except Exception as e:
        err_msg = str(e)
        logger.error("Error in general_chat: %s", err_msg, exc_info=True)

        # Helpful hints for common Bedrock access misconfigurations
        if "AccessDeniedException" in err_msg or "You don't have access to the model" in err_msg:
            hint = (
                "Access denied for the selected Bedrock model. "
                "Confirm model access is granted in the Bedrock console for this Region "
                f"({AWS_REGION}) and that BEDROCK_MODEL_ID is correct."
            )
        else:
            hint = "Unexpected error. Check AWS credentials, Region, and model ID."

        return jsonify({
            "error": "Bedrock invocation failed",
            "message": "I’m having trouble reaching the model right now.",
            "suggestions": [
                "Verify BEDROCK_MODEL_ID matches an enabled model in your Region",
                "Try us-east-1 and a region-prefixed model ID (e.g., us.anthropic...)",
                "Re-run: aws bedrock list-foundation-models --region us-east-1"
            ],
            "details": hint,
            "success": False
        }), 500

@general_chat_bp.route("/general-chat/status", methods=["GET"])
def general_chat_status():
    try:
        return jsonify({
            "status": "active",
            "agent_type": "general_support",
            "conversation_length": 0,  # single-turn demo
            "supported_topics": [
                "workplace questions", "career development", "professional growth"
            ],
            "model_id": BEDROCK_MODEL_ID,
            "region": AWS_REGION,
            "success": True
        }), 200
    except Exception:
        return jsonify({"error": "Failed to get status", "success": False}), 500
