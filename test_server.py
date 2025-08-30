# server.py
from __future__ import annotations

import sys, time, json, logging
from dataclasses import dataclass, field
from collections import deque
from typing import Any

from fastmcp import FastMCP, Context  # FastMCP server + MCP context logging

# -------------------------
# Minimal runtime state
# -------------------------
@dataclass
class RuntimeState:
    ready: bool = False
    phase: str = "pre_init"          # pre_init | initializing | ready | shutting_down
    reason: str | None = None        # why not ready (if any)
    config: dict[str, Any] = field(default_factory=dict)
    diagnostics: deque[dict[str, Any]] = field(default_factory=lambda: deque(maxlen=100))

    def log_diag(self, level: str, message: str, **extra: Any) -> None:
        self.diagnostics.append({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": level.lower(),
            "message": message,
            **({"extra": extra} if extra else {}),
        })

# -------------------------
# Configure stderr logging (never stdout)
# -------------------------
logger = logging.getLogger("startup")
handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Toggle for testing startup failure vs success
READY_TOGGLE = True   # set to False to verify handshake-time error surfacing

# -------------------------
# Pre-init self-checks
# -------------------------
def build_state() -> RuntimeState:
    state = RuntimeState()
    state.phase = "pre_init"
    state.config = {"example_flag": "value"}

    # Example fatal check gated by READY_TOGGLE
    if not READY_TOGGLE:
        state.ready = False
        state.reason = "Startup gate failed: READY_TOGGLE is False"
        state.log_diag("error", state.reason)
        logger.error(state.reason)
        return state

    state.ready = True
    state.phase = "initializing"
    state.log_diag("info", "Startup checks passed")
    logger.info("Startup checks passed")
    return state

# -------------------------
# FastMCP server
# -------------------------
mcp = FastMCP("Minimal Health-Gated Server")
mcp.state = build_state()  # attach so tools can access the shared state

# Health tool (visible in any client)
@mcp.tool
async def health(ctx: Context) -> dict:
    """
    Return readiness + latest diagnostics. Also emits a client-visible info log.
    """
    s: RuntimeState = mcp.state
    await ctx.info("Health requested", extra={"ready": s.ready, "phase": s.phase, "reason": s.reason})
    # Snapshot diagnostics to a list
    diags = list(s.diagnostics)
    return {
        "ready": s.ready,
        "phase": s.phase,
        "reason": s.reason,
        "diagnostics": diags,
    }

def main() -> None:
    s: RuntimeState = mcp.state

    # If startup failed, exit before handshake; clients will show stderr.
    if not s.ready:
        # Be explicit and fail-fast so clients don’t just say “can’t connect”.
        logger.error("Exiting with non-zero due to failed startup gate")
        sys.exit(1)

    # Mark ready and run stdio server
    s.phase = "ready"
    # Important: do not print to stdout; FastMCP handles JSON-RPC over stdout.
    mcp.run()  # defaults to stdio transport. :contentReference[oaicite:1]{index=1}

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
            # Catch unexpected init-time exceptions; surface via stderr and diag
            try:
                mcp.state.log_diag("error", "Unhandled exception during startup", error=str(e))
            except Exception:
                pass
            logger.exception("Unhandled exception during startup")
            sys.exit(1)
