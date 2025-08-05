from utils.logger import logger
import matlab.engine
import sys


def search_sessions() -> list:
    try:
        logger.info("Searching for shared MATLAB Desktop sessions...")
        sessions = matlab.engine.find_matlab()
        if not sessions:
            logger.error("No sessions found. Share a MATLAB session by running matlab.engine.shareEngine in a MATLAB desktop command window. ")
            sys.exit(1)
        return sessions 
    except Exception as e:
        logger.error("Error searching for MATLAB sessions", exc_info=True)


def connect_session(session: str):
    logger.info(f"Connecting to MATLAB session: {session}")
    try: 
        return matlab.engine.connect_matlab(session)
    except matlab.engine.EngineError as e:
        logger.error(f"Failed to connect to MATLAB: {e}", exc_info=True)
    except Exception as e:
        logger.error("Unexpected error during MATLAB connection", exc_info=True)