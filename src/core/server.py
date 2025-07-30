from core.startup import load_server_data, set_helpers
from core.eng_manager import search_sessions, connect_session
from core.state import server_state
from utils.logger import logger

def start_server():
    logger.info("Starting MATLAB MCP server...")
    sessions = search_sessions()
    if len(sessions) == 1:
        session = sessions[0]
    else:
        session = input("Multiple sessions found. Enter the session name to connect: ")
        while True:     
            if session in sessions:
                break
            else:
                session = input("Session not found. Please input a correct session name: ")
    
    server_state.eng = connect_session(session)
    server_state.sl_lib_data = load_server_data()

    set_helpers(server_state.eng)
    









