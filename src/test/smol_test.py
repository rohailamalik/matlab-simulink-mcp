from core.server import start_server
from pathlib import Path

import matlab.engine
from core.tools import open_matlab_file, open_simulink_file, save_matlab_code, run_matlab_code, get_variables, get_workspace_summary, search_library


start_server()

#file_name = "brain.m"

#status = open_matlab_file(file_name)
#print(status)

import IPython; IPython.embed()

