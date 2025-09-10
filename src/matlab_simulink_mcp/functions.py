import asyncio
import tempfile
from pathlib import Path
from difflib import SequenceMatcher

from fastmcp.exceptions import ToolError
from fastmcp.utilities.types import Image

from matlab_simulink_mcp.state import get_state, logger
from matlab_simulink_mcp.security import check_path, check_code

# TODO: figure out how to undo stuff in simulink
# TODO: maybe add system prompt as a server resource
# TODO: Later implement a canvas based editor


def _get_engine():
    eng = get_state().eng
    if eng is None:
        raise ToolError("Could not access MATLAB. Run matlab.engine.shareEngine"
        " in MATLAB, and then use access_matlab tool to reconnect.")
    return eng 

def _raise_error(e: Exception):
    logger.exception(e) 
    raise ToolError(str(e).strip().splitlines()[-1])

def _clean_evalc(s: str) -> str:
    return "\n".join(line.strip() for line in s.splitlines() if line.strip())

def _get_image(path) -> Image:
    path = Path(str(path))
    data = path.read_bytes()
    path.unlink(missing_ok=True)
    return Image(data=data, format="png")


async def access_matlab() -> str:
    """Connect to MATLAB."""

    try:
        _get_engine()
        return f"Already connected to MATLAB session: {get_state().session}"
    except ToolError:
        try:
            await asyncio.to_thread(get_state().connect_matlab)
            _get_engine()
            return f"Connected to MATLAB session: {get_state().session}"
        except ToolError as e:
            raise
    except Exception as e:
        _raise_error(e)
    

async def read_simulink_system(path: str, detail: bool=False, open: bool=False) -> Image | dict:
    """
    View a Simulink system/subsystem as either a PNG image or a detailed dictionary (if detail=True).
    Optionally open the object in MATLAB desktop.
    Detail only recommended when exact port tags or other details are needed, as it can be verbose.
    """

    eng = _get_engine()
    check_path(path)
    
    parent, _, rest = path.partition("/")
    parent = parent.removesuffix(".slx")
    path = parent if not rest else f"{parent}/{rest}"
          
    try:
        if detail:
            return await asyncio.to_thread(eng.describe_system, path, parent, open, nargout=1)
        else:
            ss_path = await asyncio.to_thread(eng.snapshot_system, path, parent, open, nargout=1)
            return _get_image(ss_path)
    except Exception as e:
        _raise_error(e)

  
async def read_matlab_code(path: str, open: bool=False) -> str:
    """
    Read the contents of a MATLAB script (.m) or text file.
    Optionally open the file in MATLAB desktop.
    """

    eng = _get_engine()
    check_path(path)
    
    try:
        if open:
            await asyncio.to_thread(eng.edit, path, nargout=0)
        return await asyncio.to_thread(eng.fileread, path, nargout=1)
    except Exception as e:
        _raise_error(e)   


async def save_matlab_code(code: str, path: str, overwrite: bool=False) -> str:
    """
    Validate and save MATLAB code to a .m file.
    Optionally overwrite if the file already exists.
    """

    eng = _get_engine()
    check_path(path)
    check_code(code)

    mode = "w" if overwrite else "x"

    try:
        cwd = await asyncio.to_thread(eng.pwd, nargout=1)
        abs_path = Path(str(cwd)) / path
        abs_path.parent.mkdir(parents=True, exist_ok=True) 
        with abs_path.open(mode) as f:
            f.write(code)
 
        issues = await asyncio.to_thread(eng.validate_code, path)
        if issues:
            return "Code saved but failed validation with errors:\n" + "\n".join(issues)
        else:
            return "Code saved and validated successfully."
        
    except Exception as e:
        _raise_error(e) 


async def run_matlab_code(code: str, get_images: bool=False) -> tuple[str, *tuple[Image, ...]]:
    """
    Execute MATLAB code and return command window output as a string and images (if asked).
    Interact programatically with Simulink if the action is not covered by a tool.
    """

    eng = _get_engine()
    check_code(code)

    imgs: list[Image] = []

    try:
        if get_images:
            await asyncio.to_thread(eng.close, 'all', nargout=0)

        try:
            cwd = await asyncio.to_thread(eng.pwd, nargout=1)
            abs_path = Path(str(cwd)) / "canvas.m"
            abs_path.parent.mkdir(parents=True, exist_ok=True) 
            with abs_path.open("w") as f:
                f.write(code)
        except PermissionError:
            with tempfile.NamedTemporaryFile("w", suffix=".m", delete=False) as f:
                f.write(code)
                abs_path = Path(f.name)
            pretext = "Could not run from current working directory. Running from temporary directory:\n"
    
        text = _clean_evalc(await asyncio.to_thread(eng.evalc, f"run('{str(abs_path)}')", nargout=1))
        if pretext:
            text = pretext + text

        abs_path.unlink(missing_ok=True)
        
        await asyncio.to_thread(eng.format_system, nargout=0)

        img_paths = await asyncio.to_thread(eng.get_images, nargout=1)
        imgs = [_get_image(p) for p in img_paths]

        return (text, *imgs) 

    except Exception as e:
        _raise_error(e)
            

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
       _raise_error(e)
    
# TODO remember the newline thing for \n 
# ['VehicleWithFourSpeedTransmission/Inertia', newline, 'Impeller']


