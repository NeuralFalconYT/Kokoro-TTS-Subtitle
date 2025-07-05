# Initalize a pipeline
from kokoro import KPipeline
# from IPython.display import display, Audio
# import soundfile as sf
import os
from huggingface_hub import list_repo_files
import uuid
import re
import gradio as gr


#translate langauge
from deep_translator import GoogleTranslator
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
def bulk_translate(text, target_language, chunk_size=500,MAX_ALLOWED_CHARACTERS = 10000):
    if len(text)>=MAX_ALLOWED_CHARACTERS:
      gr.Warning("[WARNING] Text too long — skipping translation to prevent Google Translate abuse.")
      return text
    # language_map_local = {
    # "American English": "en",
    # "British English": "en",
    # "Hindi": "hi",
    # "Spanish": "es",
    # "French": "fr",
    # "Italian": "it",
    # "Brazilian Portuguese": "pt",
    # "Japanese": "ja",
    # "Mandarin Chinese": "zh-CN"
    # }
    # lang_code = GoogleTranslator().get_supported_languages(as_dict=True).get(target_language.lower())
    lang_code=language_map_local[target_language]
    sentences = re.split(r'(?<=[.!?])\s+', text)  # Split text into sentences
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    translated_chunks = [GoogleTranslator(target=lang_code).translate(chunk) for chunk in chunks]
    result=" ".join(translated_chunks)
    return result.strip()

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


def update_pipeline(Language):
    """ Updates the pipeline only if the language has changed. """
    global pipeline, last_used_language
    # Get language code, default to 'a' if not found
    new_lang = language_map.get(Language, "a")

    # Only update if the language is different
    if new_lang != last_used_language:
        pipeline = KPipeline(lang_code=new_lang)
        last_used_language = new_lang
        try:
            pipeline = KPipeline(lang_code=new_lang)
            last_used_language = new_lang  # Update last used language
        except Exception as e:
            gr.Warning(f"Make sure the input text is in {Language}",duration=10)
            gr.Warning(f"Fallback to English Language",duration=5)
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

def tts_file_name(text,language):
    global temp_folder
    # Remove all non-alphabetic characters and convert to lowercase
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Retain only alphabets and spaces
    text = text.lower().strip()             # Convert to lowercase and strip leading/trailing spaces
    text = text.replace(" ", "_")           # Replace spaces with underscores
    language=language.replace(" ", "_").strip()
    # Truncate or handle empty text
    truncated_text = text[:20] if len(text) > 20 else text if len(text) > 0 else language

    # Generate a random string for uniqueness
    random_string = uuid.uuid4().hex[:8].upper()

    # Construct the file name
    file_name = f"{temp_folder}/{truncated_text}_{random_string}.wav"
    return file_name


# import soundfile as sf
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
    text=clean_text(text)
    update_pipeline(Language)
    generator = pipeline(text, voice=voice, speed=speed, split_pattern=r'\n+')
    save_path=tts_file_name(text,Language)
    # Open the WAV file for writing
    timestamps={}
    with wave.open(save_path, 'wb') as wav_file:
        # Set the WAV file parameters
        wav_file.setnchannels(1)  # Mono audio
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit audio)
        wav_file.setframerate(24000)  # Sample rate
        for i, result in enumerate(generator):
          gs = result.graphemes # str
        #   print(f"\n{i}: {gs}")
          ps = result.phonemes # str
          # audio = result.audio.cpu().numpy()
          audio = result.audio
          tokens = result.tokens # List[en.MToken]
          timestamps[i]={"text":gs,"words":[]}
          if Language in ["American English", "British English"]:
            for t in tokens:
                # print(t.text, repr(t.whitespace), t.start_ts, t.end_ts)
                timestamps[i]["words"].append({"word":t.text,"start":t.start_ts,"end":t.end_ts})
          audio_np = audio.numpy()  # Convert Tensor to NumPy array
          audio_int16 = (audio_np * 32767).astype(np.int16)  # Scale to 16-bit range
          audio_bytes = audio_int16.tobytes()  # Convert to bytes
          # Write the audio chunk to the WAV file
          duration_sec = len(audio_np) / 24000
          timestamps[i]["duration"] = duration_sec
          wav_file.writeframes(audio_bytes)
    if remove_silence:
      keep_silence = int(keep_silence_up_to * 1000)
      new_wave_file=remove_silence_function(save_path,minimum_silence=keep_silence)
      return new_wave_file,timestamps
    return save_path,timestamps



def adjust_timestamps(timestamp_dict):
    adjusted_timestamps = []
    last_global_end = 0  # Cumulative audio timeline

    for segment_id in sorted(timestamp_dict.keys()):
        segment = timestamp_dict[segment_id]
        words = segment["words"]
        chunk_duration = segment["duration"]

        # If there are valid words, get last word end
        last_word_end_in_chunk = (
            max(w["end"] for w in words if w["end"] not in [None, 0])
            if words else 0
        )

        silence_gap = chunk_duration - last_word_end_in_chunk
        if silence_gap < 0:  # In rare cases where end > duration (due to rounding)
            silence_gap = 0

        for word in words:
            start = word["start"] or 0
            end = word["end"] or start

            adjusted_timestamps.append({
                "word": word["word"],
                "start": round(last_global_end + start, 3),
                "end": round(last_global_end + end, 3)
            })

        # Add entire chunk duration to global end
        last_global_end += chunk_duration

    return adjusted_timestamps



import string

def write_word_srt(word_level_timestamps, output_file="word.srt", skip_punctuation=True):
    with open(output_file, "w", encoding="utf-8") as f:
        index = 1  # Track subtitle numbering separately

        for entry in word_level_timestamps:
            word = entry["word"]

            # Skip punctuation if enabled
            if skip_punctuation and all(char in string.punctuation for char in word):
                continue

            start_time = entry["start"]
            end_time = entry["end"]

            # Convert seconds to SRT time format (HH:MM:SS,mmm)
            def format_srt_time(seconds):
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                sec = int(seconds % 60)
                millisec = int((seconds % 1) * 1000)
                return f"{hours:02}:{minutes:02}:{sec:02},{millisec:03}"

            start_srt = format_srt_time(start_time)
            end_srt = format_srt_time(end_time)

            # Write entry to SRT file
            f.write(f"{index}\n{start_srt} --> {end_srt}\n{word}\n\n")
            index += 1  # Increment subtitle number

import string


def split_line_by_char_limit(text, max_chars=30):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line + " " + word) <= max_chars:
            current_line = (current_line + " " + word).strip()
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        # Check if last line is a single word and there is a previous line
        if len(current_line.split()) == 1 and len(lines) > 0:
            # Append single word to previous line
            lines[-1] += " " + current_line
        else:
            lines.append(current_line)

    return "\n".join(lines)


def write_sentence_srt(word_level_timestamps, output_file="subtitles.srt", max_words=8, min_pause=0.1):
    subtitles = []  # Stores subtitle blocks
    subtitle_words = []  # Temporary list for words in the current subtitle
    start_time = None  # Tracks start time of current subtitle

    remove_punctuation = ['"',"—"]  # Add punctuations to remove if needed

    for i, entry in enumerate(word_level_timestamps):
        word = entry["word"]
        word_start = entry["start"]
        word_end = entry["end"]

        # Skip selected punctuation from remove_punctuation list
        if word in remove_punctuation:
            continue

        # Attach punctuation to the previous word
        if word in string.punctuation:
            if subtitle_words:
                subtitle_words[-1] = (subtitle_words[-1][0] + word, subtitle_words[-1][1])
            continue

        # Start a new subtitle block if needed
        if start_time is None:
            start_time = word_start

        # Calculate pause duration if this is not the first word
        if subtitle_words:
            last_word_end = subtitle_words[-1][1]
            pause_duration = word_start - last_word_end
        else:
            pause_duration = 0

        # **NEW FIX:** If pause is too long, create a new subtitle but ensure continuity
        if (word.endswith(('.', '!', '?')) and len(subtitle_words) >= 5) or len(subtitle_words) >= max_words or pause_duration > min_pause:
            end_time = subtitle_words[-1][1]  # Use last word's end time
            subtitle_text = " ".join(w[0] for w in subtitle_words)
            subtitles.append((start_time, end_time, subtitle_text))

            # Reset for the next subtitle, but **ensure continuity**
            subtitle_words = [(word, word_end)]  # **Carry the current word to avoid delay**
            start_time = word_start  # **Start at the current word, not None**

            continue  # Avoid adding the word twice

        # Add the current word to the subtitle
        subtitle_words.append((word, word_end))

    # Ensure last subtitle is added if anything remains
    if subtitle_words:
        end_time = subtitle_words[-1][1]
        subtitle_text = " ".join(w[0] for w in subtitle_words)
        subtitles.append((start_time, end_time, subtitle_text))

    # Function to format SRT timestamps
    def format_srt_time(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        sec = int(seconds % 60)
        millisec = int((seconds % 1) * 1000)
        return f"{hours:02}:{minutes:02}:{sec:02},{millisec:03}"

    # Write subtitles to SRT file
    with open(output_file, "w", encoding="utf-8") as f:
        for i, (start, end, text) in enumerate(subtitles, start=1):
            text=split_line_by_char_limit(text, max_chars=30)
            f.write(f"{i}\n{format_srt_time(start)} --> {format_srt_time(end)}\n{text}\n\n")

    # print(f"SRT file '{output_file}' created successfully!")


import json
import re

def fix_punctuation(text):
    # Remove spaces before punctuation marks (., ?, !, ,)
    text = re.sub(r'\s([.,?!])', r'\1', text)

    # Handle quotation marks: remove spaces before and after them
    text = text.replace('" ', '"')
    text = text.replace(' "', '"')
    text = text.replace('" ', '"')

    # Track quotation marks to add space after closing quotes
    track = 0
    result = []

    for index, char in enumerate(text):
        if char == '"':
            track += 1
            result.append(char)
            # If it's a closing quote (even number of quotes), add a space after it
            if track % 2 == 0:
                result.append(' ')
        else:
            result.append(char)
    text=''.join(result)
    return text.strip()



def make_json(word_timestamps, json_file_name):
    data = {}
    temp = []
    inside_quote = False  # Track if we are inside a quoted sentence
    start_time = word_timestamps[0]['start']  # Initialize with the first word's start time
    end_time = word_timestamps[0]['end']  # Initialize with the first word's end time
    words_in_sentence = []
    sentence_id = 0  # Initialize sentence ID

    # Process each word in word_timestamps
    for i, word_data in enumerate(word_timestamps):
        word = word_data['word']
        word_start = word_data['start']
        word_end = word_data['end']

        # Collect word info for JSON
        words_in_sentence.append({'word': word, 'start': word_start, 'end': word_end})

        # Update the end_time for the sentence based on the current word
        end_time = word_end

        # Properly handle opening and closing quotation marks
        if word == '"':
            if inside_quote:
                temp[-1] += '"'  # Attach closing quote to the last word
            else:
                temp.append('"')  # Keep opening quote as a separate entry
            inside_quote = not inside_quote  # Toggle inside_quote state
        else:
            temp.append(word)

        # Check if this is a sentence-ending punctuation
        if word.endswith(('.', '?', '!')) and not inside_quote:
            # Ensure the next word is NOT a dialogue tag before finalizing the sentence
            if i + 1 < len(word_timestamps):
                next_word = word_timestamps[i + 1]['word']
                if next_word[0].islower():  # Likely a dialogue tag like "he said"
                    continue  # Do not break the sentence yet

            # Store the full sentence for JSON and reset word collection for next sentence
            sentence = " ".join(temp)
            sentence = fix_punctuation(sentence)  # Fix punctuation in the sentence
            data[sentence_id] = {
                'text': sentence,
                'duration': end_time - start_time,
                'start': start_time,
                'end': end_time,
                'words': words_in_sentence
            }

            # Reset for the next sentence
            temp = []
            words_in_sentence = []
            start_time = word_data['start']  # Update the start time for the next sentence
            sentence_id += 1  # Increment sentence ID

    # Handle any remaining words if necessary
    if temp:
        sentence = " ".join(temp)
        sentence = fix_punctuation(sentence)  # Fix punctuation in the sentence
        data[sentence_id] = {
            'text': sentence,
            'duration': end_time - start_time,
            'start': start_time,
            'end': end_time,
            'words': words_in_sentence
        }

    # Write data to JSON file
    with open(json_file_name, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    return json_file_name




import os

def modify_filename(save_path: str, prefix: str = ""):
    directory, filename = os.path.split(save_path)
    name, ext = os.path.splitext(filename)
    new_filename = f"{prefix}{name}{ext}"
    return os.path.join(directory, new_filename)
import shutil
def save_current_data():
    if os.path.exists("./last"):
        shutil.rmtree("./last")
    os.makedirs("./last",exist_ok=True)

def KOKORO_TTS_API(text, Language="American English",voice="af_bella", speed=1,translate_text=False,remove_silence=False,keep_silence_up_to=0.05):
    if translate_text:
        text=bulk_translate(text, Language, chunk_size=500)
    save_path,timestamps=generate_and_save_audio(text=text, Language=Language,voice=voice, speed=speed,remove_silence=remove_silence,keep_silence_up_to=keep_silence_up_to)
    if remove_silence==False:
        if Language in ["American English", "British English"]:
            word_level_timestamps=adjust_timestamps(timestamps)
            word_level_srt = modify_filename(save_path.replace(".wav", ".srt"), prefix="word_level_")
            normal_srt = modify_filename(save_path.replace(".wav", ".srt"), prefix="sentence_")
            json_file = modify_filename(save_path.replace(".wav", ".json"), prefix="duration_")
            write_word_srt(word_level_timestamps, output_file=word_level_srt, skip_punctuation=True)
            write_sentence_srt(word_level_timestamps, output_file=normal_srt, min_pause=0.01)
            make_json(word_level_timestamps, json_file)
            save_current_data()
            shutil.copy(save_path, "./last/")
            shutil.copy(word_level_srt, "./last/")
            shutil.copy(normal_srt, "./last/")
            shutil.copy(json_file, "./last/")
            return save_path,save_path,word_level_srt,normal_srt,json_file
    return save_path,save_path,None,None,None



def toggle_autoplay(autoplay):
        return gr.Audio(interactive=False, label='Output Audio', autoplay=autoplay)
lang_list = ['American English', 'British English', 'Hindi', 'Spanish', 'French', 'Italian', 'Brazilian Portuguese', 'Japanese', 'Mandarin Chinese']
voice_names = get_voice_names("hexgrad/Kokoro-82M")
def ui():
    # Define examples in the format you mentioned
    dummy_examples = [
        ["Hey, y'all, let’s grab some coffee and catch up!", "American English", "af_bella"],
        ["I'd like a large coffee, please.", "British English", "bf_isabella"],
        ["नमस्ते, कैसे हो?", "Hindi", "hf_alpha"],
        ["Hola, ¿cómo estás?", "Spanish", "ef_dora"],
        ["Bonjour, comment ça va?", "French", "ff_siwis"],
        ["Ciao, come stai?", "Italian", "if_sara"],
        ["Olá, como você está?", "Brazilian Portuguese", "pf_dora"],
        ["こんにちは、お元気ですか？", "Japanese", "jf_nezumi"],
        ["你好，你怎么样?", "Mandarin Chinese", "zf_xiaoni"]
    ]

    with gr.Blocks() as demo:
        # gr.Markdown("<center><h1 style='font-size: 40px;'>KOKORO TTS</h1></center>")  # Larger title with CSS
        # gr.Markdown("[Install on Your Local System](https://github.com/NeuralFalconYT/kokoro_v1)")


        with gr.Row():
            with gr.Column():
                text = gr.Textbox(label='📝 Enter Text', lines=3)

                with gr.Row():
                    language_name = gr.Dropdown(lang_list, label="🌍 Select Language", value=lang_list[0])

                with gr.Row():
                    voice_name = gr.Dropdown(voice_names, label="🎙️ Choose VoicePack", value='af_heart')#voice_names[0])

                with gr.Row():
                    generate_btn = gr.Button('🚀 Generate', variant='primary')

                with gr.Accordion('🎛️ Audio Settings', open=False):
                    speed = gr.Slider(minimum=0.5, maximum=2, value=1, step=0.1, label='⚡️Speed', info='Adjust the speaking speed')
                    translate_text = gr.Checkbox(value=False, label='🌐 Translate Text to Selected Language')
                    remove_silence = gr.Checkbox(value=False, label='✂️ Remove Silence From TTS')

            with gr.Column():
                audio = gr.Audio(interactive=False, label='🔊 Output Audio', autoplay=True)
                audio_file = gr.File(label='📥 Download Audio')
                # word_level_srt_file = gr.File(label='Download Word-Level SRT')
                # srt_file = gr.File(label='Download Sentence-Level SRT')
                # sentence_duration_file = gr.File(label='Download Sentence Duration JSON')
                with gr.Accordion('🎬 Autoplay, Subtitle, Timestamp', open=False):
                    autoplay = gr.Checkbox(value=True, label='▶️ Autoplay')
                    autoplay.change(toggle_autoplay, inputs=[autoplay], outputs=[audio])
                    word_level_srt_file = gr.File(label='📝 Download Word-Level SRT')
                    srt_file = gr.File(label='📜 Download Sentence-Level SRT')
                    sentence_duration_file = gr.File(label='⏳ Download Sentence Timestamp JSON')

        text.submit(KOKORO_TTS_API, inputs=[text, language_name, voice_name, speed,translate_text, remove_silence], outputs=[audio, audio_file,word_level_srt_file,srt_file,sentence_duration_file])
        generate_btn.click(KOKORO_TTS_API, inputs=[text, language_name, voice_name, speed,translate_text, remove_silence], outputs=[audio, audio_file,word_level_srt_file,srt_file,sentence_duration_file])

        # Add examples to the interface
        gr.Examples(examples=dummy_examples, inputs=[text, language_name, voice_name])

    return demo

def tutorial():
    # Markdown explanation for language code
    explanation = """
    ## Language Code Explanation:
    Example: `'af_bella'`
    - **'a'** stands for **American English**.
    - **'f_'** stands for **Female** (If it were 'm_', it would mean Male).
    - **'bella'** refers to the specific voice.

    The first character in the voice code stands for the language:
    - **"a"**: American English
    - **"b"**: British English
    - **"h"**: Hindi
    - **"e"**: Spanish
    - **"f"**: French
    - **"i"**: Italian
    - **"p"**: Brazilian Portuguese
    - **"j"**: Japanese
    - **"z"**: Mandarin Chinese

    The second character stands for gender:
    - **"f_"**: Female
    - **"m_"**: Male
    """
    with gr.Blocks() as demo2:
        # gr.Markdown("[Install on Your Local System](https://github.com/NeuralFalconYT/kokoro_v1)")
        gr.Markdown(explanation)  # Display the explanation
    return demo2








#@title subtitle
import os
import re
import uuid
import shutil
import platform
import datetime
import subprocess
import math
import json
import pysrt
import librosa
import soundfile as sf
from tqdm.auto import tqdm
from pydub import AudioSegment
from deep_translator import GoogleTranslator

# ---------------------- Utility Functions ----------------------

# Returns the current time formatted as HH_MM_AM/PM (for filenames or logs)
def get_current_time():
    return datetime.datetime.now().strftime("%I_%M_%p")

# Constructs an output file path for the final dubbed audio
def get_subtitle_Dub_path(srt_file_path, Language):
    file_name = os.path.splitext(os.path.basename(srt_file_path))[0]
    full_base_path = os.path.join(os.getcwd(), "TTS_DUB")
    os.makedirs(full_base_path, exist_ok=True)
    random_string = str(uuid.uuid4())[:6]
    lang = language_map_local.get(Language, Language.replace(" ", "_"))
    new_path = os.path.join(full_base_path, f"{file_name}_{lang}_{random_string}.wav")
    return new_path.replace("__", "_")

# Removes noise characters like [♫] from the subtitle text and saves a cleaned SRT
def clean_srt(input_path):
    def clean_srt_line(text):
        for bad in ["[", "]", "♫"]:
            text = text.replace(bad, "")
        return text.strip()

    subs = pysrt.open(input_path, encoding='utf-8')
    output_path = input_path.lower().replace(".srt", "") + "_.srt"
    with open(output_path, "w", encoding='utf-8') as file:
        for sub in subs:
            file.write(f"{sub.index}\n{sub.start} --> {sub.end}\n{clean_srt_line(sub.text)}\n\n")
    return output_path

# Translates subtitles using Deep Translator while preserving subtitle index order
def translate_srt(input_path, target_language="Hindi", max_segments=500, chunk_size=4000):
    output_path = input_path.replace(".srt", f"{target_language}.srt")
    subs = pysrt.open(input_path, encoding='utf-8')
    #Blocking large text translations to prevent DDoS, so Google Translate remains free forever.
    if len(subs) > max_segments:
        gr.Warning(f"Too many segments: {len(subs)} > {max_segments}. Skipping translation.")
        return input_path

    # Annotate original subtitles with <#index> to preserve mapping during translation
    original = [f"<#{i}>{s.text}" for i, s in enumerate(subs)]
    full_text = "\n".join(original)

    # Split into manageable chunks for Google Translate API
    chunks, start = [], 0
    while start < len(full_text):
        end = start + chunk_size
        split_point = full_text.rfind("<#", start, end) if end < len(full_text) else len(full_text)
        chunks.append(full_text[start:split_point])
        start = split_point

    lang_code = language_map_local.get(target_language, "en")
    translated_chunks = [GoogleTranslator(target=lang_code).translate(chunk) for chunk in chunks]
    translated_text = "\n".join(translated_chunks)

    # Rebuild subtitle dictionary after translation
    pattern = re.compile(r"<#(\d+)>(.*?)(?=<#\d+>|$)", re.DOTALL)
    translated_dict = {int(i): txt.strip() for i, txt in pattern.findall(translated_text)}

    # Assign translated text back to subtitle entries
    for i, sub in enumerate(subs):
        sub.text = translated_dict.get(i, sub.text)

    subs.save(output_path, encoding='utf-8')
    return output_path

# Cleans and optionally translates an SRT file before dubbing
def prepare_srt(srt_path, target_language, translate=False):
    path = clean_srt(srt_path)
    return translate_srt(path, target_language) if translate else path

# Checks if FFmpeg is available on the system; if not, warns user and returns fallback
# To change audio speed explicitly, we can use either FFmpeg or Librosa.
def is_ffmpeg_installed():
    ffmpeg_exe = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
    try:
        subprocess.run([ffmpeg_exe, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True, ffmpeg_exe
    except Exception:
        gr.Warning("FFmpeg not found. Falling back to librosa for audio speedup.", duration=20)
        return False, ffmpeg_exe

# Because FFmpeg can handle speeds from 0.5× to 2.0× only
def atempo_chain(factor):
    if 0.5 <= factor <= 2.0:
        return f"atempo={factor:.3f}"
    parts = []
    while factor > 2.0:
        parts.append("atempo=2.0")
        factor /= 2.0
    while factor < 0.5:
        parts.append("atempo=0.5")
        factor *= 2.0
    parts.append(f"atempo={factor:.3f}")
    return ",".join(parts)

# If FFmpeg is not found, we will use Librosa
def speedup_audio_librosa(input_file, output_file, speedup_factor):
    try:
        y, sr = librosa.load(input_file, sr=None)
        y_stretched = librosa.effects.time_stretch(y, rate=speedup_factor)
        sf.write(output_file, y_stretched, sr)
    except Exception as e:
        gr.Warning(f"Librosa speedup failed: {e}")
        shutil.copy(input_file, output_file)

# Change the audio speed if it exceeds the original SRT segment duration.
def change_speed(input_file, output_file, speedup_factor, use_ffmpeg, ffmpeg_path):
    if use_ffmpeg:
        try:
            subprocess.run(
                [ffmpeg_path, "-i", input_file, "-filter:a", atempo_chain(speedup_factor), output_file, "-y"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            gr.Error(f"FFmpeg speedup error: {e}")
            speedup_audio_librosa(input_file, output_file, speedup_factor)
    else:
        speedup_audio_librosa(input_file, output_file, speedup_factor)

# Remove silence from the start and end of the audio.
def remove_edge_silence(input_path, output_path):
    y, sr = librosa.load(input_path, sr=None)
    trimmed_audio, _ = librosa.effects.trim(y, top_db=30)
    sf.write(output_path, trimmed_audio, sr)
    return output_path

# ---------------------- Main Class ----------------------
class SRTDubbing:
    def __init__(self, use_ffmpeg=True, ffmpeg_path="ffmpeg"):
        self.use_ffmpeg = use_ffmpeg
        self.ffmpeg_path = ffmpeg_path
        self.cache_dir = "./cache"
        os.makedirs("./dummy", exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)

    @staticmethod
    # Because our target is single-speaker SRT dubbing,
    # we will calculate the speaker's average talking speed per second.
    def get_avg_speaker_speed(srt_path):
        subs = pysrt.open(srt_path, encoding='utf-8')
        speeds = []
        for sub in subs:
            duration_sec = (sub.end.ordinal - sub.start.ordinal) / 1000
            char_count = len(sub.text.replace(" ", ""))
            if duration_sec > 0 and char_count > 0:
                speeds.append(char_count / duration_sec)
        return sum(speeds) / len(speeds) if speeds else 14

    @staticmethod
    # Calculate the speaker's default talking speed (e.g., 0.5x, 1x, 1.5x)
    def get_speed_factor(srt_path, default_tts_rate=14):
        avg_rate = SRTDubbing.get_avg_speaker_speed(srt_path)
        speed_factor = avg_rate / default_tts_rate if default_tts_rate > 0 else 1.0
        return math.floor(speed_factor * 100) / 100  # Truncate

    @staticmethod
    # Merge multiple SRT segments if the gap is small and total duration
    # stays under N milliseconds
    def merge_fast_entries(entries, max_pause_gap=1000, max_merged_duration_ms=8000):
        merged = []
        i = 0
        n = len(entries)
        while i < n:
            curr = entries[i].copy()
            j = i + 1
            while j < n:
                next_ = entries[j]
                gap = next_["start_time"] - curr["end_time"]
                new_duration = next_["end_time"] - curr["start_time"]
                if gap > max_pause_gap or new_duration > max_merged_duration_ms:
                    break
                if not curr["text"].strip().endswith((".", "!", "?")):
                    curr["text"] = curr["text"].strip() + ","
                curr["text"] += " " + next_["text"]
                curr["end_time"] = next_["end_time"]
                j += 1
            merged.append(curr)
            i = j
        return merged

    @staticmethod
    # Convert SRT timestamp to milliseconds
    def convert_to_millisecond(t):
        return t.hours * 3600000 + t.minutes * 60000 + t.seconds * 1000 + int(t.milliseconds)

    # Read SRT file and convert it to our required dictionary format for dubbing
    def read_srt_file(self, file_path):
        subs = pysrt.open(file_path, encoding='utf-8')
        entries = []
        prev_end = 0
        for idx, sub in enumerate(subs, 1):
            start = self.convert_to_millisecond(sub.start)
            end = self.convert_to_millisecond(sub.end)
            pause = start - prev_end if idx > 1 else start
            entries.append({
                'entry_number': idx,
                'start_time': start,
                'end_time': end,
                'text': sub.text.strip(),
                'pause_time': pause,
                'audio_name': f"{idx}.wav",
                'previous_pause': f"{idx}_before_pause.wav",
            })
            prev_end = end

        entries = self.merge_fast_entries(entries)

        ## For debug
        # with open("./old.json", "w", encoding="utf-8") as f:
        #     json.dump(entries, f, indent=2, ensure_ascii=False)
        # with open("/content/new.json", "w", encoding="utf-8") as f:
        #     json.dump(entries, f, indent=2, ensure_ascii=False)

        return entries

    # For TTS, modify this function in the future to use a different TTS or voice cloning tool
    # def text_to_speech_srt(self, text, audio_path, language, voice, actual_duration, default_speed_factor=None):
    #     temp = "./cache/temp.wav"
    #     if default_speed_factor is None:
    #         default_speed_factor = 1.0

    #     # Step 1: Generate clean TTS audio at 1.0x speed (avoid Kokoro noise issue)
    #     path, _ = generate_and_save_audio(text, Language=language, voice=voice, speed=1.0, remove_silence=False, keep_silence_up_to=0.05)

    #     # Step 2: Always adjust the generated TTS to user's speaking speed
    #     if default_speed_factor != 1.0:
    #         temp_wav = path.replace(".wav", "_user_speed.wav")
    #         change_speed(path, temp_wav, default_speed_factor, self.use_ffmpeg, self.ffmpeg_path)
    #         path = temp_wav

    #     # Step 3: Trim edges
    #     remove_edge_silence(path, temp)
    #     audio = AudioSegment.from_file(temp)

    #     # Step 4: If no target duration given, save and exit
    #     if actual_duration == 0:
    #         shutil.move(temp, audio_path)
    #         return

    #     # Step 5: Try regeneration with silence removal if needed
    #     if len(audio) > actual_duration:
    #         path, _ = generate_and_save_audio(text, Language=language, voice=voice, speed=1.0, remove_silence=True, keep_silence_up_to=0.05)
    #         if default_speed_factor != 1.0:
    #             temp_wav = path.replace(".wav", "_tight_user_speed.wav")
    #             change_speed(path, temp_wav, default_speed_factor, self.use_ffmpeg, self.ffmpeg_path)
    #             path = temp_wav
    #         remove_edge_silence(path, temp)
    #         audio = AudioSegment.from_file(temp)

    #     # Step 6: Final fallback — force compress audio to fit
    #     if len(audio) > actual_duration:
    #         factor = len(audio) / actual_duration
    #         final_temp = "./cache/speedup_temp.wav"
    #         change_speed(temp, final_temp, factor, self.use_ffmpeg, self.ffmpeg_path)
    #         shutil.move(final_temp, audio_path)
    #     elif len(audio) < actual_duration:
    #         silence = AudioSegment.silent(duration=actual_duration - len(audio))
    #         (audio + silence).export(audio_path, format="wav")
    #     else:
    #         shutil.move(temp, audio_path)


    # For TTS, modify this function in the future to use a different TTS or voice cloning tool
    def text_to_speech_srt(self, text, audio_path, language, voice, actual_duration, default_speed_factor=None):
        import soundfile as sf
        from librosa import get_duration

        TOLERANCE_MS = 30
        temp = os.path.join(self.cache_dir, "temp.wav")

        if default_speed_factor is None:
            default_speed_factor = 1.0

        # Step 1: Generate clean TTS audio (Kokoro safe speed)
        path, _ = generate_and_save_audio(
            text, Language=language, voice=voice,
            speed=1.0, remove_silence=False, keep_silence_up_to=0.05
        )

        # Step 2: Apply user-defined speaking speed
        if default_speed_factor != 1.0:
            user_speed_path = path.replace(".wav", "_user.wav")
            change_speed(path, user_speed_path, default_speed_factor, self.use_ffmpeg, self.ffmpeg_path)
            path = user_speed_path

        # Step 3: Trim silence
        remove_edge_silence(path, temp)

        # Step 4: Duration analysis (high precision)
        y, sr = sf.read(temp)
        duration_ms = int(get_duration(y=y, sr=sr) * 1000)

        # Step 5: If very close, skip correction
        if abs(duration_ms - actual_duration) <= TOLERANCE_MS:
            shutil.move(temp, audio_path)
            return

        # Step 6: Try regenerating with silence removal if too long
        if duration_ms > actual_duration:
            path, _ = generate_and_save_audio(
                text, Language=language, voice=voice,
                speed=1.0, remove_silence=True, keep_silence_up_to=0.05
            )
            if default_speed_factor != 1.0:
                tighter = path.replace(".wav", "_tight_user.wav")
                change_speed(path, tighter, default_speed_factor, self.use_ffmpeg, self.ffmpeg_path)
                path = tighter
            remove_edge_silence(path, temp)
            y, sr = sf.read(temp)
            duration_ms = int(get_duration(y=y, sr=sr) * 1000)

        # Step 7: Final correction
        if duration_ms > actual_duration + TOLERANCE_MS:
            factor = duration_ms / actual_duration
            corrected = os.path.join(self.cache_dir, "speed_final.wav")
            change_speed(temp, corrected, factor, self.use_ffmpeg, self.ffmpeg_path)
            shutil.move(corrected, audio_path)
        elif duration_ms < actual_duration - TOLERANCE_MS:
            silence = AudioSegment.silent(duration=actual_duration - duration_ms)
            (AudioSegment.from_file(temp) + silence).export(audio_path, format="wav")
        else:
            shutil.move(temp, audio_path)


    @staticmethod
    # Insert silent gaps between two segments
    def make_silence(duration, path):
        AudioSegment.silent(duration=duration).export(path, format="wav")

    @staticmethod
    # Srt save folder
    def create_folder_for_srt(srt_file_path):
        base = os.path.splitext(os.path.basename(srt_file_path))[0]
        folder = f"./dummy/{base}_{str(uuid.uuid4())[:4]}"
        os.makedirs(folder, exist_ok=True)
        return folder

    @staticmethod
    # Join Chunks audio files
    def concatenate_audio_files(paths, output):
        audio = sum([AudioSegment.from_file(p) for p in paths], AudioSegment.silent(duration=0))
        audio.export(output, format="wav")

    # Util funtion to call other funtions
    def srt_to_dub(self, srt_path, output_path, language, voice,speaker_talk_speed=True):
        entries = self.read_srt_file(srt_path)
        folder = self.create_folder_for_srt(srt_path)
        all_audio = []
        if speaker_talk_speed:
          default_speed_factor = self.get_speed_factor(srt_path)
        else:
          default_speed_factor=1.0
        for entry in tqdm(entries):
            self.make_silence(entry['pause_time'], os.path.join(folder, entry['previous_pause']))
            all_audio.append(os.path.join(folder, entry['previous_pause']))
            tts_path = os.path.join(folder, entry['audio_name'])
            self.text_to_speech_srt(entry['text'], tts_path, language, voice, entry['end_time'] - entry['start_time'], default_speed_factor)
            all_audio.append(tts_path)
        self.concatenate_audio_files(all_audio, output_path)

# ---------------------- Entrypoint ----------------------
def srt_process(srt_path, Language="American English", voice_name="af_bella", translate=False,speaker_talk_speed=True):
    if not srt_path.endswith(".srt"):
        gr.Error("Please upload a valid .srt file", duration=5)
        return None

    use_ffmpeg, ffmpeg_path = is_ffmpeg_installed()
    processed_srt = prepare_srt(srt_path, Language, translate)
    output_path = get_subtitle_Dub_path(srt_path, Language)

    SRTDubbing(use_ffmpeg, ffmpeg_path).srt_to_dub(processed_srt, output_path, Language, voice_name,speaker_talk_speed)
    return output_path, output_path

# Example usage
# srt_file_path = "/content/last.srt" # @param {type: "string"}
# dub_audio_path, _ = srt_process(srt_file_path, Language="American English", voice_name="af_bella", translate=False,speaker_talk_speed=False)
# print(f"Audio file saved at: {dub_audio_path}")




def subtitle_ui():
  with gr.Blocks() as demo:

      gr.Markdown(
          """
          # Generate Audio File From Subtitle [Upload Only .srt file]

          To generate subtitles, you can use the [Whisper Turbo Subtitle](https://github.com/NeuralFalconYT/Whisper-Turbo-Subtitle)

          """
      )
      with gr.Row():
          with gr.Column():
              srt_file = gr.File(label='Upload .srt Subtitle File Only')
              # with gr.Row():
              language_name = gr.Dropdown(lang_list, label="🌍 Select Language", value=lang_list[0])
              # with gr.Row():
              voice = gr.Dropdown(
                      voice_names,
                      value='af_bella',
                      allow_custom_value=False,
                      label='🎙️ Choose VoicePack',
                  )
              with gr.Row():
                  generate_btn_ = gr.Button('Generate', variant='primary')

              with gr.Accordion('Other Settings', open=False):
                  speaker_speed_ = gr.Checkbox(value=True, label="⚡ Match With Speaker Average Talking Speed")
                  translate_text = gr.Checkbox(value=False, label='🌐 Translate Subtitle to Selected Language')



          with gr.Column():
              audio = gr.Audio(interactive=False, label='Output Audio', autoplay=True)
              audio_file = gr.File(label='📥 Download Audio')
              with gr.Accordion('Enable Autoplay', open=False):
                  autoplay = gr.Checkbox(value=True, label='Autoplay')
                  autoplay.change(toggle_autoplay, inputs=[autoplay], outputs=[audio])

      # srt_file.submit(
      #     srt_process,
      #     inputs=[srt_file, voice],
      #     outputs=[audio]
      # )
      generate_btn_.click(
          srt_process,
          inputs=[srt_file,language_name,voice,translate_text,speaker_speed_],
          outputs=[audio,audio_file]
      )
      return demo



import click
@click.command()
@click.option("--debug", is_flag=True, default=False, help="Enable debug mode.")
@click.option("--share", is_flag=True, default=False, help="Enable sharing of the interface.")
def main(debug, share):
# def main(debug=True, share=True):
    demo1 = ui()
    demo2 = subtitle_ui()
    demo3 = tutorial()
    demo = gr.TabbedInterface([demo1, demo2,demo3],["Multilingual TTS","SRT Dubbing","VoicePack Explanation"],title="Kokoro TTS")#,theme='JohnSmith9982/small_and_pretty')
    demo.queue().launch(debug=debug, share=share)
    # demo.queue().launch(debug=debug, share=share,server_port=9000)
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
