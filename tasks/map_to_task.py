from taskrouting_layer import route_task

def map_to_route(user_query):
    task = route_task(user_query)

    print(task)

    match task:
        case "check_balance":
            print("This is your balance")
        case "change_information":
            print("What information would you like to change")
        case "block_card":
            print("Blocking card")
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