from taskrouting_layer import route_task

def main():
    
    while True:
        user_query = input("You: ")
        if user_query.lower() == 'exit':
            print("Goodbye!")
            break
        task = route_task(user_query)
        print(f"Mapped: {task}\n")
    

if __name__ == "__main__":
    main()
