from utils import synthesize_audio, transcribe_audio
from routing.card_routing_layer import setup_card_type_route_layer
from flask_socketio import emit
from user_data import UserData
from audio_data import AudioData

audio_data = AudioData()

def block_card_initial_prompt(connection):
    if not connection:
        response = "Sorry, we are unable to process your request at the moment. Please try again later."
        synthesize_audio(response)
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': response})
        return response

    user_data = UserData()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM pba_card WHERE customerid = %s"
    cursor.execute(query, (user_data.get_data("customer_id"),))
    cards = cursor.fetchall()

    if not cards:
        synthesize_audio("Sorry, I couldn't find any cards found for your account.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "Sorry, I couldn't find any cards found for your account."})
        return

    card_options = [f"{card['card_type']} card ending with {card['card_number'][-4:]}" for card in cards]
    card_options_text = " or ".join(card_options)

    prompt_text = f"Do you want to block your {card_options_text}?"
    synthesize_audio(prompt_text)
    with open("output.mp3", "rb") as audio_file:
        tts_audio = audio_file.read()
    emit('tts_audio', {'audio': tts_audio, 'prompt': prompt_text, 'tag': 'block_card_selection'})

def handle_block_card_selection(response_text, connection):
    user_data = UserData()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM pba_card WHERE customerid = %s"
    cursor.execute(query, (user_data.get_data("customer_id"),))
    cards = cursor.fetchall()

    card_type_route_layer = setup_card_type_route_layer()
    route = card_type_route_layer(response_text)
    selected_card = next((card for card in cards if card['card_type'] == route.name), None)

    if not selected_card:
        synthesize_audio("Card type not found or invalid.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "Card type not found or invalid.", 'tag': 'block_card_selection'})
        return
    
    if selected_card['flagged'] == 1:
        synthesize_audio(f"Your {selected_card['card_type']} card is already blocked.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': f"Your {selected_card['card_type']} card is already blocked."})
        return

    update_query = "UPDATE pba_card SET flagged = 1 WHERE card_name = %s"
    cursor.execute(update_query, (selected_card['card_name'],))
    connection.commit()

    synthesize_audio(f"Your {selected_card['card_type']} card ending with {selected_card['card_number'][-4:]} has been successfully blocked.")
    with open("output.mp3", "rb") as audio_file:
        tts_audio = audio_file.read()
    emit('tts_audio', {'audio': tts_audio, 'prompt': f"Your {selected_card['card_type']} card ending with {selected_card['card_number'][-4:]} has been successfully blocked."})
