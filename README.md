# Python Sentencer: Audio Sentence Segmentation and Transcription

## Overview

**Python Sentencer** is a Python script designed to process audio files by segmenting them into sentences based on pauses. It uses the Vosk speech recognition model to transcribe the audio and generate subtitles. The tool is ideal for applications in creating audiobooks, podcasts, and other spoken content requiring precise audio segmentation and transcription.

## Features

- **Sentence-based Audio Segmentation**: Cuts audio at sentence boundaries based on pauses detected in the speech.
- **Transcription**: Uses the Vosk speech recognition model to generate text transcriptions of the audio.
- **Subtitle Creation**: Generates subtitle files compatible with most video players.

## Requirements

- Python 3.6 or later
- `vosk` library
- `pydub` library
- `numpy` library
- Audio file in WAV format

## Installation

1. Install the required Python libraries:

   ```bash
   pip install vosk pydub numpy
   ```

2. Download a Vosk model (e.g., `vosk-model-small-en-us-0.15`) from the [Vosk models page](https://alphacephei.com/vosk/models) and extract it to a directory of your choice.

## Usage

1. **Prepare the Audio File**: Ensure your audio file is in WAV format. You can use tools like `ffmpeg` to convert other audio formats to WAV.

2. **Run the Script**: Execute the script with the required arguments.

   ```bash
   python sentencer.py --audio_file path/to/audio.wav --model_dir path/to/vosk-model
   ```

### Command-Line Arguments

- `--audio_file`: Path to the input audio file (in WAV format).
- `--model_dir`: Path to the directory containing the Vosk model.

### Example

```bash
python sentencer.py --audio_file my_audio.wav --model_dir vosk-model-small-en-us-0.15
```

## Script Details

### 1. Audio Segmentation

The script uses `pydub` to process the audio file, detecting pauses to identify sentence boundaries. It then segments the audio file accordingly.

### 2. Transcription

The Vosk speech recognition model transcribes each segment of the audio, generating a textual representation of the speech.

### 3. Subtitle Generation

Based on the transcription, the script generates a subtitle file (e.g., in SRT format), which can be used in video players for synchronized text display.

## Example Script

Here's an example implementation of the `sentencer.py` script:

```python
import os
import wave
import json
import argparse
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
import numpy as np

def transcribe_audio(audio_path, model_dir):
    wf = wave.open(audio_path, "rb")
    model = Model(model_dir)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(json.loads(rec.Result()))
        else:
            results.append(json.loads(rec.PartialResult()))
    results.append(json.loads(rec.FinalResult()))
    return results

def segment_audio(audio_path, segments):
    audio = AudioSegment.from_wav(audio_path)
    for i, (start, end) in enumerate(segments):
        segment = audio[start:end]
        segment.export(f"segment_{i}.wav", format="wav")

def generate_subtitles(transcription, output_file="subtitles.srt"):
    with open(output_file, "w") as f:
        for i, result in enumerate(transcription):
            if "result" in result:
                words = result["result"]
                start_time = words[0]["start"]
                end_time = words[-1]["end"]
                text = " ".join([w["word"] for w in words])
                f.write(f"{i+1}\n")
                f.write(f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n")
                f.write(f"{text}\n\n")

def format_timestamp(seconds):
    ms = int((seconds % 1) * 1000)
    s = int(seconds)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def main(audio_file, model_dir):
    # Step 1: Transcription
    transcription = transcribe_audio(audio_file, model_dir)

    # Step 2: Identify sentence boundaries (simple heuristic based on pauses)
    segments = []
    segment_start = 0
    for result in transcription:
        if "result" in result:
            words = result["result"]
            for i in range(1, len(words)):
                if words[i]["start"] - words[i-1]["end"] > 1.0:  # Pause longer than 1 second
                    segment_end = int(words[i-1]["end"] * 1000)
                    segments.append((segment_start, segment_end))
                    segment_start = int(words[i]["start"] * 1000)
            segment_end = int(words[-1]["end"] * 1000)
    segments.append((segment_start, segment_end))

    # Step 3: Segment the audio
    segment_audio(audio_file, segments)

    # Step 4: Generate subtitles
    generate_subtitles(transcription)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Segment audio into sentences and generate transcription.")
    parser.add_argument("--audio_file", required=True, help="Path to the input audio file (WAV format).")
    parser.add_argument("--model_dir", required=True, help="Path to the Vosk model directory.")
    args = parser.parse_args()
    main(args.audio_file, args.model_dir)
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue on the GitHub repository.

## Contact

For any questions or inquiries, please contact [kiyo] at [.............].

---

This README provides an overview of the Python Sentencer script, including its features, requirements, usage instructions, and example code. For further details and updates, please refer to the project's GitHub repository.
