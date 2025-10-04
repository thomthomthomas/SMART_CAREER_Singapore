"""
!/usr/bin/env python3

Test script to verify YouTube Skills Scraper setup
Run this before using the main scraper to identify issues
"""

import json
import sys
import requests
import importlib
from pathlib import Path

def test_dependencies():
    """Test if all required packages are installed"""
    print("🔍 Testing Dependencies...")
    
    required_packages = {
        'youtube_transcript_api': 'youtube-transcript-api',
        'pytube': 'pytube', 
        'google.generativeai': 'google-generativeai',
        'gtts': 'gTTS',
        'pydub': 'pydub',
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
        'aiohttp': 'aiohttp'
    }
    
    missing_packages = []
    
    for module_name, pip_name in required_packages.items():
        try:
            importlib.import_module(module_name)
            print(f"   ✅ {pip_name}")
        except ImportError:
            print(f"   ❌ {pip_name}")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {missing_packages}")
        print("💡 Install with: pip install " + " ".join(missing_packages))
        return False
    else:
        print("✅ All dependencies installed!")
        return True

def test_config():
    """Test configuration file"""
    print("\n🔍 Testing Configuration...")
    
    config_file = Path("config.json")
    if not config_file.exists():
        print("❌ config.json not found!")
        print("💡 Run: python setup.py")
        return False, None
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        print("   ✅ config.json loaded successfully")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config.json: {e}")
        return False, None
    
    # Check required sections
    required_sections = ['api_keys', 'settings', 'directories']
    for section in required_sections:
        if section in config:
            print(f"   ✅ {section} section found")
        else:
            print(f"   ❌ {section} section missing")
            return False, None
    
    return True, config

def test_api_keys(config):
    """Test API key format and basic connectivity"""
    print("\n🔍 Testing API Keys...")
    
    api_keys = config.get('api_keys', {})
    gemini_key = api_keys.get('gemini_api_key', '')
    youtube_key = api_keys.get('youtube_api_key', '')
    
    # Check if keys are placeholder values
    placeholder_values = [
        "YOUR_GEMINI_API_KEY_HERE", 
        "YOUR_YOUTUBE_DATA_API_V3_KEY_HERE",
        "your-gemini-api-key-here",
        "your-youtube-api-key-here",
        ""
    ]
    
    # Test Gemini key format
    if gemini_key in placeholder_values:
        print("   ❌ Gemini API key is placeholder")
        print("   💡 Get key from: https://aistudio.google.com/app/apikey")
        return False
    elif gemini_key.startswith('AIzaSy') and len(gemini_key) >= 35:
        print("   ✅ Gemini API key format looks valid")
    else:
        print("   ❌ Gemini API key format appears invalid")
        return False
    
    # Test YouTube key format  
    if youtube_key in placeholder_values:
        print("   ❌ YouTube API key is placeholder")
        print("   💡 Get key from: https://console.cloud.google.com/")
        return False
    elif youtube_key.startswith('AIzaSy') and len(youtube_key) >= 35:
        print("   ✅ YouTube API key format looks valid")
    else:
        print("   ❌ YouTube API key format appears invalid") 
        return False
    
    return True

def test_youtube_api(youtube_key):
    """Test YouTube API connectivity"""
    print("\n🔍 Testing YouTube API...")
    
    test_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': 'python tutorial',
        'type': 'video',
        'maxResults': 1,
        'key': youtube_key
    }
    
    try:
        response = requests.get(test_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                print("   ✅ YouTube API working correctly")
                video_title = data['items'][0]['snippet']['title']
                print(f"   📹 Test video found: {video_title[:50]}...")
                return True
            else:
                print("   ⚠️  YouTube API responds but no videos found")
                return True
        elif response.status_code == 400:
            print("   ❌ Bad request - check API key format")
        elif response.status_code == 403:
            print("   ❌ Forbidden - check API key permissions and quota")
            error_data = response.json()
            if 'error' in error_data:
                error_msg = error_data['error'].get('message', 'Unknown error')
                print(f"   💡 Error details: {error_msg}")
        elif response.status_code == 429:
            print("   ❌ Rate limit exceeded")
        else:
            print(f"   ❌ YouTube API error: HTTP {response.status_code}")
            
        return False
        
    except requests.exceptions.Timeout:
        print("   ❌ Request timeout - check internet connection")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network error: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
    
    return False

def test_gemini_api(gemini_key):
    """Test Gemini API connectivity"""
    print("\n🔍 Testing Gemini API...")
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Simple test with low token limit
        response = model.generate_content(
            "Say hello",
            generation_config=genai.types.GenerationConfig(max_output_tokens=5)
        )
        
        if response.text:
            print("   ✅ Gemini API working correctly")
            print(f"   💬 Test response: {response.text.strip()}")
            return True
        else:
            print("   ❌ Gemini API responded but no text generated")
            return False
            
    except Exception as e:
        error_msg = str(e).lower()
        if 'api key' in error_msg or 'authentication' in error_msg:
            print("   ❌ Invalid API key")
        elif 'quota' in error_msg or 'rate limit' in error_msg:
            print("   ❌ API quota exceeded or rate limited")
        elif 'network' in error_msg or 'connection' in error_msg:
            print("   ❌ Network connection error")
        else:
            print(f"   ❌ Gemini API error: {e}")
        
        return False

def test_directories(config):
    """Test directory creation"""
    print("\n🔍 Testing Directories...")
    
    directories = config.get('directories', {})
    audio_dir = directories.get('audio_output', './audio_files')
    json_dir = directories.get('json_output', './json_outputs')
    
    try:
        Path(audio_dir).mkdir(exist_ok=True)
        Path(json_dir).mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        print(f"   ✅ Created {audio_dir}")
        print(f"   ✅ Created {json_dir}")
        print("   ✅ Created logs")
        
        return True
    except Exception as e:
        print(f"   ❌ Error creating directories: {e}")
        return False

def test_input_file():
    """Test input file"""
    print("\n🔍 Testing Input File...")
    
    input_file = Path("input_skills.json")
    if not input_file.exists():
        print("   ⚠️  input_skills.json not found (will use defaults)")
        return True
    
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        role = data.get('role', '')
        skills = data.get('skills', [])
        
        if not role:
            print("   ❌ No role specified in input file")
            return False
        
        if not skills or len(skills) == 0:
            print("   ❌ No skills specified in input file")
            return False
        
        print(f"   ✅ Role: {role}")
        print(f"   ✅ Skills: {len(skills)} found")
        
        # Show first few skills
        for i, skill in enumerate(skills[:3], 1):
            print(f"      {i}. {skill}")
        if len(skills) > 3:
            print(f"      ... and {len(skills) - 3} more")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON in input_skills.json: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error reading input file: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 YouTube Skills Scraper - Setup Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test 1: Dependencies
    if not test_dependencies():
        all_tests_passed = False
    
    # Test 2: Configuration
    config_ok, config = test_config()
    if not config_ok:
        all_tests_passed = False
        print("\n❌ Cannot continue without valid config.json")
        sys.exit(1)
    
    # Test 3: API Key formats
    if not test_api_keys(config):
        all_tests_passed = False
        print("\n❌ Cannot continue without valid API keys")
        sys.exit(1)
    
    # Test 4: YouTube API
    youtube_key = config['api_keys']['youtube_api_key']
    if not test_youtube_api(youtube_key):
        all_tests_passed = False
    
    # Test 5: Gemini API
    gemini_key = config['api_keys']['gemini_api_key']
    if not test_gemini_api(gemini_key):
        all_tests_passed = False
    
    # Test 6: Directories
    if not test_directories(config):
        all_tests_passed = False
    
    # Test 7: Input file
    if not test_input_file():
        all_tests_passed = False
    
    # Final results
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your setup is ready to use")
        print("\n🚀 Next steps:")
        print("   1. Run: python main.py")
        print("   2. Or for batch processing: python batch_processor.py")
        print("\n💡 Tips:")
        print("   • Start with 1-2 skills to test API quotas")
        print("   • Monitor your API usage in respective consoles")
        print("   • Check logs/scraper.log for detailed progress")
    else:
        print("❌ SOME TESTS FAILED!")
        print("💡 Fix the issues above before running the scraper")
        print("\n🔧 Common fixes:")
        print("   • Install missing packages: pip install -r requirements.txt")
        print("   • Update API keys in config.json")
        print("   • Check API quotas and permissions")
        print("   • Verify internet connection")
        
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)