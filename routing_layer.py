import os
from dotenv import load_dotenv
from semantic_router.encoders import OpenAIEncoder
from semantic_router.layer import RouteLayer
from semantic_router import Route

def setup_route_layer():
    # Load the .env file
    load_dotenv()

    # Set the OpenAI API key
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

    # Initialize the encoder
    encoder = OpenAIEncoder()

    # Define the routes
    check_balance = Route(
        name="check_balance",
        utterances=[
            "What is my current bank balance?",
            "Can you tell me my account balance?",
            "How much money do I have in my account?",
            "Show me my bank balance",
        ],
    )

    change_information = Route(
        name="change_information",
        utterances=[
            "I want to change my address",
            "Update my phone number",
            "Can I change my email address?",
            "I need to update my contact information",
            "I want to add my social security number",
            "I think my address is incorrect on the account",
            "I have moved to a new place and need to change my address",
            "I think my DOB is incorrect, I need to correct that information",
            "Can you update my mailing address?",
            "I need to change my billing address",
            "Update my emergency contact number",
            "How do I update my personal details?",
            "I want to update my home address",
            "Change my residential address",
            "My phone number has changed, please update it",
            "Correct my date of birth information",
            "I need to correct my name spelling on the account",
            "How can I add an alternate phone number?",
            "Please update my work phone number",
            "I want to change my secondary email address",
            "My contact information needs to be updated",
            "I need to add a new address to my account",
            "How do I remove an old address from my profile?",
            "Can you update my account with my new details?",
        ],
    )

    block_card = Route(
        name="block_card",
        utterances=[
            "I want to block my card",
            "My card is lost, please block it",
            "Can you block my credit card?",
            "I need to block my debit card",
            "Block my card immediately",
            "My card was stolen, block it",
            "How do I block my card?",
            "Deactivate my card",
            "Please block my card",
            "Stop my card",
            "I think someone is using my card, can you block it please?",
            "I suspect fraudulent activity on my card, block it now",
            "My card has been compromised, I need to block it",
            "There's an unauthorized transaction on my card, block it",
            "I lost my card, can you block it?",
            "My card is missing, I need it blocked immediately",
            "I misplaced my card, please block it for me",
            "Block my card, I think it's been stolen",
            "I can't find my card, block it right away",
            "Can you deactivate my lost card?",
            "I think my card is in the wrong hands, block it",
            "Urgently block my card, I believe it's being misused",
            "My wallet was stolen, block my card",
            "Block my card to prevent any unauthorized use",
            "I need to block my card to avoid fraud",
            "Stop all transactions on my card and block it",
            "Please block my card to prevent further misuse",
            "My card was taken, block it now",
            "Can you help me block my card?",
        ],
    )

    issue_new_card = Route(
        name="issue_new_card",
        utterances=[
            "I want to issue a new card",
            "Can I get a new credit card?",
            "Please issue a new debit card",
            "I need a replacement card",
            "How can I get a new card?",
            "Request a new card",
            "I need a new card",
            "Can you send me a new card?",
            "I want a new card",
            "Order a new card for me",
            "Can I get a replacement card?",
            "I lost my card, can I get a new one?",
            "Issue a new credit card for me",
            "I need a new debit card",
            "Please send me a replacement card",
        ],
    )

    flag_fraud = Route(
        name="flag_fraud",
        utterances=[
            "I want to flag a transaction as fraud",
            "This transaction is suspicious",
            "I did not authorize this transaction",
            "Please mark this transaction as fraudulent",
            "How do I report a fraudulent transaction?",
            "Report this as fraud",
            "This charge is fraudulent",
            "I want to report fraud",
            "Flag this charge as fraud",
            "I need to report a suspicious transaction",
            "I found an unauthorized charge on my account",
            "There's a transaction I don't recognize, report it as fraud",
            "I think my card was used fraudulently",
            "Can you help me report a fraudulent transaction?",
            "I see a suspicious charge on my statement",
            "Someone used my card without my permission",
            "I want to dispute a fraudulent charge",
            "There's a charge on my account that I didn't make",
            "I need to report an unauthorized transaction",
            "Can you mark this transaction as fraud?",
            "This purchase is fraudulent, I didn't make it",
            "I need to report fraud on my account",
            "There's a charge on my card I don't recognize",
            "Report this charge as fraudulent",
            "I want to flag this transaction as suspicious",
            "I see an unrecognized charge on my account",
            "Please report this unauthorized transaction",
            "There's a transaction I didn't approve",
            "I think my account has been compromised",
        ],
    )

    redirect_agent = Route(
        name="redirect_agent",
        utterances=[
            "I want to talk to a human agent",
            "Can you connect me to a customer service representative?",
            "Please redirect me to a human agent",
            "I need to speak with a customer service representative",
            "Connect me to a human agent",
            "I want to speak to a person",
            "Transfer me to a human agent",
            "I need to talk to a real person",
            "Can I speak with a representative?",
            "I need to talk to a customer service agent",
            "I need help from a human",
            "Put me through to a customer service rep",
            "I want to talk to someone",
            "Connect me to customer support",
            "I need to speak to a human representative",
        ],
    )

    chitchat = Route(
        name="chitchat",
        utterances=[
            "How's the weather today?",
            "What's your favorite type of music?",
            "Did you watch the game last night?",
            "How are you doing?",
            "What's your favorite movie?",
            "Have you read any good books lately?",
            "Nice weather we're having, isn't it?",
            "Do you have any plans for the weekend?",
            "What's your favorite food?",
            "How was your day?",
            "Do you like to travel?",
            "What's your favorite hobby?",
            "Have you been to any good restaurants recently?",
            "What's your favorite TV show?",
            "What do you do for fun?",
        ],
    )
    
    end_conversation = Route(
        name="end_conversation",
        utterances=[
            "That's all for now",
        "I'm done, thank you",
        "I think we're finished here",
        "That's it for today",
        "Nothing else, thanks",
        "No more questions",
        "That will be all",
        "We're good here",
        "I have no more queries",
        "This concludes our session",
        "I'm all set",
        "Thanks, that's all",
        "I'm finished, thank you",
        "We can wrap this up",
        "I don't need anything else",
        "Thanks, I'm done",
        "I appreciate the help, goodbye",
        "I have everything I need, thank you",
        "Thank you, goodbye",
        "That'll do, thanks",
        ],
    )

    # Place all of our decisions together into a single list
    routes = [
        check_balance,
        change_information,
        block_card,
        issue_new_card,
        flag_fraud,
        redirect_agent,
        chitchat,
        end_conversation
    ]

    # Initialize and return the RouteLayer
    return RouteLayer(encoder=encoder, routes=routes)
