from core.initialization import load_server_data, set_helpers
from core.matlab_connection import search_sessions, connect_session
import core.state
from utils.logger import logger
from fastmcp import FastMCP

#mcp = FastMCP("SimAI_MCP")

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
    
    core.state.eng = connect_session(session)
    core.state.sl_lib_data = load_server_data()
    core.state.session_name = session

    set_helpers(core.state.eng)

    #mcp.run(transport='stdio')

    logger.info("MATLAB MCP Server has shut down.")
    









