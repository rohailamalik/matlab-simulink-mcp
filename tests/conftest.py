import pytest, subprocess, sys, json

class MCPServerClient:
    def __init__(self, proc):
        self.proc = proc

    def send(self, msg):
        """Send a JSON-RPC request (expects a response)."""
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        return json.loads(self.proc.stdout.readline())

    def notify(self, msg):
        """Send a JSON-RPC notification (no response expected)."""
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()

    def stop(self):
        self.proc.kill()

@pytest.fixture
def mcp_server():
    proc = subprocess.Popen(
        [sys.executable, "-m", "matlab_simulink_mcp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    client = MCPServerClient(proc)
    yield client
    client.stop()


def initialize(mcp_server: MCPServerClient):
    """Perform MCP initialization handshake with the server."""
    init = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-05-31",
            "clientInfo": {"name": "pytest", "version": "0.1"}
        }
    }
    mcp_server.send(init)

    mcp_server.notify({
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    })