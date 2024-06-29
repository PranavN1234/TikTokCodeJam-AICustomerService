from taskrouting_layer import route_task
from yes_routing_layer import setup_yes_route_layer
from utils import synthesize_audio, play_audio, record_audio, transcribe_audio

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

def map_to_route(user_query):
    task = route_task(user_query)

    print(task)

    match task:
        case "check_balance":
            print("This is your balance")
        case "change_information":
            print("What information would you like to change")
        case "block_card":
            if prompt_for_confirmation("So it seems like you wanna block your card, do you wanna proceed with it?"):
                print("Blocking card!!!!!")    
        case "issue_new_card":
            print("Issue new card")
        case "flag_fraud":
            print("Flagging fraud")
        case "redirect_agent":
            print("redirecting agent")
        case "chitchat":
            print("chitchatting")
        
        case _:
            print("Something wrong")