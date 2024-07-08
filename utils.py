import speech_recognition as sr
import pygame
import time
import openai
from difflib import SequenceMatcher
from datetime import datetime
from ai_summerizer import get_summary
from user_data import UserData
from db_connection import db_connection

conversation_log = []  # Global variable to store the conversation log

def calculate_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def record_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please say something...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio_data = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            print("Recording complete.")
            with open(file_path, "wb") as audio_file:
                audio_file.write(audio_data.get_wav_data())
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start.")
        except Exception as e:
            print(f"An error occurred: {e}")

def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    # Wait until the audio is finished playing
    while pygame.mixer.music.get_busy():
        time.sleep(1)

def transcribe_audio(file_path):
    audio_file = open(file_path, "rb")
    transcription = openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    return transcription.text

def synthesize_audio(text):
    print("synthesizing text->", text)
    response = openai.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
  
    response.stream_to_file('output.mp3')

def prompt_and_listen(prompt_text):
    synthesize_audio(prompt_text)
    play_audio('output.mp3')
    record_audio('response.wav')
    return transcribe_audio('response.wav')

def log_conversation(role, text):
    global conversation_log
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conversation_log.append(f"{timestamp} - {role}: {text}")
    print(f"Logged conversation: {timestamp} - {role}: {text}")

def summarize_call(call_data):
    ai_summerizer = get_summary(call_data)
    summary_1 = ai_summerizer.summary
    tasks_1 = ai_summerizer.tasks
    print(f"Summary: {summary_1}")
    print(f"Tasks: {tasks_1}")
    return [summary_1, tasks_1]

def save_conversation(connection, customer_id):
    global conversation_log
    call_data = "\n".join(conversation_log)
    try:
        if not connection:
            return None
        else:
            summerized_call = summarize_call(call_data)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO pba_call_details (customer_id, call_summary, tasks_performed) VALUES (%s, %s, %s)", (customer_id, summerized_call[0], summerized_call[1]))
            connection.commit()
            print("Call details stored successfully.")
        conversation_log = []
    
    except Exception as e:
        print(f"An error occurred while saving conversation: {e}")
        return None
    