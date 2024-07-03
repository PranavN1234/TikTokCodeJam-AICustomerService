from flask import Flask, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import openai
from io import BytesIO
from pydub import AudioSegment
from pydub.utils import which
from dotenv import load_dotenv
from routing.map_to_task import map_to_route, handle_confirmation_response
from utils import transcribe_audio, synthesize_audio
from db_connection import db_connection, close_db_connection
from auth_manager import Authmanager
from user_data import UserData
from audio_data import AudioData
from tasks.block_card import handle_block_card_selection
from tasks.flag_transaction import handle_transaction_id_response, handle_flag_reason_response
from tasks.request_new_card import handle_card_type_selection
from tasks.change_information import handle_change_info_selection, handle_new_value_selection


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

audio_data = AudioData()

@app.route('/')
def index():
    return "Server is running"

def send_prompt(prompt_text, final=False):
    if not prompt_text:
        emit('error', {'message': 'Prompt text cannot be empty.'})
        return
    try:
        print(f"Sending prompt: {prompt_text}")
        synthesize_audio(prompt_text)
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': prompt_text, 'final': final})
    except Exception as e:
        emit('error', {'message': f"Failed to send prompt: {str(e)}"})

@socketio.on('start')
def start_interaction():
    global connection, auth_manager, user_data, auth_steps, current_step_index, authenticated
    try:
        connection = db_connection()
        if not connection:
            emit('error', {'message': 'Failed to connect to the database. Please try again later.'})
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
    except Exception as e:
        emit('error', {'message': f"Failed to start interaction: {str(e)}"})

@socketio.on('audio_response')
def handle_audio_response(data):
    global auth_manager, auth_steps, current_step_index, authenticated, pending_task
    try:
        audio_content = data.get('audio')
        tag = data.get('tag')
        print('current tag', tag)
        print("Received audio response")
        audio_segment = AudioSegment.from_file(BytesIO(audio_content), format="webm")
        audio_segment.export("response_audio.wav", format="wav")

        response_text = transcribe_audio('response_audio.wav')
        audio_data.set_data('transcribed_text', response_text)
        print(f"Transcribed text: {response_text}")
        
        task_completed = False

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
                        send_prompt("Authentication successful. Welcome to Premier Trust Bank. I am Jessica your AI Assistant. How can I assist you today?")
                else:
                    send_prompt(f"Authentication failed for {next_step['variable'].replace('_', ' ')}. Please try again.")
            else:
                send_prompt("I'm sorry, I didn't understand that. Please try again.")
        else:
            if tag == 'confirmation':
                handle_confirmation_response(response_text, connection)
            elif tag == 'block_card_selection':
                handle_block_card_selection(response_text, connection)
                task_completed = True
            elif tag == 'transaction_id':
                handle_transaction_id_response(response_text, connection)
                task_completed = True
            elif tag == 'flag_reason':
                handle_flag_reason_response(response_text, connection)
                task_completed = True
            elif tag == 'card_type_selection':
                handle_card_type_selection(response_text, connection)
                task_completed = True
            elif tag == 'change_info_selection':
                handle_change_info_selection(response_text, connection)
            elif tag == 'new_value_selection':
                handle_new_value_selection(response_text, connection)
                task_completed = True
            else:
                task_completed = map_to_route(response_text, connection)
            if task_completed:
                send_prompt("Is there anything else I can help you with?")
    except Exception as e:
        emit('error', {'message': f"Failed to handle audio response: {str(e)}"})

if __name__ == '__main__':
    try:
        socketio.run(app, port=5001, debug=True)
    except Exception as e:
        print(f"Failed to start the application: {str(e)}")
