# Initalize a pipeline
from kokoro import KPipeline
# from IPython.display import display, Audio
import soundfile as sf
import os
from huggingface_hub import list_repo_files
import uuid
import re 
import gradio as gr


# Language mapping dictionary
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

# Print installation instructions if necessary
install_messages = {
    "Japanese": "pip install misaki[ja]",
    "Mandarin Chinese": "pip install misaki[zh]"
}



def update_pipeline(Language):
    """ Updates the pipeline only if the language has changed. """
    global pipeline, last_used_language

    # Print installation instructions if necessary
    if Language in install_messages:
        # raise gr.Error(f"To Use {Language} Install: {install_messages[Language]}",duration=10)
        gr.Warning(f"To Use {Language} Install: {install_messages[Language]}",duration=10)
        # gr.Warning("Reverting to default English pipeline...", duration=5)
        # print(f"To use {Language}, install: {install_messages[Language]}")
        # print("Reverting to default English pipeline...")
        

        # Revert to default English and return immediately
        pipeline = KPipeline(lang_code="a")
        last_used_language = "a"
        return  

    # Get language code, default to 'a' if not found
    new_lang = language_map.get(Language, "a")

    # Only update if the language is different
    if new_lang != last_used_language:
        try:
            pipeline = KPipeline(lang_code=new_lang)
            last_used_language = new_lang  # Update last used language
            print(f"Pipeline updated to {Language} ({new_lang})")
        except Exception as e:
            print(f"Error initializing KPipeline: {e}\nRetrying with default language...")
            pipeline = KPipeline(lang_code="a")  # Fallback to English
            last_used_language = "a"



def get_voice_names(repo_id):
    """Fetches and returns a list of voice names (without extensions) from the given Hugging Face repository."""
    return [os.path.splitext(file.replace("voices/", ""))[0] for file in list_repo_files(repo_id) if file.startswith("voices/")]

def create_audio_dir():
    """Creates the 'kokoro_audio' directory in the root folder if it doesn't exist."""
    root_dir = os.getcwd()  # Use current working directory instead of __file__
    audio_dir = os.path.join(root_dir, "kokoro_audio")

    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
        print(f"Created directory: {audio_dir}")
    else:
        print(f"Directory already exists: {audio_dir}")
    return audio_dir

import re

def clean_text(text):
    # Define replacement rules
    replacements = {
        "–": " ",  # Replace en-dash with space
        "-": " ",  # Replace hyphen with space
        "**": " ", # Replace double asterisks with space
        "*": " ",  # Replace single asterisk with space
        "#": " ",  # Replace hash with space
    }

    # Apply replacements
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove emojis using regex (covering wide range of Unicode characters)
    emoji_pattern = re.compile(
        r'[\U0001F600-\U0001F64F]|'  # Emoticons
        r'[\U0001F300-\U0001F5FF]|'  # Miscellaneous symbols and pictographs
        r'[\U0001F680-\U0001F6FF]|'  # Transport and map symbols
        r'[\U0001F700-\U0001F77F]|'  # Alchemical symbols
        r'[\U0001F780-\U0001F7FF]|'  # Geometric shapes extended
        r'[\U0001F800-\U0001F8FF]|'  # Supplemental arrows-C
        r'[\U0001F900-\U0001F9FF]|'  # Supplemental symbols and pictographs
        r'[\U0001FA00-\U0001FA6F]|'  # Chess symbols
        r'[\U0001FA70-\U0001FAFF]|'  # Symbols and pictographs extended-A
        r'[\U00002702-\U000027B0]|'  # Dingbats
        r'[\U0001F1E0-\U0001F1FF]'   # Flags (iOS)
        r'', flags=re.UNICODE)
  
    text = emoji_pattern.sub(r'', text)

    # Remove multiple spaces and extra line breaks
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def tts_file_name(text):
    global temp_folder
    # Remove all non-alphabetic characters and convert to lowercase
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Retain only alphabets and spaces
    text = text.lower().strip()             # Convert to lowercase and strip leading/trailing spaces
    text = text.replace(" ", "_")           # Replace spaces with underscores
    
    # Truncate or handle empty text
    truncated_text = text[:20] if len(text) > 20 else text if len(text) > 0 else "empty"
    
    # Generate a random string for uniqueness
    random_string = uuid.uuid4().hex[:8].upper()
    
    # Construct the file name
    file_name = f"{temp_folder}/{truncated_text}_{random_string}.wav"
    return file_name


import soundfile as sf
import numpy as np
import wave
from pydub import AudioSegment
from pydub.silence import split_on_silence

def remove_silence_function(file_path,minimum_silence=50):
    # Extract file name and format from the provided path
    output_path = file_path.replace(".wav", "_no_silence.wav")
    audio_format = "wav"
    # Reading and splitting the audio file into chunks
    sound = AudioSegment.from_file(file_path, format=audio_format)
    audio_chunks = split_on_silence(sound,
                                    min_silence_len=100,
                                    silence_thresh=-45,
                                    keep_silence=minimum_silence) 
    # Putting the file back together
    combined = AudioSegment.empty()
    for chunk in audio_chunks:
        combined += chunk
    combined.export(output_path, format=audio_format)
    return output_path

def generate_and_save_audio(text, Language="American English",voice="af_bella", speed=1,remove_silence=False,keep_silence_up_to=0.05):
    
    update_pipeline(Language)
    generator = pipeline(text, voice=voice, speed=speed, split_pattern=r'\n+')
    save_path=tts_file_name(text)
    # Open the WAV file for writing
    with wave.open(save_path, 'wb') as wav_file:
        # Set the WAV file parameters
        wav_file.setnchannels(1)  # Mono audio
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit audio)
        wav_file.setframerate(24000)  # Sample rate

        # Process each audio chunk
        for i, (gs, ps, audio) in enumerate(generator):
            # print(f"{i}. {gs}")
            # print(f"Phonetic Transcription: {ps}")
            # display(Audio(data=audio, rate=24000, autoplay=i==0))
            print("\n")
            # Convert the Tensor to a NumPy array
            audio_np = audio.numpy()  # Convert Tensor to NumPy array
            audio_int16 = (audio_np * 32767).astype(np.int16)  # Scale to 16-bit range
            audio_bytes = audio_int16.tobytes()  # Convert to bytes

            # Write the audio chunk to the WAV file
            wav_file.writeframes(audio_bytes)
    if remove_silence:            
      keep_silence = int(keep_silence_up_to * 1000)
      new_wave_file=remove_silence_function(save_path,minimum_silence=keep_silence)
      return new_wave_file,new_wave_file
    return save_path,save_path





def ui():
    def toggle_autoplay(autoplay):
        return gr.Audio(interactive=False, label='Output Audio', autoplay=autoplay)

    # Define examples in the format you mentioned
    dummy_examples = [
        ["Hello, how are you?", "American English", "af_bella", 1.0, False],
        ["Hello, how are you?", "British English", "bf_alice", 1.0, False],
        ["नमस्ते, कैसे हो?", "Hindi", "hf_alpha", 1.0, False],
        ["Hola, ¿cómo estás?", "Spanish", "ef_dora", 1.0, False],
        ["Bonjour, comment ça va?", "French", "ff_siwis", 1.0, False],
        ["Ciao, come stai?", "Italian", "if_sara", 1.0, False],
        ["Olá, como você está?", "Brazilian Portuguese", "pf_dora", 1.0, False],
        ["こんにちは、お元気ですか？", "Japanese", "jf_nezumi", 1.0, False],
        ["你好，你怎么样?", "Mandarin Chinese", "zf_xiaoni", 1.0, False]
    ]
    
    with gr.Blocks(theme='JohnSmith9982/small_and_pretty') as demo:
        gr.Markdown("<center><h1 style='font-size: 30px;'>KOKORO TTS</h1></center>")  # Larger title with CSS
        lang_list = ['American English', 'British English', 'Hindi', 'Spanish', 'French', 'Italian', 'Brazilian Portuguese', 'Japanese', 'Mandarin Chinese']
        voice_names = get_voice_names("hexgrad/Kokoro-82M")

        with gr.Row():
            with gr.Column():
                text = gr.Textbox(label='Enter Text', lines=3)
                
                with gr.Row():
                    language_name = gr.Dropdown(lang_list, label="Select Language", value=lang_list[0])

                with gr.Row():
                    voice_name = gr.Dropdown(voice_names, label="Choose VoicePack", value=voice_names[0])

                with gr.Row():
                    generate_btn = gr.Button('Generate', variant='primary')

                with gr.Accordion('Audio Settings', open=False):
                    speed = gr.Slider(minimum=0.25, maximum=2, value=1, step=0.1, label='⚡️Speed', info='Adjust the speaking speed')
                    remove_silence = gr.Checkbox(value=False, label='✂️ Remove Silence From TTS')

            with gr.Column():
                audio = gr.Audio(interactive=False, label='Output Audio', autoplay=True)
                audio_file = gr.File(label='Download Audio')

                with gr.Accordion('Enable Autoplay', open=False):
                    autoplay = gr.Checkbox(value=True, label='Autoplay')
                    autoplay.change(toggle_autoplay, inputs=[autoplay], outputs=[audio])

        text.submit(generate_and_save_audio, inputs=[text, language_name, voice_name, speed, remove_silence], outputs=[audio, audio_file])
        generate_btn.click(generate_and_save_audio, inputs=[text, language_name, voice_name, speed, remove_silence], outputs=[audio, audio_file])

        # Add examples to the interface
        gr.Examples(examples=dummy_examples, inputs=[text, language_name, voice_name, speed, remove_silence])

    return demo


import click
@click.command()
@click.option("--debug", is_flag=True, default=False, help="Enable debug mode.")
@click.option("--share", is_flag=True, default=False, help="Enable sharing of the interface.")
def main(debug, share):
    demo = ui()
    demo.queue().launch(debug=debug, share=share)
    #Run on local network
    # laptop_ip="192.168.0.30"
    # port=8080
    # demo.queue().launch(debug=debug, share=share,server_name=laptop_ip,server_port=port)



# Initialize default pipeline
last_used_language = "a"
pipeline = KPipeline(lang_code=last_used_language)
temp_folder = create_audio_dir()
if __name__ == "__main__":
    main()    
