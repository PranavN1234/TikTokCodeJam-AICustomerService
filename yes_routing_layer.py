# yes_routing_layer.py

from semantic_router.encoders import OpenAIEncoder
from semantic_router.layer import RouteLayer
from semantic_router import Route

def setup_yes_route_layer():
    # Initialize the encoder
    encoder = OpenAIEncoder()

    # Define the yes route
    yes_route = Route(
        name="affirmative",
        utterances=[
            "yes",
            "yeah",
            "yep",
            "affirmative",
            "sure",
            "of course",
            "definitely",
            "absolutely",
            "indeed",
            "certainly",
            "ok",
            "okay",
            "alright",
            "aye",
            "roger",
            "uh-huh",
            "yup",
            "correct",
            "I agree",
            "that's right",
            "right",
            "go ahead",
            "yeah sure"
        ],
    )

    # Initialize and return the RouteLayer with the yes route
    return RouteLayer(encoder=encoder, routes=[yes_route])
