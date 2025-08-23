from simai.llm.agent import sim_agent
from simai.core.state import init_state
from langchain_core.messages import HumanMessage

init_state()

def respond(user_input: str, chat_history):
    chat_history["messages"].append(HumanMessage(content=user_input))
    chat_history = sim_agent.invoke(chat_history)
    messages = chat_history["messages"]
    return messages[-1].content, chat_history

def run_chat():
    print("=== SimAI Test Chat ===")
    print("Type 'exit' or 'quit' to quit.\n")

    chat = {"messages": []}
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        try:
            response, chat = respond(user_input, chat)
            print(f"Assistant: {response}\n")
        except Exception as e:
            print(f"Critical error: {e}")
            input("Press enter to retry.")

if __name__ == "__main__":
    run_chat()
