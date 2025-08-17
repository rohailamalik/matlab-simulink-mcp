from llm.agent import SimAgent
from core.server import start_server
from langchain_core.messages import HumanMessage

start_server() 

def respond(user_input: str, chat_history):
    chat_history["messages"].append(HumanMessage(content=user_input))
    chat_history = SimAgent.invoke(chat_history)
    messages = chat_history["messages"]
    return messages[-1].content, chat_history
    
print("=== TechAssist AI Test Chat ===")
print("Type 'exit' or 'quit' to quit.\n")

chat = {"messages": []}
while True:
    user_input = input("You: ")
    if user_input.lower() in {"exit", "quit"}:
        print("Goodbye.")
        break

    response, chat = respond(user_input, chat)
    print(f"Assistant: {response}\n")