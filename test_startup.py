"""Test that the application can start up successfully."""

import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("Testing AI Shadow Coach Startup")
print("=" * 60)

# Test 1: Config loads correctly
print("\n[1/4] Testing configuration...")
try:
    from backend.config import Config
    print(f"  [OK] COACH_TYPE: {Config.COACH_TYPE}")
    print(f"  [OK] GEMINI_API_KEY: {'SET' if Config.GEMINI_API_KEY else 'NOT SET'}")
    print(f"  [OK] GEMINI_MODEL: {Config.GEMINI_MODEL}")
except Exception as e:
    print(f"  [ERROR] {e}")
    sys.exit(1)

# Test 2: Coach can be created
print("\n[2/4] Testing coach creation...")
try:
    from backend.coaches import create_coach
    coach = create_coach(Config.COACH_TYPE)
    print(f"  [OK] Created {Config.COACH_TYPE} coach successfully")
except Exception as e:
    print(f"  [ERROR] {e}")
    sys.exit(1)

# Test 3: FastAPI app can be imported
print("\n[3/4] Testing FastAPI app import...")
try:
    from backend.main import app
    print(f"  [OK] FastAPI app imported successfully")
except Exception as e:
    print(f"  [ERROR] {e}")
    sys.exit(1)

# Test 4: Quick coach interaction test
print("\n[4/4] Testing coach interaction...")
try:
    response = coach.chat("Hello, can you ask me a question?")
    print(f"  [OK] Coach responded (length: {len(response)} chars)")
    print(f"\n  Sample response:")
    print(f"  {response[:200]}..." if len(response) > 200 else f"  {response}")
except Exception as e:
    print(f"  [ERROR] {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] ALL TESTS PASSED!")
print("\nYour application is ready to run:")
print("  python -m uvicorn backend.main:app --reload")
print("\nOr use the launch script:")
print("  .\\launch.ps1")
print("=" * 60)
