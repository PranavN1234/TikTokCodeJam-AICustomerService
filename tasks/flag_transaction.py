from utils import synthesize_audio, play_audio, record_audio, transcribe_audio
from value_extractor import get_value
from yes_routing_layer import setup_yes_route_layer
from user_data import UserData
from db_connection import db_connection, close_db_connection
from value_extractor import get_value

def prompt_for_confirmation(prompt_text):
    synthesize_audio(prompt_text)
    play_audio('output.mp3')
    record_audio('response.wav')
    response = transcribe_audio('response.wav')
    
    yes_route_layer = setup_yes_route_layer()
    route = yes_route_layer(response)
    
    return route.name == "affirmative"

def handle_general_dispute():
    
    connection = db_connection()
    if not connection:
        synthesize_audio("Failed to connect to the database.")
        play_audio('output.mp3')
        return

    cursor = connection.cursor(dictionary=True)
    user_data = UserData()
    query = """
    SELECT t_id, from_account, to_account, amount, timestamp 
    FROM pba_transactions 
    WHERE from_account = %s OR to_account = %s
    ORDER BY timestamp DESC 
    LIMIT 4
    """
    cursor.execute(query, (user_data.get_data("account_number"), user_data.get_data("account_number")))
    transactions = cursor.fetchall()
    close_db_connection(connection)

    if not transactions:
        synthesize_audio("No recent transactions found for your account.")
        play_audio('output.mp3')
        return

    transaction_details = "\n".join(
        [f"Transaction ID: {t['t_id']}, Amount: {t['amount']}, Date: {t['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}" for t in transactions]
    )
    synthesize_audio(f"Here are your recent transactions: {transaction_details}. Please provide the transaction ID you'd like to dispute.")
    play_audio('output.mp3')
    
    flag_specific_transaction()

def flag_specific_transaction(user_query=None):

    
    connection = db_connection()
    if not connection:
        synthesize_audio("Failed to connect to the database.")
        play_audio('output.mp3')
        return
    
    if user_query:
        transaction_id = get_value(user_query, "transaction_id", "Check if the user response had a potential transaction id otherwise return empty string").value.lower()

    if not transaction_id:
        synthesize_audio("Please provide the transaction ID you'd like to dispute.")
        play_audio('output.mp3')
        record_audio('response.wav')
        transaction_id = get_value(transcribe_audio('response.wav'), "transaction_id", "Extract the transaction id from the given user response").value.lower()

    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM pba_transactions WHERE LOWER(t_id) = %s"
    cursor.execute(query, (transaction_id,))
    transaction = cursor.fetchone()

    if not transaction:
        synthesize_audio("Transaction not found.")
        play_audio('output.mp3')
        return

    synthesize_audio("Please provide a reason for flagging this transaction. Was the card with you when the transaction was made?")
    play_audio('output.mp3')
    record_audio('response.wav')
    flag_reason = transcribe_audio('response.wav')

    # Extract specific values from the user input
    flag_reason_value = get_value(flag_reason, "reason", "Extract the reason for flagging the transaction and whether the card was with the user or not.")

    update_query = "UPDATE pba_transactions SET flagged = 1, flag_reason = %s WHERE t_id = %s"
    cursor.execute(update_query, (flag_reason_value.value, transaction_id))
    connection.commit()
    close_db_connection(connection)
    synthesize_audio("The transaction has been successfully flagged.")
    play_audio('output.mp3')