from routing.taskrouting_layer import route_task
from routing.yes_routing_layer import setup_yes_route_layer
from routing.transaction_dispute_layer import setup_transaction_dispute_route_layer
from routing.change_info_routing_layer import setup_change_info_route_layer
from tasks.change_information import change_information, generic_change_information
from utils import synthesize_audio, play_audio, record_audio, transcribe_audio
from tasks.block_card import block_card
from tasks.flag_transaction import handle_general_dispute, flag_specific_transaction
from tasks.check_balance import check_user_balance
from tasks.request_new_card import prompt_for_card_type, issue_new_card
from ai_service import ai_response
from user_data import UserData
from tasks.handle_bank_info import get_bank_info

def prompt_for_confirmation(prompt_text):
    synthesize_audio(prompt_text)
    play_audio('output.mp3')
    record_audio('response.wav')
    response = transcribe_audio('response.wav')
    
    yes_route_layer = setup_yes_route_layer()
    route = yes_route_layer(response)
    
    if route.name == "affirmative":
        return True
    else:
        return False

def map_to_route(user_query, connection):
    task = route_task(user_query)

    print(task)

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
            if prompt_for_confirmation("So it seems like you wanna block your card, do you wanna proceed with it?"):
                block_card(connection)    
        case "issue_new_card":
            card_type = prompt_for_card_type()
            if card_type and prompt_for_confirmation(f"So you want to issue a new {card_type} card, do you want to proceed?"):
                issue_new_card(connection, card_type)
        case "flag_fraud":
            if prompt_for_confirmation("So it seems like you want to flag a transaction, sorry for your troubles, shall we proceed?"):
                transaction_dispute_route_layer = setup_transaction_dispute_route_layer()
                route = transaction_dispute_route_layer(user_query)
                if route.name == "general_dispute":
                    handle_general_dispute(connection)
                elif route.name == "specific_dispute":
                    flag_specific_transaction(connection, user_query)
        case "redirect_agent":
            print("redirecting agent")
        case "end_conversation":
            synthesize_audio("Thank you for using our service. Goodbye!")
            play_audio('output.mp3')
            return False
        case "chitchat":
            chitchat_response = ai_response(user_query)
            synthesize_audio(chitchat_response)
            play_audio('output.mp3')
            print("chitchatting")
        case "bank_info":
            get_bank_info(user_query)
            print("bank info")
        case _:
            print("Something wrong")
    
    # Add the user query to recent queries
    user_data.add_recent_query(user_query)

    return True