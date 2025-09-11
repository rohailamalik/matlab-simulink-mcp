# MATLAB Simulink MCP Server

[![PyPI version](https://img.shields.io/pypi/v/matlab-simulink-mcp.svg)](https://pypi.org/project/matlab-simulink-mcp/)
[![Python versions](https://img.shields.io/pypi/pyversions/matlab-simulink-mcp.svg)](https://pypi.org/project/matlab-simulink-mcp/)

This [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol) server allows MCP clients (such as Claude Desktop or other LLM-based agents) to interact with **MATLAB** and **Simulink** in real time. It runs locally on your machine and is built on top of the [FastMCP](https://github.com/modelcontextprotocol/fastmcp) library.

---

## Features

- Read, write, and run MATLAB code and scripts
- Parse and interact with Simulink files
- Access MATLAB workspace variables and outputs (including visualizations)
- Basic safety layer to prevent execution of unsafe commands (configurable)
- Non-blocking execution (async MATLAB engine calls)
- Automatic installation of MATLAB Engine package if unavailable

---

## Requirements

- **MATLAB** R2022b or later  
- **Python** 3.10–3.12 (check your MATLAB docs for supported versions)

---

## Installation

### Option 1 — Download Binary (MATLAB R2025a only)
If you don’t want to interact with Python at all, you can download a prebuilt **exe/app** from the [Releases](../../releases) page and run it directly. In that case you can skip the steps below.

---

### Option 2 — From Source

1. Clone the repository:

   ```bash
   git clone https://github.com/rohailamalik/matlab-simulink-mcp
   cd matlab-simulink-mcp

2. Create a Python virtual environment (recommended: uv):
   
    ```bash
    uv venv --python 3.12    # match Python to your MATLAB-supported version
    source .venv/Scripts/activate   # on macOS/Linux: source .venv/bin/activate
    uv sync

Without uv:
    ```bash
    python3.12 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    pip install .

3. Alternatively, skip step 1, create virtual environment and install directly via PyPI:
    ```bash
    uv pip install matlab-simulink-mcp
    # or
    pip install matlab-simulink-mcp

4. On first run, if the MATLAB Engine is not installed, the server will open a console window and guide you through installation.
This requires admin permissions.
If you prefer to install manually, see MathWorks docs or install a matching matlabengine version from PyPI.



## Configuration (Claude Desktop)

1. Install Claude Desktop.

2. Open Settings → Developer → Edit Config.

3. In the claude_desktop_config.json, add or update:

{
  "mcpServers": {
    "MatlabMCP": {
      "command": "absolute-path-to/.venv/Scripts/python", 
      "args": ["-m", "matlab_simulink_mcp"]
    }
  }
}

On macOS/Linux, use absolute-path-to/.venv/bin/python.

Note: Only use / or \\ in the paths, not \. 

If using the standalone exe/app, just point command to the binary and omit args.


4. Save and restart Claude Desktop. (Ensure it is fully closed in Task Manager/Activity Monitor.)

5. On first launch, the server may open multiple consoles to install MATLAB Engine. Interact with one, complete installation, then restart Claude if needed.

6. Check running status in Settings → Developer, or click the equalizer button in the chat box.

7. Logs:

Claude MCP logs:

Windows: %APPDATA%\Claude\logs\mcp-server-MatlabMCP.log

macOS: ~/Library/Logs/Claude/mcp-server-MatlabMCP.log

Server logs: written to your user log directory (or configured via .env).


## Debugging

FastMCP 2.0 includes an MCP Inspector for manual testing without an LLM client. 

    ```bash
    cd scripts
    fastmcp dev debugger.py


This launches a UI to send dummy requests directly to the server.

## Repository Structure

matlab-simulink-mcp/
├─ src/matlab_simulink_mcp/
│  ├─ data/               # Data files and resources
│  ├─ installer/          # MATLAB Engine installer
│  │  ├─ installer.py
│  │  ├─ launcher.py
│  │  └─ win_elevate.py
│  ├─ functions.py        # Baseline MCP tool functions
│  ├─ log_utils.py        # Logging utilities
│  ├─ security.py         # Safety layer for code execution
│  ├─ server.py           # Main server script
│  ├─ state.py            # Server lifespan objects (logger, engine)
├─ .env                   # Optional config (e.g. LOG_DIR)
├─ pyproject.toml
├─ requirements.txt
├─ uv.lock
└─ README.md

## FAQ

Q: Which Python version should I install?
A: Match it to the highest Python version supported by your MATLAB release (see MathWorks docs).

Q: The console disappears too quickly!
A: Add --console in your Claude config args to keep the server console open.

Q: Multiple installer consoles opened on first run.
A: This is expected if Claude sends multiple startup requests. Complete one installation, then restart Claude Desktop.