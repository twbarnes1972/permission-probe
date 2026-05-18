#!/usr/bin/env node
// Probe Claude Code's permission matcher behavior without triggering prompts.
//
// What this does:
//   1. Loads the user's ~/.claude/settings.json
//   2. Parses every Edit(...)/Read(...)/Write(...) allow rule
//   3. Compiles each pattern with picomatch (same lib Claude Code uses) under
//      multiple option variants (default, windows:true, posix-form input, etc.)
//   4. Tests each rule against a list of paths we ACTUALLY want to access
//   5. Prints a matrix: which rule+path+option combo matches vs. doesn't.
//
// This tells us, without ever invoking Claude's Edit tool, which rule form
// would auto-allow which file path. Compare the printed "expected match" to
// real-world prompt/no-prompt behavior to narrow down what the matcher is
// actually doing.

const fs = require('fs');
const path = require('path');
const pm = require('picomatch');

const SETTINGS = path.join(process.env.USERPROFILE || process.env.HOME, '.claude', 'settings.json');

// Paths to probe against the rules in your settings.json. Replace with the
// real paths that prompt for you — the variety below exercises different
// separator / drive-letter forms so you can see which (if any) ever match.
const TEST_PATHS = [
  'C:\\Data\\projects\\current-repo\\README.md',                           // inside CWD
  'C:\\Data\\projects\\sibling-repo\\NOTES.md',                            // sibling repo (typical prompt case)
  'C:\\Data\\projects\\other-repo\\file.md',
  'C:/Data/projects/sibling-repo/NOTES.md',                                // forward-slash form
  '/c/Data/projects/sibling-repo/NOTES.md',                                // POSIX-Windows form
];

// Pattern variants we'll synthesize for each rule, to compare effects.
function variants(pattern) {
  return {
    'as-written':       pattern,
    'forward-slash':    pattern.replace(/\\/g, '/'),
    'backslash':        pattern.replace(/\//g, '\\'),
    'posix-drive':      pattern.replace(/^([A-Za-z]):/, (_, d) => `//${d.toLowerCase()}`),
    'no-anchor':        '**/' + pattern.replace(/^[A-Za-z]:[\\/]/, ''),
  };
}

// picomatch options we'll try for each pattern variant.
function optionsMatrix() {
  return {
    'no-opts':              undefined,
    'empty-obj':            {},
    'windows:true':         { windows: true },
    'windows:false':        { windows: false },
    'posix:true':           { posix: true },
    'nocase:true':          { nocase: true },
    'win+nocase':           { windows: true, nocase: true },
    'dot:true,win':         { windows: true, dot: true },
  };
}

function tryMatch(pattern, opts, file) {
  try {
    const isMatch = pm(pattern, opts);
    return isMatch(file);
  } catch (e) {
    return `ERR:${e.message.slice(0, 40)}`;
  }
}

function loadSettings() {
  const raw = fs.readFileSync(SETTINGS, 'utf8');
  return JSON.parse(raw);
}

// Parse "Edit(C:/Data/**)" into { tool: 'Edit', pattern: 'C:/Data/**' }
function parseRule(rule) {
  const m = rule.match(/^([A-Za-z_]+)\(([^)]*)\)$/);
  if (!m) return { tool: rule, pattern: null };
  return { tool: m[1], pattern: m[2] };
}

function main() {
  console.log('=== Claude Code Permission Matcher Probe ===');
  console.log(`Settings file: ${SETTINGS}`);
  console.log(`Node platform: ${process.platform}, version: ${process.version}`);
  console.log(`picomatch version: ${require('picomatch/package.json').version}`);
  console.log('');

  const settings = loadSettings();
  const allow = settings.permissions?.allow ?? [];
  const addlDirs = settings.permissions?.additionalDirectories ?? [];

  console.log(`additionalDirectories: ${JSON.stringify(addlDirs)}`);
  console.log(`Sample of allow rules (path-glob only):`);
  const pathRules = allow.filter(r => /^(Edit|Read|Write)\(/.test(r));
  pathRules.forEach(r => console.log('  ' + r));
  console.log('');

  // For each test path, try every (pattern variant, options) combination across
  // every rule. Print rows where ANY combo matches.
  const optMatrix = optionsMatrix();

  for (const filePath of TEST_PATHS) {
    console.log(`\n### File: ${filePath}`);
    console.log(`    path.resolve = ${path.resolve(filePath)}`);
    for (const rule of pathRules) {
      const { tool, pattern } = parseRule(rule);
      const vars = variants(pattern);
      const anyMatch = [];
      const noMatch = [];
      for (const [varName, varPat] of Object.entries(vars)) {
        for (const [optName, opts] of Object.entries(optMatrix)) {
          const result = tryMatch(varPat, opts, filePath);
          const label = `${varName} / ${optName}`;
          if (result === true) anyMatch.push(`${label}  pattern="${varPat}"`);
          else if (typeof result === 'string') noMatch.push(`${label}  ${result}`);
        }
      }
      if (anyMatch.length) {
        console.log(`  RULE: ${rule}`);
        anyMatch.slice(0, 6).forEach(m => console.log(`    MATCH via  ${m}`));
        if (anyMatch.length > 6) console.log(`    ...and ${anyMatch.length - 6} more`);
      }
    }
  }

  // additionalDirectories prefix check (the way it's likely implemented):
  // path.resolve(dirEntry) is the canonical key; file is "in" the dir if its
  // resolved path starts with key + sep.
  console.log('\n=== additionalDirectories prefix check ===');
  for (const dir of addlDirs) {
    const resolved = path.resolve(dir);
    console.log(`\n  entry: ${dir}`);
    console.log(`  resolved: ${resolved}`);
    for (const filePath of TEST_PATHS) {
      const resolvedFile = path.resolve(filePath);
      const isInside = resolvedFile.startsWith(resolved + path.sep) || resolvedFile === resolved;
      console.log(`    ${isInside ? 'INSIDE ' : 'outside'}: ${filePath}  (resolved=${resolvedFile})`);
    }
  }
}

main();
