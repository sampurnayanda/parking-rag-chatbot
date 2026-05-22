from app.chatbot.chatbot import chat
from app.database.db import init_db

def main():
    init_db()  # initialize database

    print("🚗 Parking Assistant Chatbot")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        response = chat(user_input)
        print("Bot:", response)


if __name__ == "__main__":
    main()