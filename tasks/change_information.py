from routing.change_info_routing_layer import setup_change_info_route_layer
from utils import synthesize_audio, play_audio, record_audio, transcribe_audio
from user_data import UserData
from value_extractor import get_value
from routing.yes_routing_layer import setup_yes_route_layer

def prompt_for_confirmation(prompt_text):
    synthesize_audio(prompt_text)
    # play_audio('output.mp3')
    record_audio('response.wav')
    response = transcribe_audio('response.wav')
    
    yes_route_layer = setup_yes_route_layer()
    route = yes_route_layer(response)
    
    return route.name == "affirmative"

def prompt_for_new_value(attribute):
    if attribute == "address":
        synthesize_audio("Please provide your full new address.")
        # play_audio('output.mp3')
        record_audio('response_address.wav')
        full_address = transcribe_audio('response_address.wav')
        
        # Use value_extractor to parse the full address into components
        street = get_value(full_address, "street", "Extract the street from the user-provided address.").value
        city = get_value(full_address, "city", "Extract the city from the user-provided address.").value
        zip_code = get_value(full_address, "zip", "Extract the zip code from the user-provided address.").value
        state = get_value(full_address, "state", "Extract the state from the user-provided address in a 2 letter code like NY, MN, CA etc.").value
        
        return (street, city, zip_code, state)
    else:
        synthesize_audio(f"Please provide the new {attribute}.")
        # play_audio('output.mp3')
        record_audio('response.wav')
        new_value = transcribe_audio('response.wav')
        value = get_value(new_value, attribute, f"Extract the new {attribute} from the user response in a proper format.")
        return value.value

def update_information(connection, attribute, new_value):
    user_data = UserData()
    customer_id = user_data.get_data("customer_id")
    
    cursor = connection.cursor()

    if attribute == "address":
        cstreet, ccity, czip, cstate = new_value
        query = """
        UPDATE pba_customer 
        SET cstreet = %s, ccity = %s, czip = %s, cstate = %s 
        WHERE customerid = %s
        """
        cursor.execute(query, (cstreet, ccity, czip, cstate, customer_id))
    elif attribute == "email":
        query = "UPDATE pba_customer SET email = %s WHERE customerid = %s"
        cursor.execute(query, (new_value, customer_id))
    else:
        return False
    
    connection.commit()
    return True

def change_information(connection, attribute):
    confirm = prompt_for_confirmation(f"You want to change your {attribute}. Do you want to proceed?")
    
    if confirm:
        new_value = prompt_for_new_value(attribute)
        confirm_value = prompt_for_confirmation(f"You want to change your {attribute} to {new_value}. Do you want to proceed?")
        
        if confirm_value:
            success = update_information(connection, attribute, new_value)
            if success:
                synthesize_audio(f"Your {attribute} has been successfully updated.")
            else:
                synthesize_audio("There was an issue updating your information. Please try again later.")
        else:
            synthesize_audio("No changes were made to your account information.")
    else:
        synthesize_audio("No changes were made to your account information.")
    
    # play_audio('output.mp3')
    

def generic_change_information(connection, user_query):
    synthesize_audio("What information would you like to change on your account? Your options are address or email.")
    # play_audio('output.mp3')
    record_audio('response.wav')
    response = transcribe_audio('response.wav')
    
    change_info_layer = setup_change_info_route_layer()
    route = change_info_layer(response)
    
    if route.name == "change_email_address":
            change_information(connection, "email")
    elif route.name == "change_address":
            change_information(connection, "address")
    else:
        synthesize_audio("Sorry, it is not possible to change this information through this service. Please make an appointment on the website.")
        # play_audio('output.mp3')