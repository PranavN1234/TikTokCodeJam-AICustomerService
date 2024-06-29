from db_connection import db_connection, close_db_connection

def check_balance():
    """
    Function to check the balance of the user's account.
    """
    connection = db_connection()
    if connection is None:
        return "Sorry, we are unable to process your request at the moment. Please try again later."
    
    cursor = connection.cursor()
    cursor.execute("SELECT balance FROM accounts WHERE user_id = 12345")
    result = cursor.fetchone()
    
    if result is None:
        close_db_connection(connection)
        return "Sorry, we could not find your account information. Please try again later."
    
    balance = result[0]
    close_db_connection(connection)
    return f"Your current account balance is ${balance}"    

# 77508215
# What was your first pet’s name?
# Max
# Bhanu
# Gupta
# 1996-03-18