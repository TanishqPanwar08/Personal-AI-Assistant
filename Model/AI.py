import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import datetime
from textblob import TextBlob
import pickle

# Initialize text to speech engine
engine = pyttsx3.init()

# Set female voice
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Index 1 represents a female voice

model_file_path = "D:\Hand Gesture\Model\Saved Model\model.pkl"

# Function to speak
def speak(text, emotion=""):
    if emotion:
        text += f" ({emotion})"
    engine.say(text)
    engine.runAndWait()

# Function to recognize speech
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio)
        print("User said:", query)
        return query.lower()
    except sr.UnknownValueError:
        print("Sorry, I didn't get that.")
        return ""
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        return ""

# Function to open a website
def open_website(url):
    webbrowser.open(url)
    
def speech_recg_model(file_path):
    with open(file_path, 'rb') as file:
        model = pickle.load(file)
    return model 

# Function to adjust system volume
def set_volume(volume_level):
    os.system("nircmd.exe changesysvolume " + str(volume_level))

# Function to adjust system brightness
def set_brightness(percentage):
    os.system("nircmd.exe setbrightness " + str(percentage))

# Function to open an application
def open_app(app_name):
    try:
        os.startfile(app_name)
    except FileNotFoundError:
        speak("App not found.")

# Function to analyze emotion from text
def analyze_emotion(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0.5:
        return "excited"
    elif sentiment > 0:
        return "happy"
    elif sentiment < -0.5:
        return "angry"
    elif sentiment < 0:
        return "sad"
    else:
        return "neutral"

print("Hi, I'm your personal AI assistant. How can I help you?")

# Main loop
if __name__ == "__main__":
    speak("Hi, I'm your personal AI assistant. How can I help you?")

    while True:
        speak("What can I do for you?")
        print('What can I do for you?')
        command = listen()

        # Analyze emotion from the user's command
        user_emotion = analyze_emotion(command)

        if "open web" in command:
            words = command.split()
            website = words[words.index("web") + 1]
            open_website("https://www." + website + ".com")
            speak(f"Task is done. What's next?", user_emotion)
        elif "set volume to" in command:
            words = command.split()
            try:
                volume_level = int(words[words.index("to") + 1])
                set_volume(volume_level)
                speak(f"Volume set to {volume_level}.", user_emotion)
            except (ValueError, IndexError):
                speak("Please specify the volume level.")
        elif "set brightness to" in command:
            words = command.split()
            try:
                index_to = words.index("to")
                brightness_percentage = int(words[index_to + 1])
                set_brightness(brightness_percentage)
                speak(f"Brightness set to {brightness_percentage} percent.", user_emotion)
            except (ValueError, IndexError):
                speak("Please specify the brightness level.")
        elif "time" in command:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            speak(f"The current time is {current_time}.", user_emotion)
        elif "open app" in command:
            words = command.split()
            app_name = " ".join(words[words.index("app") + 1:])
            open_app(app_name)
            speak(f"Task is done. What's next?", user_emotion)
        elif "stop" in command or "exit" in command:
            speak("Goodbye!", user_emotion)
            break

        # Add more commands for other functionalities
