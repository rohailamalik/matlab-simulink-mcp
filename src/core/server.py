from core.startup import load_server_data, set_helpers, set_up_canvas
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
    
    server_state.session = session
    server_state.eng = connect_session(session)
    server_state.sl_lib_data = load_server_data()
    server_state.canvas_path = set_up_canvas()
    server_state.helpers_path = set_helpers(server_state.eng)




# TODO: Incorporate a check engine function and run it on a separate thread on loop
# TODO: Making the startup a bit more robust. 
# TODO: Work on the logger
# TODO: TEST TEST TEST
# TODO: exe compilation
    









