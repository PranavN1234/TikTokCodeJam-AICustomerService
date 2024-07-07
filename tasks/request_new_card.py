from utils import synthesize_audio, play_audio, transcribe_audio
from routing.card_routing_layer import setup_card_type_route_layer
from db_connection import db_connection, close_db_connection
from user_data import UserData
from utils import synthesize_audio, log_conversation
import random
import datetime
from flask_socketio import emit
from audio_data import AudioData
import logging

audio_data = AudioData()

def generate_card_number():
    """Generates a 16-digit card number."""
    return ''.join([str(random.randint(0, 9)) for _ in range(16)])

def generate_cvv():
    """Generates a 3-digit CVV."""
    return ''.join([str(random.randint(0, 9)) for _ in range(3)])

def generate_pin():
    """Generates a 4-digit PIN."""
    return ''.join([str(random.randint(0, 9)) for _ in range(4)])

def prompt_for_card_type_initial(connection):
    try:
        synthesize_audio("Would you like a credit card or a debit card?")
        log_conversation("AI", "Would you like a credit card or a debit card?")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "Would you like a credit card or a debit card?", 'tag': 'card_type_selection'})
    except Exception as e:
        logging.error(f"Error in prompt_for_card_type_initial: {str(e)}")
        synthesize_audio("Sorry, I am unable to process your request at the moment. Please try again later.")
        log_conversation("AI", "Sorry, I am unable to process your request at the moment. Please try again later.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "Sorry, I am unable to process your request at the moment. Please try again later.", 'response': 'no_response'})
        
def handle_card_type_selection(response_text, connection):
    try:
        card_type_route_layer = setup_card_type_route_layer()
        route = card_type_route_layer(response_text)
        card_type = route.name if route else None

        if card_type:
            issue_new_card(connection, card_type)
        else:
            synthesize_audio("Card type not recognized. Please try again from the top.")
            log_conversation("AI", "Card type not recognized. Please try again from the top.")
            with open("output.mp3", "rb") as audio_file:
                tts_audio = audio_file.read()
            emit('tts_audio', {'audio': tts_audio, 'prompt': "Card type not recognized. Please try again from the top.", 'response': 'no_response'})
    except Exception as e:
        logging.error(f"Error in handle_card_type_selection: {str(e)}")
        synthesize_audio("Sorry, I am unable to process your request at the moment. Please try again later.")
        log_conversation("AI", "Sorry, I am unable to process your request at the moment. Please try again later.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "Sorry, I am unable to process your request at the moment. Please try again later.", 'response': 'no_response'})
        
def issue_new_card(connection, card_type):
    try:
        if not connection:
            response = "Sorry, we are unable to process your request at the moment. Please try again later."
            log_conversation("AI", response)
            synthesize_audio(response)
            with open("output.mp3", "rb") as audio_file:
                tts_audio = audio_file.read()
            emit('tts_audio', {'audio': tts_audio, 'prompt': response, 'response': 'no_response'})
            return response

        user_data = UserData()
        customer_id = user_data.get_data("customer_id")
        card_number = generate_card_number()
        cvv = generate_cvv()
        pin = generate_pin()
        expiry_date = datetime.date.today().replace(year=datetime.date.today().year + 5)  # 5 years from today
        
        cursor = connection.cursor(dictionary=True)
        query = """
        UPDATE pba_card
        SET card_number = %s, cvv = %s, pin = %s, expiry_date = %s, flagged = 0
        WHERE customerid = %s AND card_type = %s AND flagged = 1
        """
        cursor.execute(query, (card_number, cvv, pin, expiry_date, customer_id, card_type))
        connection.commit()

        response = f"A new {card_type} card has been issued to your account. You should receive it in 5-7 business days."
        log_conversation("AI", response)
        synthesize_audio(response)
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': response, 'response': 'no_response'})
    except Exception as e:
        logging.error(f"Error in issue_new_card: {str(e)}")
        response = "Sorry, we are unable to process your request at the moment. Please try again later."
        log_conversation("AI", response)
        synthesize_audio(response)
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': response, 'response': 'no_response'})