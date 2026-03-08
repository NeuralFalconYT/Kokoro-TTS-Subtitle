"""
Multi-Speaker TTS Interface for Kokoro TTS
Allows users to create dialogues and multi-speaker audio with easy speaker assignment
"""

import os
import re
import uuid
import shutil
import wave
import numpy as np
from kokoro import KPipeline
from huggingface_hub import list_repo_files
from pydub import AudioSegment
import gradio as gr
from deep_translator import GoogleTranslator

# ==================== Global Variables ====================
last_used_language = "a"
pipeline = KPipeline(lang_code=last_used_language)

# Language mapping
language_map = {
    "American English": "a",
    "British English": "b",
    "Hindi": "h",
    "Spanish": "e",
    "French": "f",
    "Italian": "i",
    "Brazilian Portuguese": "p",
    "Japanese": "j",
    "Mandarin Chinese": "z"
}

language_map_local = {
    "American English": "en",
    "British English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "Italian": "it",
    "Brazilian Portuguese": "pt",
    "Japanese": "ja",
    "Mandarin Chinese": "zh-CN"
}

# ==================== Utility Functions ====================

def get_voice_names(repo_id="hexgrad/Kokoro-82M"):
    """Fetches voice names from Hugging Face repository."""
    return sorted([
        os.path.splitext(file.replace("voices/", ""))[0] 
        for file in list_repo_files(repo_id) 
        if file.startswith("voices/")
    ])

def create_output_dir():
    """Creates output directory for multi-speaker audio files."""
    output_dir = "./multispeaker_output"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def clean_text(text):
    """Clean text for TTS generation."""
    replacements = {"–": " ", "-": " ", "**": " ", "*": " ", "#": " "}
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove emojis
    emoji_pattern = re.compile(
        r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|'
        r'[\U0001F700-\U0001F77F]|[\U0001F780-\U0001F7FF]|[\U0001F800-\U0001F8FF]|'
        r'[\U0001F900-\U0001F9FF]|[\U0001FA00-\U0001FA6F]|[\U0001FA70-\U0001FAFF]|'
        r'[\U00002702-\U000027B0]|[\U0001F1E0-\U0001F1FF]', flags=re.UNICODE
    )
    text = emoji_pattern.sub(r'', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_unique_filename(prefix="multispeaker"):
    """Generate a unique filename for output audio."""
    output_dir = create_output_dir()
    random_string = uuid.uuid4().hex[:8]
    return os.path.join(output_dir, f"{prefix}_{random_string}.wav")

# ==================== Speaker Configuration ====================

def parse_speaker_config(config_text):
    """
    Parse speaker configuration from text format.
    Expected format: SpeakerName:voice_name
    Example:
    John:af_bella
    Mary:bf_isabella
    """
    speakers = {}
    for line in config_text.strip().split('\n'):
        line = line.strip()
        if not line or ':' not in line:
            continue
        parts = line.split(':', 1)
        if len(parts) == 2:
            speaker_name = parts[0].strip()
            voice_name = parts[1].strip()
            speakers[speaker_name] = voice_name
    return speakers

def format_speaker_config(speakers_dict):
    """Format speaker dictionary to text for display."""
    return '\n'.join([f"{name}:{voice}" for name, voice in speakers_dict.items()])

# ==================== Script Parsing ====================

def parse_script(script_text, default_speaker="Speaker1"):
    """
    Parse multi-speaker script.
    Supports formats:
    - SpeakerName: Dialogue text
    - [SpeakerName] Dialogue text
    - SpeakerName | Dialogue text
    - SpeakerName(voice_name): Dialogue text (inline voice override)
    - {pause: 1.5} for custom pause duration
    
    Returns list of tuples: (speaker, text, language_override, voice_override, pause_override)
    """
    lines = []
    current_speaker = default_speaker
    current_pause = None
    
    for line in script_text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Check for custom pause directive
        pause_match = re.match(r'^\{pause:\s*([\d.]+)\}', line)
        if pause_match:
            current_pause = float(pause_match.group(1))
            lines.append(("_PAUSE_", f"{{pause: {current_pause}}}", None, None, current_pause))
            continue
        
        # Format 1: SpeakerName(voice_override): Dialogue
        match = re.match(r'^([A-Za-z0-9_]+)\s*\(([A-Za-z0-9_]+)\)\s*:\s*(.+)$', line)
        if match:
            current_speaker = match.group(1)
            voice_override = match.group(2)
            text = match.group(3).strip()
            lines.append((current_speaker, text, None, voice_override, current_pause))
            current_pause = None
            continue
        
        # Format 2: SpeakerName: Dialogue
        match = re.match(r'^([A-Za-z0-9_]+)\s*:\s*(.+)$', line)
        if match:
            current_speaker = match.group(1)
            text = match.group(2).strip()
            lines.append((current_speaker, text, None, None, current_pause))
            current_pause = None
            continue
        
        # Format 3: [SpeakerName] Dialogue
        match = re.match(r'^\[([A-Za-z0-9_]+)\]\s*(.+)$', line)
        if match:
            current_speaker = match.group(1)
            text = match.group(2).strip()
            lines.append((current_speaker, text, None, None, current_pause))
            current_pause = None
            continue
        
        # Format 4: SpeakerName | Dialogue
        match = re.match(r'^([A-Za-z0-9_]+)\s*\|\s*(.+)$', line)
        if match:
            current_speaker = match.group(1)
            text = match.group(2).strip()
            lines.append((current_speaker, text, None, None, current_pause))
            current_pause = None
            continue
        
        # Format 5: Continuation of previous speaker's dialogue
        lines.append((current_speaker, line, None, None, current_pause))
        current_pause = None
    
    return lines

# ==================== Audio Generation ====================

def generate_speaker_audio(text, voice, language="American English", speed=1.0):
    """Generate audio for a single speaker's line."""
    global pipeline, last_used_language
    
    text = clean_text(text)
    lang_code = language_map.get(language, "a")
    
    # Update pipeline if language changed
    if lang_code != last_used_language:
        try:
            pipeline = KPipeline(lang_code=lang_code)
            last_used_language = lang_code
        except Exception:
            gr.Warning(f"Fallback to English for {language}")
            pipeline = KPipeline(lang_code="a")
            last_used_language = "a"
    
    # Generate audio
    try:
        generator = pipeline(text, voice=voice, speed=speed, split_pattern=r'\n+')
        audio_chunks = []
        
        for result in generator:
            audio = result.audio
            audio_np = audio.numpy()
            audio_int16 = (audio_np * 32767).astype(np.int16)
            audio_chunks.append(audio_int16.tobytes())
        
        if not audio_chunks:
            return None, 0
        
        # Combine all chunks
        combined_audio = b''.join(audio_chunks)
        audio_array = np.frombuffer(combined_audio, dtype=np.int16)
        
        # Calculate duration
        duration_sec = len(audio_array) / 24000
        
        return audio_array, duration_sec
    
    except Exception as e:
        gr.Error(f"Audio generation failed: {str(e)}")
        return None, 0

def create_multispeaker_audio(
    script_lines,
    speaker_config,
    language="American English",
    speed=1.0,
    pause_between_lines=0.2,
    normalize_volumes=True
):
    """
    Create multi-speaker audio from script.

    Args:
        script_lines: List of (speaker, text, lang_override, voice_override, pause_override) tuples
        speaker_config: Dict mapping speaker names to voice names
        language: Default language
        speed: Default speed
        pause_between_lines: Pause in seconds between lines
        normalize_volumes: Whether to normalize volumes across speakers

    Returns:
        Tuple of (output_path, combined_audio_array)
    """
    output_path = generate_unique_filename()

    # Generate audio for each line
    all_audio = []
    speaker_volumes = {}  # Track volumes for normalization

    for line_data in script_lines:
        # Handle both old format (3-tuple) and new format (5-tuple)
        if len(line_data) == 3:
            speaker, text, _ = line_data
            voice_override = None
            pause_override = None
        else:
            speaker, text, _, voice_override, pause_override = line_data
        
        # Skip pause directives (handled separately)
        if speaker == "_PAUSE_":
            continue
        
        voice = voice_override or speaker_config.get(speaker)
        if not voice:
            gr.Warning(f"No voice assigned for speaker '{speaker}', skipping...")
            continue

        audio_array, duration = generate_speaker_audio(text, voice, language, speed)

        if audio_array is not None and len(audio_array) > 0:
            # Track volume for normalization
            if normalize_volumes:
                rms = np.sqrt(np.mean(audio_array.astype(np.float32)**2))
                speaker_volumes[speaker] = speaker_volumes.get(speaker, []) + [rms]

            all_audio.append((speaker, audio_array, pause_override))

    # Normalize volumes if requested
    if normalize_volumes and speaker_volumes:
        # Calculate average volume per speaker
        avg_volumes = {spk: np.mean(vols) for spk, vols in speaker_volumes.items()}
        global_avg = np.mean(list(avg_volumes.values()))

        # Normalize each speaker's audio
        normalized_audio = []
        for speaker, audio_array, pause_override in all_audio:
            if avg_volumes.get(speaker, 0) > 0:
                scale_factor = global_avg / avg_volumes[speaker]
                # Limit scaling to prevent clipping
                scale_factor = min(scale_factor, 2.0)
                audio_normalized = (audio_array.astype(np.float32) * scale_factor).astype(np.int16)
                normalized_audio.append((speaker, audio_normalized, pause_override))
            else:
                normalized_audio.append((speaker, audio_array, pause_override))
        all_audio = normalized_audio

    # Combine all audio with pauses
    combined = []
    for i, (speaker, audio_array, pause_override) in enumerate(all_audio):
        combined.append(audio_array)

        # Determine pause duration (override takes precedence)
        if pause_override is not None:
            pause_samples = int(24000 * pause_override)
        elif i < len(all_audio) - 1:  # Don't add pause after last line
            pause_samples = int(24000 * pause_between_lines)
        else:
            pause_samples = 0

        if pause_samples > 0:
            pause_audio = np.zeros(pause_samples, dtype=np.int16)
            combined.append(pause_audio)

    if not combined:
        gr.Error("No audio was generated. Check your script and speaker configuration.")
        return None, None

    # Concatenate all audio
    final_audio = np.concatenate(combined)

    # Save to WAV file
    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(24000)
        wav_file.writeframes(final_audio.tobytes())

    return output_path, final_audio

# ==================== Main Processing Function ====================

def process_multispeaker_script(
    script_text,
    speaker_config_text,
    language="American English",
    speed=1.0,
    pause_duration=0.2,
    normalize_audio=True,
    auto_translate=False
):
    """
    Main function to process multi-speaker script and generate audio.
    """
    # Parse inputs
    speaker_config = parse_speaker_config(speaker_config_text)
    
    if not speaker_config:
        gr.Error("Please define at least one speaker with a voice assignment.")
        return None, None, "No speakers defined"
    
    script_lines = parse_script(script_text)
    
    if not script_lines:
        gr.Error("Please enter script text.")
        return None, None, "No script text"
    
    # Translate if requested
    if auto_translate:
        translated_lines = []
        for speaker, text, lang_override in script_lines:
            try:
                lang_code = language_map_local.get(language, "en")
                translated = GoogleTranslator(target=lang_code).translate(text)
                translated_lines.append((speaker, translated, lang_override))
            except Exception:
                translated_lines.append((speaker, text, lang_override))
        script_lines = translated_lines
    
    # Generate audio
    output_path, audio_array = create_multispeaker_audio(
        script_lines=script_lines,
        speaker_config=speaker_config,
        language=language,
        speed=speed,
        pause_between_lines=pause_duration,
        normalize_volumes=normalize_audio
    )
    
    # Generate info text
    info_lines = []
    for line_data in script_lines:
        if len(line_data) == 3:
            speaker, text, _ = line_data
            voice_override = None
            pause_override = None
        else:
            speaker, text, _, voice_override, pause_override = line_data
        
        if speaker == "_PAUSE_":
            info_lines.append(f"⏸️ **Custom Pause:** {pause_override}s")
            continue
            
        voice = voice_override or speaker_config.get(speaker, "Not assigned")
        voice_indicator = f" ({voice_override})" if voice_override else ""
        pause_indicator = f" [⏸️ {pause_override}s]" if pause_override else ""
        info_lines.append(f"**{speaker}**{voice_indicator}: {text[:60]}...{pause_indicator}")
    
    info_text = "### 📋 Generated Lines:\n" + "\n".join(info_lines)
    if len(script_lines) > 10:
        info_text += f"\n\n*...and {len(script_lines) - 10} more lines*"
    
    return output_path, output_path, info_text

# ==================== Gradio UI ====================

def create_multispeaker_ui():
    """Create the multi-speaker TTS interface."""
    
    voice_names = get_voice_names()
    
    # Default speaker config
    default_config = """Speaker1:af_bella
Speaker2:bf_isabella
Speaker3:af_nicole
Speaker4:bf_emma"""
    
    # Default script example with advanced features
    default_script = """Speaker1: Hello! Welcome to our multi-speaker TTS demo.
Speaker2: This is amazing! We can now create dialogues with different voices.
{pause: 0.5}
Speaker1: Exactly! Each speaker can have their own unique voice.
Speaker2: And it's so easy to use!
Speaker3: Don't forget, you can add more speakers too!
Speaker4: The possibilities are endless with this tool."""
    
    with gr.Blocks(title="Multi-Speaker TTS", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 🎭 Multi-Speaker TTS Studio
            
            Create natural dialogues and conversations with multiple speakers. 
            Assign different voices to each speaker and generate seamless multi-speaker audio.
            
            **Quick Start:**
            1. **Configure speakers** with voice assignments (format: `SpeakerName:voice_name`)
            2. **Write your script** with speaker labels (format: `SpeakerName: Dialogue text`)
            3. **Adjust settings** and click Generate!
            
            **Advanced Features:**
            - Use `{pause: 1.5}` for custom pause duration
            - Use `Speaker(voice_name): text` for inline voice override
            - Enable volume normalization for consistent audio levels
            """
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🔊 Speaker Configuration")
                gr.Markdown("Define speakers and assign voices (one per line)")
                speaker_config = gr.Textbox(
                    label="Speaker Config",
                    value=default_config,
                    lines=8,
                    placeholder="Speaker1:af_bella\nSpeaker2:bf_isabella",
                    info="Format: SpeakerName:voice_name"
                )
                
                with gr.Accordion("📦 Voice Library", open=False):
                    gr.Markdown("Available voices:")
                    voice_list = gr.Markdown("\n".join([f"- `{v}`" for v in voice_names[:20]]))
                    gr.Markdown(f"*...and {len(voice_names) - 20} more voices*")
                
                with gr.Accordion("⚙️ Audio Settings", open=True):
                    language = gr.Dropdown(
                        choices=list(language_map.keys()),
                        value="American English",
                        label="🌍 Language"
                    )
                    speed = gr.Slider(
                        minimum=0.5,
                        maximum=2.0,
                        value=1.0,
                        step=0.1,
                        label="⚡ Speaking Speed"
                    )
                    pause_duration = gr.Slider(
                        minimum=0.0,
                        maximum=2.0,
                        value=0.2,
                        step=0.1,
                        label="⏸️ Pause Between Lines (seconds)"
                    )
                    normalize_audio = gr.Checkbox(
                        value=True,
                        label="🔊 Normalize Speaker Volumes"
                    )
                    auto_translate = gr.Checkbox(
                        value=False,
                        label="🌐 Auto-translate Script to Target Language"
                    )
                
                generate_btn = gr.Button("🚀 Generate Multi-Speaker Audio", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                gr.Markdown("### 📝 Script")
                gr.Markdown("Write dialogue with speaker labels")
                script = gr.Textbox(
                    label="Script",
                    value=default_script,
                    lines=15,
                    placeholder="Speaker1: Hello there!\nSpeaker2: Hi! How are you?",
                    info="Formats: 'Speaker: text' or '[Speaker] text' or 'Speaker | text'"
                )
                
                gr.Markdown("### 🎧 Output")
                audio_output = gr.Audio(
                    label="Generated Audio",
                    type="filepath",
                    autoplay=True
                )
                audio_download = gr.File(label="📥 Download Audio File")
                
                gr.Markdown("### 📋 Generation Info")
                generation_info = gr.Markdown("Click Generate to see details...")
        
        # Examples
        gr.Markdown("### 💡 Examples")
        gr.Examples(
            examples=[
                [
                    "Speaker1:af_bella\nSpeaker2:bf_isabella",
                    "Speaker1: Good morning! Ready for the meeting?\nSpeaker2: Absolutely! I've prepared all the documents.\nSpeaker1: Great! Let's get started then.\nSpeaker2: Following you!"
                ],
                [
                    "Narrator:af_nicole\nJohn:af_bella\nMary:bf_emma",
                    "Narrator: It was a beautiful morning.\nJohn: What a lovely day!\n{pause: 0.8}\nMary: Perfect for a walk in the park.\nNarrator: And so they set off together."
                ],
                [
                    "Host:af_heart\nGuest:bf_isabella\nCoHost:af_nicole",
                    "Host: Welcome back to our podcast!\nGuest: Thanks for having me!\nCoHost: We're excited to hear your story.\nHost: Let's dive right in!"
                ],
                [
                    "Alice:af_bella\nBob:bf_isabella",
                    "Alice: Did you hear about the new project?\nBob: Yes! It sounds exciting.\n{pause: 0.3}\nAlice: We should join the team.\nBob: I'm already on it!"
                ],
                [
                    "Teacher:af_nicole\nStudent:bf_emma",
                    "Teacher: Today we'll learn about Python programming.\nStudent: That sounds fun!\nTeacher: It's a powerful language for many applications.\n{pause: 0.5}\nStudent: I can't wait to start coding!"
                ]
            ],
            inputs=[speaker_config, script],
            label="Click to load example"
        )
        
        # Connect button
        generate_btn.click(
            fn=process_multispeaker_script,
            inputs=[
                script,
                speaker_config,
                language,
                speed,
                pause_duration,
                normalize_audio,
                auto_translate
            ],
            outputs=[audio_output, audio_download, generation_info]
        )
        
        # Also generate on script submit
        script.submit(
            fn=process_multispeaker_script,
            inputs=[
                script,
                speaker_config,
                language,
                speed,
                pause_duration,
                normalize_audio,
                auto_translate
            ],
            outputs=[audio_output, audio_download, generation_info]
        )
    
    return demo

# ==================== Entry Point ====================

import click

@click.command()
@click.option("--debug", is_flag=True, default=False, help="Enable debug mode.")
@click.option("--share", is_flag=True, default=False, help="Enable sharing.")
@click.option("--port", type=int, default=7860, help="Port to run on.")
def main(debug, share, port):
    demo = create_multispeaker_ui()
    demo.queue().launch(debug=debug, share=share, server_port=port)

if __name__ == "__main__":
    main()
