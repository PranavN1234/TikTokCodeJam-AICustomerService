import speech_recognition as sr
import pygame
import time
import openai
from taskrouting_layer import route_task

def record_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please say something...")
        audio_data = recognizer.listen(source)
        print("Recording complete.")
        with open(file_path, "wb") as audio_file:
            audio_file.write(audio_data.get_wav_data())

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

def map_to_route(user_query):
    task = route_task(user_query)

    print(task)

    match task:
        case "check_balance":
            print("This is your balance")
        case "change_information":
            print("What information would you like to change")
        case "block_card":
            print("Blocking card")
        case "issue_new_card":
            print("Issue new card")
        case "flag_fraud":
            print("Flagging fraud")
        case "redirect_agent":
            print("redirecting agent")
        case "chitchat":
            print("chitchatting")
        
        case _:
            print("Something wrong")