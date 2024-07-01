from routing.taskrouting_layer import route_task
from routing.yes_routing_layer import setup_yes_route_layer
from routing.transaction_dispute_layer import setup_transaction_dispute_route_layer
from routing.change_info_routing_layer import setup_change_info_route_layer
from tasks.change_information import change_information, generic_change_information
from utils import synthesize_audio, play_audio, transcribe_audio
from tasks.block_card import block_card
from tasks.flag_transaction import handle_general_dispute, flag_specific_transaction
from tasks.check_balance import check_user_balance
from tasks.request_new_card import prompt_for_card_type, issue_new_card
from ai_service import ai_response
from user_data import UserData
from tasks.handle_bank_info import get_bank_info
from flask_socketio import emit

def handle_confirmation_response(response_text, connection, pending_task):
    print('handle confirmation response called')
    yes_route_layer = setup_yes_route_layer()
    route = yes_route_layer(response_text)
    
    if route.name == "affirmative":
        pending_task(connection)
        emit('prompt', {'message': "Is there anything else I can help you with?"})
        return True
    else:
        emit('prompt', {'message': "Confirmation not received. Please try again."})
        return False

def map_to_route(user_query, connection):
    task = route_task(user_query)
    user_data = UserData()

    match task:
        case "check_balance":
            check_user_balance(connection)
        case "change_information":
            change_information_layer = setup_change_info_route_layer()
            route = change_information_layer(user_query)
            if route.name == "generic_info_change":
                generic_change_information(connection, user_query)
            elif route.name == "change_email_address":
                change_information(connection, "email")
            elif route.name == "change_address":
                change_information(connection, "address")
        case "block_card":
            pending_task = lambda connection: block_card(connection)
            synthesize_audio("So it seems like you wanna block your card, do you wanna proceed with it?")
            with open("output.mp3", "rb") as audio_file:
                tts_audio = audio_file.read()
            emit('tts_audio', {'audio': tts_audio, 'prompt': "So it seems like you wanna block your card, do you wanna proceed with it?"})
            return pending_task
        case "issue_new_card":
            card_type = prompt_for_card_type()
            if card_type:
                pending_task = lambda connection: issue_new_card(connection, card_type)
                synthesize_audio(f"So you want to issue a new {card_type} card, do you want to proceed?")
                with open("output.mp3", "rb") as audio_file:
                    tts_audio = audio_file.read()
                emit('tts_audio', {'audio': tts_audio, 'prompt': f"So you want to issue a new {card_type} card, do you want to proceed?"})
                return pending_task
        case "flag_fraud":
            pending_task = handle_general_dispute
            synthesize_audio("So it seems like you want to flag a transaction, sorry for your troubles, shall we proceed?")
            with open("output.mp3", "rb") as audio_file:
                tts_audio = audio_file.read()
            emit('tts_audio', {'audio': tts_audio, 'prompt': "So it seems like you want to flag a transaction, sorry for your troubles, shall we proceed?"})
            return pending_task
        case "redirect_agent":
            emit('prompt', {'message': "redirecting agent"})
        case "end_conversation":
            synthesize_audio("Thank you for using our service. Goodbye!")
            with open("output.mp3", "rb") as audio_file:
                tts_audio = audio_file.read()
            emit('tts_audio', {'audio': tts_audio, 'prompt': "Thank you for using our service. Goodbye!", 'final': True})
            return False
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
    return True
