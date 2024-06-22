import os
from pydub import AudioSegment, silence
from tqdm import tqdm  # Import tqdm for progress bar

# Function to detect pauses in the audio
def detect_pauses(audio, min_silence_len=500, silence_thresh=-40):
    # Detect silent parts of the audio
    pauses = silence.detect_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh
    )
    return pauses

# Function to segment audio based on pauses
def segment_audio_by_pauses(audio, pauses):
    segments = []
    start_time = 0
    for start_pause, end_pause in pauses:
        end_time = start_pause
        segment = audio[start_time:end_time]
        segments.append(segment)
        start_time = end_pause
    # Add the last segment
    if start_time < len(audio):
        segment = audio[start_time:]
        segments.append(segment)
    return segments

# Function to process audio files sequentially
def process_audio_files_sequential(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get the list of audio files in the input folder
    audio_files = [f for f in os.listdir(input_folder) if f.endswith(".wav")]

    # Iterate over all audio files in the input folder with a progress bar
    for audio_filename in tqdm(audio_files, desc="Processing audio files"):
        audio_path = os.path.join(input_folder, audio_filename)
        # Load the audio file
        audio = AudioSegment.from_wav(audio_path)
        # Detect pauses in the audio
        pauses = detect_pauses(audio)
        # Segment audio based on pauses
        segments = segment_audio_by_pauses(audio, pauses)
        # Save each segment to the output folder with a progress bar
        for i, segment in tqdm(enumerate(segments), desc=f"Segmenting {audio_filename}", total=len(segments), leave=False):
            segment.export(os.path.join(output_folder, f"{os.path.splitext(audio_filename)[0]}_segment_{i}.wav"), format="wav")

# Example usage
input_folder = r"C:\Users\notam\Music\ttsbraa"
output_folder =  r"C:\Users\notam\Music\ttsaudio"
process_audio_files_sequential(input_folder, output_folder)
