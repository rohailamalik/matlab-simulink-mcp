# This file is for setting up the project root path
# It is used to resolve relative paths in the project
# It should always be placed at the root of the project directory

import sys
from pathlib import Path

def get_file_path() -> Path:
    if getattr(sys, 'frozen', False): 
        return Path(sys._MEIPASS)  
    return Path(__file__).resolve().parent

root_path = get_file_path()