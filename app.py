from flask import Flask, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import openai
from io import BytesIO
from pydub import AudioSegment
from pydub.utils import which
from dotenv import load_dotenv
from routing.map_to_task import handle_confirmation_response, map_to_route
from utils import transcribe_audio, synthesize_audio
from db_connection import db_connection, close_db_connection
from auth_manager import Authmanager
from user_data import UserData

# Load the .env file
load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS
socketio = SocketIO(app, cors_allowed_origins="*")

# Set the path for ffmpeg
AudioSegment.converter = which("ffmpeg")

connection = None
auth_manager = None
user_data = None
auth_steps = None
current_step_index = 0
authenticated = False
pending_task = None

@app.route('/')
def index():
    return "Server is running"

def send_prompt(prompt_text, final=False):
    if not prompt_text:
        emit('error', {'message': 'Prompt text cannot be empty.'})
        return
    print(f"Sending prompt: {prompt_text}")
    synthesize_audio(prompt_text)
    with open("output.mp3", "rb") as audio_file:
        tts_audio = audio_file.read()
    emit('tts_audio', {'audio': tts_audio, 'prompt': prompt_text, 'final': final})

@socketio.on('start')
def start_interaction():
    global connection, auth_manager, user_data, auth_steps, current_step_index, authenticated
    connection = db_connection()
    if not connection:
        emit('error', {'message': 'Failed to connect to the database. Exiting.'})
        return

    auth_steps = [
        {
            "prompt": "Please can you tell me your account number.",
            "variable": "account_number",
            "semantic_description": "Extract only account number as integer no spaces or special characters.",
            "auth_function": "authenticate_account_number"
        },
        {
            "prompt": "Please state your first and last name.",
            "variable": "name",
            "semantic_description": "Extract the name from the user query in english just the name no special formatting needed.",
            "auth_function": "authenticate_name"
        },
        {
            "prompt": "Please say your date of birth",
            "variable": "dob",
            "semantic_description": "Extract the date of birth from the user response in YYYY-MM-DD.",
            "auth_function": "authenticate_dob"
        },
        {
            "prompt": "",  # This will be dynamically set based on the security question
            "variable": "security_answer",
            "semantic_description": "Extract just the security answer from the user response, so for example the response is I want to be an artist, just take artist as the answer ",
            "auth_function": "authenticate_security_answer"
        }
    ]

    auth_manager = Authmanager(connection, auth_steps)
    user_data = auth_manager.user_data
    current_step_index = 0
    authenticated = False

    next_step = auth_steps[current_step_index]
    send_prompt(next_step["prompt"])

@socketio.on('audio_response')
def handle_audio_response(audio_data):
    global auth_manager, auth_steps, current_step_index, authenticated, pending_task

    print("Received audio response")
    audio_segment = AudioSegment.from_file(BytesIO(audio_data), format="webm")
    audio_segment.export("response_audio.wav", format="wav")

    response_text = transcribe_audio('response_audio.wav')
    print(f"Transcribed text: {response_text}")

    if not authenticated:
        next_step = auth_steps[current_step_index]
        response_value = auth_manager.handle_auth_step_response(response_text, next_step)
        
        if response_value:
            auth_function = getattr(auth_manager, next_step["auth_function"])
            print(f"Auth function result: {auth_function(response_value)}")
            if auth_function(response_value):
                current_step_index += 1
                if current_step_index < len(auth_steps):
                    next_step = auth_steps[current_step_index]
                    if next_step["variable"] == "security_answer":
                        next_step["prompt"] = f"What is the answer to your security question: {user_data.get_data('security_question')}?"
                    send_prompt(next_step["prompt"])
                else:
                    user_data.set_data("authenticated", True)
                    authenticated = True
                    send_prompt("Authentication successful. Welcome to Premier Trust Bank. I am Jessica your AI Assistant.", final=True)
            else:
                send_prompt(f"Authentication failed for {next_step['variable'].replace('_', ' ')}. Please try again.")
        else:
            send_prompt("I'm sorry, I didn't understand that. Please try again.")
    else:
        if pending_task:
            result = handle_confirmation_response(response_text, connection, pending_task)
            if result:
                pending_task = None
            else:
                send_prompt("Confirmation not received. Please try again.")
        else:
            pending_task = map_to_route(response_text, connection)
            if isinstance(pending_task, str):
                send_prompt(pending_task)
            elif pending_task:
                # Do not prompt for additional help yet; wait for confirmation response first.
                pass
            else:
                send_prompt("Thank you for using our service. Goodbye.", final=True)
                close_db_connection(connection)

if __name__ == '__main__':
    socketio.run(app, port=5001, debug=True)
