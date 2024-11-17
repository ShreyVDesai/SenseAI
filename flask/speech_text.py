import whisper
import pyaudio
import wave
from gtts import gTTS
from playsound import playsound
from pydub import AudioSegment
from pydub.playback import play

def text_to_speech(text):
    print("Converting text to speech...")
    tts = gTTS(text=text, lang='en')
    tts.save("output_audio.mp3")
    # Load the audio with pydub and play it
    audio = AudioSegment.from_mp3("output_audio.mp3")
    play(audio)
    print("Text-to-speech playback completed.")


# Constants for audio recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "recorded_audio.wav"

# Initialize Whisper model (base model is recommended for general use)
whisper_model = whisper.load_model("base")

# Function to record audio
def record_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Recording...")
    frames = []

    for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording completed.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded audio as a .wav file
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Function to convert speech to text using Whisper
def speech_to_text():
    print("Converting speech to text...")
    result = whisper_model.transcribe(WAVE_OUTPUT_FILENAME)
    text = result["text"]
    print("Transcribed text:", text)
    return text

# # Function to convert text to speech using gTTS
# def text_to_speech(text):
#     print("Converting text to speech...")
#     tts = gTTS(text=text, lang='en')
#     tts.save("output_audio.mp3")
#     playsound("output_audio.mp3")
#     print("Text-to-speech playback completed.")

# Main function to run the STT and TTS process
def main():
    # Step 1: Record audio
    record_audio()

    # Step 2: Convert recorded audio to text
    transcribed_text = speech_to_text()

    # Step 3: Convert text back to speech
    text_to_speech(transcribed_text)

if __name__ == "__main__":
    main()
