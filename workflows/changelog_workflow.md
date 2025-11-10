# System Prompt Changelog Update Workflow

This document provides step-by-step instructions for updating `system_prompt_changelog_full.md` with new Claude Code versions.

## Prerequisites

Before starting, ensure you have:
- Trace files (`.jsonl`) in `.claude-trace/` directory for versions to process
- Access to `version_dates.md` for publication dates
- The existing `system_prompt_changelog_full.md` file
- The `src/extract_system_prompts.py` script for extracting system prompts

## Workflow Steps

### Step 1: Identify Versions to Add

The user will specify which version(s) need to be added to the changelog. Common scenarios:
- Single version: "Add v2.0.35"
- Multiple versions: "Add v2.0.35, v2.0.36, and v2.0.37"
- Range: "Add versions from v2.0.35 to v2.0.38"

### Step 2: Extract System Prompts (If Needed)

Check if system prompt files exist for the requested versions:

```bash
ls output/system_prompts/system_prompt_X.X.X.txt 2>/dev/null
```

If any files are missing, **automatically extract them** from trace files:

```bash
python src/extract_system_prompts.py log-*_X.X.X.jsonl
```

The extraction script:
- Looks for trace files in `.claude-trace/` directory
- Extracts the system prompt from the first real user interaction
- Saves to `output/system_prompts/system_prompt_X.X.X.txt`
- Updates metadata in `output/system_prompts/metadata.json`

**Note:** Only inform the user if both the system prompt file AND the trace file are missing.

### Step 3: Standardize Environment-Specific Sections

After extraction, **manually standardize environment-specific content** to ensure diffs show actual version changes, not environment differences.

#### Auto-Approved Tools Line

**Location:** After the closing `</example>` tag for the Task tool with subagent_type=Explore examples, before the "Here is useful information about the environment" section.

**Required format:**
```


You can use the following tools without requiring user approval: [Approved tools from Claude Code settings]


Here is useful information about the environment you are running in:
```

**Whitespace requirements:**
- Exactly **2 blank lines BEFORE** the auto-approved tools line
- Exactly **2 blank lines AFTER** the auto-approved tools line

**What to replace:**
- If the line exists with specific tools listed → Replace with placeholder
- If the line is missing entirely → Add it with the placeholder
- This section is injected from user configuration (`.claude/settings.json`), not Claude Code version

**Example:**
```bash
# Before (with tools):
You can use the following tools without requiring user approval: Bash(chmod:*), Bash(python3:*), Bash(awk:*), Bash(tail:*)

# Before (missing):
[line doesn't exist]

# After (standardized):
You can use the following tools without requiring user approval: [Approved tools from Claude Code settings]
```

#### Git Status Section

**Location:** After the "Code References" example section, before the `END OF SYSTEM PROMPT` delimiter.

**Required format:**
```
</example>

[Dynamic git repository status injected when in a git repository]

========================================================================================================================
END OF SYSTEM PROMPT
```

**Whitespace requirements:**
- Exactly **1 blank line BEFORE** the placeholder line
- Exactly **1 blank line AFTER** the placeholder line

**What to replace:**
- If a multi-line `gitStatus:` section exists → Replace entire block with single placeholder line
- If the section is missing → Add the placeholder line
- This section is dynamically generated based on actual repository state when in a git repository

**Example:**
```bash
# Before (with git status - may be 15-20 lines):
gitStatus: This is the git status at the start of the conversation...
Current branch: main
Status: M file.txt
Recent commits: ...

# Before (missing):
[line doesn't exist]

# After (standardized):
[Dynamic git repository status injected when in a git repository]
```

**Why standardize?**
- These sections vary based on user configuration, repository state, and working directory
- They are NOT version-specific changes to Claude Code
- Standardizing eliminates false positives in version diffs
- Enables accurate tracking of actual system prompt evolution across versions

### Step 4: Get Publication Dates

Look up the publication dates in `version_dates.md`:

```bash
grep "^| X.X.X " version_dates.md
```

Note the dates for each version you're adding.

### Step 5: Run Diffs Sequentially

For each version pair, run a diff to see what changed:

```bash
diff -u output/system_prompts/system_prompt_[OLD_VERSION].txt output/system_prompts/system_prompt_[NEW_VERSION].txt
```

**Important:** Always diff against the immediate predecessor:
- If adding v2.0.35, diff v2.0.34 → v2.0.35
- If adding v2.0.36, diff v2.0.35 → v2.0.36
- And so on...

**Note:** If a predecessor version is missing (e.g., no v2.0.31), diff against the latest available version before it.

### Step 6: Analyze Each Diff

For each diff output, determine:

1. **What changed?** (Added lines, removed lines, modified lines)
2. **Which block?** (Block 1 or Block 2 - almost always Block 2)
3. **What are the line numbers?** (From the actual system prompt file)
4. **How similar are they?** (Estimate percentage based on change size)
5. **What type of change?**
   - Substantive (new features, policy changes, guidance additions)
   - Formatting only (whitespace, blank lines)
   - Modification (extending existing text)

### Step 7: Identify Patterns

Check if the change is part of a recurring pattern:

**Known Toggle Patterns:**
- **Parallel tool calls toggle** (v2.0.2 ↔ v2.0.5 ↔ v2.0.8)
- **Auto-approved tools toggle** (v2.0.25 onwards - repeatedly added/removed/modified)

If the change continues or starts a toggle pattern, add the appropriate pattern warning.

### Step 8: Write Changelog Entries

For each new version, create a changelog entry following this **exact format**:

```markdown
## vX.X.X • YYYY-MM-DD

**Summary:** [One concise line describing what changed]

**Analysis:** [1-2 sentences explaining why this change matters or what it accomplishes]

**Changes:** [N] block(s) modified • [XX.X]% similar [• ⚠️ **Pattern:** [pattern description] (if applicable)]

### Block 2 (TEXT)

#### ➕ Added
- Line [XXX]:
  > [Verbatim quoted text from the file]

- Lines [XXX-YYY]:
  > [Verbatim quoted multi-line text]

#### ➖ Removed
- Line [XXX]:
  > [Verbatim quoted text from the file]

#### 🔄 Modified
- Line [XXX]: [Brief description of what was modified]

  **Added:**
  > [Only the added portion, verbatim]
```

**Format Rules:**

1. **Version header:** `## vX.X.X • YYYY-MM-DD` (use date from version_dates.md)

2. **Summary:** Single concise line, active voice, describes the change clearly

3. **Analysis:** Your interpretation of why this matters (1-2 sentences)

4. **Changes line:**
   - Block count: "1 block modified" or "2 blocks modified"
   - Similarity: Percentage (e.g., "97.2% similar")
   - Pattern warning (if applicable): `⚠️ **Pattern:** [description]`

5. **Block section:** Almost always "Block 2 (TEXT)"

6. **Change sections:**
   - Use `➕ Added` for new content
   - Use `➖ Removed` for deleted content
   - Use `🔄 Modified` for extended/changed lines (not wholesale replacements)
   - Quote text **verbatim** from the system prompt files
   - Include line numbers from the files

**Special Cases:**

**Formatting-only changes:**
```markdown
## vX.X.X • YYYY-MM-DD

**Summary:** Formatting cleanup [brief description]

**Analysis:** No substantial changes - [describe what formatting changed].

**Changes:** 1 block modified • 99.X% similar • ⚠️ **Trivial** (formatting only)

### Block 2 (TEXT)

_Changes are whitespace-only formatting adjustments - no content modifications_
```

**No changes:**
```markdown
## vX.X.X • YYYY-MM-DD

**Summary:** No changes from vX.X.X
```

### Step 9: Prepend Entries to Changelog

**Critical:** The changelog is **reverse chronological** (newest first, oldest last).

Always add new entries at the **top** of the file, immediately after the format description and before the previous newest version.

**Location to insert:**
```markdown
# Claude Code System Prompt Changelog

**Format:** Reverse chronological (newest first) • Each version shows changes from previous version

---

[INSERT NEW ENTRIES HERE]

## v[PREVIOUS_NEWEST] • YYYY-MM-DD
[existing entry]
```

Use the Edit tool to prepend the new entries.

### Step 10: Verify and Confirm

After updating:

1. Confirm the number of entries added
2. Verify dates are correct
3. Check that entries are in reverse chronological order (newest at top)
4. Ensure all pattern warnings are applied consistently

Report back to the user with:
- How many versions were added
- Any notable changes (major features, pattern shifts, etc.)
- Any versions that couldn't be processed (missing files)

## Common Patterns Reference

### Toggle Patterns

**Parallel Tool Calls Toggle:**
- v2.0.2: Detailed dependency handling
- v2.0.5: Reverted to simpler approach → `⚠️ **Pattern:** Reverts v2.0.2 change (toggle begins)`
- v2.0.8: Restored detailed version → `⚠️ **Pattern:** Restores v2.0.2 change (toggle complete)`

**Auto-Approved Tools Toggle:**
- v2.0.25: Removed → `⚠️ **Pattern:** Auto-approved tools toggle begins`
- v2.0.26: Added back → `⚠️ **Pattern:** Auto-approved tools restored (toggle)`
- v2.0.28: Removed again → `⚠️ **Pattern:** Auto-approved tools removed again (toggle)`
- v2.0.29: Added back again → `⚠️ **Pattern:** Auto-approved tools restored again (toggle)`
- v2.0.30: Removed → `⚠️ **Pattern:** Auto-approved tools removed (toggle continues)`
- v2.0.32: Added back with expansions → `⚠️ **Pattern:** Auto-approved tools expanded (toggle + additions)`

When you encounter these sections being modified, check the pattern history and apply the appropriate warning.

## Example Session

**User:** "Add v2.0.35 to the changelog"

**Your workflow:**

1. Check: `ls output/system_prompts/system_prompt_2.0.35.txt 2>/dev/null`
   - If missing: `python src/extract_system_prompts.py log-*_2.0.35.jsonl`
2. Standardize environment sections (auto-approved tools, gitStatus)
3. Get date: `grep "^| 2.0.35 " version_dates.md` → "2025-11-06"
4. Run diff: `diff -u output/system_prompts/system_prompt_2.0.34.txt output/system_prompts/system_prompt_2.0.35.txt`
5. Analyze the diff output
6. Identify: Block 2 modified, 98.5% similar, added 3 lines
7. Check for patterns (none in this case)
8. Write entry following the format above
9. Prepend to changelog using Edit tool
10. Confirm: "Added v2.0.35 (2025-11-06) to the changelog. Change: [brief description]"

## Tips for Success

- **Always standardize first** - Replace environment-specific sections before running diffs
- **Read the existing changelog** to understand the established tone and style
- **Be precise** with line numbers - verify them in the actual system prompt files
- **Quote verbatim** - copy text exactly as it appears, don't paraphrase
- **Stay concise** - summaries should be one line, analysis should be 1-2 sentences
- **Watch for patterns** - toggle behaviors are important to flag
- **Use formatting markers** - Trivial changes get special treatment
- **Double-check ordering** - newest must be at the top

## Troubleshooting

**Missing predecessor version:**
- Diff against the last available version before the one you're adding
- Note the gap in your summary if relevant

**Very large changes (>50 lines):**
- Still include the full verbatim text in Removed sections
- User prefers verbose documentation of what was removed

**Multiple blocks changed:**
- Document each block separately
- Update the "Changes" line to reflect total block count

**Uncertain about similarity percentage:**
- Estimate conservatively based on lines changed vs. total lines
- Small changes (1-3 lines): 99%+
- Medium changes (5-15 lines): 95-99%
- Large changes (50+ lines): 80-95%
- Massive changes (100+ lines): <80%
