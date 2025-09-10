import os
from dotenv import load_dotenv

import matlab_simulink_mcp
from matlab_simulink_mcp.utils.log_utils import create_log_file, create_logger, create_console 
from matlab_simulink_mcp.utils.paths import get_full_path

load_dotenv()
matlab_dir = get_full_path(matlab_simulink_mcp, os.getenv("MATLAB_DIR"))
log_dir = get_full_path(matlab_simulink_mcp, os.getenv("LOG_DIR"))

log_file = create_log_file(filename=matlab_simulink_mcp.__name__, dir=log_dir)
logger = create_logger(name=matlab_simulink_mcp.__name__, log_file=log_file)
log_console = create_console(log_file=log_file)