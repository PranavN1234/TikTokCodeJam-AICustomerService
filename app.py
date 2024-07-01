from flask import Flask, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import pygame
import openai
from io import BytesIO
from pydub import AudioSegment
from pydub.utils import which
from dotenv import load_dotenv

# Load the .env file
load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS
socketio = SocketIO(app, cors_allowed_origins="*")

# Set the path for ffmpeg
AudioSegment.converter = which("ffmpeg")



@socketio.on('audio')
def handle_audio(audio_data):
    audio_segment = AudioSegment.from_file(BytesIO(audio_data), format="webm")
    audio_segment.export("received_audio.wav", format="wav")

    play_audio('received_audio.wav')

    # Generate TTS audio
    tts_text = "This is a response from the server."
    synthesize_audio(tts_text)

    # Send TTS audio back to the frontend
    with open("output.mp3", "rb") as audio_file:
        tts_audio = audio_file.read()
        socketio.emit('tts_audio', tts_audio)

def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue

def synthesize_audio(text):
    response = openai.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
    )
    response.stream_to_file('output.mp3')

if __name__ == '__main__':
    socketio.run(app, port=5001, debug=True)
