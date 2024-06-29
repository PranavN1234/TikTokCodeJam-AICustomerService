import os
from dotenv import load_dotenv
from semantic_router.encoders import OpenAIEncoder
from semantic_router.layer import RouteLayer
from semantic_router import Route

# Load the .env file
load_dotenv()

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize the encoder
encoder = OpenAIEncoder()

# Define the routes
routes = [
    Route(name="show_menu", utterances=[
        "What are the specials today?", 
        "Show me the menu", 
        "I would love to eat something great today",
        "What's on the menu?", 
        "Can I see the menu?", 
        "What do you have for dinner?",
        "Any specials today?",
        "I'm hungry, what's available?",
        "Tell me today's specials",
        "Can you show me your menu?"
    ]),
    Route(name="order_item", utterances=[
        "I want to order a pizza", 
        "Can I get a burger?", 
        "I would love to try the cheeseburger", 
        "I want to order some food", 
        "Can I place an order?", 
        "I would like to order a pepperoni pizza", 
        "I want to get a Caesar Salad",
        "Can I order spaghetti?",
        "I would like a grilled cheese",
        "I'd like to have a burger"
    ]),
    Route(name="cancel_order", utterances=[
        "Cancel my order", 
        "I want to cancel my order", 
        "I don't feel like getting a burger anymore", 
        "Can I cancel my order?", 
        "Please cancel my food order", 
        "I need to cancel my order",
        "Cancel the pizza I ordered earlier",
        "I changed my mind, cancel the burger",
        "I want to cancel my food",
        "Please cancel the order"
    ]),
]

# Initialize the Route Layer
rl = RouteLayer(encoder=encoder, routes=routes)

def route_task(user_query):
    """
    Routes the user query to the appropriate task.

    Args:
    - user_query (str): The query from the user.

    Returns:
    - str: The name of the route (task) that the query is routed to.
    """
    route = rl(user_query)
    return route.name
