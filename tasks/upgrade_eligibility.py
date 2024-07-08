from collections import defaultdict
from user_data import UserData
from utils import synthesize_audio
from flask_socketio import emit
from decimal import Decimal
from modified_prompting import modify_prompt
# Card cutoff scores JSON mapper
CARD_DETAILS = {
    'standard': {'cutoff_score': 10000, 'credit_limit': 5000, 'interest_rate': 15.0},
    'silver': {'cutoff_score': 13000, 'credit_limit': 10000, 'interest_rate': 14.0},
    'gold': {'cutoff_score': 16000, 'credit_limit': 15000, 'interest_rate': 13.0},
    'platinum': {'cutoff_score': 19000, 'credit_limit': 20000, 'interest_rate': 12.0},
    'diamond': {'cutoff_score': 22000, 'credit_limit': 30000, 'interest_rate': 10.0}
}

def fetch_customer_eligibility_data(connection, customer_id):
    cursor = connection.cursor(dictionary=True)
    query = """
    SELECT credit_score, income_level, employment_status, credit_history_years, 
           payment_history, credit_utilization_ratio, debt_to_income_ratio, existing_debt
    FROM pba_customer_eligibility
    WHERE customerid = %s
    """
    cursor.execute(query, (customer_id,))
    return cursor.fetchone()

def fetch_customer_current_card(connection, customer_id):
    cursor = connection.cursor(dictionary=True)
    query = """
    SELECT card_status
    FROM pba_card
    WHERE customerid = %s AND card_type LIKE 'Credit%%'
    """
    cursor.execute(query, (customer_id,))
    return cursor.fetchone()

def calculate_eligibility_score(customer_data):
    print('Calculating eligibility score')
    weights = {
        'credit_score': 0.3,
        'income_level': 0.2,
        'employment_status': 0.1,
        'credit_history_years': 0.1,
        'payment_history': 0.1,
        'credit_utilization_ratio': 0.1,
        'debt_to_income_ratio': 0.05,
        'existing_debt': 0.05
    }
    
    # Map employment status to a numeric value
    employment_status = 1 if customer_data['employment_status'] == 'Employed' else 0
    
    # Convert payment history to a float percentage
    payment_history = float(Decimal(customer_data['payment_history']) / 100)
    
    # Convert other values to floats
    credit_utilization_ratio = float(Decimal(customer_data['credit_utilization_ratio']) / 100)
    debt_to_income_ratio = float(Decimal(customer_data['debt_to_income_ratio']) / 100)
    existing_debt = float(Decimal(customer_data['existing_debt']) / 10000)  # Assuming a scaling factor

    score = (
        float(customer_data['credit_score']) * weights['credit_score'] +
        float(customer_data['income_level']) * weights['income_level'] +
        employment_status * weights['employment_status'] +
        float(customer_data['credit_history_years']) * weights['credit_history_years'] +
        payment_history * weights['payment_history'] +
        (1 - credit_utilization_ratio) * weights['credit_utilization_ratio'] +
        (1 - debt_to_income_ratio) * weights['debt_to_income_ratio'] +
        (1 - existing_debt) * weights['existing_debt']
    )
    
    print(f'Calculated score: {score}')
    return score

def check_upgrade_eligibility(connection):
    user_data = UserData()
    customer_id = user_data.get_data('customer_id')
    print(customer_id)
    customer_data = fetch_customer_eligibility_data(connection, customer_id)
    print(customer_data)
    current_card = fetch_customer_current_card(connection, customer_id)
    print(current_card)

    if not customer_data or not current_card:
        print('Entering here')
        prompt_text = 'You are not eligible for any card upgrades at this moment.'
        synthesize_audio(prompt_text)
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': prompt_text})
        return
    
    # Calculate the eligibility score
    eligibility_score = calculate_eligibility_score(customer_data)
    print(eligibility_score)
    
    # Get the cutoff score for the current card type
    current_card_type = current_card['card_status'].lower()
    print(current_card_type)
    current_card_cutoff_score = CARD_DETAILS.get(current_card_type, {}).get('cutoff_score')
    print(current_card_cutoff_score)
    if current_card_cutoff_score is None:
        prompt_text = 'You are not eligible for any card upgrades at this moment.'
        synthesize_audio(prompt_text)
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': prompt_text})
        return

    # Find eligible cards for upgrade
    eligible_upgrade = None
    for card_type, details in CARD_DETAILS.items():
        if details['cutoff_score'] > current_card_cutoff_score and eligibility_score >= details['cutoff_score']:
            eligible_upgrade = card_type
            break

    print(eligible_upgrade)
    if eligible_upgrade:
        card_details = CARD_DETAILS[eligible_upgrade]
        prompt_text = (
            f"You are eligible for an upgrade to the {eligible_upgrade} card. "
            f"This card has a credit limit of {card_details['credit_limit']} "
            f"and an interest rate of {card_details['interest_rate']}%. "
            "an email has been sent on further instructions on how to apply"
        )

        modified_prompt = modify_prompt(prompt_text, "The user has been made eligible for the following upgrade, style the response in a nice manner")
        synthesize_audio(prompt_text)
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {
            'audio': tts_audio, 
            'prompt': modified_prompt, 
            'credit_limit': card_details['credit_limit'],
            'interest_rate': card_details['interest_rate'],
            'response': 'no_response'
        })
    else:
        prompt_text = 'You are not eligible for any card upgrades at this moment.'
        synthesize_audio(prompt_text)
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': prompt_text})
        return