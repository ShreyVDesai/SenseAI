"""
Voice and Text-Based Conversational AI Application

This Flask-based application allows users to interact with an AI model using either text-based or voice-based input.
The application supports recording audio, converting it to text using Whisper, and generating AI-driven responses.
It also features text-to-speech playback for visually-impaired users, aiming to provide a sensory-rich experience.
"""


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

# Initialize Flask app and load environment variables
app = Flask(__name__)
load_dotenv()

# Set OpenAI API key and app secret key
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


def record_audio_while_space():
    """
    Record audio while the spacebar is pressed and save it to a .wav file.

    Uses PyAudio for real-time audio recording. """
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


def speech_to_text():
    """
    Convert the recorded audio to text using the Whisper model.

    Returns:
        str: Transcribed text from the audio.
    """
    print("Converting speech to text...")
    result = whisper_model.transcribe(WAVE_OUTPUT_FILENAME)
    text = result["text"]
    print("Transcribed text:", text)
    return text


def text_to_speech(text):
    """
    Convert text to speech using gTTS and play it using pydub.

    Args:
        text (str): The text to be converted to speech.
    """
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


def ask_for_mode(max_retries=3):
    """
    Prompt the user to select between 'voice' or 'text' mode.

    Args:
        max_retries (int): Maximum number of retries for valid input.

    Returns:
        str: Selected mode ('voice' or 'text').
    """
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


@app.route('/', methods=['GET', 'POST'])
def start():
    """
    Render the mode selection page.

    Returns:
        Template: HTML template for mode selection.
    """
    return render_template('mode_selection.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """
    Handle text-based chat interactions with the AI model.

    Uses OpenAI's GPT-3.5 Turbo for generating responses.
    """

    if 'conversation_history' not in session:
        session['conversation_history'] = []
    # session.clear()
    response = ""

    if request.method == 'POST':
        user_input = request.form['user_input']
        print("User input:", user_input)
        user_input = f"""
        Describe the following: {user_input}.
        Note: The user is blind and cannot perceive visual descriptions such as color, shape, or beauty. 
        So, Answer them by conveying the essence, beauty, visual elements and emotional intensity of the object or scene using descriptions that appeal to other senses such as how it smells, feels to the touch, sounds, tastes, or evokes emotion. 
        Help the user perceive it in a way that is as vivid and awe-inspiring as if they could see it. 
        Your description should make them feel like they aren't blind but at the same time it should not use any terms of blindness or visual impairment or tell them they are blind.
        Try to describe the visual elements using other senses so the blind person can experience with their knowledge of other senses, how it feels to behold it.
        Avoid NSFW content entirely. If the question contains illegal, NSFW content or contains content not for kids, respond with: "Sorry, I can't answer that."
        If the question asks you to describe adult or romantic themes avoid it entirely and respond with: "Sorry, I can't answer that."
        If your answer contains adult or romantic themes, avoid it entirely and respond with: "Sorry, I can't answer that."
        """

        # Append user's input to conversation history
        session['conversation_history'].append(
            {"role": "user", "content": user_input})

        if USE_OPENAI:
            try:
                # Log the API request
                print(f"Making request to OpenAI with input: {user_input}")

                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=session['conversation_history']
                )

                # Check if response exists
                if 'choices' in completion and len(completion['choices']) > 0:
                    response = completion.choices[0].message['content']
                else:
                    response = "Sorry, I couldn't get a valid response. Please try again."

                # Append the bot's response to conversation history
                session['conversation_history'].append(
                    {"role": "assistant", "content": response})

            except openai.error.OpenAIError as e:
                response = f"OpenAI API Error: {str(e)}"
                print(f"OpenAI API Error: {str(e)}")  # Detailed error logging
            except Exception as e:
                response = f"An unexpected error occurred: {str(e)}"
                print(f"Unexpected error: {str(e)}")  # Log unexpected errors

        # Return a JSON response for the frontend to consume
        return jsonify({"response": response})

    return render_template('index.html', response=response)

# Clear conversation history route


@app.route('/clear', methods=['POST'])
def clear_history():
    """
    Clear the conversation history stored in the session.

    Returns:
        JSON: Confirmation message.
    """
    session.pop('conversation_history', None)
    return jsonify({"message": "Conversation history cleared."})


@app.route('/voice_interaction', methods=['GET'])
def voice_interaction():
    """
    Activate the voice-based interaction mode.

    Returns:
        Template: HTML template for voice interaction.
    """
    def generate_response():
        while True:
            text_to_speech("Press and hold the spacebar to record.")

            # Wait for spacebar press
            while not keyboard.is_pressed("space"):
                time.sleep(0.1)

            transcribed_text = rerecorder()
            text_to_speech("Processing your request.")

            user_input = f"""
            Describe the following: {transcribed_text}.
            Note: The user is blind and cannot perceive visual descriptions such as color, shape, or beauty. 
            So, Answer them by conveying the essence, beauty, visual elements and emotional intensity of the object or scene using descriptions that appeal to other senses such as how it smells, feels to the touch, sounds, tastes, or evokes emotion. 
            Help the user perceive it in a way that is as vivid and awe-inspiring as if they could see it. 
            Your description should make them feel like they aren't blind but at the same time it should not use any terms of blindness or visual impairment or tell them they are blind.
            Try to describe the visual elements using other senses so the blind person can experience with their knowledge of other senses, how it feels to behold it.
            Avoid NSFW content entirely. If the question or subject is inappropriate, illegal or NSFW, respond with: "Sorry, I can't answer that."
            """

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
    """
    Record and confirm audio input, converting it to text.

    Returns:
        str: Confirmed transcribed text from the recording.
    """
    time.sleep(1)
    record_audio_while_space()

    # Transcribe the audio
    transcribed_text = speech_to_text()

    # Speak out the transcribed text for confirmation
    text_to_speech(
        f"You said: {transcribed_text}. Press space to rerecord or wait 3 seconds to confirm.")

    start_time = time.time()

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


if __name__ == '__main__':
    app.run(debug=True)
