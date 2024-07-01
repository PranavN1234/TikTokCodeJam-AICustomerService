from user_data import UserData
from utils import synthesize_audio, play_audio

def check_user_balance(connection):
    """
    Function to check the balance of the user's account.
    """
    if not connection:
        response =  "Sorry, we are unable to process your request at the moment. Please try again later."
        synthesize_audio(response)
        # play_audio('output.mp3')
        return response
    user_data = UserData()
    account_number = user_data.get_data("account_number")
    
    cursor = connection.cursor(dictionary=True)
    query = "SELECT acct_type FROM pba_account WHERE acct_no = %s"
    cursor.execute(query, (account_number,))
    account_info = cursor.fetchone()
    
    if not account_info:
        response = "Sorry, we could not find your account information. Please try again later."
        synthesize_audio(response)
        # play_audio('output.mp3')
        return response
    
    account_type = account_info["acct_type"]
    
    if account_type == "Checking":
        query = "SELECT balance FROM pba_checking WHERE acct_no = %s"
    elif account_type == "Savings":
        query = "SELECT balance FROM pba_savings WHERE acct_no = %s"
    elif account_type == "Loan":
        query = "SELECT loan_amount FROM pba_loan WHERE acct_no = %s"
    else:
        response = "Invalid account type found. Please contact customer support."
        synthesize_audio(response)
        # play_audio('output.mp3')
        return response
    
    cursor.execute(query, (account_number,))
    result = cursor.fetchone()
    
    if not result:
        response = "Sorry, we could not find your account information. Please try again later."
        synthesize_audio(response)
        # play_audio('output.mp3')
        return response

    balance = result["balance"]
    response = f"The current balance in your ${account_type} account is ${balance:.2f}"
    synthesize_audio(response)
    # play_audio('output.mp3')
        

# 77508215
# What was your dream job? artist
# Pranav Iyer
# 1996-03-18
# Npq7ddd
# 1996-18-03
# max
