import shutil
import os
from gradio_client import Client

# Ensure the output directory exists
output_dir = "api_output"
os.makedirs(output_dir, exist_ok=True)

# Initialize the Gradio client
api_url = "http://127.0.0.1:7860/"
client = Client(api_url)

def text_to_speech(
    text="Hello",
    language="American English",
    voice_name="af_nicole",
    speed=1,
    remove_silence=False,
):
    result = client.predict(
        text=text,
        Language=language,
        voice=voice_name,
        speed=speed,
        remove_silence=remove_silence,
        api_name="/generate_and_save_audio"
    )
    
    if isinstance(result, tuple):
        result = result[0]  # Extract the first element if it's a tuple

    save_at = os.path.join(output_dir, os.path.basename(result))
    shutil.move(result, save_at)
    print(f"Saved at {save_at}")

    return save_at

# Example usage
if __name__ == "__main__":
    text = "Hello, how are you?"
    language = "American English"
    voice_name = "af_nicole"
    speed = 1
    remove_silence = False

    audio_path = text_to_speech(text, language, voice_name, speed, remove_silence)
    print(f"Audio file saved at: {audio_path}")



# languages = [
#     "American English",
#     "British English",
#     "Hindi",
#     "Spanish",
#     "French",
#     "Italian",
#     "Brazilian Portuguese",
#     "Japanese",
#     "Mandarin Chinese"
# ]
