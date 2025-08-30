def test_startup(mcp_server):
    assert mcp_server.proc.poll() is None 

def test_initialize(mcp_server):
    resp = mcp_server.send({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-05-31",
            "clientInfo": {"name": "pytest", "version": "0.1"}
        }
    })
    assert "result" in resp


from tests.conftest import initialize

def test_list_tools_returns_tools(mcp_server):
    initialize(mcp_server)  
    resp = mcp_server.send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    assert "result" in resp
    assert "tools" in resp["result"]
    assert isinstance(resp["result"]["tools"], list)
