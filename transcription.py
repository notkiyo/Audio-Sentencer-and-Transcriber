import os
import sys
import wave
import json
import vosk
from tqdm import tqdm

def transcribe_audio(file_path, model):
    wf = wave.open(file_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000, 32000, 48000]:
        print(f"Skipping {file_path}. Audio file must be WAV format mono PCM.")
        return ""

    rec = vosk.KaldiRecognizer(model, wf.getframerate())

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
    wf.close()

    transcription = " ".join([res.get('text', '') for res in results])
    return transcription

def transcribe_folder(audio_folder, model):
    transcriptions = {}
    audio_files = [file_name for file_name in os.listdir(audio_folder) if os.path.isfile(os.path.join(audio_folder, file_name)) and file_name.endswith('.wav')]

    for file_name in tqdm(audio_files, desc=f"Transcribing {audio_folder}"):
        file_path = os.path.join(audio_folder, file_name)
        transcription = transcribe_audio(file_path, model)
        transcriptions[file_name] = transcription

    return transcriptions

def main(audio_folders, model_folder):
    if not os.path.exists(model_folder):
        print("Model folder not found. Please provide a valid model folder path.")
        return

    model = vosk.Model(model_folder)
    all_transcriptions = {}

    for audio_folder in audio_folders:
        if not os.path.exists(audio_folder):
            print(f"Audio folder {audio_folder} not found. Skipping.")
            continue
        
        transcriptions = transcribe_folder(audio_folder, model)
        all_transcriptions[audio_folder] = transcriptions

    return all_transcriptions

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python transcribe_folders.py <model-folder> <audio-folder-1> [<audio-folder-2> ... <audio-folder-N>]")
        sys.exit(1)

    model_folder = sys.argv[1]
    audio_folders = sys.argv[2:]

    all_transcriptions = main(audio_folders, model_folder)

    for folder, transcriptions in all_transcriptions.items():
        print(f"Transcriptions for folder {folder}:")
        for file_name, transcription in transcriptions.items():
            print(f"  Transcription for {file_name}:\n{transcription}")
