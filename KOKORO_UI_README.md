# Kokoro TTS Studio - Colab Notebook

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Fujitoo/Kokoro-TTS-Subtitle/blob/development/kokoro_ui.ipynb)

## Quick Start

### Option 1: Open in Google Colab
Click the badge above to launch the interactive Gradio UI directly in your browser.

### Option 2: Run Locally
```bash
# Install dependencies
pip install gradio

# Run the app
python kokoro_ui.py
```

## Features

### 🎤 Single Speaker Mode
- Enter text and convert to speech with a single voice
- Choose from 22 Kokoro voices
- Optional speaker name labeling

### 👥 Multi Speaker Mode
- Write dialogue scripts in natural format
- Assign different voices to each speaker
- Dynamic speaker management (add/remove)
- Perfect for audiobooks, podcasts, and conversations

## Available Voices

| Category | Voices |
|----------|--------|
| **American Female** | `af_heart`, `af_bella`, `af_nicole`, `af_aoede`, `af_sky`, `af_sarah`, `af_nova`, `af_river` |
| **American Male** | `am_adam`, `am_michael`, `am_echo`, `am_eric`, `am_liam`, `am_onyx` |
| **British Female** | `bf_emma`, `bf_isabella`, `bf_alice`, `bf_lily` |
| **British Male** | `bm_george`, `bm_lewis`, `bm_daniel`, `bm_fable` |

## Script Format (Multi Speaker)

```
Speaker 1: Hello there!
Speaker 2: Hi, how are you doing?
Speaker 1: I'm doing great, thanks for asking!
```

The UI automatically detects unique speaker names from your script.

## Files

| File | Description |
|------|-------------|
| `kokoro_ui.py` | Standalone Gradio app |
| `kokoro_ui.ipynb` | Jupyter/Colab notebook version |

## Requirements

- Python 3.8+
- Gradio 4.0+

```bash
pip install gradio
```

## License

Part of the Kokoro-TTS-Subtitle project.
