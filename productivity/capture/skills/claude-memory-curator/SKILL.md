---
name: "claude-memory-curator"
description: "Maintenance skill for Claude Code's file-based memory system at ~/.claude/projects/*/memory/. Use when you want to: audit memory files for staleness, find outdated entries, check MEMORY.md index integrity (missing pointers, orphaned files), identify memories that should be promoted to CLAUDE.md, or consolidate duplicate memories. Triggers: 'check my memory', 'audit memory', 'memory cleanup', 'stale memory', 'memory index', 'MEMORY.md'. This is a personal skill — not intended for upstream contribution."
license: MIT
metadata:
  version: 1.0.0
  author: Stan Varashilov (Steffonet)
  category: productivity
  personal: true
  updated: 2026-06-03
---

# Claude Memory Curator

You are auditing and maintaining the file-based memory system that Claude Code uses to persist context across conversations.

Memory lives in: `~/.claude/projects/<project-slug>/memory/`

---

## What You're Checking

### 1. MEMORY.md Index Integrity
- Every `.md` file in the memory folder should have an entry in `MEMORY.md`
- Every link in `MEMORY.md` should point to a file that exists
- No line in `MEMORY.md` should exceed ~150 characters
- `MEMORY.md` should not exceed 200 lines (lines past 200 are truncated at load)

### 2. Staleness
Memory files have an implicit TTL depending on type:
| Type | Staleness threshold |
|---|---|
| `project` | > 14 days without update |
| `feedback` | Never stale — rules don't expire unless contradicted |
| `user` | > 90 days |
| `reference` | > 30 days for URLs, > 90 days for paths |

Check the `metadata.updated` date or the last git commit touching the file.

### 3. Duplicate / Overlapping Memories
Two memories covering the same fact. Flag for consolidation.

### 4. Promotion Candidates
A memory qualifies for promotion to `CLAUDE.md` if:
- It's been referenced in 3+ sessions, OR
- It contains a hard rule that should apply globally (not just this project), OR
- It's feedback that contradicts Claude's default behavior

### 5. Orphaned Files
`.md` files in the memory directory not listed in `MEMORY.md`.

---

## Audit Workflow

**Step 1 — Read the index**
Read `MEMORY.md`. Note every linked file.

**Step 2 — Scan the directory**
List all `.md` files. Cross-check against index. Flag orphans and broken links.

**Step 3 — Check each memory file**
For each file:
- Read frontmatter: `name`, `description`, `type`, `updated`
- Assess staleness by type threshold
- Flag if: body contradicts a known current fact, contains relative dates (e.g., "last Thursday"), references a file path or function that no longer exists

**Step 4 — Check for duplicates**
Look for two memories covering the same fact. Suggest which to keep.

**Step 5 — Check MEMORY.md length**
Count lines. Warn if approaching 200.

**Step 6 — Report**

Output a structured report:

```
## Memory Audit Report — [project slug]
Date: [today]

### Summary
- Total memory files: N
- Orphaned (not in index): N
- Broken index links: N
- Stale (by type threshold): N
- Duplicate pairs: N
- Promotion candidates: N

### Issues

#### Stale
- [filename] — type: project, last updated: YYYY-MM-DD, reason: [...]

#### Orphaned
- [filename] — not listed in MEMORY.md

#### Broken Links
- MEMORY.md line N: links to [filename] which does not exist

#### Duplicates
- [file-a] and [file-b] both describe [topic] — suggest merging into [file-a]

#### Promotion Candidates
- [filename] — reason: [applied in 3+ sessions / global rule / contradicts default]

### Recommended Actions
1. [action]
2. [action]
```

---

## Applying Fixes

Only apply fixes if the user confirms. For each fix type:

**Orphan fix:** Ask user — keep (add to index) or delete?

**Stale fix:** Ask user to confirm the updated fact, then rewrite the memory body.

**Duplicate fix:** Show both memories side by side, propose the merged version, wait for approval.

**Promotion fix:** Draft the CLAUDE.md entry, show it to the user, add only on approval.

**Broken link fix:** Offer to remove the dangling MEMORY.md entry.

---

## File Paths

Stan's memory locations:
- Global: `C:\Users\Stant\.claude\projects\C--Users-Stant\memory\`
- system32 project: `C:\Users\Stant\.claude\projects\C--Windows-system32\memory\`
- MEMORY.md index: in each of the above folders

To audit all projects at once, run `memory_auditor.py`.
