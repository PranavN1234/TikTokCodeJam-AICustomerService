from collections import defaultdict
from user_data import UserData
from ai_service import analyze_transaction
from utils import synthesize_audio
from flask_socketio import emit

def fetch_and_categorize_transactions(connection, account_number):
    cursor = connection.cursor(dictionary=True)
    query = """
    SELECT t_id, from_account, to_account, amount, timestamp, category
    FROM pba_transactions
    WHERE from_account = %s
    ORDER BY timestamp DESC
    LIMIT 30
    """
    cursor.execute(query, (account_number,))
    transactions = cursor.fetchall()

    categories = defaultdict(float)
    for transaction in transactions:
        categories[transaction['category']] += float(transaction['amount'])

    return transactions, categories

def perform_transaction_analysis(connection):
    user_data = UserData()
    account_number = user_data.get_data('account_number')
    transactions, categories = fetch_and_categorize_transactions(connection, account_number)
    analysis = analyze_transaction(transactions, categories)

    # Synthesize the analysis text to audio
    synthesize_audio(analysis)
    with open("output.mp3", "rb") as audio_file:
        tts_audio = audio_file.read()

    # Emit the audio response along with the analysis and categories
    emit('tts_audio', {'audio': tts_audio, 'prompt': analysis, 'categories': dict(categories)})