#  MINI-PROJECT 4

## **Title**
**SenseAI: Immersive Audio Descriptions for Low-Vision and Blind People**

## **Description**
**SenseAI** is a Flask-based web application designed to enrich the sensory experiences of low-vision and blind People. It provides a dynamic interface with **Voice Interaction Mode** as the primary feature, allowing people to explore their surroundings and access information in a way that is both **immersive** and **emotionally engaging**. 

Using **Generative AI** , SenseAI delivers real-time audio descriptions that go beyond simple functionality needs. It creates vivid, sensory-rich narratives, offering blind and low-vision People a deeper connection to the environment around them. For instance, instead of saying, “Red is a color.,” SenseAI might describe it as:  
*"Red is a bold and vibrant color that is often associated with strong emotions like love, passion, and energy. It can remind you of things like ripe strawberries, juicy apples, or a cozy fire. When you think of red, you might imagine a stop sign or a beautiful sunset painting the sky in warm hues. It's a color that can make you feel excited and alive!"*



## **Features**
- **Voice and Text Modes**:  
  - People can interact with the system using intuitive voice commands, offering a hands-free experience or can use text mode depending on their preference.  
  - Designed with accessibility and simplicity, ensuring a playful, engaging interaction for People.  

## **Target Audience**
**SenseAI** specifically aims to help **low-vision and blind People**, creating an application that:  
- **Engages curiosity and creativity** through rich, imaginative narratives.  
- **Supports learning and exploration**, making it easier for People to understand their surroundings and participate in activities.  
- **Enhances accessibility and independence**, allowing People to navigate and engage with the world more confidently.  


## Directory Structure

### Files

#### `flask/app.py`
- This is the main Flask application file.
- Handles routing for different pages of the application.
- Manages the application logic for voice and text interaction modes.
------
### `flask/static/` Directory

This folder holds the CSS templates containing design elements. It includes:
------
### `flask/templates/` Directory

This folder holds the HTML templates for rendering the web pages dynamically. It includes:

#### `index.html`
- The text mode page of the application.

#### `mode_selection.html`
- A page allowing users to select between interaction modes (Voice or Text).
- Landing page for the application.

#### `voice_mode.html`
- The page for Voice Interaction mode.
- Provides instructions for voice-based interaction and ensures user-friendly guidance.
-----
#### `documentation.md`
- Contains detailed documentation of the project's structure and functionality.
- Serves as a guide for developers and contributors to understand the project.

#### `requirements.txt`
- Lists all the dependencies required to run the application.
- Helps to set up the project environment by installing the necessary libraries.


-------


# Instructions to Run the SenseAI Flask App

1. **Open the files in a Code editor**

2. **Install dependencies:**
   Ensure Python is installed, then run the following command to install required packages:
   ```
   pip install -r requirements.txt
   ```

3. **Run the Flask app:**
   Start the Flask app by running: Make sure to give relative paths where ever necessary or cd into the flask directory.
   ```
   python app.py
   ```

4. **Access the app:**
   Open your browser and go to `http://127.0.0.1:5000/` to use the application.




#Testing

User can test :

1.  **Text Mode** at 'http://127.0.0.1:5000/chat' . Use inovative prompts to see how the system responds.

2. **Voice mode** at 'http://127.0.0.1:5000/voice_interaction'. User can test for the model responses to the questions as well as how the system transcribes the questions and answers.