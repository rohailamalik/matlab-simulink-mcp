# MATLAB Simulink MCP Server

[![PyPI version](https://img.shields.io/pypi/v/matlab-simulink-mcp.svg)](https://pypi.org/project/matlab-simulink-mcp/)
[![Python versions](https://img.shields.io/pypi/pyversions/matlab-simulink-mcp.svg)](https://pypi.org/project/matlab-simulink-mcp/)

This **Model Context Protocol (MCP)** server lets MCP clients (such as Claude Desktop or other LLM-based agents) to interact with **MATLAB** and **Simulink** in real time. It runs locally, is built on [FastMCP 2.0](https://gofastmcp.com/getting-started/welcome), and communicates with MATLAB and Simulink via the MATLAB Engine for Python API.

## Features

- **Allows an LLM client to**
  - Read, write, and execute MATLAB code and scripts
  - Parse and interact with Simulink models
  - Access workspace and results (inculding visualizations)

- **Execution Safety**
  - Basic safeguards against unsafe commands
  - Restricted to current working directory (only manually changeable)

- **Robust Runtime**
  - Non-blocking execution (asyncronous MATLAB engine calls)
  - Automatic installation of MATLAB Engine library if unavailable

## Requirements

- **MATLAB** R2022b or later  
- **Python** 3.10–3.12 (check [which version](https://www.mathworks.com/support/requirements/python-compatibility.html) is supported by your MATLAB installation)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/rohailamalik/matlab-simulink-mcp
   cd matlab-simulink-mcp
   ```

2. Create and activate a Python virtual environment ([uv](https://pypi.org/project/uv/0.1.32/) is recommended, automatically installs Python version if missing):

    ```bash
    uv venv --python 3.12           # match Python to your MATLAB-supported version
    source .venv/Scripts/activate   # on macOS/Linux: source .venv/bin/activate
    ```

    Without uv, you will first need to download and install the required Python version manually:

    ```bash
    python3.12 -m venv .venv        # match Python to your MATLAB-supported version
    source .venv/Scripts/activate   # on macOS/Linux: source .venv/bin/activate
    ```

3. Install dependencies:

    ```bash
    uv sync
    # or without uv
    pip install -r requirements.txt
    pip install .
    ```

4. Alternatively, create the virtual environment and install directly from [PyPI](https://pypi.org/project/matlab-simulink-mcp/#description):

    ```bash
    uv pip install matlab-simulink-mcp
    # or without uv
    pip install matlab-simulink-mcp
    ```

5. On the first run, if MATLAB Engine is not found, the server will open a console window and guide you through installation.

    - This requires admin permission and the application will request for it.
    - If you prefer to install manually, install a [matching PyPI version](https://pypi.org/project/matlabengine/#history) or from your [MATLAB installation](https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html).

## Configuration (Claude Desktop)

1. Open [Claude Desktop](https://claude.ai/download) Settings → Developer → Edit Config.

2. In the `claude_desktop_config.json`, add or update:

    ```json
    {
    "mcpServers": {
        "MATLAB_Simulink_MCP": {
            "command": "<absolute-path-to>/.venv/Scripts/python.exe", // absolute path to your Python environment executable
            "args": [
                "-m", 
                "matlab_simulink_mcp"
                ],
            "env": {
                "LOG_DIR": "<absolute-path-to>/logs" // Optional: absolute path to a folder for logs
                }
            }
        }
    }
    ```

    On macOS/Linux, use `<absolute-path-to>/.venv/bin/python` in `command`.

    **Note**: Only use `/` or `\\` in the paths, not `\`.

3. Save and restart Claude Desktop. (Ensure it is fully closed in Task Manager/Activity Monitor.)

4. On first launch, the server may open multiple consoles to install MATLAB Engine. Interact with one, complete installation, then restart Claude if needed.

5. Server's status can be checked from Settings → Developer, or the equalizer button in Claude's chat box.

6. Prompt Claude to write, run or read MATLAB code, scripts or Simulink models. Claude (and any client) is restricted to the current MATLAB working directory, which can only be changed manually for safety reasons.

7. The server logs outputs and errors to both Claude's and its own log file. To keep a log file tracking console open, add `"--console"` to Claude config args.

    - Claude logs: `/logs/mcp-server-MatlabMCP.log` in the same folder as `claude_desktop_config.json`.
    - Server logs: In the folder specified via environment variable `LOG_DIR`, user log directory otherwise.

## Debugging

FastMCP 2.0 includes an [MCP Inspector](https://github.com/modelcontextprotocol/inspector) for manual testing and debugging without an LLM client. It launches a web UI to send dummy requests directly to the server. To use it, run the following code and then click on connect in the UI:

```bash
cd scripts
fastmcp dev debugger.py
```

## Project Structure

```txt

matlab-simulink-mcp/
├─ scripts
│  ├─ debugger.py           # Entry point for MCP inspector
├─ src/matlab_simulink_mcp/
│  ├─ data/                 # Data files and resources
│  ├─ installer/            # MATLAB Engine installer
│  │  ├─ installer.py
│  │  ├─ launcher.py
│  │  └─ win_elevate.py
│  ├─ functions.py          # Baseline MCP tool functions
│  ├─ log_utils.py          # Logging utilities
│  ├─ security.py           # Safety layer for code execution
│  ├─ server.py             # Main server script
│  ├─ state.py              # Server lifespan objects (logger, engine)
│  ├─ __main__.py           # Main entry point
├─ .env                     # Optional environment variables (e.g. LOG_DIR)
├─ pyproject.toml           # Project metadata and dependencies
├─ requirements.txt         # Package dependencies for pip
├─ uv.lock                  # Package dependencies for uv
└─ README.md                # This file

```
