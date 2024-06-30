from utils import record_audio, transcribe_audio, synthesize_audio, play_audio, prompt_and_listen
from routing.map_to_task import map_to_route
from auth_manager import Authmanager
from db_connection import db_connection, close_db_connection
from user_data import UserData

def main():
    
    connection = db_connection()
    if not connection:
        print("Failed to connect to the database. Exiting.")
        return
    
    auth_manager = Authmanager(connection)
    authenticated = auth_manager.authenticate_user()
    
    print(authenticated)
    
    if authenticated:
        synthesize_audio("Authentication successful. Welcome to Premier Trust Bank. I am Jessica your AI Assistant.")
        play_audio('output.mp3')
        user_data = UserData()
        print("user data: ", user_data.all_data())
        counter = 0
    
        while True:
            if counter == 0:
                user_query = prompt_and_listen("Please tell me how can I assist you today?")
            else:
                user_query = prompt_and_listen("Is there anything else I can help you with?")
            if user_query:
                continue_conversation = map_to_route(user_query, connection)
                if not continue_conversation:
                    break
            else:
                synthesize_audio("I'm sorry I didn't catch that, please repeat")
                play_audio("output.mp3")
            counter += 1
    
    close_db_connection(connection)

if __name__ == "__main__":
    main()
