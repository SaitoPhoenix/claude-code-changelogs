# Request Flow Changelog Entry Template

## Entry Format

**IMPORTANT:** Each changelog entry must follow this EXACT structure. Do NOT add additional sections. Do NOT provide exhaustive detail. Focus on WHAT changed, not extensive analysis.

---

### Template Structure

```markdown
## vX.X.X • YYYY-MM-DD

**Summary:** [Single sentence: what changed in this version]
**Analysis:** [1-3 sentences: describe the details of the changes and infer impact]
**Request Count:** XX → XX ([+/-]X requests)

### Changes

#### ➕ Added
[Only if requests were added - list new request types and their purpose, one line each]
- [Index] REQUEST_TYPE: Brief purpose
- [Index] REQUEST_TYPE: Brief purpose

#### ➖ Removed
[Only if requests were removed - list removed request types, one line each]
- [Previous Index] REQUEST_TYPE: What it did

#### 🔄 Modified
[Only if existing requests changed behavior - one line each]
- [Index] REQUEST_TYPE: What changed (e.g., "Model upgraded: haiku-3.5 → haiku-4.5")

#### ↕️ Reordered
[Only if request sequence changed - describe the reordering concisely]
- Brief description of what moved where

```

