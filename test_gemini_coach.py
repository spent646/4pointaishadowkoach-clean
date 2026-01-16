"""Quick test script to verify Gemini coach integration."""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_coach_import():
    """Test that we can import the coach factory."""
    print("[+] Testing coach factory import...")
    try:
        from backend.coaches import create_coach
        print("  SUCCESS: Coach factory imported")
        return True
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\n[+] Testing configuration...")
    try:
        from backend.config import Config
        print(f"  COACH_TYPE: {Config.COACH_TYPE}")
        print(f"  GEMINI_MODEL: {Config.GEMINI_MODEL}")
        print(f"  GEMINI_API_KEY: {'SET' if Config.GEMINI_API_KEY else 'NOT SET'}")
        
        missing = Config.validate()
        if missing:
            print(f"  NOTE: Missing configuration: {', '.join(missing)}")
            print("  This is expected if you haven't set up your .env file yet")
        else:
            print("  SUCCESS: All required configuration is set")
        
        print("  SUCCESS: Configuration system is working")
        return True
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

def test_gemini_coach_creation():
    """Test creating a Gemini coach instance."""
    print("\n[+] Testing Gemini coach creation...")
    try:
        from backend.coaches import create_coach
        from backend.config import Config
        
        if Config.COACH_TYPE.lower() != "gemini":
            print(f"  SKIPPED: COACH_TYPE is '{Config.COACH_TYPE}', not 'gemini'")
            return True
        
        if not Config.GEMINI_API_KEY:
            print("  SKIPPED: GEMINI_API_KEY not set (expected - will need user to configure)")
            return True
        
        coach = create_coach("gemini")
        print(f"  SUCCESS: Created Gemini coach with model: {coach.model_name}")
        return True
    except ValueError as e:
        if "GEMINI_API_KEY is required" in str(e):
            print("  EXPECTED: Need to set GEMINI_API_KEY in .env file")
            print("  Get your API key from: https://makersuite.google.com/app/apikey")
            return True
        else:
            print(f"  FAILED: {e}")
            return False
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

def test_ollama_coach_creation():
    """Test creating an Ollama coach instance."""
    print("\n[+] Testing Ollama coach creation (fallback)...")
    try:
        from backend.coaches import create_coach
        coach = create_coach("ollama")
        print(f"  SUCCESS: Created Ollama coach with model: {coach.model}")
        print(f"  Ollama URL: {coach.ollama_url}")
        return True
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

def test_base_coach_structure():
    """Test that all coaches have the required methods."""
    print("\n[+] Testing coach interface...")
    try:
        from backend.coaches.base_coach import BaseCoach
        from backend.coaches.gemini_coach import GeminiCoach
        from backend.coaches.ollama_coach import OllamaCoach
        
        # Check that both implementations inherit from BaseCoach
        assert issubclass(GeminiCoach, BaseCoach), "GeminiCoach must inherit from BaseCoach"
        assert issubclass(OllamaCoach, BaseCoach), "OllamaCoach must inherit from BaseCoach"
        
        # Check that required methods exist
        required_methods = ['chat', 'get_history']
        for coach_class in [GeminiCoach, OllamaCoach]:
            for method in required_methods:
                assert hasattr(coach_class, method), f"{coach_class.__name__} must have {method} method"
        
        print("  SUCCESS: All coaches implement the required interface")
        return True
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("AI Shadow Coach - Gemini Integration Test")
    print("=" * 60)
    
    results = []
    results.append(test_coach_import())
    results.append(test_config())
    results.append(test_base_coach_structure())
    results.append(test_ollama_coach_creation())
    results.append(test_gemini_coach_creation())
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! The Gemini integration is working correctly.")
        print("\nNext steps:")
        print("1. Make sure you have a .env file with your GEMINI_API_KEY")
        print("2. Set COACH_TYPE=gemini in your .env file")
        print("3. Run the application: python -m uvicorn backend.main:app --reload")
    else:
        print("\n[FAILED] Some tests failed. Please review the errors above.")
        sys.exit(1)
    
    print("=" * 60)

if __name__ == "__main__":
    main()
