# System Prompt Changelog Update Workflow

This document provides step-by-step instructions for updating `system_prompt_changelog_full.md` with new Claude Code versions.

## Prerequisites

Before starting, ensure you have:
- New system prompt files in `system_prompts/` directory (format: `system_prompt_X.X.X.txt`)
- Access to `version_dates.md` for publication dates
- The existing `system_prompt_changelog_full.md` file

## Workflow Steps

### Step 1: Identify Versions to Add

The user will specify which version(s) need to be added to the changelog. Common scenarios:
- Single version: "Add v2.0.35"
- Multiple versions: "Add v2.0.35, v2.0.36, and v2.0.37"
- Range: "Add versions from v2.0.35 to v2.0.38"

### Step 2: Verify System Prompt Files Exist

Check that the necessary system prompt files exist:

```bash
ls system_prompts/system_prompt_X.X.X.txt
```

If any files are missing, inform the user which versions cannot be processed.

### Step 3: Get Publication Dates

Look up the publication dates in `version_dates.md`:

```bash
grep "^| X.X.X " version_dates.md
```

Note the dates for each version you're adding.

### Step 4: Run Diffs Sequentially

For each version pair, run a diff to see what changed:

```bash
diff -u system_prompts/system_prompt_[OLD_VERSION].txt system_prompts/system_prompt_[NEW_VERSION].txt
```

**Important:** Always diff against the immediate predecessor:
- If adding v2.0.35, diff v2.0.34 → v2.0.35
- If adding v2.0.36, diff v2.0.35 → v2.0.36
- And so on...

**Note:** If a predecessor version is missing (e.g., no v2.0.31), diff against the latest available version before it.

### Step 5: Analyze Each Diff

For each diff output, determine:

1. **What changed?** (Added lines, removed lines, modified lines)
2. **Which block?** (Block 1 or Block 2 - almost always Block 2)
3. **What are the line numbers?** (From the actual system prompt file)
4. **How similar are they?** (Estimate percentage based on change size)
5. **What type of change?**
   - Substantive (new features, policy changes, guidance additions)
   - Formatting only (whitespace, blank lines)
   - Modification (extending existing text)

### Step 6: Identify Patterns

Check if the change is part of a recurring pattern:

**Known Toggle Patterns:**
- **Parallel tool calls toggle** (v2.0.2 ↔ v2.0.5 ↔ v2.0.8)
- **Auto-approved tools toggle** (v2.0.25 onwards - repeatedly added/removed/modified)

If the change continues or starts a toggle pattern, add the appropriate pattern warning.

### Step 7: Write Changelog Entries

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

### Step 8: Prepend Entries to Changelog

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

### Step 9: Verify and Confirm

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

1. Check: `ls system_prompts/system_prompt_2.0.35.txt` ✓
2. Get date: `grep "^| 2.0.35 " version_dates.md` → "2025-11-06"
3. Run diff: `diff -u system_prompts/system_prompt_2.0.34.txt system_prompts/system_prompt_2.0.35.txt`
4. Analyze the diff output
5. Identify: Block 2 modified, 98.5% similar, added 3 lines
6. Check for patterns (none in this case)
7. Write entry following the format above
8. Prepend to changelog using Edit tool
9. Confirm: "Added v2.0.35 (2025-11-06) to the changelog. Change: [brief description]"

## Tips for Success

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
