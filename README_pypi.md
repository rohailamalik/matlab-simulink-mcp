# MATLAB Simulink MCP Server

This Model Context Protocol (MCP) server allows MCP clients (such as Claude Desktop or other LLM-based agents) to interact with **MATLAB** and **Simulink** in real time. It runs locally, is built on top of the [FastMCP 2.0](https://gofastmcp.com/getting-started/welcome) library, and uses MATLAB Engine for Python API to communicate with MATLAB and Simulink.

## Features

- Read, write, and run MATLAB code and scripts
- Parse and interact with Simulink files
- Access MATLAB workspace variables and outputs (including visualizations)
- Basic safety layer to prevent execution of unsafe commands (configurable)
- Non-blocking execution (async MATLAB engine calls)
- Automatic installation of MATLAB Engine package if unavailable

## Requirements

- **MATLAB** R2022b or later  
- **Python** 3.10–3.12 (check MATLAB's [supported versions](https://www.mathworks.com/support/requirements/python-compatibility.html))

## Installation

1. Install using:

    ```bash
    uv pip install matlab-simulink-mcp
    # or
    pip install matlab-simulink-mcp
    ```

2. On the first run, if the MATLAB Engine is not installed, the server will open a console window and guide you through installation.

    - This requires admin permission and the server will request for it.
    - If you prefer to install manually, install a [matching PyPi version](https://pypi.org/project/matlabengine/#history) or from your [MATLAB installation](https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html).

## Configuration (Claude Desktop)

1. Install [Claude Desktop](https://claude.ai/download).

2. Open Settings → Developer → Edit Config.

3. In the `claude_desktop_config.json`, add or update:

    ```json
    {
    "mcpServers": {
        "MATLAB_Simulink_MCP": {
            "command": "absolute-path-to/.venv/Scripts/python.exe", // absolute path to your venv/global environment executable
            "args": ["-m", "matlab_simulink_mcp"]
            }
        }
    }
    ```

    On macOS/Linux, use `absolute-path-to/.venv/bin/python` in `command`.

    **Note**: Only use `/` or `\\` in the paths, not `\`.

4. Save and restart Claude Desktop. (Ensure it is fully closed in Task Manager/Activity Monitor.)

5. On first launch, the server may open multiple consoles to install MATLAB Engine. Interact with one, complete installation, then restart Claude if needed.

6. Check running status in Settings → Developer, or click the equalizer button in Claude's chat box.

7. The server logs outputs and errors to both Claude's and its own log file. To keep a log file tracking console open, add `--console` in Claude config args.

    - Claude MCP logs (Windows): `%APPDATA%\Claude\logs\mcp-server-MatlabMCP.log`
    - Claude MCP logs (macOS): `~/Library/Logs/Claude/mcp-server-MatlabMCP.log`
    - Server logs: written to your user log directory (or configured via `.env`).

## Debugging

FastMCP 2.0 includes an MCP Inspector for manual testing without an LLM client. It launches a UI to send dummy requests directly to the server.

To use it, import `mcp` from `matlab_simulink_mcp.server` into a script and run the script using `fastmcp dev script_name.py`
