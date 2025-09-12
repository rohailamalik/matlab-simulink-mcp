import subprocess, sys, time, platform
from pathlib import Path


def run() -> int:
    import matlab_simulink_mcp.installer.installer as installer

    # Prevent multiple installation script launches # commented cuz problematic as if file from another session or smth exists the installer wont run at all.
    lockfile = Path.home() / ".matlab_engine_install.lock"
    ''' 
    if lockfile.exists(): 
        time.sleep(5)  
        return -1 # wait command, essentially proceed but wait.
    lockfile.write_text("running")
    '''
    try: 
        time.sleep(2)
        # Launch installation process 
        system = platform.system()
        if system == "Windows": 
            proc = subprocess.Popen(
                [sys.executable, "-m", installer.__name__],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        elif system == "Darwin": 
            proc = subprocess.Popen(["open", "-a", "Terminal", sys.executable, "-m", installer.__name__])
        elif system == "Linux":
            proc = subprocess.Popen(["x-terminal-emulator", "-e", sys.executable, "-m", installer.__name__])

        # Wait for installation to finish
        ret = proc.wait()

        

        # Return installation status (ret returns 1 if error)
        if ret == 1:
            return 0
        if ret == 0:
            time.sleep(2) # ensuring that installed package is now recognized
            return 1
    
    finally:
        if lockfile.exists():
             lockfile.unlink()

if __name__ == "__main__":
    run()

