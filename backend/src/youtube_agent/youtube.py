import json
import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import re
from datetime import datetime
import os
from urllib.parse import quote_plus
import time

# Third-party imports
from supadata import Supadata, SupadataError
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# Configure logging (fixed: remove stray space in asctime)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

@dataclass
class VideoContent:
    video_id: str
    title: str
    channel: str
    view_count: int
    duration: str
    transcript: str


@dataclass
class SkillAnalysis:
    skill: str
    videos: List[VideoContent]
    subskills: List[str]
    key_takeaways: List[str]
    important_info: List[str]
    summary: str

@dataclass
class ComprehensiveAnalysis:
    main_role: str
    skills_breakdown: List[SkillAnalysis]
    important_considerations: List[str]
    learning_path: List[str]
    created_at: str

class EnhancedTranscriptExtractor:
    """Enhanced transcript extractor using Supadata and YouTube Data API"""
    
    @staticmethod
    def extract_with_supadata(video_id: str, supadata_api_key: str) -> str:
        """Primary method: Use Supadata API for transcription"""
        try:
            supadata = Supadata(api_key=supadata_api_key)
            text_transcript = supadata.youtube.transcript(
                video_id=video_id,
                text=True
            )
            if text_transcript and text_transcript.content:
                logger.info(f"Successfully extracted transcript for {video_id} using Supadata")
                return text_transcript.content
        except SupadataError as e:
            logger.warning(f"Supadata transcription failed for {video_id}: {e}")
        except Exception as e:
            logger.warning(f"Error with Supadata transcription for {video_id}: {e}")
        return ""

    @staticmethod
    def extract_with_youtube_api_description(video_id: str, youtube_api_key: str) -> str:
        """Fallback method: Use YouTube Data API to get description"""
        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'part': 'snippet',
                'id': video_id,
                'key': youtube_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["items"]:
                    description = data["items"][0]["snippet"].get("description", "")
                    if description and len(description) > 100:
                        logger.info(f"Using YouTube API description for {video_id}")
                        return f"Video Description: {description}"
                        
        except Exception as e:
            logger.warning(f"YouTube API description extraction failed for {video_id}: {e}")
            
        return ""

    @classmethod
    def extract_transcript(cls, video_id: str, supadata_api_key: str, youtube_api_key: str) -> str:
        """Main method that tries all extraction methods"""
        
        # Method 1: Supadata API (primary)
        transcript = cls.extract_with_supadata(video_id, supadata_api_key)
        if transcript:
            return transcript
            
        # Method 2: YouTube Data API description (fallback)
        if youtube_api_key:
            transcript = cls.extract_with_youtube_api_description(video_id, youtube_api_key)
            if transcript:
                return transcript
            
        logger.error(f"All transcript extraction methods failed for video {video_id}")
        return ""

class YouTubeSkillsScraper:
    def __init__(self, gemini_api_key: str, youtube_api_key: str, supadata_api_key: str):
        """
        Initialize the scraper with API keys
        
        Args:
            gemini_api_key: Google Gemini API key
            youtube_api_key: YouTube Data API v3 key
            supadata_api_key: Supadata API key
        """
        self.gemini_api_key = gemini_api_key
        self.youtube_api_key = youtube_api_key
        self.supadata_api_key = supadata_api_key
        
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Initialize transcript extractor
        self.transcript_extractor = EnhancedTranscriptExtractor()
        
        # Create directories
        self.json_dir = Path("json_outputs")
        self.json_dir.mkdir(exist_ok=True)
        
        # Rate limiting
        self.request_delay = 1  # seconds between requests

    async def search_youtube_videos(self, role: str, skill: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Search YouTube for tutorial videos on a specific skill within a role context"""
        search_query = f"{role} {skill} tutorial"
        url = "https://www.googleapis.com/youtube/v3/search"
        
        params = {
            'part': 'snippet',
            'q': search_query,
            'type': 'video',
            'order': 'relevance',
            'maxResults': max_results,
            'key': self.youtube_api_key,
            'videoDuration': 'medium',  # Prefer medium-length videos
            'videoDefinition': 'any',
            'videoCaption': 'closedCaption'  # Prefer videos with captions
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Found {len(data.get('items', []))} videos for skill: {skill}")
                        return data.get("items", [])
                    else:
                        logger.error(f"YouTube API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error searching YouTube for {skill}: {e}")
            return []

    def get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed video information including view count and duration"""
        url = "https://www.googleapis.com/youtube/v3/videos"
        
        params = {
            'part': 'snippet,statistics,contentDetails',
            'id': video_id,
            'key': self.youtube_api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["items"]:
                    return data["items"][0]
        except Exception as e:
            logger.error(f"Error getting video details for {video_id}: {e}")
        
        return None

    def get_video_transcript(self, video_id: str) -> str:
        """Extract transcript from YouTube video using enhanced extractor"""
        try:
            transcript = self.transcript_extractor.extract_transcript(
                video_id, 
                self.supadata_api_key,
                self.youtube_api_key
            )
            
            if transcript:
                logger.info(f"Successfully extracted transcript for {video_id} ({len(transcript)} characters)")
                return transcript
            else:
                logger.warning(f"No transcript could be extracted for video {video_id}")
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting transcript for {video_id}: {e}")
            return ""

    async def analyze_skill_with_gemini(self, skill: str, video_contents: List[VideoContent]) -> SkillAnalysis:
        """Use Gemini to analyze videos and extract subskills"""
        
        if not video_contents:
            return SkillAnalysis(
                skill=skill,
                videos=[],
                subskills=[],
                key_takeaways=[],
                important_info=[],
                summary=f"No video content available for {skill}"
            )
        
        # Prepare content for analysis
        analysis_text = f"Skill: {skill}\n\n"
        for i, video in enumerate(video_contents, 1):
            content_preview = video.transcript[:800] if video.transcript else "No transcript available"
            analysis_text += f"Video {i}: {video.title}\n"
            analysis_text += f"Channel: {video.channel}\n"
            analysis_text += f"Views: {video.view_count:,}\n"
            analysis_text += f"Content: {content_preview}...\n\n"
        
        prompt = f"""
        Analyze the following skill and video content to extract learning insights:

        {analysis_text}

        Please provide a comprehensive analysis for the skill "{skill}" including:

        1. SUBSKILLS: List 5-8 specific subskills or topics that learners need to master, formatted as bullet points with specific examples (e.g., for SQL: SELECT, COUNT, JOIN).
        2. KEY_TAKEAWAYS: Important concepts or practical applications to note, formatted as bullet points.
        3. IMPORTANT_INFO: Any crucial information or best practices related to the skill, formatted as bullet points.
        4. SUMMARY: A detailed learning summary covering what students will learn.

        Format your response exactly as:

        SUBSKILLS:
        - [subskill 1: example 1, example 2]
        - [subskill 2: example 1, example 2]

        KEY_TAKEAWAYS:
        - [key takeaway 1]
        - [key takeaway 2]

        IMPORTANT_INFO:
        - [important info 1]
        - [important info 2]

        SUMMARY:
        [Write a comprehensive paragraph about what learners will gain from these videos]
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            content = response.text
            
            # Parse response
            subskills = []
            key_takeaways = []
            important_info = []
            summary = ""
            
            lines = content.split("\n")
            in_subskills = False
            in_key_takeaways = False
            in_important_info = False
            in_summary = False
            
            for line in lines:
                line = line.strip()
                if "SUBSKILLS:" in line.upper():
                    in_subskills = True
                    in_key_takeaways = False
                    in_important_info = False
                    in_summary = False
                elif "KEY_TAKEAWAYS:" in line.upper():
                    in_subskills = False
                    in_key_takeaways = True
                    in_important_info = False
                    in_summary = False
                elif "IMPORTANT_INFO:" in line.upper():
                    in_subskills = False
                    in_key_takeaways = False
                    in_important_info = True
                    in_summary = False
                elif "SUMMARY:" in line.upper():
                    in_subskills = False
                    in_key_takeaways = False
                    in_important_info = False
                    in_summary = True
                elif in_subskills and line.startswith("-"):
                    subskill = line[1:].strip()
                    if subskill:
                        subskills.append(subskill)
                elif in_key_takeaways and line.startswith("-"):
                    key_takeaway = line[1:].strip()
                    if key_takeaway:
                        key_takeaways.append(key_takeaway)
                elif in_important_info and line.startswith("-"):
                    info = line[1:].strip()
                    if info:
                        important_info.append(info)
                elif in_summary and line:
                    summary += line + " "
            
            logger.info(f"Gemini analysis completed for {skill}: {len(subskills)} subskills identified")
            
            return SkillAnalysis(
                skill=skill,
                videos=video_contents,
                subskills=subskills,
                key_takeaways=key_takeaways,
                important_info=important_info,
                summary=summary.strip()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing skill with Gemini: {e}")
            return SkillAnalysis(
                skill=skill,
                videos=video_contents,
                subskills=["Analysis failed - please review manually"],
                key_takeaways=["Analysis failed - please review manually"],
                important_info=["Analysis failed - please review manually"],
                summary=f"Gemini analysis failed for {skill}. Videos were processed successfully."
            )

    async def process_single_skill(self, role: str, skill: str) -> SkillAnalysis:
        """Process a single skill: search videos, extract content, analyze"""
        logger.info(f"🎯 Processing skill: {skill}")
        
        # Search for videos
        video_items = await self.search_youtube_videos(role, skill)
        if not video_items:
            logger.warning(f"No videos found for skill: {skill}")
            return SkillAnalysis(skill=skill, videos=[], subskills=[], key_takeaways=[], important_info=[], summary="No content found")
        
        video_contents = []
        for item in video_items:
            video_id = item["id"]["videoId"]
            
            # Get video details
            details = self.get_video_details(video_id)
            if not details:
                logger.warning(f"Could not get details for video {video_id}, skipping.")
                continue
            
            title = details["snippet"]["title"]
            channel = details["snippet"]["channelTitle"]
            view_count = int(details["statistics"].get("viewCount", 0))
            
            # Parse duration (ISO 8601 format)
            duration_iso = details["contentDetails"].get("duration", "PT0S")
            duration_seconds = self._parse_youtube_duration(duration_iso)
            duration_formatted = f"{duration_seconds // 60}m {duration_seconds % 60}s"
            
            # Get transcript
            transcript = self.get_video_transcript(video_id)
            
            video_contents.append(
                VideoContent(
                    video_id=video_id,
                    title=title,
                    channel=channel,
                    view_count=view_count,
                    duration=duration_formatted,
                    transcript=transcript
                )
            )
            
            # Add delay to respect API rate limits
            await asyncio.sleep(self.request_delay)
            
        # Analyze with Gemini
        return await self.analyze_skill_with_gemini(skill, video_contents)

    def _parse_youtube_duration(self, duration_iso: str) -> int:
        """Parses ISO 8601 duration string to total seconds"""
        # This is a simplified parser and might not cover all edge cases
        total_seconds = 0
        
        # Extract hours, minutes, seconds
        hours_match = re.search(r'(\d+)H', duration_iso)
        minutes_match = re.search(r'(\d+)M', duration_iso)
        seconds_match = re.search(r'(\d+)S', duration_iso)
        
        if hours_match: 
            total_seconds += int(hours_match.group(1)) * 3600
        if minutes_match:
            total_seconds += int(minutes_match.group(1)) * 60
        if seconds_match:
            total_seconds += int(seconds_match.group(1))
            
        return total_seconds

    async def generate_comprehensive_analysis(self, role: str, skill_analyses: List[SkillAnalysis]) -> ComprehensiveAnalysis:
        """Generate a comprehensive analysis for the main role"""
        
        if not skill_analyses:
            return ComprehensiveAnalysis(
                main_role=role,
                skills_breakdown=[],
                important_considerations=["No skills analyzed"],
                learning_path=["No learning path generated"],
                created_at=datetime.now().isoformat()
            )
            
        analysis_text = f"Comprehensive analysis for the role: {role}\n\n"
        for skill_analysis in skill_analyses:
            analysis_text += f"Skill: {skill_analysis.skill}\n"
            analysis_text += f"Summary: {skill_analysis.summary}\n\n"
            
        prompt = f"""
        Based on the following skill analyses for the role of "{role}", generate:

        1. IMPORTANT_CONSIDERATIONS: 3-5 general important considerations for someone pursuing this role, formatted as bullet points.
        2. LEARNING_PATH: A step-by-step learning path (5-7 steps) to master the skills for this role, formatted as numbered list.

        Skill Analyses:
        {analysis_text}

        Format your response exactly as:

        IMPORTANT_CONSIDERATIONS:
        - [consideration 1]
        - [consideration 2]

        LEARNING_PATH:
        1. [step 1]
        2. [step 2]
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            content = response.text
            
            important_considerations = []
            learning_path = []
            
            lines = content.split("\n")
            in_considerations = False
            in_learning_path = False
            
            for line in lines:
                line = line.strip()
                if "IMPORTANT_CONSIDERATIONS:" in line.upper():
                    in_considerations = True
                    in_learning_path = False
                elif "LEARNING_PATH:" in line.upper():
                    in_considerations = False
                    in_learning_path = True
                elif in_considerations and line.startswith("-"):
                    consideration = line[1:].strip()
                    if consideration:
                        important_considerations.append(consideration)
                elif in_learning_path and re.match(r"^\d+\.", line):
                    step = re.sub(r"^\d+\.\s*", "", line).strip()
                    if step:
                        learning_path.append(step)
            
            logger.info("Comprehensive analysis generated by Gemini")
            
            return ComprehensiveAnalysis(
                main_role=role,
                skills_breakdown=skill_analyses,
                important_considerations=important_considerations,
                learning_path=learning_path,
                created_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error generating comprehensive analysis with Gemini: {e}")
            return ComprehensiveAnalysis(
                main_role=role,
                skills_breakdown=skill_analyses,
                important_considerations=["Comprehensive analysis failed"],
                learning_path=["Learning path generation failed"],
                created_at=datetime.now().isoformat()
            )

    async def run_analysis(self, role: str, skills: List[str]) -> ComprehensiveAnalysis:
        """Main entry point to run the full analysis for a given role and list of skills"""
        logger.info(f"Starting comprehensive analysis for role: {role} with skills: {skills}")
        
        skill_analyses = []
        for skill in skills:
            skill_analysis = await self.process_single_skill(role, skill)
            skill_analyses.append(skill_analysis)
            
        comprehensive_analysis = await self.generate_comprehensive_analysis(role, skill_analyses)
        
        # Save the result to a JSON file (fixed nested quotes)
        output_filename = f"{role.replace(' ', '_')}_comprehensive_analysis.json"
        output_path = self.json_dir / output_filename
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(asdict(comprehensive_analysis), f, indent=4, ensure_ascii=False)
            
        logger.info(f"Comprehensive analysis saved to {output_path}")
        
        return comprehensive_analysis

