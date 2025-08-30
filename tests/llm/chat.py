from tests.llm.agent import agent
from langchain_core.messages import HumanMessage
from matlab_simulink_mcp.core.state import get_state

get_state().initialize()

def respond(user_input: str, chat):
    chat["messages"].append(HumanMessage(content=user_input))
    chat = agent.invoke(chat)
    messages = chat["messages"]
    return messages[-1].content, chat

def run_chat():
    print("=== Test Chat ===")
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
