from core.server import start_server
from pathlib import Path

import matlab.engine
start_server()
from core.state import server_state, get_state
from core.tools import open_matlab_file


start_server()

file_name = "C:\Data\Research\Doctoral\src\SimAI\server.m"

status = open_matlab_file(file_name)
print(status)

import IPython; IPython.embed()

