import asyncio
import tempfile
from pathlib import Path
from difflib import SequenceMatcher
from fastmcp.exceptions import ToolError
from fastmcp.utilities.types import Image
import traceback

from matlab_simulink_mcp.core.state import get_engine, get_state
from matlab_simulink_mcp.utils.convert import fetch
from matlab_simulink_mcp.utils.security import check_path, check_code
from matlab_simulink_mcp.utils.logger import logger

# TODO: Incorporate image reading and multi modality, also needed for simulink broader view using snapshots
# for graph reading etc it's just an addon, not necessary since the llm can just parse through arrays plotting the graph
# though it is not much optimal at large lengths etc
# TODO: figure out some how to undo stuff in simulink
# TODO: maybe add system prompt as a server resource


def _raise_error(msg: str, exception: Exception):
    tb = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
    main = str(exception).strip().splitlines()[-1]
    logger.error(tb) 
    raise ToolError(f"{msg} {main}")

def _ancestorize(path: str) -> tuple[str, str]:
    parts = path.split("/", 1)
    ancestor = parts[0]
    rest = parts[1] if len(parts) > 1 else ""

    ancestor = ancestor.removesuffix(".slx")

    new_path = ancestor if not rest else f"{ancestor}/{rest}"

    return new_path, ancestor

def _clean_evalc(s: str) -> str:
    lines = [line.strip() for line in s.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)



async def access_matlab() -> str:
    """Connect to MATLAB."""

    try:
        get_engine()
        return f"Already connected to MATLAB session: {get_state().session}"
    except ToolError:
        try:
            await asyncio.to_thread(get_state().connect_matlab)
            get_engine()
            return f"Connected to MATLAB session: {get_state().session}"
        except ToolError as e:
            raise
    except Exception as e:
        _raise_error("Failed to connect to MATLAB.", e)


async def snapshot_simulink_system(path: str, open: bool = False) -> Image:
    """
    Capture a Simulink system/subsystem as a PNG image.
    Optionally open the object in MATLAB desktop in addition.
    Recommened for "seeing" the overall layout of a system.
    """

    eng = get_engine()
    check_path(path)
    path, parent = _ancestorize(path)

    try: 
        ss_path = await asyncio.to_thread(eng.snapshot_system, path, parent, open, nargout=1)
        ss_path = Path(str(ss_path))
        data = ss_path.read_bytes()
        ss_path.unlink(missing_ok=True)
        return Image(data=data, format="png")
    
    except Exception as e:
        _raise_error("Error taking snapshot.", e)

    

async def read_simulink_system(path: str, open: bool = False) -> dict:
    """
    Return layout information for a Simulink system/subsystem, including elements, ports, and connections. 
    Optionally open the object in MATLAB desktop in addition.
    Only recommended when exact port tags or other details are needed, as the output can be quite verbose.
    """

    eng = get_engine()
    check_path(path)
    path, parent = _ancestorize(path)
          
    try:
        content = await asyncio.to_thread(eng.describe_system, path, parent, open, nargout=1)
        return content 
    except Exception as e:
        _raise_error("Error reading file.", e)
    

async def clean_simulink_system(path: str, arrange: bool = False) -> str: # a bit buggy on matlab side, see last log, maybe incprorate ports too in addition to lines. so delete partial/fully oprhaned lines and fully orphaned blocks
    """ # maybe merge with a tool for only writing matlab commands for simulink stuff and  just running these commands automatically 
    # need to figure out how to get current system for that tho, since gcs only works for currently open system
    Clean up a Simulink system or subsystem by deleting unconnected lines.
    Optionally also improve block layout arrangement in addition. 
    """

    eng = get_engine()
    check_path(path)
    path, parent = _ancestorize(path)
    
    try:
        return await asyncio.to_thread(eng.format_system, path, parent, arrange, nargout=1)
    except Exception as e:
        _raise_error("Error executing operation.", e)       

  
async def read_matlab_code(path: str, open: bool = False) -> str:
    """
    Read the contents of a MATLAB script (.m) or text file.
    Optionally open the file in MATLAB desktop in addition.
    """

    eng = get_engine()

    check_path(path)
    
    if open:
        try:
            await asyncio.to_thread(eng.edit, path, nargout=0)
        except Exception as e:
            _raise_error(f"Unexpected error while opening in desktop.", e)

    try:
        content = await asyncio.to_thread(eng.fileread, path, nargout=1)
        return content
    except Exception as e:
        _raise_error(f"Unexpected error when reading file.", e)   


async def save_matlab_code(code: str, path: str, overwrite: bool = False) -> str:
    """
    Validate and save MATLAB code to a .m file.
    Optionally overwrite if the file already exists.
    """

    eng = get_engine()

    check_path(path)
    check_code(code)

    mode = "w" if overwrite else "x"

    try:
        cwd = await asyncio.to_thread(eng.pwd, nargout=1)
        abs_path = Path(str(cwd)) / path
        abs_path.parent.mkdir(parents=True, exist_ok=True) 
        with abs_path.open(mode) as f:
            f.write(code)
    except Exception as e:
        _raise_error(f"Error saving the code.", e)
    
    try: 
        issues = await asyncio.to_thread(eng.validate_code, path)
        if issues:
            return "Code saved but failed validation with errors:\n" + "\n".join(issues)
        else:
            return "Code saved and validated successfully."
    except Exception as e:
        _raise_error(f"Error validating the code.", e) 
    
    


async def run_matlab_code(code: str) -> str:
    """
    Execute MATLAB code and return command window output as a string.
    Interact programatically with Simulink if the action is not covered by a tool.
    """

    # TODO: Later implement a canvas based editor
    eng = get_engine()

    check_code(code)

    async def _write_and_run(abs_path: Path) -> str:
        with abs_path.open("w") as f:
            f.write(code)
        content = await asyncio.to_thread(eng.evalc, f"run('{abs_path}')", nargout=1)
        return _clean_evalc(content)

    try: 
        cwd = await asyncio.to_thread(eng.pwd, nargout=1)
        abs_path = Path(str(cwd)) / "canvas.m"
        return await _write_and_run(abs_path)
    except PermissionError:
        abs_path = Path(tempfile.gettempdir()) / "canvas.m"
        return await _write_and_run(abs_path)
    except Exception as e:
        _raise_error("Unexpected error while running MATLAB code.", e)


async def get_variables(variables: list[str], convert: bool = False) -> dict:
    """
    Fetch variables from the MATLAB workspace.
    Optionally return converted Python types instead of string representations.
    """

    eng = get_engine()

    answer = {}
    for var in variables:
        try:
            # Cannot do "if in eng.workspace" since it is not a native Python dict, rather a MATLAB object with some dict-like properties.
            # eng.exist automatically ensuanswer that the var is a proper variable name, without any code injection which could execute through evalc
            exists = await asyncio.to_thread(eng.exist, var, "var") 
            if exists == 1: 
                if convert:
                    answer[var] = fetch(eng, var)
                else:
                    content = await asyncio.to_thread(eng.evalc, f"disp({var})", nargout=1)
                    answer[var] = _clean_evalc(content)
            else:
                answer[var] = "Not in workspace"

        except Exception:
            _raise_error(f"Error getting variable '{var}'.") 

    return answer   
    


def search_library(query: str) -> list:
    """
    Search the Simulink block library for a block name and return matching source paths.
    """

    try: 
        simlib = get_state().simlib
        candidates = [(name, path) for name, entry in simlib.items() for path in entry["paths"]]
        ranked = sorted(
            candidates,
            key=lambda item: SequenceMatcher(None, query.lower(), item[0].lower()).ratio(),
            reverse=True
        )
        return [path for _, path in ranked[:3]]
    
    except Exception as e:
       _raise_error(f"Error searching Simulink library.")
    
# TODO remember the newline thing for \n 
# ['VehicleWithFourSpeedTransmission/Inertia', newline, 'Impeller']


