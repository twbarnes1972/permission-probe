[← Back to conventions](conventions.md)

# Markdown Documentation Conventions

How documentation is organized in this repo. The reference implementations are [`documentation/documentation.md`](../documentation.md) and the section indexes under it — when in doubt, mirror what they do.

## Directory layout

Documentation lives under `documentation/`. Each topical area gets its own subdirectory containing an index file named after the directory, plus one file per sub-topic:

```
documentation/
├── documentation.md                  # Top-level index
├── conventions/
│   ├── conventions.md                # Section index
│   ├── powershell.md                 # One topic per file
│   └── markdown-documentation.md     # (this file)
└── device/
    ├── device.md                     # Section index
    └── ...
```

The section directory and its index file share a name (`conventions/conventions.md`, `device/device.md`). This makes the index path predictable from the directory name alone.

## File rules

Every markdown file follows three rules:

1. **First line is a back-link** to the parent index, in the form `[← Back to <parent>](<relative-path>)`. The chain is unambiguous: a topic file links to its section index, a section index links to `documentation.md`, and `documentation.md` links to `README.md`. No file links to itself or skips levels.

2. **Second line blank, third line is `# Title`** — a single H1 matching the file's role. Section index files are titled with the section name (`# Conventions`, `# Device`); topic files are titled with the topic (`# PowerShell Script Conventions`).

3. **Index files only index** — they list their children with one-line descriptions and don't carry standalone content. Real content lives in topic files. If an index starts growing prose, that prose should become its own topic file and the index should link to it.

## Index format

Section indexes use a simple bulleted list under a `## Sections` (top level) or `## Index` (section level) heading. Each entry is one line: `- [Title](path.md) — one-line hook`.

```markdown
## Index

- [PowerShell scripts](powershell.md) — location, error handling, console + log output
- [Markdown documentation](markdown-documentation.md) — how docs are organized in this repo
```

Keep the hooks short and concrete — they should answer "what's in here?" not "why does this matter?". Save the longer framing for the topic file itself.

## Linking up from the repo root

`README.md` is the entry point and links to `documentation/documentation.md` from its **Documentation** section. New top-level sections (peers of `conventions/` and `device/`) get linked from `documentation.md`, not from `README.md` directly — the README only knows about the index.

## When to add a new section vs. a new topic file

- **New topic in an existing section** (e.g. a second conventions doc): add the file under the existing directory, link from the section index.
- **New section** (a topic area that doesn't fit any existing index): create a new subdirectory under `documentation/`, add `<name>/<name>.md` as the index with the standard back-link to `documentation.md`, and link the new section from `documentation.md`.

Don't nest sections more than one level deep. If a section grows enough that it wants subsections, that's a sign to flatten it into multiple peer sections instead.
