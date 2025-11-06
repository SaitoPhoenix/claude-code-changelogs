# Claude Code LLM Instructions Changelogs

A project that captures and analyzes Claude Code's evolution by examining raw API traces to Anthropic. We extract system prompts, tool definitions, and data flows to create comprehensive changelogs of the changes to the core LLM instructions and orchestration logic across versions.

## What This Project Does

This project evaluates a trace of raw API calls made when using Claude Code, then extracts and analyzes:

- **System prompts** - The core instructions that define Claude Code's behavior
- **Tool definitions** - The tools available to Claude Code and their specifications
- **Data flows** - Detailed analysis of how raw API calls are structured and sequenced

Trace's are captured using the claude-trace tool by badlogic.  You can find the tool [here](https://github.com/badlogic/lemmy/tree/main/apps/claude-trace).

## Changelogs

The primary outputs of this project are the changelogs documenting Claude Code's evolution:

### 📋 [Tool Definitions Changelog](tool_definitions_changelog.md)

View changes to Claude Code's available tools across versions - additions, removals, and modifications to tool schemas and descriptions.

### 📋 [System Prompt Changelog](system_prompt_changelog.md)

View changes to Claude Code's core system prompt - the instructions that define its behavior, capabilities, and operational guidelines.

### 📅 [Version Dates](version_dates.md)

Reference for Claude Code version publication dates.

## Detailed Flows

For in-depth analysis of specific version behaviors, detailed API flow analyses are available in `output/detailed_flows/`.

### Flow Structure

Each detailed flow file (`detailed_flow_*.txt`) contains:

- **Request Sequence** - Chronological order of API requests with types and purposes
- **User Messages** - The actual prompts and interactions from the user
- **Model Responses** - Claude's responses and reasoning
- **Tool Calls** - Which tools were invoked and when
- **Phase Boundaries** - Natural breakpoints in the interaction flow (marked by health checks)
- **Summary** - Overview with any detected unknown patterns or endpoints

These flows help understand how Claude Code orchestrates API calls to accomplish tasks, revealing the request patterns and decision-making process.

## Contributing

Want to help track these undocumented Claude Code changes or improve the analysis tools? Here's how the project works.

### 1. `extract_system_prompts.py`

Extracts system prompts from Claude Code trace files.

**What it does:**
- Finds all `.jsonl` trace files in `.claude-trace/` directory
- Extracts the system prompt from the first real user interaction (Sonnet model)
- Saves each version's system prompt to `output/system_prompts/` directory
- Generates metadata about block structure and extraction details

**Usage:**
```bash
python src/extract_system_prompts.py --all
```

**Output:**
- `output/system_prompts/system_prompt_{version}.txt` - Individual system prompt files
- `output/system_prompts/metadata.json` - Metadata about all extracted versions

**Requirements:**
- `.claude-trace/` directory containing `.jsonl` trace files

---

### 2. `extract_tools.py`

Extracts tool definitions from Claude Code trace files.

**What it does:**
- Accepts specific trace file(s) as arguments OR uses `--extract-all` flag
- Extracts tool definitions from the first real user interaction (Sonnet model)
- Saves each version's tools to `output/tool_definitions/` directory in both text and JSON formats
- Generates metadata about tool counts, names, and extraction details

**Usage:**
```bash
# Extract from specific file(s)
python src/extract_tools.py <trace_file> [<trace_file> ...]

# Extract from all files in .claude-trace/
python src/extract_tools.py --extract-all
```

**Examples:**
```bash
# Single file
python src/extract_tools.py .claude-trace/log-2025-10-31-21-48-26_2.0.5.jsonl

# Multiple files
python src/extract_tools.py .claude-trace/log-*_2.0.30.jsonl .claude-trace/log-*_2.0.31.jsonl

# All files
python src/extract_tools.py --extract-all
```

**Output:**
- `output/tool_definitions/tools_{version}.txt` - Human-readable tool definitions with descriptions and schemas (all tools)
- `output/tool_definitions/tools_{version}.json` - Machine-readable JSON format (all tools)
- `output/tool_definitions/tools_no_mcp_{version}.txt` - Human-readable format excluding MCP tools (core tools only)
- `output/tool_definitions/tools_no_mcp_{version}.json` - JSON format excluding MCP tools (core tools only)
- `output/tool_definitions/metadata.json` - Metadata about all extracted versions including core vs MCP tool counts

**Requirements:**
- Valid `.jsonl` trace file paths

---

### 3. `detailed_flow.py`

Analyzes Claude Code API traces and shows detailed request flows.

**What it does:**
- Loads and parses `.jsonl` trace files
- Shows all API requests in chronological order with context
- Identifies request types, purposes, and patterns
- Extracts user messages, tool calls, and responses
- Detects unknown/new request types and patterns
- Uses health checks (GET `/api/hello`) as phase delimiters

**Usage:**
```bash
python src/detailed_flow.py <trace.jsonl>
```

**Example:**
```bash
python src/detailed_flow.py .claude-trace/api-trace_2.0.30.jsonl
```

**Output:**
Detailed analysis report showing:
- Request sequence with types and purposes
- User messages and model responses
- Tool calls made during execution
- Phase boundaries
- Summary with detected unknowns

---

## Workflow

Typical workflow for analyzing Claude Code versions:

1. **Collect traces**: Run Claude Code with trace logging enabled to generate `.jsonl` files in `.claude-trace/`

2. **Extract prompts**:
   ```bash
   python src/extract_system_prompts.py --all
   ```

3. **Extract tools** (from specific files or all):
   ```bash
   python src/extract_tools.py .claude-trace/log-*_2.0.30.jsonl
   # OR
   python src/extract_tools.py --extract-all
   ```

4. **Analyze flow** (optional):
   ```bash
   python src/detailed_flow.py .claude-trace/api-trace_2.0.30.jsonl > output/detailed_flows/detailed_flow_2.0.30.txt
   ```

5. **Update changelogs** (manual workflow):
   - For system prompts: See `workflows/changelog_workflow.md`
   - For tool definitions: Follow the same workflow pattern
   - Run diffs between versions and write changelog entries

## Directory Structure

```
.
├── README.md                          # Main documentation
├── system_prompt_changelog.md         # System prompt changelog
├── tool_definitions_changelog.md      # Tool definitions changelog
├── version_dates.md                   # Version publication dates
│
├── workflows/                         # Process workflows
│   ├── changelog_workflow.md          # How to update changelogs
│   └── create_trace_workflow.md       # How to create traces
│
├── fixtures/                          # Test fixtures
│   └── TEST.md                        # Sample file for trace creation
│
├── src/                               # Python scripts
│   ├── extract_system_prompts.py      # Extract system prompts
│   ├── extract_tools.py               # Extract tool definitions
│   └── detailed_flow.py               # Analyze API flows
│
├── output/                            # Generated outputs
│   ├── system_prompts/                # Extracted system prompts
│   │   ├── system_prompt_*.txt
│   │   └── metadata.json
│   ├── tool_definitions/              # Extracted tool definitions
│   │   ├── tools_*.txt                # All tools (text)
│   │   ├── tools_*.json               # All tools (JSON)
│   │   ├── tools_no_mcp_*.txt         # Core tools only (text)
│   │   ├── tools_no_mcp_*.json        # Core tools only (JSON)
│   │   └── metadata.json
│   └── detailed_flows/                # API flow analyses
│       └── detailed_flow_*.txt
│
└── .claude-trace/                     # Input trace files
    └── log-*.jsonl
```

## Features

### Detailed Flow Analysis
- Automatic request type detection
- Graceful handling of unknown endpoints and patterns
- Tool call tracking
- Context-aware message classification
- Multi-model support (Haiku, Sonnet)
- Phase-based organization

### System Prompt Extraction
- Multi-block system prompt support
- Version metadata tracking
- Duplicate detection and skipping
- Structured output format

### Tool Definition Extraction
- Extracts all tool definitions (name, description, input schema)
- Quadruple output format per version:
  - Full text (all tools)
  - Full JSON (all tools)
  - Core-only text (MCP excluded)
  - Core-only JSON (MCP excluded)
- Separates core Claude Code tools from environment-specific MCP tools
- Tool count tracking per version (total, core, and MCP separately)
- Version metadata with detailed tool inventories
- Identifies tool additions/removals across versions
- MCP tool filtering for cleaner cross-version comparisons

### Manual Changelog Workflows
- Documented workflow in `CHANGELOG_WORKFLOW.md`
- Sequential version comparison using `diff` command
- Block-level change tracking (added, removed, modified)
- Similarity estimation for modified blocks
- Human/LLM analysis for summaries and pattern recognition
- Markdown format for readability
- Separate changelogs for system prompts and tool definitions

## Requirements

- Python 3.7+
- Standard library only (no external dependencies)

## Notes

- Trace files must be in `.jsonl` format (one JSON object per line)
- System prompts are extracted from Sonnet model requests (warmup requests are skipped)
- Tool definitions are extracted from the first real user interaction
- Changelog updates follow manual workflow documented in `CHANGELOG_WORKFLOW.md`
- All scripts use UTF-8 encoding for file operations
