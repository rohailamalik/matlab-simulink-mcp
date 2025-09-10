import subprocess, sys
from pathlib import Path
import time


def install(engine_dir):
    log_file = Path(__file__).with_name("install.log")
    with open(log_file, "w") as f:
        proc = subprocess.run(
            [sys.executable, "setup.py", "install"],
            cwd=engine_dir,
            stdout=f,
            stderr=subprocess.STDOUT
        )
        f.write(f"\n{proc.returncode}\n")
        time.sleep(2)  

if __name__ == "__main__":
    engine_dir = sys.argv[1]
    install(engine_dir)