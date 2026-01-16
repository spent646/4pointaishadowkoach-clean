"""Test placeholder transcription without Deepgram."""

import sys
import time

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("Testing Placeholder Transcription")
print("=" * 60)

# Test 1: Import transcriber
print("\n[1/3] Importing transcriber...")
try:
    from backend.transcriber import DeepgramTranscriber
    print("  [OK] Transcriber imported")
except Exception as e:
    print(f"  [ERROR] {e}")
    sys.exit(1)

# Test 2: Create transcriber instance (should use placeholder mode)
print("\n[2/3] Creating transcriber (placeholder mode)...")
try:
    transcriber = DeepgramTranscriber()
    if transcriber.deepgram_available:
        print("  [WARNING] Deepgram SDK is installed - this test is for placeholder mode")
        print("  Continuing anyway...")
    else:
        print("  [OK] Using placeholder mode (Deepgram not available)")
except Exception as e:
    print(f"  [ERROR] {e}")
    sys.exit(1)

# Test 3: Simulate audio stream with transcription callback
print("\n[3/3] Testing placeholder transcription...")
print("  Simulating audio chunks and waiting for transcripts...\n")

transcripts_received = []

def on_transcript(text: str, is_final: bool):
    """Callback for transcription events."""
    transcripts_received.append((text, is_final))
    print(f"  [TRANSCRIPT] {text} (final={is_final})")

try:
    # Start stream A
    transcriber.start_stream("A", on_transcript)
    
    # Simulate sending 100 audio chunks (should trigger ~2 test transcripts)
    dummy_audio = b'\x00' * 1024  # 1KB of silence
    
    for i in range(100):
        transcriber.send_audio("A", dummy_audio)
        time.sleep(0.01)  # Small delay to simulate real-time
        
        if (i + 1) % 25 == 0:
            print(f"  Sent {i + 1}/100 audio chunks...")
    
    # Wait a moment for any final callbacks
    time.sleep(0.5)
    
    # Check results
    print(f"\n  Total transcripts received: {len(transcripts_received)}")
    
    if len(transcripts_received) > 0:
        print("\n  [SUCCESS] Placeholder transcription is working!")
        print("\n  Sample transcripts:")
        for text, is_final in transcripts_received[:3]:
            print(f"    - {text}")
    else:
        print("\n  [WARNING] No transcripts received")
        print("  The placeholder might need more audio chunks to trigger")
    
    # Cleanup
    transcriber.stop_stream("A")
    
except Exception as e:
    print(f"\n  [ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("[DONE] Test complete")
print("\nNow restart your application and you should see")
print("placeholder transcripts appearing in the UI!")
print("=" * 60)
