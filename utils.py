import speech_recognition as sr
import pygame
import time
import openai
from difflib import SequenceMatcher


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
    response = openai.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
  
    response.stream_to_file('output.mp3')
