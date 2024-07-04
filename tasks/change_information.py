from routing.change_info_routing_layer import setup_change_info_route_layer
from utils import synthesize_audio
from user_data import UserData
from value_extractor import get_value
from flask_socketio import emit
from audio_data import AudioData
import logging

audio_data = AudioData()

def change_information_initial_prompt(connection):
    try:
        synthesize_audio("What information would you like to change on your account? Your options are address or email.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "What information would you like to change on your account? Your options are address or email.", 'tag': 'change_info_selection'})
    except Exception as e:
        logging.error(f"Error in change_information_initial_prompt: {str(e)}")
        synthesize_audio("An error occurred while processing your request. Please try again later.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "An error occurred while processing your request. Please try again later.", 'response': 'no_response'})


def handle_change_info_selection(response_text, connection):
    try:
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
            emit('tts_audio', {'audio': tts_audio, 'prompt': "Sorry, it is not possible to change this information through this service. Please make an appointment on the website.", 'response': 'no_response'})
    except Exception as e:
        logging.error(f"Error in handle_change_info_selection: {str(e)}")
        synthesize_audio("An error occurred while processing your request. Please try again later.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "An error occurred while processing your request. Please try again later.", 'response': 'no_response'})


def change_information(connection, attribute):
    try:
        audio_data.set_data('attribute', attribute)
        prompt_for_new_value(attribute, connection)
    except Exception as e:
        logging.error(f"Error in change_information: {str(e)}")
        synthesize_audio("An error occurred while processing your request. Please try again later.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "An error occurred while processing your request. Please try again later.", "response": "no_response"})

def prompt_for_new_value(attribute, connection):
    try:
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
    except Exception as e:
        logging.error(f"Error in prompt_for_new_value: {str(e)}")
        synthesize_audio("An error occurred while processing your request. Please try again later.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "An error occurred while processing your request. Please try again later.", "response": "no_response"})

def handle_new_value_selection(response_text, connection):
    try:
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
                synthesize_audio("Invalid address format. please try again from the start.")
                with open("output.mp3", "rb") as audio_file:
                    tts_audio = audio_file.read()
                emit('tts_audio', {'audio': tts_audio, 'prompt': "Invalid address format, please try again from the start.", 'response': 'no_response'})
                return
            query = """
            UPDATE pba_customer 
            SET cstreet = %s, ccity = %s, czip = %s, cstate = %s 
            WHERE customerid = %s
            """
            cursor.execute(query, (street, city, zip_code, state, customer_id))
        elif attribute == "email":
            email = get_value(response_text, "email", "Extract the email address from the user response in a correct format and all lowercase characters.").value
            query = "UPDATE pba_customer SET email = %s WHERE customerid = %s"
            cursor.execute(query, (email, customer_id))
        else:
            synthesize_audio("Invalid attribute. Please try again.")
            with open("output.mp3", "rb") as audio_file:
                tts_audio = audio_file.read()
            emit('tts_audio', {'audio': tts_audio, 'prompt': "Invalid attribute. Please try again from the start.", 'response': 'no_response'})
            return

        connection.commit()
        synthesize_audio(f"Your {attribute} has been successfully updated.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': f"Your {attribute} has been successfully updated.",'response': 'no_response'})
    except Exception as e:
        logging.error(f"Error in handle_new_value_selection: {str(e)}")
        synthesize_audio("An error occurred while processing your request. Please try again later.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "An error occurred while processing your request. Please try again later.", 'response': 'no_response'})