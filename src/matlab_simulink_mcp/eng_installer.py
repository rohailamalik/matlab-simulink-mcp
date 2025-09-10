import sys
import ctypes
import platform
import time
import subprocess
from pathlib import Path

system = platform.system()


def import_engine():
    try:
        import matlab.engine
        return True
    except ImportError:
        return False

def get_engine_setup_path(matlab_dir: Path | None) -> Path:
    if not matlab_dir:
        if system == "Windows":
            parent = Path("C:/Program Files/MATLAB")
        elif system == "Linux":
            parent = Path("/usr/local/MATLAB")
        elif system == "Darwin":
            parent = Path("/Applications")
        else:
            raise OSError(f"Unsupported OS: {system}.")

        candidates = [p for p in parent.glob("R20[2-9][0-9][ab]*") if p.is_dir()]
        if not candidates:
            raise FileNotFoundError(f"No valid MATLAB installations found in {parent}")

        matlab_dir = sorted(candidates)[-1] # find the latest version
        if not matlab_dir.exists():
            raise FileNotFoundError(f"MATLAB installation not found in {matlab_dir}. Please set MATLAB_DIR environment variable to your MATLAB installation directory.")
    
    setup_path = matlab_dir / "extern/engines/python/setup.py"
    if not setup_path.exists():
        raise FileNotFoundError(f"MATLAB Python engine setup not found at {setup_path}. Please verify your MATLAB installation directory.")
    
    return setup_path.parent
    
    
def install_engine_win(setup_path: Path):
    installer = Path(__file__).with_name("win_installer.py").resolve()
    args = subprocess.list2cmdline([str(installer), str(setup_path)])
    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, args, None, 1)
    if ret <= 32:
        raise PermissionError("Installation failed due to permission issues or some other error.")
    
    status = installer.with_name("install.log")
    for _ in range(30):
        if status.exists():
            lines = open(status).read().strip().splitlines()
            if lines:
                last = lines[-1]
                if last == "0":
                    #status.unlink() had to comment because claude sends request twice in init so it couldnt delete this
                    return
                elif last.isdigit():
                    e = "\n".join(lines[:-1])
                    #status.unlink()
                    raise RuntimeError(f"Failed to install MATLAB engine. \n: {e}")
        time.sleep(1)
    raise TimeoutError("Installer did not finish in time.")


def install_engine_mac_linux(setup_path: Path):
    try:
        subprocess.run(["sudo", sys.executable, "setup.py", "install"],
            cwd=setup_path,
            check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to install MATLAB engine. \n: {e}")


def install_engine(matlab_dir: Path | None):
    try: 
        setup_path = get_engine_setup_path(matlab_dir)

        time.sleep(2) # Wait for a while so that user sees that they need to grant permission.

        if system == "Windows":
            install_engine_win(setup_path)
        elif system in ["Linux", "Darwin"]:
            install_engine_mac_linux(setup_path)
        else:
            raise OSError(f"Unsupported OS: {system}.")
    
    except Exception as e:
        raise e

