from utils import record_audio, transcribe_audio, synthesize_audio, play_audio
from routing.map_to_task import map_to_route
from auth_manager import Authmanager
from db_connection import db_connection, close_db_connection
from user_data import UserData

def prompt_and_listen(prompt_text):
    synthesize_audio(prompt_text)
    play_audio('output.mp3')
    record_audio('response.wav')
    return transcribe_audio('response.wav')

def main():
    
    connection = db_connection()
    if not connection:
        print("Failed to connect to the database. Exiting.")
        return
    
    auth_manager = Authmanager(connection)
    authenticated = auth_manager.authenticate_user()
    
    print(authenticated)
    
    if authenticated:
        synthesize_audio("Authentication successful. Welcome to Chase Bank. I am Jessica your AI Assistant. How can I assist you today?")
        play_audio('output.mp3')
        user_data = UserData()
        print("user data: ", user_data.all_data())
    
    
        while True:

            user_query = prompt_and_listen("Please tell me how can I assist you today")
            if user_query:
                continue_conversation = map_to_route(user_query, connection)
                if not continue_conversation:
                    break
            else:
                synthesize_audio("I'm sorry I didn't catch that, please repeat")
                play_audio("output.mp3")
    
    close_db_connection(connection)

if __name__ == "__main__":
    main()
