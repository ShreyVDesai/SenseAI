# from flask import Flask, render_template, request
# import random
# import openai
# from dotenv import load_dotenv
# import os

# app = Flask(__name__)

# openai.api_key = os.getenv("OPENAI_API_KEY")

# # Predefined random responses for now
# random_responses = [
#     "Hello! How can I help you?",
#     "I'm just a bot, but I'm learning!",
#     "That's interesting, tell me more.",
#     "Could you clarify that?",
#     "Thanks for sharing!"
# ]

# # Switch between Random Response Mode and OpenAI API Mode
# USE_OPENAI = True  # Set to True when ready to use OpenAI's API


# @app.route('/', methods=['GET', 'POST'])
# def chat():
#     response = ""
#     if request.method == 'POST':
#         user_input = request.form['user_input']

#         if USE_OPENAI:
#             # Generate response using OpenAI API
#             try:
#                 completion = openai.ChatCompletion.create(
#                     model="gpt-3.5-turbo",
#                     messages=[{"role": "user", "content": user_input}]
#                 )
#                 response = completion.choices[0].message['content']
#             except Exception as e:
#                 response = f"Error: {e}"  # Handle errors gracefully
#         else:
#             # Generate a random response for now
#             response = random.choice(random_responses)

#     return render_template('index.html', response=response)


# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, session
import random
import openai
from dotenv import load_dotenv
import os
import whisper
import pyaudio
import wave
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import threading
import keyboard
import time

app = Flask(__name__)
load_dotenv()


openai.api_key = os.getenv("OPENAI_API_KEY")
app.secret_key = 'abcdefg'

# Predefined random responses for now
random_responses = [
    "Hello! How can I help you?",
    "I'm just a bot, but I'm learning!",
    "That's interesting, tell me more.",
    "Could you clarify that?",
    "Thanks for sharing!"
]

# Constants for audio recording
FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 16000
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "recorded_audio.wav"
whisper_model = whisper.load_model("base")
USE_OPENAI = True  # Switch to OpenAI API mode

# Function to record audio while spacebar is pressed


def record_audio_while_space():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Hold the spacebar to record...")
    frames = []

    while keyboard.is_pressed("space"):
        data = stream.read(CHUNK)
        frames.append(data)

    text_to_speech("Recording stopped.")

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

# Function to convert text to speech using gTTS


# def text_to_speech(text):
#     try:
#         print("Converting text to speech...")
#         tts = gTTS(text=text, lang='en')
#         output_file = "output_audio.mp3"
#         tts.save(output_file)
#         audio = AudioSegment.from_mp3(output_file)
#         play(audio)
#         print("Text-to-speech playback completed.")
#     finally:
#         # Clean up the audio file

#         if os.path.exists(output_file):
#             os.remove(output_file)
#             print(f"Deleted temporary file: {output_file}")
#         if os.path.exists('recorded_audio.wav'):
#             os.remove('recorded_audio.wav')
#             print(f"Deleted temporary file: recorded_audio.wav")

# def text_to_speech(text, mode='text'):
#     output_file = f"output_audio_{mode}.mp3"  # Temporary audio file
#     try:
#         print(f"Generating speech for {mode} mode...")
#         tts = gTTS(text=text, lang='en')
#         tts.save(output_file)

#         audio = AudioSegment.from_mp3(output_file)
#         play(audio)
#     except Exception as e:
#         print(f"Error during TTS or playback: {e}")
#     finally:
#         if os.path.exists(output_file):
#             try:
#                 os.remove(output_file)
#                 print(f"Deleted temporary file: {output_file}")
#             except Exception as e:
#                 print(f"Error deleting {output_file}: {e}")

def text_to_speech(text):
    output_file = "output_audio.mp3"
    try:
        print("Converting text to speech...")
        tts = gTTS(text=text, lang='en')
        tts.save(output_file)
        print(f"File saved: {os.path.exists(output_file)}")

        # Verify file creation before loading
        if os.path.exists(output_file):
            audio = AudioSegment.from_mp3(output_file)
            play(audio)
            print("Text-to-speech playback completed.")
        else:
            print(f"Error: {output_file} was not created.")
    finally:
        # Clean up files
        for file in [output_file, 'recorded_audio.wav']:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"Deleted temporary file: {file}")
                except Exception as e:
                    print(f"Failed to delete {file}: {e}")


@app.route('/', methods=['GET', 'POST'])
def chat(verbal=False):
    session.clear()
    response = ""
    # render_template('index.html', response=response)
    text_to_speech("Press enter to switch to verbal mode")
    time.sleep(1)
    if verbal:

        handle_speech_interaction()
        text_to_speech("Press enter to exit verbal mode")
        time.sleep(1)
        return render_template('index.html', response=response)

    else:

        if request.method == 'POST':
            user_input = request.form['user_input']
            print(user_input)
            # if USE_OPENAI:
            #     try:
            #         completion = openai.ChatCompletion.create(
            #             model="gpt-3.5-turbo",
            #             messages=[{"role": "user", "content": user_input}]
            #         )
            #         response = completion.choices[0].message['content']
            #         text_to_speech(response)  # Read out the AI's response
            #     except Exception as e:
            #         response = f"Error: {e}"  # Handle errors gracefully
            # else:
            #     response = random.choice(random_responses)
            #     text_to_speech(response)  # Read out the random response
    #
    return render_template('index.html', response=response)


def rerecorder():
    text_to_speech("Recording")
    record_audio_while_space()

    # Transcribe the audio
    transcribed_text = speech_to_text()

    # Speak out the transcribed text for confirmation
    text_to_speech(
        f"You said: {transcribed_text}. Press space to rerecord or wait 3 seconds to confirm.")
    st = time.time()
    while st-time.time() < 3:
        if keyboard.is_pressed("space"):
            transcribed_text = rerecorder()
    return transcribed_text

# Function to handle recording, transcription, confirmation, and sending to the model


def handle_speech_interaction():

    while True:
        text_to_speech("Press and hold the spacebar to record")
        # Wait for the spacebar to start recording
        # print("Press and hold the spacebar to record...")
        while not keyboard.is_pressed("space"):
            time.sleep(0.1)

        # Record audio while spacebar is pressed
        # if keyboard.is_pressed("space"):

        transcribed_text = rerecorder()

        # Allow 3 seconds for rerecording
        # time.sleep(3)

        text_to_speech(f"You have confirmed. Your request is being processed.")
        if not keyboard.is_pressed("space"):
            print("Confirmed: Sending to model...")
            # Simulate sending the confirmed text to the Flask app
            # with app.test_request_context('/'):
            user_input = f"Describe the following in terms of its visual components. Be descriptive, but sensitive to the user's condition. The topic: {transcribed_text}"
            # if USE_OPENAI:
            #     completion = openai.ChatCompletion.create(
            #         model="gpt-3.5-turbo",
            #         messages=[{"role": "user", "content": user_input}]
            #     )
            #     response = completion.choices[0].message['content']
            #     print("Model Response:", response)
            #     text_to_speech(response)
            # else:
            #     response = random.choice(random_responses)
            #     print("Random Response:", response)
            #     text_to_speech(response)
            if USE_OPENAI:
                try:
                    completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": user_input}])
                    response = completion.choices[0].message['content']
                except openai.error.OpenAIError as e:
                    response = f"OpenAI API Error: {str(e)}"
                except Exception as e:
                    response = f"An unexpected error occurred: {str(e)}"

        print("Response from OpenAI:", response)

        return response


if __name__ == '__main__':
    # Start the speech interaction in a separate thread
    # threading.Thread(target=handle_speech_interaction, daemon=True).start()
    app.run(debug=True)
