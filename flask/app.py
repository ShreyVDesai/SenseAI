import threading
import time
import openai
import keyboard
import os
import whisper
import pyaudio
import wave
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from dotenv import load_dotenv
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import sys

app = Flask(__name__)
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
app.secret_key = 'abcdefg'

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


def text_to_speech(text):
    output_file = "output_audio.mp3"
    try:
        print("Converting text to speech...")
        tts = gTTS(text=text, lang='en')
        tts.save(output_file)

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
                except Exception as e:
                    print(f"Failed to delete {file}: {e}")

# Initial voice prompt asking user if they want to use voice or text mode


def ask_for_mode(max_retries=3):
    retries = 0
    text_to_speech(
        "Would you like to use voice mode or text mode? Please say 'voice' or 'text'. When you're ready, press space and speak.")
    while retries < max_retries:

        # Record the user's response to the question
        response = rerecorder()

        if "voice" in response.lower():
            return "voice"
        elif "text" in response.lower():
            return "text"
        else:
            retries += 1
            text_to_speech(
                f"Sorry, I didn't understand. You have {max_retries - retries} attempts left. Please say 'voice' or 'text'.")

    # If max retries exceeded, default to 'text' mode or provide a fallback
    text_to_speech("Too many failed attempts. Defaulting to text mode.")
    return "text"


# @app.route('/', methods=['GET', 'POST'])
# def start():
#     # Ask the user for the mode (voice or text)
#     mode = ask_for_mode()

#     # Redirect to the appropriate flow based on the mode
#     if mode == "voice":
#         return redirect(url_for('voice_interaction'))
#     else:
#         return redirect(url_for('chat'))
@app.route('/', methods=['GET', 'POST'])
def start():
    return render_template('mode_selection.html')

# Main route for the chat interface (text-based mode)


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    session.clear()
    response = ""

    if request.method == 'POST':
        user_input = request.form['user_input']
        print("User input:", user_input)

        if USE_OPENAI:
            try:
                # Log the API request
                print(f"Making request to OpenAI with input: {user_input}")

                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_input}]
                )

                # Check if response exists
                if 'choices' in completion and len(completion['choices']) > 0:
                    response = completion.choices[0].message['content']
                else:
                    response = "Sorry, I couldn't get a valid response. Please try again."

            except openai.error.OpenAIError as e:
                response = f"OpenAI API Error: {str(e)}"
                print(f"OpenAI API Error: {str(e)}")  # Detailed error logging
            except Exception as e:
                response = f"An unexpected error occurred: {str(e)}"
                print(f"Unexpected error: {str(e)}")  # Log unexpected errors
        

        # Return a JSON response for the frontend to consume
        return jsonify({"response": response})

    return render_template('index.html', response=response)


# # Function to handle verbal interaction (voice mode)
# @app.route('/voice_interaction', methods=['GET', 'POST'])
# def voice_interaction():
#     while True:
#         text_to_speech("Press and hold the spacebar to record.")
#         while not keyboard.is_pressed("space"):
#             time.sleep(0.1)

#         # Record audio while spacebar is pressed
#         transcribed_text = rerecorder()

#         text_to_speech(f"You have confirmed. Your request is being processed.")
#         user_input = f"Describe the following to a visually impaired person. Be descriptive, but sensitive to the user's condition and don't describe it terms of other visual imagery. Describe it in terms of the feelings that it evokes. The topic: {transcribed_text}"

#         if USE_OPENAI:
#             try:
#                 print(f"Making request to OpenAI with input: {user_input}")

#                 completion = openai.ChatCompletion.create(
#                     model="gpt-3.5-turbo",
#                     messages=[{"role": "user", "content": user_input}]
#                 )

#                 # Check if response exists
#                 if 'choices' in completion and len(completion['choices']) > 0:
#                     response = completion.choices[0].message['content']
#                 else:
#                     response = "Sorry, I couldn't get a valid response. Please try again."

#             except openai.error.OpenAIError as e:
#                 response = f"OpenAI API Error: {str(e)}"
#                 print(f"OpenAI API Error: {str(e)}")  # Detailed error logging
#             except Exception as e:
#                 response = f"An unexpected error occurred: {str(e)}"
#                 print(f"Unexpected error: {str(e)}")  # Log unexpected errors

#         print("Response from OpenAI:", response)
#         text_to_speech(f"Here is the response: {response}")

#         # Ask if the user has another question or wants to quit
#         text_to_speech(
#             "Do you have another question or do you want to quit? Say 'another question' or 'quit'.")

#         # Record the user's decision
#         decision = rerecorder().lower()

#         if "quit" in decision:
#             text_to_speech("Goodbye!")
#             os._exit(0)  # Close the Flask application
#         elif "another question" in decision:
#             continue  # Repeat the loop to ask another question

@app.route('/voice_interaction', methods=['GET'])
def voice_interaction():
    # Render a simple page to indicate voice mode is active
    def generate_response():
        while True:
            text_to_speech("Press and hold the spacebar to record.")

            # Wait for spacebar press
            while not keyboard.is_pressed("space"):
                time.sleep(0.1)

            transcribed_text = rerecorder()
            text_to_speech("Processing your request.")

            user_input = f"Describe the following: {transcribed_text}"

            response = "Placeholder response"
            if USE_OPENAI:
                try:
                    completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": user_input}]
                    )
                    response = completion.choices[0].message['content']
                except Exception as e:
                    response = f"Error: {e}"

            text_to_speech(response)

            # Check if the user wants to quit
            text_to_speech("Do you want to ask another question or quit?")
            decision = rerecorder().lower()
            if "quit" in decision:
                text_to_speech("Goodbye!")
                os._exit(0)

    # Run the interaction loop in a background thread
    threading.Thread(target=generate_response).start()

    return render_template('voice_mode.html')


@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        data = request.get_json()  # Get the data from the frontend
        user_message = data.get("message")
        verbal = data.get("verbal")

        # You can add logic for handling the verbal flag, for now just use OpenAI's API
        if USE_OPENAI:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}]
            )

            # Check if response exists
            if 'choices' in completion and len(completion['choices']) > 0:
                response = completion.choices[0].message['content']
            else:
                response = "Sorry, I couldn't get a valid response. Please try again."
        else:
            response = "This is a fallback response."

        # Return the response back to the frontend
        return jsonify({"response": response})
    except Exception as e:
        print(f"Error in /get_response: {str(e)}")
        return jsonify({"response": "Error: Unable to get response."})


# Function to handle recording, transcription, confirmation, and sending to the model


def rerecorder():
    # text_to_speech("Recording... Speak now.")
    time.sleep(1)
    record_audio_while_space()

    # Transcribe the audio
    transcribed_text = speech_to_text()

    # Speak out the transcribed text for confirmation
    text_to_speech(
        f"You said: {transcribed_text}. Press space to rerecord or wait 3 seconds to confirm.")

    start_time = time.time()
    # confirmed = False
    time.sleep(0.1)
    while True:  # Wait for 3 seconds to confirm
        if time.time() - start_time > 3:
            text_to_speech(f"I heard: {transcribed_text}.")
            return transcribed_text
        if keyboard.is_pressed("space"):  # If space is pressed, rerecord
            text_to_speech("recording... Speak now.")
            time.sleep(0.1)
            record_audio_while_space()
            transcribed_text = speech_to_text()  # Rerecord if space is pressed
            start_time = time.time()

    # If no space press, confirm the transcribed text
    # confirmed = True

    # if confirmed:
    #     text_to_speech(f"Confirmed: {transcribed_text}.")
    #     return transcribed_text


if __name__ == '__main__':
    app.run(debug=True)
