from utils import synthesize_audio, play_audio, transcribe_audio, record_audio
from routing.card_routing_layer import setup_card_type_route_layer
from routing.yes_routing_layer import setup_yes_route_layer
from db_connection import db_connection, close_db_connection
from user_data import UserData

def prompt_for_confirmation(prompt_text):
    synthesize_audio(prompt_text)
    play_audio('output.mp3')
    record_audio('response.wav')
    response = transcribe_audio('response.wav')
    
    yes_route_layer = setup_yes_route_layer()
    route = yes_route_layer(response)
    
    return route.name == "affirmative"

def block_card(connection):
    if not connection:
        response =  "Sorry, we are unable to process your request at the moment. Please try again later."
        synthesize_audio(response)
        play_audio('output.mp3')
        return response
    user_data = UserData()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM pba_card WHERE customerid = %s"
    cursor.execute(query, (user_data.get_data("customer_id"),))
    cards = cursor.fetchall()

    if not cards:
        synthesize_audio("Sorry I couldn't find any cards found for your account.")
        play_audio('output.mp3')
        return

    card_options = [f"{card['card_type']} card ending with {card['card_number'][-4:]}" for card in cards]
    card_options_text = " or ".join(card_options)

    synthesize_audio(f"Do you want to block your {card_options_text}?")
    play_audio('output.mp3')
    record_audio('response.wav')
    response = transcribe_audio('response.wav')

    card_type_route_layer = setup_card_type_route_layer()
    route = card_type_route_layer(response)
    print("route is", route)
    selected_card = next((card for card in cards if card['card_type'] == route.name), None)

    if not selected_card:
        synthesize_audio("Card type not found or invalid.")
        play_audio('output.mp3')
        return
    
    if selected_card['flagged'] == 1:
        synthesize_audio(f"Your {selected_card['card_type']} card is already blocked.")
        play_audio('output.mp3')
        return
    
    update_query = "UPDATE pba_card SET flagged = 1 WHERE card_name = %s"
    cursor.execute(update_query, (selected_card['card_name'],))
    connection.commit()
    synthesize_audio(f"Your {selected_card['card_type']} card ending with {selected_card['card_number'][-4:]} has been successfully blocked.")
    play_audio('output.mp3')
    




    