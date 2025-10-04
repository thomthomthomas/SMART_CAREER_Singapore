import json
from pathlib import Path
import os
from typing import Dict, List

def find_json_files(directory: str, filename: str) -> Dict[str, Path]:
    """
    Recursively searches a directory for all files with a given name
    and returns them in a dictionary mapping filename to full path.

    Args:
        directory (str): The path to the main folder to start the search.
        filename (str): The name of the file to find (e.g., 'config.json').

    Returns:
        Dict[str, Path]: A dictionary where keys are the filenames and
                         values are the full Path objects for all found files.

    Raises:
        FileNotFoundError: If no files with the given name are found.
    """
    # Create a Path object for the starting directory
    base_path = Path(directory)
    
    # Use rglob() to recursively search for all files with the given name
    file_generator = base_path.rglob(f"**/{filename}")
    
    # Create a dictionary mapping the filename to its full path
    found_files = {file.name: file for file in file_generator}
    
    if not found_files:
        raise FileNotFoundError(f"The file '{filename}' was not found in '{directory}' or any of its subdirectories.")
        
    return found_files

def get_json_file_paths(filename: str) -> Dict[str, Path]:
    """
    Finds all JSON file paths with a specific name from the current script's
    directory and its subdirectories, returning a dictionary of paths.

    Args:
        filename (str): The name of the JSON file to find.

    Returns:
        Dict[str, Path]: A dictionary where keys are filenames and values
                         are the full Path objects for the found files.
    """
    current_script_directory = os.path.abspath(os.path.dirname(__file__))
    
    try:
        return find_json_files(current_script_directory, filename)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return {}

def load_json_data(file_path: Path) -> dict:
    """
    Load JSON data from a file.
    
    Args:
        file_path (Path): Path to the JSON file.
        
    Returns:
        dict: The loaded JSON data.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON from {file_path}: {e}")
        return {}

def save_json_data(file_path: Path, data: dict):
    """
    Save JSON data to a file.
    
    Args:
        file_path (Path): Path to save the JSON file.
        data (dict): The data to save.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved updated data to: {file_path}")
    except Exception as e:
        print(f"Error saving JSON to {file_path}: {e}")

def extract_top_skills(website_modules_data: dict, top_n: int = 5) -> List[str]:
    """
    Extract top N skills from the website modules data.
    
    Args:
        website_modules_data (dict): The loaded website modules JSON data.
        top_n (int): Number of top skills to extract.
        
    Returns:
        List[str]: List of top N skill module names.
    """
    try:
        ranked_modules = website_modules_data.get('overall_ranked_modules', {}).get('ranked_modules', [])
        
        if not ranked_modules:
            print("No ranked modules found in the data.")
            return []
        
        # Extract top N module names
        top_skills = [module['module'] for module in ranked_modules[:top_n]]
        return top_skills
        
    except Exception as e:
        print(f"Error extracting top skills: {e}")
        return []

def update_input_skills(input_skills_path: Path, top_skills: List[str], role: str = "Data Analyst"):
    """
    Update the input skills JSON file with new top skills.
    
    Args:
        input_skills_path (Path): Path to the input skills JSON file.
        top_skills (List[str]): List of top skills to update.
        role (str): The role to set in the JSON file.
    """
    try:
        # Load existing data to preserve role if it exists
        existing_data = load_json_data(input_skills_path)
        current_role = existing_data.get('role', role)
        
        # Create new data structure
        new_data = {
            "role": current_role,
            "skills": top_skills
        }
        
        # Save the updated data
        save_json_data(input_skills_path, new_data)
        
        print(f"Updated input_skills.json with top {len(top_skills)} skills:")
        for i, skill in enumerate(top_skills, 1):
            print(f"  {i}. {skill}")
            
    except Exception as e:
        print(f"Error updating input skills: {e}")

def load_json_from_main_folder(main_folder: str, json_filename: str):
    """
    Finds all JSON file paths with a specific name from a main folder and prints them.

    Args:
        main_folder (str): The path to the top-level folder.
        json_filename (str): The name of the JSON file to find.
    """
    try:
        # Step 1: Find all file paths and store them in a dictionary
        json_paths_dict = find_json_files(main_folder, json_filename)
        
        print(f"Found {len(json_paths_dict)} files named '{json_filename}':")
        
        # Step 2: Iterate through the dictionary and print each file path
        for filename, json_path in json_paths_dict.items():
            print(f"\n--- Found file '{filename}' at path: {json_path} ---")
            
    except FileNotFoundError as e:
        print(f"Error: {e}")

def process_json_file(filename: str, directory: str):
    """
    Searches for a JSON file by name and prints its path(s) if found.
    """
    print(f"Searching for '{filename}' in '{directory}'...")
    try:
        found_files = find_json_files(directory, filename)
        if found_files:
            print(f"Found {len(found_files)} '{filename}' file(s):")
            for file_name, path in found_files.items():
                print(f"  - {path}")
        return found_files
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return {}

def update_skills_from_modules(directory: str = None):
    """
    Main function to find both JSON files, extract top 5 skills from website_modules,
    and update the input_skills.json file.
    
    Args:
        directory (str): Directory to search in. If None, uses current script directory.
    """
    if directory is None:
        directory = os.path.abspath(os.path.dirname(__file__))
    
    print("=== Starting Skills Update Process ===\n")
    
    # Step 1: Find both files
    print("Step 1: Finding JSON files...")
    website_modules_files = process_json_file("website_modules_output.json", directory)
    input_skills_files = process_json_file("input_skills.json", directory)
    
    if not website_modules_files or not input_skills_files:
        print("Error: Could not find both required files.")
        return
    
    # Get the first found file of each type
    website_modules_path = list(website_modules_files.values())[0]
    input_skills_path = list(input_skills_files.values())[0]
    
    print(f"\nUsing files:")
    print(f"  Website modules: {website_modules_path}")
    print(f"  Input skills: {input_skills_path}")
    
    # Step 2: Load website modules data
    print("\nStep 2: Loading website modules data...")
    website_data = load_json_data(website_modules_path)
    
    if not website_data:
        print("Error: Could not load website modules data.")
        return
    
    # Step 3: Extract top 5 skills
    print("\nStep 3: Extracting top 5 skills...")
    top_5_skills = extract_top_skills(website_data, 5)
    
    if not top_5_skills:
        print("Error: Could not extract top skills.")
        return
    
    print(f"Extracted top 5 skills: {top_5_skills}")
    
    # Step 4: Update input skills file
    print("\nStep 4: Updating input skills file...")
    update_input_skills(input_skills_path, top_5_skills)
    
    print("\n=== Skills Update Process Complete ===")

# Example Usage:
if __name__ == "__main__":
    current_working_directory = os.getcwd()  # Use current working directory
    
    # Original functionality
    print("=== Original File Search ===")
    process_json_file("input_skills.json", current_working_directory)
    print("-" * 20)
    process_json_file("website_modules_output.json", current_working_directory)
    
    print("\n" + "=" * 50 + "\n")
    
    # New functionality - update skills from modules
    update_skills_from_modules()