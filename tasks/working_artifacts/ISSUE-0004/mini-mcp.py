"""Minimal MCP stdio server for permission-matcher testing. One tool: ping -> pong.

No dependencies, no credentials, newline-delimited JSON-RPC per MCP stdio transport.
"""
import json
import sys


def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = msg.get("method")
        msg_id = msg.get("id")
        if method == "initialize":
            send({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": msg.get("params", {}).get("protocolVersion", "2024-11-05"),
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "mini", "version": "1.0.0"},
                },
            })
        elif method == "tools/list":
            send({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [{
                        "name": "ping",
                        "description": "Returns the string 'pong'. Used for permission-matcher testing.",
                        "inputSchema": {"type": "object", "properties": {}},
                    }]
                },
            })
        elif method == "tools/call":
            send({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": "pong"}]},
            })
        elif method == "ping":
            send({"jsonrpc": "2.0", "id": msg_id, "result": {}})
        elif msg_id is not None:
            send({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            })
        # notifications (no id) are ignored


if __name__ == "__main__":
    main()
