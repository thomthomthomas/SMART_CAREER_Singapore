__init__.py is to allow other files to call the webscraper

To run it it requires a list of websites and a subject topic use the following function:
run_scraper_tool(topic: str, websites: List[str])

Output is json file with site name, course name (topic), modules (of that course), courses from the site for that topic, and related urls
Toggle True false for no of sites to be tested
run_scraper(test_skills, test_websites, search_all=False)

The following line is commented out
# scraper.save_results(results, "enhanced_web_scraped_output.json") #generates the comprehensive file

change this to increase websites searched for skills
for result in search_response.get("results", [])[:1]: # Limit to the first course