import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import time
import re

from tavily import TavilyClient
import google.generativeai as genai
from google.api_core import exceptions

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class TavilyWebScraper:
    def __init__(self, tavily_api_key: str, gemini_api_key: str):
        self.client = TavilyClient(api_key=tavily_api_key)
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")

    def _perform_tavily_search(self, query: str, search_depth: str = "basic", include_answer: bool = False, include_raw_content: bool = False, max_results: int = 5) -> Dict[str, Any]:
        """Performs a Tavily search and returns the results."""
        try:
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                include_answer=include_answer,
                include_raw_content=include_raw_content,
                max_results=max_results
            )
            return response
        except Exception as e:
            logger.error(f"Tavily search failed for query \'{query}\': {e}")
            return {"results": []}

    def _extract_content_from_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Extracts content from a list of URLs using Tavily's search with raw_content."""
        extracted_data = []
        for url in urls:
            try:
                # Use Tavily search with include_raw_content=True to extract content
                response = self.client.search(query=url, include_raw_content=True, max_results=1)
                if response and response.get("results"):
                    # The raw_content is usually in the first result's content field
                    content = response["results"][0].get("content")
                    extracted_data.append({"url": url, "content": content})
                else:
                    logger.warning(f"No content found for {url} using Tavily search.")
            except Exception as e:
                logger.warning(f"Failed to extract content from {url}: {e}")
        return extracted_data

    def _call_gemini_with_retry(self, prompt: str, max_retries: int = 3, initial_delay: int = 5) -> str:
        """Calls Gemini API with retry logic for rate limits."""
        for i in range(max_retries):
            try:
                response = self.gemini_model.generate_content(prompt)
                return response.text
            except exceptions.ResourceExhausted as e:
                delay = initial_delay * (2 ** i)
                logger.warning(f"Rate limit exceeded. Retrying in {delay} seconds... ({e})")
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}")
                return ""
        logger.error(f"Max retries exceeded for Gemini API call.")
        return ""

    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extracts a JSON object from a string that might contain markdown."""
        # Find the start and end of the JSON block
        json_match = re.search(r"```json\n(.*\n)```", response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from extracted string: {e}. String: {json_str}")
                return {}
        else:
            # If no markdown block is found, try to parse the whole string
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                logger.error(f"The whole response is not valid JSON. Response: {response_text}")
                return {}

    def _extract_modules_from_course_page(self, url: str, skill: str) -> List[str]:
        """Extracts course modules from a given URL using Tavily's extract and Gemini for summarization."""
        extracted_content = self._extract_content_from_urls([url])
        if not extracted_content or not extracted_content[0].get("content"):
            return []

        content = extracted_content[0]["content"]
        prompt = f"""
        From the following content of a course page about \'{skill}\' , identify and list the main modules, sections, or key topics of the course.
        Present the modules as a JSON array of strings. Each string should be a concise title of a module or topic.
        If no clear modules, sections, or key topics are found, return an empty JSON array.

        Content: {content}
        """
        response_text = self._call_gemini_with_retry(prompt)
        try:
            modules = self._extract_json_from_response(response_text)
            if isinstance(modules, dict) and not modules:
                return [] # Return empty list if an empty dictionary is returned
            elif isinstance(modules, list):
                return modules
            else:
                logger.warning(f"Gemini returned non-list or non-empty dict for modules: {response_text}")
                return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse modules JSON from Gemini response: {e}. Response: {response_text}")
            return []

    def _rank_modules_by_relevance(self, modules: List[str], skill: str) -> List[Dict[str, Any]]:
        """Ranks modules by relevance to the given skill using Gemini API."""
        if not modules:
            return []
        
        # Remove duplicates while preserving order
        unique_modules = list(dict.fromkeys(modules))
        
        if not unique_modules:
            return []
        
        prompt = f"""
        You are an expert curriculum advisor. Given the following list of course modules/topics and a target skill, 
        rank them from most relevant to least relevant for someone learning "{skill}".
        
        Modules to rank:
        {json.dumps(unique_modules, indent=2)}
        
        Target Skill: {skill}
        
        Please return a JSON array of objects, where each object contains:
        - "module": the exact module name from the input list
        - "relevance_score": a number from 1-10 (10 being most relevant)
        - "reason": a brief explanation (1-2 sentences) of why this module is relevant to {skill}
        
        Order the array from highest relevance_score to lowest relevance_score.
        
        Example format:
        [
          {{
            "module": "Module Name",
            "relevance_score": 9,
            "reason": "Brief explanation of relevance"
          }}
        ]
        """
        
        response_text = self._call_gemini_with_retry(prompt)
        try:
            ranked_modules = self._extract_json_from_response(response_text)
            if isinstance(ranked_modules, list):
                # Validate the structure
                valid_modules = []
                for module in ranked_modules:
                    if isinstance(module, dict) and "module" in module and "relevance_score" in module and "reason" in module:
                        valid_modules.append(module)
                    else:
                        logger.warning(f"Invalid module structure in ranking response: {module}")
                return valid_modules
            else:
                logger.warning(f"Gemini returned non-list for module ranking: {response_text}")
                # Fallback: return modules with default scores
                return [{"module": module, "relevance_score": 5, "reason": "Could not determine relevance"} for module in unique_modules]
        except Exception as e:
            logger.error(f"Failed to parse module ranking JSON from Gemini response: {e}. Response: {response_text}")
            # Fallback: return modules with default scores
            return [{"module": module, "relevance_score": 5, "reason": "Could not determine relevance"} for module in unique_modules]

    def process_skills_for_web_content(self, skills: List[str], websites_to_scrape: List[str], search_all_websites: bool = False, rank_modules: bool = True) -> Dict[str, Any]:
        """Processes a list of skills to gather web content from specified websites and formats for the new JSON output."""
        output_data = {"websites": []}
        all_collected_modules = []  # Collect all modules from all websites

        websites_to_process = websites_to_scrape if search_all_websites else websites_to_scrape[:1]
        for website_url in websites_to_process:
            website_name = website_url.replace("https://www.", "").replace("http://www.", "").split("/")[0].split(".")[0].capitalize()
            website_entry = {
                "website_name": website_name,
                "website_url": website_url,
                "topic": skills[0] if skills else "", # Assuming one skill for simplicity as per example
                "modules": [],
                "courses": []
            }

            # Search for courses within the domain
            query = f"course {skills[0]} site:{website_url}"
            search_response = self._perform_tavily_search(query, max_results=5) # Increased max_results for courses
            # Add delay between website searches
            time.sleep(2)

            website_modules = []
            for result in search_response.get("results", [])[:2]: # Limit to the first course
                course_title = result.get("title")
                course_url = result.get("url")
                if course_title and course_url:
                    # Extract modules for each course
                    modules = self._extract_modules_from_course_page(course_url, skills[0])
                    website_entry["courses"].append({
                        "title": course_title,
                        "url": course_url
                    })
                    website_modules.extend(modules) # Collect modules for this website
            
            # Add modules to the website entry
            website_entry["modules"] = website_modules
            # Add modules to the overall collection
            all_collected_modules.extend(website_modules)
            
            output_data["websites"].append(website_entry)

        # Add overall ranked modules section
        if rank_modules and all_collected_modules and skills:
            logger.info(f"Ranking {len(all_collected_modules)} total modules from all websites for skill: {skills[0]}")
            ranked_modules = self._rank_modules_by_relevance(all_collected_modules, skills[0])
            output_data["overall_ranked_modules"] = {
                "skill": skills[0],
                "total_modules_found": len(all_collected_modules),
                "unique_modules_ranked": len(ranked_modules),
                "ranked_modules": ranked_modules
            }
            logger.info(f"Successfully ranked {len(ranked_modules)} unique modules with technical relevance focus")

        return output_data

    def save_results(self, data: Dict[str, Any], filename: str = "web_scraped_output.json"):
        """Saves the processed data to a JSON file in the same directory as the script."""
        try:
            # Get the directory where the script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Create the full path for the output file
            output_path = os.path.join(script_dir, filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"ðŸ'¾ Web scraping results saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save web scraping results: {e}")

def run_scraper(skills: List[str], websites: List[str], search_all: bool = False, rank_modules: bool = True, output_filename: str = "website_modules_output.json"):
    TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

    if not TAVILY_API_KEY:
        TAVILY_API_KEY = "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" # Replace with your actual key or load from config
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not found in environment variables. Using the provided key directly.")
        GEMINI_API_KEY = "AIzaSyDzPNREAUb3Nh-n2jwDXLHThr7ECir9AUM"

    scraper = TavilyWebScraper(tavily_api_key=TAVILY_API_KEY, gemini_api_key=GEMINI_API_KEY)

    print(f"\nTesting TavilyWebScraper with skills: {skills} and websites: {websites}")
    print(f"Module ranking: {'Enabled' if rank_modules else 'Disabled'}")
    results = scraper.process_skills_for_web_content(skills, websites, search_all_websites=search_all, rank_modules=rank_modules)
    scraper.save_results(results, output_filename)
    print(f"Test completed. Check {output_filename} for results.")

if __name__ == "__main__":
    test_skills = ["Data Analyst"]
    test_websites = [
        "https://www.coursera.org",
        "https://www.edx.org",
        "https://www.udemy.com/"
    ]
    run_scraper(test_skills, test_websites, search_all=True, rank_modules=True)