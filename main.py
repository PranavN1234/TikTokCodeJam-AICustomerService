from taskrouting_layer import route_task
from value_extractor import get_value

# Basic menu list
menu = [
    {"name": "Pepperoni Pizza", "price": "$12.99"},
    {"name": "Cheeseburger", "price": "$8.99"},
    {"name": "Caesar Salad", "price": "$7.99"},
    {"name": "Spaghetti Bolognese", "price": "$10.99"},
    {"name": "Grilled Cheese", "price": "$5.99"},
]

# List to keep track of current orders
current_orders = []

def display_menu():
    """
    Returns a formatted string of the menu.
    """
    menu_str = "Today's Menu:\n"
    for item in menu:
        menu_str += f"{item['name']} - {item['price']}\n"
    return menu_str

def display_orders():
    """
    Returns a formatted string of the current orders.
    """
    if not current_orders:
        return "No current orders."
    
    orders_str = "Current Orders:\n"
    for item in current_orders:
        orders_str += f"{item}\n"
    return orders_str

def handle_query(user_query):
    # Route the query to determine the intent
    route_name = route_task(user_query)
    
    # Depending on the route, extract additional details if necessary
    if route_name == "show_menu":
        response = display_menu()
    elif route_name == "order_item":
        item_name = get_value(user_query, "item name", "Extract the item name from the user query")
        current_orders.append(item_name.value)
        response = f"Ordering item: {item_name.value}\n{display_orders()}"
    elif route_name == "cancel_order":
        item_name = get_value(user_query, "item name", "Extract the item name to cancel from the user query")
        if item_name.value in current_orders:
            current_orders.remove(item_name.value)
            response = f"Cancelling order for: {item_name.value}\n{display_orders()}"
        else:
            response = f"No order found for: {item_name.value}\n{display_orders()}"
    else:
        response = "Sorry, I didn't understand your request."

    return response

def main():
    print("Welcome to the Restaurant Bot!")
    print("Type 'exit' to quit the program.\n")
    
    # while True:
    #     user_query = input("You: ")
    #     if user_query.lower() == 'exit':
    #         print("Goodbye!")
    #         break
    #     response = handle_query(user_query)
    #     print(f"Bot: {response}\n")

    item_size = get_value("I would love a large not wait not large a small", "item_size", "Extract item size from user query")

    print(f"item size is {item_size}")

if __name__ == "__main__":
    main()
