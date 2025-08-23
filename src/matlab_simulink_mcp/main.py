from matlab_simulink_mcp.utils.logger import logger
import matlab.engine
from matlab_simulink_mcp.core.state import get_state
from matlab_simulink_mcp.core.server import mcp


def search_sessions() -> list[str]:
    try:
        return matlab.engine.find_matlab() or []
    except Exception as e:
        raise RuntimeError("Error searching for sessions.")


def select_session() -> str:
    while True:
        sessions = search_sessions()
        if not sessions:
            logger.info(
                "No shared sessions found. "
                "Run `matlab.engine.shareEngine` in MATLAB to share a session."
            )
            input("Press Enter to retry...")
            continue

        if len(sessions) == 1:
            return sessions[0]

        logger.info("Multiple shared sessions found:")
        for i, s in enumerate(sessions, 1):
            logger.info(f"  {i}. {s}")

        while True:
            choice = input("Select a session by typing its index: ").strip()
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(sessions):
                    return sessions[idx - 1]
            logger.info("Invalid choice. Please enter a valid number.")


def run():
    try:
        logger.info("Searching for shared MATLAB sessions.")
        session = select_session()
        
        logger.info(f"Connecting to MATLAB session: {session}")
        get_state().initialize()
        
        logger.info(f"Connected to MATLAB session: {session}")
        mcp.run(transport='stdio')
    
    except Exception as e:
        raise RuntimeError("Error: {e}")
    

if __name__ == "__main__":
    run()
    #raise SystemExit(run())