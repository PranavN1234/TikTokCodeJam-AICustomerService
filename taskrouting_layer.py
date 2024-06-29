from routing_layer import setup_route_layer

rl  = setup_route_layer()

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
