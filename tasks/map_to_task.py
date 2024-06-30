from taskrouting_layer import route_task
from yes_routing_layer import setup_yes_route_layer
from transaction_dispute_layer import setup_transaction_dispute_route_layer
from utils import synthesize_audio, play_audio, record_audio, transcribe_audio
from tasks.block_card import block_card
from tasks.flag_transaction import handle_general_dispute, flag_specific_transaction
from tasks.check_balance import check_user_balance
from card_routing_layer import setup_card_type_route_layer
from tasks.request_new_card import prompt_for_card_type, issue_new_card


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

    match task:
        case "check_balance":
            check_user_balance(connection)
        case "change_information":
            print("What information would you like to change")
        case "block_card":
            if prompt_for_confirmation("So it seems like you wanna block your card, do you wanna proceed with it?"):
                block_card()    
        case "issue_new_card":
            card_type = prompt_for_card_type()
            if card_type and prompt_for_confirmation(f"So you want to issue a new {card_type} card, do you want to proceed?"):
                issue_new_card(connection, card_type)
        case "flag_fraud":
            if prompt_for_confirmation("So it seems like you want to flag a transaction, sorry for your troubles, shall we proceed?"):
                transaction_dispute_route_layer = setup_transaction_dispute_route_layer()
                route = transaction_dispute_route_layer(user_query)
                if route.name == "general_dispute":
                    handle_general_dispute()
                elif route.name == "specific_dispute":
                    flag_specific_transaction(user_query)
        case "redirect_agent":
            print("redirecting agent")
        case "end_conversation":
            synthesize_audio("Thank you for using our service. Goodbye!")
            play_audio('output.mp3')
            return False
        case "chitchat":
            print("chitchatting")
        
        case _:
            print("Something wrong")
        
    return True