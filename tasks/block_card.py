from utils import synthesize_audio, transcribe_audio, log_conversation
from routing.card_routing_layer import setup_card_type_route_layer
from flask_socketio import emit
from user_data import UserData
from audio_data import AudioData
import logging

audio_data = AudioData()

def block_card_initial_prompt(connection):
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
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM pba_card WHERE customerid = %s"
        cursor.execute(query, (user_data.get_data("customer_id"),))
        cards = cursor.fetchall()

        if not cards:
            log_conversation("AI", "Sorry, I couldn't find any cards found for your account.")
            synthesize_audio("Sorry, I couldn't find any cards found for your account.")
            with open("output.mp3", "rb") as audio_file:
                tts_audio = audio_file.read()
            emit('tts_audio', {'audio': tts_audio, 'prompt': "Sorry, I couldn't find any cards found for your account.", 'response': 'no_response'})
            return

        card_options = [f"{card['card_type']} card ending with {card['card_number'][-4:]}" for card in cards]
        card_options_text = " or ".join(card_options)

        prompt_text = f"Do you want to block your {card_options_text}?"
        log_conversation("AI", prompt_text)
        synthesize_audio(prompt_text)
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': prompt_text, 'tag': 'block_card_selection'})

    except Exception as e:
        logging.error(f"Error in block_card_initial_prompt: {str(e)}")
        log_conversation("AI", "Sorry, I am unable to process your request at the moment. Please try again later.")
        synthesize_audio("Sorry, I am unable to process your request at the moment. Please try again later.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "Sorry, I am unable to process your request at the moment. Please try again later.", 'response': 'no_response'})

def handle_block_card_selection(response_text, connection):
    try:
        user_data = UserData()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM pba_card WHERE customerid = %s"
        cursor.execute(query, (user_data.get_data("customer_id"),))
        cards = cursor.fetchall()

        card_type_route_layer = setup_card_type_route_layer()
        route = card_type_route_layer(response_text)
        selected_card = next((card for card in cards if card['card_type'] == route.name), None)

        if not selected_card:
            log_conversation("AI", "Card type not found or invalid.")
            synthesize_audio("Card type not found or invalid.")
            with open("output.mp3", "rb") as audio_file:
                tts_audio = audio_file.read()
            emit('tts_audio', {'audio': tts_audio, 'prompt': "Card type not found or invalid.", 'response': 'no_response'})
            return
        
        if selected_card['flagged'] == 1:
            log_conversation("AI", f"Your {selected_card['card_type']} card is already blocked.")
            synthesize_audio(f"Your {selected_card['card_type']} card is already blocked.")
            with open("output.mp3", "rb") as audio_file:
                tts_audio = audio_file.read()
            emit('tts_audio', {'audio': tts_audio, 'prompt': f"Your {selected_card['card_type']} card is already blocked.", 'response': 'no_response'})
            return

        update_query = "UPDATE pba_card SET flagged = 1 WHERE card_name = %s"
        cursor.execute(update_query, (selected_card['card_name'],))
        connection.commit()

        log_conversation("AI", f"Your {selected_card['card_type']} card ending with {selected_card['card_number'][-4:]} has been successfully blocked.")
        synthesize_audio(f"Your {selected_card['card_type']} card ending with {selected_card['card_number'][-4:]} has been successfully blocked.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': f"Your {selected_card['card_type']} card ending with {selected_card['card_number'][-4:]} has been successfully blocked.", 'response': 'no_response'})

    except Exception as e:
        logging.error(f"Error in handle_block_card_selection: {str(e)}")
        log_conversation("AI", "An error occurred while processing your request. Please try again later.")
        synthesize_audio("An error occurred while processing your request. Please try again later.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "An error occurred while processing your request. Please try again later."})