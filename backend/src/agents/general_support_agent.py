"""
General Support Agent for Smart Career SG
Handles workplace challenges, career development, and professional growth queries
"""

import logging
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

class GeneralSupportAgent:
    """
    Agent responsible for handling general job support queries including
    workplace challenges, career development, and professional growth guidance.
    """
    
    def __init__(self):
        """Initialize the General Support Agent with necessary configurations."""
        self.logger = logging.getLogger(__name__)
        self.conversation_history = []
        self.supported_topics = [
            "workplace_challenges",
            "career_development", 
            "professional_growth",
            "work_life_balance",
            "interview_preparation",
            "networking",
            "skill_development",
            "performance_improvement"
        ]
    
    def process_message(self, message: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a user message and generate an appropriate response.
        
        Args:
            message (str): The user's message
            user_context (Optional[Dict]): Additional context about the user
            
        Returns:
            Dict[str, Any]: Response containing message, suggestions, and metadata
        """
        try:
            # Add message to conversation history
            self.conversation_history.append({
                "type": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Analyze message intent
            intent = self._analyze_intent(message)
            
            # Generate response based on intent
            response = self._generate_response(message, intent, user_context)
            
            # Add response to conversation history
            self.conversation_history.append({
                "type": "bot",
                "content": response["message"],
                "timestamp": datetime.now().isoformat(),
                "intent": intent
            })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return {
                "message": "I apologize, but I encountered an error processing your request. Please try rephrasing your question.",
                "suggestions": [
                    "Ask about workplace challenges",
                    "Inquire about career development",
                    "Seek advice on professional growth"
                ],
                "error": True
            }
    
    def _analyze_intent(self, message: str) -> str:
        """
        Analyze the user's message to determine intent.
        
        Args:
            message (str): The user's message
            
        Returns:
            str: The identified intent category
        """
        message_lower = message.lower()
        
        # Intent classification logic
        if any(keyword in message_lower for keyword in ["stress", "difficult", "problem", "challenge", "conflict"]):
            return "workplace_challenges"
        elif any(keyword in message_lower for keyword in ["career", "promotion", "advance", "growth", "develop"]):
            return "career_development"
        elif any(keyword in message_lower for keyword in ["skill", "learn", "improve", "training", "course"]):
            return "skill_development"
        elif any(keyword in message_lower for keyword in ["interview", "job search", "application", "resume"]):
            return "interview_preparation"
        elif any(keyword in message_lower for keyword in ["network", "connection", "relationship", "mentor"]):
            return "networking"
        elif any(keyword in message_lower for keyword in ["balance", "time", "productivity", "efficiency"]):
            return "work_life_balance"
        else:
            return "general_support"
    
    def _generate_response(self, message: str, intent: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate a response based on the message and identified intent.
        
        Args:
            message (str): The user's message
            intent (str): The identified intent
            user_context (Optional[Dict]): Additional user context
            
        Returns:
            Dict[str, Any]: Generated response with suggestions
        """
        # Response templates based on intent
        response_templates = {
            "workplace_challenges": {
                "message": "I understand you're facing some workplace challenges. These situations can be stressful, but there are effective strategies to address them. Could you provide more specific details about the challenge you're experiencing?",
                "suggestions": [
                    "Tell me about a specific conflict with a colleague",
                    "I'm struggling with my workload",
                    "My manager and I have communication issues",
                    "I'm feeling overwhelmed at work"
                ]
            },
            "career_development": {
                "message": "Career development is an exciting journey! I'm here to help you navigate your professional growth. What specific aspect of your career development would you like to focus on?",
                "suggestions": [
                    "How can I get promoted in my current role?",
                    "What skills should I develop for advancement?",
                    "How do I transition to a leadership position?",
                    "I want to change career paths"
                ]
            },
            "skill_development": {
                "message": "Continuous learning and skill development are key to professional success. I can help you identify the right skills to focus on and create a learning plan. What area would you like to develop?",
                "suggestions": [
                    "Technical skills for my current role",
                    "Leadership and management skills",
                    "Communication and presentation skills",
                    "Industry-specific certifications"
                ]
            },
            "interview_preparation": {
                "message": "Interview preparation is crucial for landing your dream job. I can help you prepare effectively and boost your confidence. What aspect of interview preparation would you like to work on?",
                "suggestions": [
                    "Common interview questions and answers",
                    "How to research the company",
                    "Salary negotiation strategies",
                    "Follow-up after interviews"
                ]
            },
            "networking": {
                "message": "Building professional networks is essential for career growth. I can provide strategies for effective networking both online and offline. What networking challenge are you facing?",
                "suggestions": [
                    "How to network as an introvert",
                    "Building connections on LinkedIn",
                    "Attending industry events effectively",
                    "Maintaining professional relationships"
                ]
            },
            "work_life_balance": {
                "message": "Achieving work-life balance is important for both professional success and personal well-being. I can help you develop strategies to manage your time and energy more effectively. What's your main concern?",
                "suggestions": [
                    "Managing long work hours",
                    "Setting boundaries with colleagues",
                    "Improving productivity and efficiency",
                    "Dealing with work-related stress"
                ]
            },
            "general_support": {
                "message": "I'm here to help with any career-related questions or challenges you might have. Whether it's about your current job, career planning, or professional development, feel free to share what's on your mind.",
                "suggestions": [
                    "I need advice about my current job situation",
                    "How can I improve my professional skills?",
                    "I'm considering a career change",
                    "Help me with workplace communication"
                ]
            }
        }
        
        return response_templates.get(intent, response_templates["general_support"])
    
    def get_conversation_history(self) -> List[Dict]:
        """
        Get the current conversation history.
        
        Returns:
            List[Dict]: List of conversation messages
        """
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []