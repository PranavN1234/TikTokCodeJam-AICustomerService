from routing.taskrouting_layer import route_task
from routing.yes_routing_layer import setup_yes_route_layer
from routing.transaction_dispute_layer import setup_transaction_dispute_route_layer
from routing.change_info_routing_layer import setup_change_info_route_layer
from tasks.change_information import change_information_initial_prompt
from tasks.block_card import block_card_initial_prompt
from tasks.request_new_card import prompt_for_card_type_initial
from tasks.flag_transaction import handle_general_dispute
from tasks.check_balance import check_user_balance
from ai_service import ai_response
from user_data import UserData
from tasks.handle_bank_info import get_bank_info
from flask_socketio import emit
from audio_data import AudioData
from utils import synthesize_audio

audio_data = AudioData()

def prompt_for_confirmation(prompt_text):
    synthesize_audio(prompt_text)
    with open("output.mp3", "rb") as audio_file:
        tts_audio = audio_file.read()
    print("sending tts audio", prompt_text)
    emit('tts_audio', {'audio': tts_audio, 'prompt': prompt_text, 'tag': 'confirmation'})

def handle_confirmation_response(response_text, connection):
    yes_route_layer = setup_yes_route_layer()
    route = yes_route_layer(response_text)
    print('response text', response_text)
    if route.name == "affirmative":
        # Process the confirmed action
        process_confirmed_action(connection)
    else:
        synthesize_audio("Confirmation not received. Please try again.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "Confirmation not received. Please try again."})
        return

def process_confirmed_action(connection):
    # Handle the confirmed action here
    if audio_data.get_data('pending_task') == "block_card":
        block_card_initial_prompt(connection)
    elif audio_data.get_data('pending_task') == "issue_new_card":
        prompt_for_card_type_initial(connection)
    elif audio_data.get_data('pending_task') == "change_information":
        change_information_initial_prompt(connection)

def map_to_route(user_query, connection):
    task = route_task(user_query)
    user_data = UserData()
    audio_data.set_data('pending_task', task)
    match task:
        case "check_balance":
            if prompt_for_confirmation("Do you want to check your balance?"):
                check_user_balance(connection)
        case "change_information":
            prompt_for_confirmation("Do you want to change your information?")
        case "block_card":
            prompt_for_confirmation("So it seems like you wanna block your card, do you wanna proceed with it?")   
        case "issue_new_card":
            prompt_for_confirmation("So you want to issue a new card, do you want to proceed?")
        case "flag_fraud":
            if prompt_for_confirmation("So it seems like you want to flag a transaction, sorry for your troubles, shall we proceed?"):
                handle_general_dispute(connection)
        case "redirect_agent":
            emit('prompt', {'message': "Redirecting to a live agent..."})
        case "end_conversation":
            synthesize_audio("Thank you for using our service. Goodbye!")
            with open("output.mp3", "rb") as audio_file:
                tts_audio = audio_file.read()
            emit('tts_audio', {'audio': tts_audio, 'prompt': "Thank you for using our service. Goodbye!", 'final': True})
        case "chitchat":
            chitchat_response = ai_response(user_query)
            synthesize_audio(chitchat_response)
            with open("output.mp3", "rb") as audio_file:
                tts_audio = audio_file.read()
            emit('tts_audio', {'audio': tts_audio, 'prompt': chitchat_response})
        case "bank_info":
            get_bank_info(user_query)
        case _:
            emit('error', {'message': "Something went wrong"})

    user_data.add_recent_query(user_query)