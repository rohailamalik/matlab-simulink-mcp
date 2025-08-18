'''

from core.startup import search_sessions
from core.state import get_state
from utils.logger import logger


def start_server():
    logger.info("Searching for shared MATLAB sessions...")

    sessions = []
    while not sessions:
        sessions = search_sessions() or []
        if not sessions:
            logger.info("No shared MATLAB sessions found.")
            logger.info("In MATLAB, run: matlab.engine.shareEngine")
            input("Press enter to retry.")

    if len(sessions) == 1:
        session = sessions[0]
    else:
        logger.info(f"Multiple sessions found: {sessions}")
        while True:
            session = input("Enter session name to connect: ")
            if session in sessions:
                break
            logger.info("Session not found. Please input a correct session name.")

    get_state().set(session)
    logger.info(f"Connected to MATLAB session: {session}")
    get_state().validate()

'''


# TODO remember the newline thing for \n 
# ['VehicleWithFourSpeedTransmission/Inertia', newline, 'Impeller']

# SimuGen is more specific, we want our tools to be more generelizable and wrappeable partially at least as an mcp server
# maybe switch to logger.debug instead of raise (+ sys exit)

# TODO: Incorporate a check engine function and run it on a separate thread on loop
# TODO: Making the startup a bit more robust. 
# TODO: TEST TEST TEST
# TODO: exe compilation
    
# TODO: In tools, introduce a fallback where the saving/writing/running directory is changed from working directory to temp
# TODO: Incorporate image reading and multi modality, also needed for simulink broader view using snapshots
# for graph reading etc it's just an addon, not necessary since the llm can just parse through arrays plotting the graph
# though it is not much optimal at large lengths etc






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


