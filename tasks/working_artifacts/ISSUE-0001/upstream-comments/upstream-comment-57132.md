<!--
Cross-link comment for: https://github.com/anthropics/claude-code/issues/57132
"[Bug] Allow rules under ~/.claude/ show as loaded per /permissions but don't match at runtime"

Same root cause as #36884 (already commented there with full analysis).
Post this as a short cross-link comment so maintainers can consolidate.
-->

Same root cause as [#36884](https://github.com/anthropics/claude-code/issues/36884#issuecomment-4474702923): the `XIq` rule predicate in claude.exe's permission matcher hard-rejects any rule with `ruleValue.ruleContent !== undefined`, so all path-globbed `Edit(...)` / `Read(...)` / `Write(...)` and (per your May 17 comment) `Skill(...)` and `mcp__...(...)` rules fail to match for tools that don't have their own content matcher.

Full disassembly + reproducer matrix in [that comment](https://github.com/anthropics/claude-code/issues/36884#issuecomment-4474702923). Treating these two as duplicates is probably the right move.
