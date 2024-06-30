from db_connection import db_connection, close_db_connection
from user_data import UserData
from utils import synthesize_audio, play_audio

def check_user_balance(connection):
    """
    Function to check the balance of the user's account.
    """
    if not connection:
        response =  "Sorry, we are unable to process your request at the moment. Please try again later."
        synthesize_audio(response)
        play_audio('output.mp3')
        return response
    user_data = UserData()
    account_number = user_data.get_data("account_number")
    cursor = connection.cursor(dictionary=True)
    query = "SELECT balance FROM pba_checking WHERE acct_no = %s"
    cursor.execute(query, (account_number,))
    result = cursor.fetchone()
    
    if not result:
        response = "Sorry, we could not find your account information. Please try again later."
        synthesize_audio(response)
        play_audio('output.mp3')
        return response

    balance = result["balance"]
    response = f"Your current account balance is ${balance:.2f}"
    synthesize_audio(response)
    play_audio('output.mp3')
        

# 55994780
# What was your dream job? artist
# Pranav Iyer

# 1992-01-15