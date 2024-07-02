from routing.change_info_routing_layer import setup_change_info_route_layer
from utils import synthesize_audio
from user_data import UserData
from value_extractor import get_value
from flask_socketio import emit
from audio_data import AudioData

audio_data = AudioData()

def change_information_initial_prompt(connection):
    synthesize_audio("What information would you like to change on your account? Your options are address or email.")
    with open("output.mp3", "rb") as audio_file:
        tts_audio = audio_file.read()
    emit('tts_audio', {'audio': tts_audio, 'prompt': "What information would you like to change on your account? Your options are address or email.", 'tag': 'change_info_selection'})

def handle_change_info_selection(response_text, connection):
    change_info_layer = setup_change_info_route_layer()
    route = change_info_layer(response_text)

    if route.name == "change_email_address":
        change_information(connection, "email")
    elif route.name == "change_address":
        change_information(connection, "address")
    else:
        synthesize_audio("Sorry, it is not possible to change this information through this service. Please make an appointment on the website.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "Sorry, it is not possible to change this information through this service. Please make an appointment on the website."})

def change_information(connection, attribute):
    audio_data.set_data('attribute', attribute)
    prompt_for_new_value(attribute, connection)

def prompt_for_new_value(attribute, connection):
    if attribute == "address":
        synthesize_audio("Please provide your full new address.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "Please provide your full new address.", 'tag': 'new_value_selection'})
    elif attribute == "email":
        synthesize_audio(f"Please provide the new {attribute}.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': f"Please provide the new {attribute}.", 'tag': 'new_value_selection'})

def handle_new_value_selection(response_text, connection):
    user_data = UserData()
    customer_id = user_data.get_data("customer_id")
    cursor = connection.cursor()
    attribute = audio_data.get_data('attribute')
    if attribute == "address":
        full_address = response_text
        street = get_value(full_address, "street", "Extract the street from the user-provided address.").value
        city = get_value(full_address, "city", "Extract the city from the user-provided address.").value
        zip_code = get_value(full_address, "zip", "Extract the zip code from the user-provided address.").value
        state = get_value(full_address, "state", "Extract the state from the user-provided address in a 2 letter code like NY, MN, CA etc.").value
        if not all([street, city, zip_code, state]):
            synthesize_audio("Invalid address format. Please provide the full address including street, city, state, and zip code.")
            with open("output.mp3", "rb") as audio_file:
                tts_audio = audio_file.read()
            emit('tts_audio', {'audio': tts_audio, 'prompt': "Invalid address format. Please provide the full address including street, city, state, and zip code.", 'tag': 'new_value_selection', 'attribute': attribute})
            return
        query = """
        UPDATE pba_customer 
        SET cstreet = %s, ccity = %s, czip = %s, cstate = %s 
        WHERE customerid = %s
        """
        cursor.execute(query, (street, city, zip_code, state, customer_id))
    elif attribute == "email":
        query = "UPDATE pba_customer SET email = %s WHERE customerid = %s"
        cursor.execute(query, (response_text, customer_id))
    else:
        synthesize_audio("Invalid attribute. Please try again.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "Invalid attribute. Please try again.", 'tag': 'new_value_selection', 'attribute': attribute})
        return

    connection.commit()
    synthesize_audio(f"Your {attribute} has been successfully updated.")
    with open("output.mp3", "rb") as audio_file:
        tts_audio = audio_file.read()
    emit('tts_audio', {'audio': tts_audio, 'prompt': f"Your {attribute} has been successfully updated."})
