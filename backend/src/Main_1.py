import os
import json
from TavilyScp.tavily_web_s import run_scraper
from youtube_agent.main import mainYTagent
from json_finder.jsonF import process_json_file,update_skills_from_modules,find_json_files
#from youtube_agent import youtube

test_skills = input("Input the skill or skip to default to Data Analyst for testing type: t/T")

if test_skills == "T" or "t":
    test_skills = ["Data Analyst"]
test_websites = [
    "https://www.coursera.org",
    "https://www.edx.org",
    "https://www.udemy.com/"
]
#run the scraper to find related skills/modules
run_scraper(test_skills, test_websites, search_all=True, rank_modules=True)

# Get the current working directory and pass it explicitly  
main_directory = os.getcwd()

# Call with explicit directory parameter
update_skills_from_modules(main_directory)

# Call youtube agent to run and work with the 5 skills
mainYTagent()

#gets path to result json file
main_directory = os.getcwd()
print("Result is: " + str(find_json_files(main_directory, "Data_Analyst_comprehensive_analysis.json")))