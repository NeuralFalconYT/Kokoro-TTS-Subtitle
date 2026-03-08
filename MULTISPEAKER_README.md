# Multi-Speaker TTS Studio

## Overview

The Multi-Speaker TTS Studio allows you to create natural dialogues and conversations with multiple speakers using the Kokoro TTS model. Each speaker can have their own unique voice, and you have full control over pacing, volume normalization, and more.

## Features

### Core Features
- **Multiple Speaker Support**: Define unlimited speakers with unique voice assignments
- **Script-Based Interface**: Write dialogues naturally with speaker labels
- **Voice Assignment**: Assign different Kokoro voices to each speaker
- **Volume Normalization**: Automatically balance audio levels across speakers
- **Custom Pauses**: Insert precise pauses between lines for dramatic effect
- **Inline Voice Overrides**: Change voice for specific lines without modifying config

### Advanced Features
- **Multiple Input Formats**: Support for various script formatting styles
- **Auto-Translation**: Translate entire script to target language
- **Speed Control**: Adjust speaking speed globally
- **Pause Control**: Fine-tune timing between lines

## Usage

### Basic Script Format

```
Speaker1: Hello! How are you today?
Speaker2: I'm doing great, thanks for asking!
Speaker1: Would you like to grab some coffee?
Speaker2: That sounds wonderful!
```

### Speaker Configuration

Define speakers in the configuration box:

```
Speaker1:af_bella
Speaker2:bf_isabella
Speaker3:af_nicole
```

### Advanced Script Features

#### Custom Pauses
Insert precise pauses (in seconds):
```
Speaker1: That's amazing!
{pause: 1.5}
Speaker2: I know, right?
```

#### Inline Voice Override
Temporarily use a different voice for a specific line:
```
Speaker1(af_whisper): This is a secret...
Speaker1: But normally I sound like this.
```

#### Alternative Formats
All these formats are supported:
```
Speaker1: Colon format
[Speaker2] Bracket format
Speaker3 | Pipe format
```

## Running the Interface

### Standalone Mode
```bash
python multispeaker.py
```

### With Custom Options
```bash
python multispeaker.py --debug --share --port 7860
```

### Integration with Main App
The multi-speaker module can be integrated into the main `beta.py` application by importing the UI:

```python
from multispeaker import create_multispeaker_ui

# In your main app
demo_multispeaker = create_multispeaker_ui()
demo = gr.TabbedInterface([demo1, demo2, demo_multispeaker], 
                          ["TTS", "SRT Dubbing", "Multi-Speaker"])
```

## Examples

### Podcast Intro
```
Host:af_heart
CoHost:bf_isabella
Guest:af_bella

Host: Welcome to Tech Talk Podcast!
CoHost: Great to have you all here!
Guest: Thanks for having me on the show.
Host: Today we're discussing AI advancements.
```

### Audiobook Dialogue
```
Narrator:af_nicole
Hero:af_bella
Villain:bf_isabella

Narrator: The hero approached the villain cautiously.
Hero: There's still time to do the right thing.
{pause: 0.5}
Villain: You really think I'd listen to you?
Narrator: The tension was palpable.
```

### Customer Service Scenario
```
Agent:af_bella
Customer:bf_emma

Agent: Thank you for calling support. How can I help?
Customer: My account seems to have an issue.
Agent: I'd be happy to look into that for you.
{pause: 0.3}
Customer: Great, I appreciate your help!
```

## Tips for Best Results

1. **Voice Selection**: Choose voices with complementary tones for natural conversations
2. **Pause Timing**: Use 0.2-0.5s for natural conversation flow, 0.5-1.5s for dramatic pauses
3. **Volume Normalization**: Keep this enabled for consistent output levels
4. **Script Length**: For very long scripts, consider breaking into scenes
5. **Speaker Names**: Use simple, alphanumeric names (no spaces or special characters)

## Troubleshooting

### No Audio Generated
- Check that all speakers have voice assignments
- Verify speaker names match between config and script
- Ensure text doesn't contain unsupported characters

### Audio Quality Issues
- Try reducing speed if audio sounds distorted
- Enable volume normalization for consistent levels
- Check that eSpeak NG is properly installed

### Voice Not Changing
- Verify voice name is correct (check Voice Library)
- Ensure voice is compatible with selected language
- Try inline voice override for testing

## Voice Library

Available voices depend on the Kokoro model. Common voices include:

**American English (a)**:
- Female: `af_bella`, `af_nicole`, `af_heart`, `af_sarah`
- Male: `am_adam`, `am_michael`

**British English (b)**:
- Female: `bf_isabella`, `bf_emma`, `bf_giselle`
- Male: `bm_george`, `bm_lewis`

**Other Languages**:
- Hindi: `hf_alpha`, `hf_beta`
- Spanish: `ef_dora`, `em_alex`
- French: `ff_siwis`, `fm_remy`
- Italian: `if_sara`, `im_marco`
- Portuguese: `pf_dora`, `pm_rafael`
- Japanese: `jf_nezumi`, `jm_kumo`
- Chinese: `zf_xiaoni`, `zm_yunjian`

## API Usage

You can also use the multi-speaker functions programmatically:

```python
from multispeaker import (
    parse_speaker_config,
    parse_script,
    create_multispeaker_audio
)

# Parse configuration
speakers = parse_speaker_config("Speaker1:af_bella\nSpeaker2:bf_isabella")

# Parse script
lines = parse_script("Speaker1: Hello!\nSpeaker2: Hi there!")

# Generate audio
output_path, audio_array = create_multispeaker_audio(
    script_lines=lines,
    speaker_config=speakers,
    language="American English",
    speed=1.0,
    pause_between_lines=0.2,
    normalize_volumes=True
)
```

## Future Enhancements

Planned features:
- [ ] Per-speaker speed control
- [ ] Export to multiple formats (MP3, OGG)
- [ ] Real-time preview
- [ ] Speaker timeline visualization

## Credits

Built on top of the amazing [Kokoro TTS](https://huggingface.co/hexgrad/Kokoro-82M) model by hexgrad.

## License

Same as the main project - Kokoro model is licensed under Apache License 2.0.
