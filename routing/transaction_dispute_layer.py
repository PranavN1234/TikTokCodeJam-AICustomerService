from semantic_router.encoders import OpenAIEncoder
from semantic_router.layer import RouteLayer
from semantic_router import Route

def setup_transaction_dispute_route_layer():
    encoder = OpenAIEncoder()

    general_dispute_route = Route(
        name="general_dispute",
        utterances=[
            "I don't recognize my last transaction",
            "The last 3 transactions on my card were made by someone else",
            "I don't get the past 4 transactions",
            "The recent transactions on my account seem suspicious",
            "I didn't make the last few purchases",
            "My last few transactions are incorrect",
            "Someone else made the last transactions on my card",
            "The last transactions don't look right",
            "The last transactions are not mine",
            "I didn't make the recent transactions",
            "The past few transactions are not mine",
            "I think my card was used by someone else for the last few transactions",
            "The recent transactions are unauthorized",
            "I have unauthorized transactions on my account",
            "The last transactions were not made by me",
            "I don't remember making the last few transactions",
        ],
    )

    specific_dispute_route = Route(
        name="specific_dispute",
        utterances=[
            "I don't recognize this transaction",
            "I don't recognize the transaction number",
            "The transaction number XYZ is not mine",
            "The transaction ID ABCD is unauthorized",
            "I didn't make the transaction with ID",
            "The transaction with number XYZ is incorrect",
            "I don't remember the transaction with ID",
            "The transaction with reference number ABCD is not mine",
            "I want to dispute the transaction number",
            "The transaction ID XYZ is fraudulent",
            "I didn't authorize the transaction with number",
            "I want to flag the transaction with ID",
            "The transaction with reference number is suspicious",
            "I need to report the transaction number",
            "The transaction number ABCD is not valid",
            "There's a problem with the transaction ID",
        ],
    )

    return RouteLayer(encoder=encoder, routes=[general_dispute_route, specific_dispute_route])
