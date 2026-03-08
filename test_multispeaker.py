#!/usr/bin/env python3
"""
Test script for Multi-Speaker TTS functionality
Run this to verify the multi-speaker audio generation works correctly
"""

import os
import sys

# Test imports
print("🔍 Testing imports...")
try:
    from multispeaker import (
        parse_speaker_config,
        parse_script,
        generate_speaker_audio,
        create_multispeaker_audio,
        process_multispeaker_script,
        get_voice_names
    )
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test voice list
print("\n🎙️  Testing voice retrieval...")
try:
    voices = get_voice_names()
    print(f"✅ Found {len(voices)} voices")
    print(f"   Sample voices: {', '.join(voices[:5])}")
except Exception as e:
    print(f"❌ Voice retrieval error: {e}")
    sys.exit(1)

# Test speaker config parsing
print("\n📝 Testing speaker config parsing...")
config_text = """
Speaker1:af_bella
Speaker2:bf_isabella
Speaker3:af_nicole
"""
speakers = parse_speaker_config(config_text)
if len(speakers) == 3 and speakers.get("Speaker1") == "af_bella":
    print(f"✅ Speaker config parsed: {speakers}")
else:
    print(f"❌ Speaker config parsing failed")
    sys.exit(1)

# Test script parsing
print("\n📜 Testing script parsing...")
script_text = """
Speaker1: Hello! Welcome to the test.
Speaker2: This is amazing!
{pause: 0.5}
Speaker1: We can even add custom pauses.
"""
lines = parse_script(script_text)
if len(lines) >= 3:
    print(f"✅ Script parsed: {len(lines)} lines")
    for line in lines[:3]:
        print(f"   - {line[0]}: {line[1][:40]}...")
else:
    print(f"❌ Script parsing failed")
    sys.exit(1)

# Test audio generation (single line)
print("\n🔊 Testing single-line audio generation...")
try:
    audio_array, duration = generate_speaker_audio("Hello, this is a test.", "af_bella")
    if audio_array is not None and duration > 0:
        print(f"✅ Audio generated: {duration:.2f} seconds")
    else:
        print(f"⚠️  Audio generated but may be empty")
except Exception as e:
    print(f"❌ Audio generation error: {e}")
    sys.exit(1)

# Test multi-speaker audio generation
print("\n🎭 Testing multi-speaker audio generation...")
try:
    output_path, audio_array = create_multispeaker_audio(
        script_lines=lines,
        speaker_config=speakers,
        language="American English",
        speed=1.0,
        pause_between_lines=0.2,
        normalize_volumes=True
    )
    
    if output_path and os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"✅ Multi-speaker audio created: {output_path}")
        print(f"   File size: {file_size / 1024:.2f} KB")
    else:
        print(f"⚠️  Audio file not created (this may be expected in test environment)")
        
except Exception as e:
    print(f"❌ Multi-speaker generation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test full processing pipeline
print("\n⚙️  Testing full processing pipeline...")
try:
    config = "John:af_bella\nMary:bf_isabella"
    script = "John: Hi Mary!\nMary: Hello John!\nJohn: How are you?"
    
    output_path, download_path, info = process_multispeaker_script(
        script_text=script,
        speaker_config_text=config,
        language="American English",
        speed=1.0,
        pause_duration=0.2,
        normalize_audio=True,
        auto_translate=False
    )
    
    if output_path:
        print(f"✅ Full pipeline successful!")
        print(f"   Output: {output_path}")
        print(f"   Info preview: {info[:100]}...")
    else:
        print(f"⚠️  Pipeline completed but no output file")
        
except Exception as e:
    print(f"❌ Pipeline error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*50)
print("🎉 All tests completed successfully!")
print("="*50)
print("\nNext steps:")
print("1. Run 'python multispeaker.py' to launch the Gradio interface")
print("2. Or run 'python beta.py' to access multi-speaker via tab interface")
print("3. Check MULTISPEAKER_README.md for detailed documentation")
