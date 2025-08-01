from core.server import start_server
import math
import numpy as np
from typing import Any, Dict, List 
from core.tools import open_matlab_file, open_simulink_file, save_matlab_code, get_variables, get_workspace_summary, search_library, run_matlab_code


import matlab.engine
start_server()
from core.state import server_state, get_engine


from utils.converters import fetch

eng = server_state.eng

import IPython; IPython.embed()