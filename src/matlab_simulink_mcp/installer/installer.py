import sys, ctypes, platform, time, subprocess
from pathlib import Path


system = platform.system()

def verify_matlab_path(user_input: str) -> Path | None:
    """Validate that a user-specified directory contains MATLAB Engine setup."""
    while True:
        if not user_input:
            print("Aborting installation operation.")
            return None

        path = Path(user_input).expanduser().resolve()
        if path.is_dir():
            setup_path = path / "extern" / "engines" / "python" / "setup.py"
            if setup_path.exists():
                return setup_path.parent
            else:
                user_input = input(
                    f"MATLAB Python engine setup not found at {setup_path}.\n"
                    f"Please enter a valid MATLAB installation directory or press Enter to abort: "
                ).strip()
        else:
            user_input = input(
                "Invalid directory. Please enter a correct path to a MATLAB installation, or press Enter to abort: "
            ).strip()


def get_matlab_path() -> Path | None:
    system = platform.system()
    if system == "Windows": 
        parent = Path("C:/Program Files/MATLAB") 
    elif system == "Linux": 
        parent = Path("/usr/local/MATLAB") 
    elif system == "Darwin": 
        parent = Path("/Applications") 
    else: 
        raise OSError(f"Unsupported OS: {system}.")

    installations = [p for p in parent.glob("R20[2-9][0-9][ab]*") if p.is_dir()]
    installations.sort()

    try:
        if not installations:
            print("No MATLAB installations found in default directories.")
            choice = input("Please enter a path to MATLAB installation (or press Enter to abort): ").strip()
            return verify_matlab_path(choice)

        elif len(installations) == 1:
            matlab_path = installations[0]
            print(f"Found a MATLAB installation at {matlab_path}")
            choice = input(
                "Enter y to install MATLAB Engine from this installation (requires admin permissions), \n "
                "or enter another path (or press Enter to abort): "
            ).strip()
            if choice.lower() == "y":
                return verify_matlab_path(str(matlab_path))
            else:
                return verify_matlab_path(choice)

        else:  # multiple installs
            print("Multiple MATLAB installations found:")
            for i, inst in enumerate(installations, 1):
                print(f"[{i}] {inst}")

            while True:
                choice = input("Select installation by number (installing requires admin permissions), \n "
                "Or, Enter another installation path (or press Enter to abort): ").strip()
                if not choice:
                    print("Aborting by user choice.")
                    return None
                if choice.isdigit():
                    idx = int(choice)
                    if 1 <= idx <= len(installations):
                        return verify_matlab_path(str(installations[idx - 1]))
                    else:
                        print("Invalid selection.")
                        continue
                else:
                    return verify_matlab_path(choice)

    except KeyboardInterrupt:
        print("Aborted by user (Ctrl+C).")
        return None
    

from matlab_simulink_mcp.installer import win_elevate
win_install_log = "install.log"

def install_engine_win(setup_path: Path):
    script = Path(win_elevate.__file__).resolve()
    status = script.with_name(win_install_log)

    args = subprocess.list2cmdline([str(script), str(setup_path)])
    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, args, None, 1)
    if ret <= 32:
        raise RuntimeError("Installation failed due to permission issues or some other error.")
    
    for _ in range(15):
        if status.exists():
            lines = open(status).read().strip().splitlines()
            if lines:
                last = lines[-1]
                if last == "0":
                    #status.unlink() # had to comment because claude sends request twice in init so it couldnt delete this
                    return 
                elif last.isdigit():
                    e = "\n".join(lines[:-1])
                    #status.unlink()
                    raise RuntimeError(f"Failed to install MATLAB engine. \n: {e}")
        time.sleep(1)
    raise TimeoutError("Installer did not finish in time.")


def install_engine_mac_linux(setup_path: Path):
    subprocess.run(
        ["sudo", sys.executable, "setup.py", "install"],
        cwd=setup_path,
        check=True)


def install_engine():
    try: 
        print("***MATLAB Engine for Python API Package Installer***")
        print("This process will install the matlab.engine package from a MATLAB installation on this machine. \n")
        setup_path = get_matlab_path()
        if not setup_path:
            sys.exit(1)

        print(f"Installing MATLAB engine into current Python environment from: \n {setup_path}")

        time.sleep(2) # Wait for a while so that user sees that they need to grant permission.

        if system == "Windows":
            install_engine_win(setup_path)
        elif system in ["Linux", "Darwin"]:
            install_engine_mac_linux(setup_path)
        else:
            raise OSError(f"Unsupported OS: {system}.")
        
        print(f"Installation completed successfully.")
        sys.exit(0)

    except KeyboardInterrupt:
        print("Aborted by user (Ctrl+C).")
        sys.exit(1)
        
    except Exception as e:
        print(str(e))
        quit = input("Press any key to close.")
        if quit: 
            sys.exit(1)

if __name__ == "__main__":
    install_engine()



                