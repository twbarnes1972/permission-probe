"""Drive an interactive Claude Code TUI session under ConPTY (Windows) for permission testing.

Why: permission behavior diverges between the `--print`/sdk-cli entrypoint and the
interactive TUI (`cli`) entrypoint — see ISSUE-0004. `--print` can't test the TUI half.
This driver spawns claude.exe under a real pseudo-terminal (pywinpty), so claude sees a
genuine TTY and runs the actual TUI code path (verify via `entrypoint=cli` in the debug
log), types one prompt, and watches the screen for a success marker vs a permission dialog.

It auto-answers ONLY the workspace-trust dialog. It never answers a permission prompt —
the appearance of one is the signal being measured.

Requires: `pip install pywinpty`. Windows only (ConPTY).

Usage:
    set PP_SANDBOX=C:/path/to/sandbox-config-dir   (used as CLAUDE_CONFIG_DIR)
    set PP_CWD=C:/path/to/test-project-cwd
    python tui-driver.py <scenario>                (see SCENARIOS; default "mcp")

The sandbox config dir should contain a crafted settings.json (the rules under test, no
hooks), a .claude.json pre-seeded with onboarding/trust flags, and a copy of
.credentials.json for auth. See ISSUE-0004 § Resolution for the full recipe.
"""
import os
import re
import sys
import time
import threading

import winpty

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SANDBOX = os.environ.get("PP_SANDBOX") or sys.exit("set PP_SANDBOX to the sandbox CLAUDE_CONFIG_DIR")
CWD = os.environ.get("PP_CWD") or sys.exit("set PP_CWD to the test project cwd")
CLAUDE = os.environ.get("CLAUDE_EXE", os.path.expanduser("~/.local/bin/claude.exe"))
LOG_DIR = os.environ.get("PP_LOG_DIR", CWD)
TARGET = os.environ.get("PP_TARGET_FILE", "")  # file to edit, for the editdeny scenario

SCENARIOS = {
    # Does a bare MCP allow rule auto-approve in the TUI? (needs mini-mcp.py registered
    # in the sandbox .claude.json and "mcp__mini__ping" in settings.json allow)
    "mcp": {
        "log": os.path.join(LOG_DIR, "mcp-tui.log"),
        "prompt": "Call the MCP tool mcp__mini__ping with no arguments and report its exact output.",
        "verdict_patterns": [r"pong", r"Do you want", r"don't ask again", r"Always allow", r"permission"],
    },
    # Does a path-globbed Edit(...) deny rule block in the TUI? (needs PP_TARGET_FILE,
    # bare Read/Edit in allow, and an Edit(<glob over target>) deny rule)
    # Marker words are assembled by the model so they never appear verbatim in the
    # echoed prompt — otherwise the watcher would match the echo instantly.
    "editdeny": {
        "log": os.path.join(LOG_DIR, "editdeny-tui.log"),
        "prompt": (
            "Use the Edit tool to edit the file " + TARGET + " "
            "replacing PLACEHOLDER_X with PLACEHOLDER_Y. First Read the file, then Edit it. "
            "If any tool call is blocked or rejected, reply with exactly the two words STATUS DENIED "
            "joined together with no space between them, and stop. "
            "If the edit succeeds, reply with exactly the two words STATUS WORKED joined together "
            "with no space between them. "
            "Do not use Bash, PowerShell, or any tool other than Read and Edit."
        ),
        "verdict_patterns": [r"STATUSDENIED", r"STATUSWORKED", r"Do you want", r"don't ask again"],
    },
}

SCENARIO = SCENARIOS[sys.argv[1] if len(sys.argv) > 1 else "mcp"]
LOG = SCENARIO["log"]
PROMPT = SCENARIO["prompt"]

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[a-zA-Z]|\x1b\][^\x07]*\x07|\x1b[=>]|\x1b\([B0]")


def strip_ansi(s):
    return ANSI_RE.sub("", s)


def main():
    env = dict(os.environ)
    env["CLAUDE_CONFIG_DIR"] = SANDBOX
    env.pop("CLAUDECODE", None)
    env.pop("CLAUDE_CODE_ENTRYPOINT", None)

    proc = winpty.PtyProcess.spawn(
        [CLAUDE, "--debug", "permission,tool", "--debug-file", LOG],
        cwd=CWD, env=env, dimensions=(45, 160),
    )

    chunks = []
    lock = threading.Lock()

    def reader():
        while True:
            try:
                data = proc.read(4096)
            except (EOFError, ConnectionAbortedError, OSError):
                return
            if data:
                with lock:
                    chunks.append(data)

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    def screen():
        with lock:
            return strip_ansi("".join(chunks))

    def wait_for(patterns, timeout, label):
        """Wait until any pattern appears (returns match) or timeout (returns None)."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            text = screen()
            for p in patterns:
                if re.search(p, text, re.IGNORECASE):
                    return p
            if not proc.isalive():
                print(f"[driver] process died while waiting for {label}")
                return None
            time.sleep(0.5)
        return None

    print("[driver] waiting for TUI to be ready...")
    hit = wait_for([r"trust the files", r"\? for shortcuts", r"Try \"", r"pasted", r">\s"], 60, "startup")
    if hit is None:
        print("[driver] STARTUP TIMEOUT")
    elif "trust" in hit:
        print("[driver] trust dialog detected -> accepting (Enter)")
        proc.write("\r")
        wait_for([r"\? for shortcuts", r"Try \""], 30, "post-trust startup")

    time.sleep(2.0)
    print("[driver] sending prompt")
    proc.write(PROMPT)
    time.sleep(1.0)
    proc.write("\r")

    verdict_hit = wait_for(SCENARIO["verdict_patterns"], 120, "verdict")
    time.sleep(3.0)  # let the screen settle / capture full response
    final = screen()

    print("[driver] verdict pattern hit:", verdict_hit)
    print("=" * 70)
    print(final[-3500:])
    print("=" * 70)

    # exit cleanly: Escape (dismiss any dialog w/o choosing), then /exit
    try:
        proc.write("\x1b")
        time.sleep(0.5)
        proc.write("/exit")
        time.sleep(0.5)
        proc.write("\r")
        time.sleep(3.0)
        if proc.isalive():
            proc.write("\x03")
            time.sleep(1.0)
            proc.write("\x03")
            time.sleep(2.0)
    except Exception as e:
        print("[driver] exit cleanup:", e)

    print("[driver] alive after exit attempts:", proc.isalive())


if __name__ == "__main__":
    main()
