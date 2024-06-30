from semantic_router.encoders import OpenAIEncoder
from semantic_router.layer import RouteLayer
from semantic_router import Route

def setup_card_type_route_layer():
    encoder = OpenAIEncoder()

    debit_route = Route(
        name="Debit",
        utterances=[
            "debit",
            "debit card",
            "my debit",
            "debit one",
            "John smith debit"
            "My debit card",
            "I would like to block the debit",
            "I wanna block the debit"
        ],
    )

    credit_route = Route(
        name="Credit",
        utterances=[
            "credit",
            "credit card",
            "my credit",
            "credit one",
            "My credit card",
            "I would love to block the credit card",
            "The credit card"
        ],
    )

    return RouteLayer(encoder=encoder, routes=[debit_route, credit_route])
