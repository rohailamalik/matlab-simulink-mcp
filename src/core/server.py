from core.startup import load_server_data, set_helpers, set_cwd, set_security
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
    server_state.cwd = set_cwd(server_state.eng)
    server_state.helpers_path = set_helpers(server_state.eng)
    server_state.sl_lib_data = load_server_data()
    server_state.advanced_security = set_security(server_state.eng)




# TODO: Incorporate a check engine function and run it on a separate thread on loop
# TODO: Making the startup a bit more robust. 
# TODO: Work on the logger
# TODO: TEST TEST TEST
# TODO: exe compilation
    
# TODO: In tools, introduce a fallback where the saving/writing/running directory is changed from working directory to temp
# TODO: Simulink opening tool maybe

# TODO: CWD fetching with each tool call instead of from state.


# TODO: Ban builtin and some other sutff
# TODO: Ban unwrappable functions 


# Strategy: 
# Any function writing or reading or running stuff, absolute paths are not allowed at all. 
# This limits only accessing the files which are on path. 


# LLM writes code to run or save
# Run a string check. Detect .. or absolute paths. They are not allowed at all. Absolute paths may be detectable through string checks.
# This limits llm to only access or work with whatever is inside the cwd or is on the path.
# The only option left for the llm is to add the file it's trying to access is by inputting the full path which is forbidden by the first absolute path ban
# or it has to add that to matlab path, which again needs it to provide an absolute path which against is banned.
# an additional possible check is to ban addpath, removepath etc all path related functions.
# any line beginning with a ! is banned
# system command is banned through a wrapper. so is unix.
# " eval, feval, etc are banned but not evalc since it is used for running code from tools.  


# goal is to prevent absolute paths or ..
# introducing wrapper functions. they are for every function that uses a path argument(s). these wrappers are put first in the path so they are always run. 
# these detect absolute paths or .. and deny execution.
# eval, feval etc are all banned via wrappers. so is str2func. and system and unix etc 
# evalc cannot be banned. since it is used in a tool. instead evalc wrapper uses string checks on abovementioned commands including str2func. 



# builtin is the most dangrous thing kinda. it is banned through string check. 
# secondly, str2func seems to be the only method that calls a function through hidden ways like strings detached etc. 
# so in wrapper of str2func we put a check for builtin. if it is called we block it. there is also a string check in main code text too. 



# TODO. IMPLEMENT MODES. HIGH SAFETY LOW SAFTEY WHICH ARE STORED IN STATE. HIGH SAFETY HAS ALL WRAPPER STUFF LOW SAFTEY IS ONLY STRING CHECKS



# what is left is to update wrapers