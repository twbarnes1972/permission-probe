[← Back to claude](claude.md)

# Mental Model

Per Claude, here's the mental model — what's in my context at session start, roughly in the order it arrives:

1. **Base system prompt** (compiled into Claude Code, not visible to me as quotable text but I follow it). Identity, tool descriptions, tone, standing rules.
2. **Auto-memory** — the contents of `~/.claude/projects/<encoded-path>/memory/MEMORY.md` and the individual memory files it references. That's how the Windows DISM gotcha will reach me next session.
3. **Global CLAUDE.md** (`~/.claude/CLAUDE.md`) — your cross-project conventions.
4. **Project CLAUDE.md** (`<repo>/CLAUDE.md`) — repo-specific conventions.
5. **Environment block** — cwd, git status snapshot, branch, model, OS, available skills, MCP server descriptions.
6. **Tool schemas** — JSON definitions of every tool I can call.
7. **Your first message.**

Then mid-conversation, new things keep arriving:

- Your subsequent messages
- Tool results (sometimes with `<system-reminder>` tags appended by the runtime — those nudges about TaskCreate you've been seeing are an example; they're injected by the harness, not by you)
- IDE notifications (the "user selected lines X-Y" or "user opened file Z" reminders)
- Hook output (if you had any configured; you don't currently for the projects we've worked in)
- Compaction summaries when context gets long — older turns get summarized into a single block and earlier raw content drops out

A few things worth flagging because they often surprise people:

- **I can't see other sessions.** Each Claude Code session is a fresh context. Memory is the only continuity channel.
- **`<system-reminder>` tags are not from you.** They're machine-generated and the base prompt explicitly tells me they "bear no direct relation" to the surrounding tool result. So when you see "you selected lines X" appear in my view, that's the IDE telling me, not something you typed.
- **Skills are listed but not loaded until I invoke them.** The descriptions tell me what's available; the actual skill body only enters context if I call `Skill(...)` or you type `/skill-name`.
- **MCP tools follow the same pattern** — schemas for the ones loaded at startup are present from the start; deferred ones (the giant list at session open) need a `ToolSearch` call before I can use them.

So when you give me an instruction in a message, it lands on top of all that — and I'm reconciling it against the standing rules + the two CLAUDE.md files + memory + the conversation so far. Usually they're consistent. When they're not, the most-specific source tends to win in my judgment, but as I said earlier — there's no formal precedence enforced by the runtime.
