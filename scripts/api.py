import shutil
import os
from gradio_client import Client

# Ensure the output directory exists
output_dir = "./api_output"
os.makedirs(output_dir, exist_ok=True)

# paste here the gradio app url
api_url = "https://7194ed6cc0b6cb4724.gradio.live/"

client = Client(api_url)

def text_to_speech(
    text="Hello",
    language="American English",
    voice_name="af_bella",
    speed=1,
    auto_translate=False,
    remove_silence=False,
):
    result = client.predict(
		text=text,
		Language=language,
		voice=voice_name,
		speed=speed,
		translate_text=auto_translate,
		remove_silence=remove_silence,
		api_name="/KOKORO_TTS_API"
    )

    print(f"API Response: {result}")  # Debugging output

    if not result or not isinstance(result, (list, tuple)):  # Ensure result is a list/tuple
        print("Error: API did not return valid file paths.")
        return []

    save_files = []    
    for id, i in enumerate(result):
        if not isinstance(i, str) or not os.path.exists(i):  # Check if file path is valid
            print(f"Warning: Invalid or missing file - {i}")
            continue  # Skip invalid files
        
        save_at = os.path.join(output_dir, os.path.basename(i))
        shutil.move(i, save_at)
        # print(f"Saved at {save_at}")
        save_files.append(save_at)

    return save_files

# Example usage
if __name__ == "__main__":
    text = "Hello, how are you?"
    language = "American English"
    voice_name = "af_bella"
    speed = 1
    auto_translate = False
    remove_silence = False

    save_files = text_to_speech(text, language, voice_name, speed, auto_translate, remove_silence)
    audio_path=save_files[0]
    word_level_srt=save_files[1]
    sentence_level_srt=save_files[2]
    timestamp_json=save_files[3]
    print(f"Audio file saved at: {audio_path}")
    print(f"Word-level SRT file saved at: {word_level_srt}")
    print(f"Sentence-level SRT file saved at: {sentence_level_srt}")
    print(f"Timestamp JSON file saved at: {timestamp_json}")
