from semantic_router.encoders import OpenAIEncoder
from semantic_router.layer import RouteLayer
from semantic_router import Route

def setup_change_info_route_layer():
    encoder = OpenAIEncoder()

    change_generic_info = Route(
        name="generic_info_change",
        utterances=[
            "I need to update my contact information",
            "My contact information needs to be updated",
            "I would like to change some information",
            "I want to update my account with new information"
        ],
    )

    change_email = Route(
        name="change_email_address",
        utterances=[
            "I want to change my email address",
            "Update my email",
            "Change my email address",
            "I need to update my email",
            "I would like to change my email",
            "I want to update my email address",
        ],
    )
    
    change_address = Route(
        name="change_address",
        utterances=[
            "I want to change my address",
            "Update my address",
            "Change my address",
            "I need to update my address",
            "I want to change my resdential address"
        ],
    )

    return RouteLayer(encoder=encoder, routes=[change_generic_info, change_address, change_email])