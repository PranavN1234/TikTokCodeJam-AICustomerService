from utils import synthesize_audio, transcribe_audio
from value_extractor import get_value
from user_data import UserData
from flask_socketio import emit
from audio_data import AudioData

audio_data = AudioData()

def handle_general_dispute(connection):
    if not connection:
        synthesize_audio("Failed to connect to the database.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "Failed to connect to the database."})
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
    if not transactions:
        synthesize_audio("No recent transactions found for your account.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "No recent transactions found for your account."})
        return

    transaction_details = "\n".join(
        [f"Transaction ID: {t['t_id']}, Amount: {t['amount']}, Date: {t['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}" for t in transactions]
    )
    prompt_text = f"Here are your recent transactions: {transaction_details}. Please provide the transaction ID you'd like to dispute."
    synthesize_audio(prompt_text)
    with open("output.mp3", "rb") as audio_file:
        tts_audio = audio_file.read()
    emit('tts_audio', {'audio': tts_audio, 'prompt': prompt_text, 'tag': 'transaction_id'})

def handle_transaction_id_response(response_text, connection):
    transaction_id = get_value(response_text, "transaction_id", "Check if the user response had a potential transaction id otherwise return empty string").value.lower()
    if not transaction_id:
        synthesize_audio("Please provide the transaction ID you'd like to dispute.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "Please provide the transaction ID you'd like to dispute.", 'tag': 'transaction_id'})
        return
    
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM pba_transactions WHERE LOWER(t_id) = %s"
    cursor.execute(query, (transaction_id,))
    transaction = cursor.fetchone()

    if not transaction:
        synthesize_audio("Transaction not found.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': "Transaction not found.", 'tag': 'transaction_id'})
        return

    audio_data.set_data('transaction_id', transaction_id)
    prompt_text = "Please provide a reason for flagging this transaction. Was the card with you when the transaction was made?"
    synthesize_audio(prompt_text)
    with open("output.mp3", "rb") as audio_file:
        tts_audio = audio_file.read()
    emit('tts_audio', {'audio': tts_audio, 'prompt': prompt_text, 'tag': 'flag_reason'})

def handle_flag_reason_response(response_text, connection):
    transaction_id = audio_data.get_data('transaction_id')
    flag_reason_value = get_value(response_text, "reason", "Extract the reason for flagging the transaction and whether the card was with the user or not.").value

    cursor = connection.cursor(dictionary=True)
    update_query = "UPDATE pba_transactions SET flagged = 1, flag_reason = %s WHERE t_id = %s"
    cursor.execute(update_query, (flag_reason_value, transaction_id))
    connection.commit()
    
    prompt_text = "The transaction has been successfully flagged."
    synthesize_audio(prompt_text)
    with open("output.mp3", "rb") as audio_file:
        tts_audio = audio_file.read()
    emit('tts_audio', {'audio': tts_audio, 'prompt': prompt_text})
