from routing.taskrouting_layer import route_task
from routing.yes_routing_layer import setup_yes_route_layer
from routing.transaction_dispute_layer import setup_transaction_dispute_route_layer
from routing.change_info_routing_layer import setup_change_info_route_layer
from tasks.change_information import change_information_initial_prompt
from tasks.block_card import block_card_initial_prompt
from tasks.flag_transaction import handle_general_dispute, handle_transaction_id_response
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

    pending_task = audio_data.get_data('pending_task')
    # Handle the confirmed action here
    if pending_task == "block_card":
        block_card_initial_prompt(connection)
    elif pending_task == "flag_general_dispute":
        handle_general_dispute(connection)
    elif pending_task == "flag_specific_transaction":
        handle_transaction_id_response(connection, audio_data.get_data('user_query'))
    elif audio_data.get_data('pending_task') == "issue_new_card":
        prompt_for_card_type_initial(connection)
    elif audio_data.get_data('pending_task') == "change_information":
        change_information_initial_prompt(connection)

def map_to_route(user_query, connection):
    task = route_task(user_query)
    user_data = UserData()
    audio_data.set_data('pending_task', task)
    audio_data.set_data('user_query', user_query)
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
            dispute_layer = setup_transaction_dispute_route_layer()
            route = dispute_layer(user_query)
            if route.name == "general_dispute":
                audio_data.set_data('pending_task', 'flag_general_dispute')
                prompt_for_confirmation("So it seems like you have a general transaction dispute lets get some more info")
            elif route.name == "specific_dispute":
                audio_data.set_data('pending_task', 'flag_specific_transaction')
                prompt_for_confirmation("So it seems like you have issues with a specific transaction, shall we resolve your dispute")
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