from utils import synthesize_audio, play_audio, record_audio, transcribe_audio
from card_routing_layer import setup_card_type_route_layer
from db_connection import db_connection, close_db_connection
from user_data import UserData
from utils import synthesize_audio, play_audio
import random
import datetime

def generate_card_number():
    """Generates a 16-digit card number."""
    return ''.join([str(random.randint(0, 9)) for _ in range(16)])

def generate_cvv():
    """Generates a 3-digit CVV."""
    return ''.join([str(random.randint(0, 9)) for _ in range(3)])

def generate_pin():
    """Generates a 4-digit PIN."""
    return ''.join([str(random.randint(0, 9)) for _ in range(4)])

def prompt_for_card_type():
    synthesize_audio("Would you like a credit card or a debit card?")
    play_audio('output.mp3')
    record_audio('response.wav')
    response = transcribe_audio('response.wav')
    
    card_type_route_layer = setup_card_type_route_layer()
    route = card_type_route_layer(response)
    
    return route.name if route else None


def issue_new_card(connection, card_type):
    if not connection:
        response = "Sorry, we are unable to process your request at the moment. Please try again later."
        synthesize_audio(response)
        play_audio('output.mp3')
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
    synthesize_audio(response)
    play_audio('output.mp3')