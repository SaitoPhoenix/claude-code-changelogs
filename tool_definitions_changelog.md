# Claude Code Tool Definitions Changelog (No MCP)

**Format:** Reverse chronological (newest first) • Each version shows changes from previous version

**Scope:** Core Claude Code tools only (MCP tools excluded)

---

## v2.0.34 • 2025-11-05

**Summary:** Enhanced Task tool with agent context awareness

**Analysis:** Added documentation explaining that agents with "access to current context" can see the full conversation history, allowing for more concise prompts that reference earlier context instead of repeating information.

**Changes:** 1 tool modified • 99.9% similar

### Tool: Task

#### ➕ Added
- Line 55: Added guidance about agents with access to current context
  > Agents with "access to current context" can see the full conversation history before the tool call. When using these agents, you can write concise prompts that reference earlier context (e.g., "investigate the error discussed above") instead of repeating information. The agent will receive all prior messages and understand the context.

---

## v2.0.33 • 2025-11-04

**Summary:** No changes from v2.0.32

---

## v2.0.32 • 2025-11-03

**Summary:** Enhanced Grep tool with pagination controls

**Analysis:** Added offset parameter and clarified default behavior for head_limit. The offset parameter enables pagination through search results, and head_limit now defaults based on experiment configuration rather than showing unlimited results.

**Changes:** 1 tool modified • 99.7% similar

### Tool: Grep

#### 🔄 Modified
- Line 403: Clarified line numbers default behavior

  **Changed from:**
  > Show line numbers in output (rg -n). Requires output_mode: "content", ignored otherwise.

  **Changed to:**
  > Show line numbers in output (rg -n). Requires output_mode: "content", ignored otherwise. Defaults to true.

#### 🔄 Modified
- Line 415: Updated head_limit default behavior

  **Changed from:**
  > Limit output to first N lines/entries, equivalent to "| head -N". Works across all output modes: content (limits output lines), files_with_matches (limits file paths), count (limits count entries). When unspecified, shows all results from ripgrep.

  **Changed to:**
  > Limit output to first N lines/entries, equivalent to "| head -N". Works across all output modes: content (limits output lines), files_with_matches (limits file paths), count (limits count entries). Defaults based on "cap" experiment value: 0 (unlimited), 20, or 100.

#### ➕ Added
- Lines 418-421: Added offset parameter for pagination
  > "offset": {
  >   "type": "number",
  >   "description": "Skip first N lines/entries before applying head_limit, equivalent to \"| tail -n +N | head -N\". Works across all output modes. Defaults to 0."
  > }

---

## v2.0.31 • 2025-10-31

**Summary:** No changes from v2.0.30

---

## v2.0.30 • 2025-10-30

**Summary:** Refined Task tool documentation and expanded agent capabilities

**Analysis:** Comprehensive cleanup of Task tool documentation including expanded tool access for Explore and Plan agents (changed from specific tools to "All tools"), added introductory context about agent specialization, fixed typos in examples, and removed redundant blank lines.

**Changes:** 1 tool modified • 99.5% similar

### Tool: Task

#### ➕ Added
- Lines 33-34: Added introductory context about Task tool
  > The Task tool launches specialized agents (subprocesses) that autonomously handle complex tasks. Each agent type has specific capabilities and tools available to it.

#### 🔄 Modified
- Lines 39-40: Expanded tool access for Explore and Plan agents

  **Changed from:**
  > - Explore: Fast agent specialized for exploring codebases... (Tools: Glob, Grep, Read, Bash)
  > - Plan: Fast agent specialized for exploring codebases... (Tools: Glob, Grep, Read, Bash)

  **Changed to:**
  > - Explore: Fast agent specialized for exploring codebases... (Tools: All tools)
  > - Plan: Fast agent specialized for exploring codebases... (Tools: All tools)

#### 🔄 Modified
- Line 44: Renamed section header for consistency

  **Changed from:**
  > When NOT to use the Agent tool:

  **Changed to:**
  > When NOT to use the Task tool:

#### 🔄 Modified
- Lines 45-47: Updated tool name references in guidance

  **Changed from:**
  > - If you want to read a specific file path, use the Read or Glob tool instead of the Agent tool
  > - If you are searching for code within a specific file or set of 2-3 files, use the Read tool instead of the Agent tool

  **Changed to:**
  > - If you want to read a specific file path, use the Read or Glob tool instead of the Task tool
  > - If you are searching for code within a specific file or set of 2-3 files, use the Read tool instead of the Task tool

#### ➖ Removed
- Line 53: Removed line about background agents (AgentOutputTool functionality)
  > For agents that run in the background, you will need to use AgentOutputTool to retrieve their results once they are done. You can continue to work while async agents run in the background - when you need their results to continue you can use AgentOutputTool in blocking mode to pause and wait for their results.

#### 🔄 Modified
- Lines 85, 93: Fixed typos in example usage

  **Changed from:**
  > assistant: Uses the Task tool to launch the with the code-reviewer agent
  > assistant: "I'm going to use the Task tool to launch the with the greeting-responder agent"

  **Changed to:**
  > assistant: Uses the Task tool to launch the code-reviewer agent
  > assistant: "I'm going to use the Task tool to launch the greeting-responder agent"

#### ➖ Removed
- Line 445: Removed extra blank line in ExitPlanMode documentation

---

## v2.0.29 • 2025-10-29

**Summary:** Re-added background agent documentation

**Analysis:** Restored documentation about background agents and AgentOutputTool that was removed in v2.0.28. This suggests the functionality was temporarily removed but is now available again.

**Changes:** 1 tool modified • 99.9% similar

### Tool: Task

#### ➕ Added
- Line 53: Restored background agent documentation
  > For agents that run in the background, you will need to use AgentOutputTool to retrieve their results once they are done. You can continue to work while async agents run in the background - when you need their results to continue you can use AgentOutputTool in blocking mode to pause and wait for their results.

---

## v2.0.28 • 2025-10-27

**Summary:** Added Plan agent and model selection to Task tool

**Analysis:** Introduced a new "Plan" agent type for codebase exploration and added optional parameters for model selection (sonnet/opus/haiku) and agent resumption. Removed documentation about background agents, suggesting simplified synchronous execution model.

**Changes:** 1 tool modified • 99.3% similar

### Tool: Task

#### ➕ Added
- Line 39: Added new Plan agent type
  > - Plan: Fast agent specialized for exploring codebases. Use this when you need to quickly find files by patterns (eg. "src/components/**/*.tsx"), search code for keywords (eg. "API endpoints"), or answer questions about the codebase (eg. "how do API endpoints work?"). When calling this agent, specify the desired thoroughness level: "quick" for basic searches, "medium" for moderate exploration, or "very thorough" for comprehensive analysis across multiple locations and naming conventions. (Tools: Glob, Grep, Read, Bash)

#### ➖ Removed
- Line 52: Removed background agent documentation
  > For agents that run in the background, you will need to use AgentOutputTool to retrieve their results once they are done. You can continue to work while async agents run in the background - when you need their results to continue you can use AgentOutputTool in blocking mode to pause and wait for their results.

#### ➕ Added
- Lines 112-125: Added model selection and resume parameters
  > "model": {
  >   "type": "string",
  >   "enum": [
  >     "sonnet",
  >     "opus",
  >     "haiku"
  >   ],
  >   "description": "Optional model to use for this agent. If not specified, inherits from parent. Prefer haiku for quick, straightforward tasks to minimize cost and latency."
  > },
  > "resume": {
  >   "type": "string",
  >   "description": "Optional agent ID to resume from. If provided, the agent will continue from the previous execution transcript."
  > }

---

## v2.0.27 • 2025-10-24

**Summary:** No changes from v2.0.26

---

## v2.0.26 • 2025-10-23

**Summary:** Renamed sandbox override parameter

**Analysis:** Renamed the dangerouslyOverrideSandbox parameter to dangerouslyDisableSandbox for improved clarity about the parameter's purpose.

**Changes:** 1 tool modified • 99.9% similar

### Tool: Bash

#### 🔄 Modified
- Line 285: Renamed sandbox override parameter

  **Changed from:**
  > "dangerouslyOverrideSandbox": {

  **Changed to:**
  > "dangerouslyDisableSandbox": {

---

## v2.0.25 • 2025-10-21

**Summary:** Removed sleep background execution note

**Analysis:** Removed a specific warning about not using run_in_background with 'sleep' command, simplifying the usage documentation.

**Changes:** 1 tool modified • 99.9% similar

### Tool: Bash

#### 🔄 Modified
- Line 154: Simplified background execution note

  **Changed from:**
  > You can use the `run_in_background` parameter to run the command in the background, which allows you to continue working while the command runs. You can monitor the output using the Bash tool as it becomes available. Never use `run_in_background` to run 'sleep' as it will return immediately. You do not need to use '&' at the end of the command when using this parameter.

  **Changed to:**
  > You can use the `run_in_background` parameter to run the command in the background, which allows you to continue working while the command runs. You can monitor the output using the Bash tool as it becomes available. You do not need to use '&' at the end of the command when using this parameter.

---

## v2.0.24 • 2025-10-20

**Summary:** Added sandbox override parameter to Bash tool

**Analysis:** Introduced a new dangerouslyOverrideSandbox parameter to allow running commands outside the sandbox when needed. This is a significant capability expansion that should be used with caution.

**Changes:** 1 tool modified • 99.6% similar

### Tool: Bash

#### ➕ Added
- Lines 284-287: Added dangerouslyOverrideSandbox parameter
  > "dangerouslyOverrideSandbox": {
  >   "type": "boolean",
  >   "description": "Set this to true to dangerously override sandbox mode and run commands without sandboxing."
  > }

---

## v2.0.23 • 2025-10-20

**Summary:** No changes from v2.0.22

---

## v2.0.22 • 2025-10-17

**Summary:** No changes from v2.0.21

---

## v2.0.21 • 2025-10-16

**Summary:** Added AskUserQuestion tool and enhanced ExitPlanMode (17 tools)

**Analysis:** Introduced the new AskUserQuestion tool to enable interactive clarification during execution. Enhanced ExitPlanMode with guidance on handling ambiguity in plans, recommending use of AskUserQuestion before finalizing plans. This represents a shift toward more interactive and clarifying workflows.

**Changes:** 2 tools modified, 1 tool added • Tool count increased from 16 to 17

### Tool: ExitPlanMode

#### ➕ Added
- Lines 420-425: Added section on handling ambiguity in plans
  > ## Handling Ambiguity in Plans
  > Before using this tool, ensure your plan is clear and unambiguous. If there are multiple valid approaches or unclear requirements:
  > 1. Use the AskUserQuestion tool to clarify with the user
  > 2. Ask about specific implementation choices (e.g., architectural patterns, which library to use)
  > 3. Clarify any assumptions that could affect the implementation
  > 4. Only proceed with ExitPlanMode after resolving ambiguities

#### ➕ Added
- Line 431: Added example demonstrating AskUserQuestion usage
  > 3. Initial task: "Add a new feature to handle user authentication" - If unsure about auth method (OAuth, JWT, etc.), use AskUserQuestion first, then use exit plan mode tool after clarifying the approach.

### Tool: AskUserQuestion (NEW)

#### ➕ Added
- New tool at position 15 for asking user questions during execution
  > Use this tool when you need to ask the user questions during execution. This allows you to:
  > 1. Gather user preferences or requirements
  > 2. Clarify ambiguous instructions
  > 3. Get decisions on implementation choices as you work
  > 4. Offer choices to the user about what direction to take.
  >
  > Usage notes:
  > - Users will always be able to select "Other" to provide custom text input
  > - Use multiSelect: true to allow multiple answers to be selected for a question

---

## v2.0.20 • 2025-10-16

**Summary:** Added Skill tool (16 tools)

**Analysis:** Introduced the new Skill tool to enable execution of specialized skills within the conversation. Skills provide domain-specific capabilities that can be invoked by name. This is a major expansion enabling extensible functionality through a skill system.

**Changes:** 1 tool added • Tool count increased from 15 to 16

### Tool: Skill (NEW)

#### ➕ Added
- New tool at position 15 for executing skills within the conversation
  > Execute a skill within the main conversation
  >
  > <skills_instructions>
  > When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively. Skills provide specialized capabilities and domain knowledge.
  >
  > How to use skills:
  > - Invoke skills using this tool with the skill name only (no arguments)
  > - When you invoke a skill, you will see <command-message>The "{name}" skill is loading</command-message>
  > - The skill's prompt will expand and provide detailed instructions on how to complete the task
  > - Examples:
  >   - `command: "pdf"` - invoke the pdf skill
  >   - `command: "xlsx"` - invoke the xlsx skill
  >   - `command: "ms-office-suite:pdf"` - invoke using fully qualified name
  >
  > Important:
  > - Only use skills listed in <available_skills> below
  > - Do not invoke a skill that is already running
  > - Do not use this tool for built-in CLI commands (like /help, /clear, etc.)
  > </skills_instructions>

---

## v2.0.19 • 2025-10-15

**Summary:** No changes from v2.0.18

---

## v2.0.18 • 2025-10-15

**Summary:** Enhanced Explore agent with thoroughness level guidance

**Analysis:** Added explicit guidance to specify thoroughness levels ("quick", "medium", or "very thorough") when calling the Explore agent, enabling better control over exploration depth and resource usage.

**Changes:** 1 tool modified • 99.8% similar

### Tool: Task

#### 🔄 Modified
- Line 36: Enhanced Explore agent description with thoroughness levels

  **Changed from:**
  > - Explore: Fast agent specialized for exploring codebases. Use this when you need to quickly find files by patterns (eg. "src/components/**/*.tsx"), search code for keywords (eg. "API endpoints"), or answer questions about the codebase (eg. "how do API endpoints work?") (Tools: Glob, Grep, Read, Bash)

  **Changed to:**
  > - Explore: Fast agent specialized for exploring codebases. Use this when you need to quickly find files by patterns (eg. "src/components/**/*.tsx"), search code for keywords (eg. "API endpoints"), or answer questions about the codebase (eg. "how do API endpoints work?"). When calling this agent, specify the desired thoroughness level: "quick" for basic searches, "medium" for moderate exploration, or "very thorough" for comprehensive analysis across multiple locations and naming conventions. (Tools: Glob, Grep, Read, Bash)

---

## v2.0.17 • 2025-10-15

**Summary:** Added Explore agent to Task tool

**Analysis:** Introduced a new "Explore" agent type specialized for fast codebase exploration tasks like finding files by patterns, searching for keywords, and answering questions about the codebase.

**Changes:** 1 tool modified • 99.7% similar

### Tool: Task

#### ➕ Added
- Line 36: Added new Explore agent type
  > - Explore: Fast agent specialized for exploring codebases. Use this when you need to quickly find files by patterns (eg. "src/components/**/*.tsx"), search code for keywords (eg. "API endpoints"), or answer questions about the codebase (eg. "how do API endpoints work?") (Tools: Glob, Grep, Read, Bash)

---

## v2.0.15 • 2025-10-14

**Summary:** Improved ExitPlanMode examples formatting

**Analysis:** Minor formatting improvement to better organize the examples section of the ExitPlanMode tool documentation.

**Changes:** 1 tool modified • 99.9% similar

### Tool: ExitPlanMode

#### 🔄 Modified
- Line 417: Improved examples section formatting

  **Changed from:**
  > Eg.

  **Changed to:**
  > ## Examples

---

## v2.0.14 • 2025-10-10

**Summary:** No changes from v2.0.13

---

## v2.0.13 • 2025-10-09

**Summary:** No changes from v2.0.12

---

## v2.0.12 • 2025-10-09

**Summary:** Enhanced SlashCommand with intent matching and reorganized documentation

**Analysis:** Added prominent "Intent Matching" section to encourage checking if user requests match slash commands before starting tasks. Removed "Available Commands:" section placeholder that appeared before usage notes, improving document flow.

**Changes:** 1 tool modified • 99.6% similar

### Tool: SlashCommand

#### ➕ Added
- Lines 1032-1034: Added intent matching reminder
  > **IMPORTANT - Intent Matching:**
  > Before starting any task, CHECK if the user's request matches one of the slash commands listed below. This tool exists to route user intentions to specialized workflows.

#### ➖ Removed
- Lines 1044-1046: Removed premature "Available Commands" section
  > Available Commands:
  >
  >

---

## v2.0.11 • 2025-10-08

**Summary:** No changes from v2.0.10

---

## v2.0.10 • 2025-10-07

**Summary:** Minor formatting cleanup in ExitPlanMode tool

**Analysis:** Removed trailing whitespace from ExitPlanMode tool description, improving code cleanliness.

**Changes:** 1 tool modified • 99.9% similar

### Tool: ExitPlanMode

#### 🔄 Modified
- Line 414: Cleaned up trailing whitespace

  **Changed from:**
  > Use this tool when you are in plan mode and have finished presenting your plan and are ready to code. This will prompt the user to exit plan mode.

  **Changed to:**
  > Use this tool when you are in plan mode and have finished presenting your plan and are ready to code. This will prompt the user to exit plan mode.

---

## v2.0.9 • 2025-10-06

**Summary:** No changes from v2.0.8

---

## v2.0.8 • 2025-10-04

**Summary:** Restored v2.0.2 changes and added Task agent background execution

**Analysis:** This version restored all the changes from v2.0.2 that were reverted in v2.0.5, including the refined parallel execution guidance across Bash, Glob, Read, and SlashCommand tools. Additionally, added documentation for background agent execution using AgentOutputTool in the Task tool.

**Changes:** 6 tools modified • 98.5% similar

### Tool: Task

#### ➕ Added
- Line 49: Added documentation for background agent execution
  > For agents that run in the background, you will need to use AgentOutputTool to retrieve their results once they are done. You can continue to work while async agents run in the background - when you need their results to continue you can use AgentOutputTool in blocking mode to pause and wait for their results.

#### 🔄 Modified
- Line 46: Changed usage notes from numbered list to bullet points

  **Changed from:**
  > 1. Launch multiple agents concurrently

  **Changed to:**
  > - Launch multiple agents concurrently

### Tool: Bash

#### 🔄 Modified
- Lines 160-161: Enhanced parallel/sequential execution guidance (same as v2.0.2)

#### 🔄 Modified
- Lines 185, 194, 230: Changed wording for consistency (same as v2.0.2)

#### ➕ Added
- Lines 200-201: Added explicit sequential execution note for git status (same as v2.0.2)

### Tool: Glob

#### 🔄 Modified
- Line 300: Changed batching language to parallel execution (same as v2.0.2)

### Tool: Read

#### 🔄 Modified
- Lines 457-458: Clarified parallel reading and screenshot handling (same as v2.0.2)

### Tool: SlashCommand

#### ➕ Added
- Lines 1031-1033: Added explanation of how slash commands work (same as v2.0.2)

#### 🔄 Modified
- Lines 1039-1049: Reorganized and clarified usage restrictions (same as v2.0.2)

#### ➕ Added
- Lines 1046-1049: Added notes about sequential execution and command invocation (same as v2.0.2)

---

## v2.0.5 • 2025-10-02

**Summary:** Reverted v2.0.2 changes to pre-v2.0.2 wording

**Analysis:** This version rolled back all the parallel execution refinements introduced in v2.0.2, reverting to the earlier "batch your tool calls" language and removing the detailed examples and notes about sequential execution. This appears to be a temporary rollback that was later restored in v2.0.8.

**Changes:** 5 tools modified • 98.2% similar

### Tool: Bash

#### 🔄 Modified
- Lines 160-161: Reverted to simpler execution guidance

  **Changed from (v2.0.2):**
  > If the commands are independent and can run in parallel, make multiple Bash tool calls in a single message. For example, if you need to run "git status" and "git diff", send a single message with two Bash tool calls in parallel.
  > If the commands depend on each other and must run sequentially, use a single Bash call with '&&' to chain them together (e.g., `git add . && git commit -m "message" && git push`). For instance, if one operation must complete before another starts (like mkdir before cp, Write before Bash for git operations, or git add before git commit), run these operations sequentially instead.

  **Changed to:**
  > If the commands are independent and can run in parallel, make multiple Bash tool calls in a single message
  > If the commands depend on each other and must run sequentially, use a single Bash call with '&&' to chain them together (e.g., `git add . && git commit -m "message" && git push`)

#### 🔄 Modified
- Lines 185, 194, 230: Reverted to "batch" wording

  **Changed from (v2.0.2):**
  > You can call multiple tools in a single response. When multiple independent pieces of information are requested and all commands are likely to succeed, run multiple tool calls in parallel for optimal performance.

  **Changed to:**
  > You have the capability to call multiple tools in a single response. When multiple independent pieces of information are requested and all commands are likely to succeed, batch your tool calls together for optimal performance.

#### 🔄 Modified
- Line 199: Reverted git status execution note

  **Changed from (v2.0.2):**
  > - Run git status after the commit completes to verify success.
  > Note: git status depends on the commit completing, so run it sequentially after the commit.

  **Changed to:**
  > - Run git status to make sure the commit succeeded.

#### 🔄 Modified
- Line 194: Removed "in parallel" specification

  **Changed from (v2.0.2):**
  > run the following commands:

  **Changed to:**
  > run the following commands in parallel:

### Tool: Glob

#### 🔄 Modified
- Line 300: Reverted to batch terminology

  **Changed from (v2.0.2):**
  > You can call multiple tools in a single response. It is always better to speculatively perform multiple searches in parallel if they are potentially useful.

  **Changed to:**
  > You have the capability to call multiple tools in a single response. It is always better to speculatively perform multiple searches as a batch that are potentially useful.

### Tool: Read

#### 🔄 Modified
- Lines 456-457: Reverted to batch terminology and restored full screenshot path example

  **Changed from (v2.0.2):**
  > You can call multiple tools in a single response. It is always better to speculatively read multiple potentially useful files in parallel.
  > You will regularly be asked to read screenshots. If the user provides a path to a screenshot, ALWAYS use this tool to view the file at the path. This tool will work with all temporary file paths.

  **Changed to:**
  > You have the capability to call multiple tools in a single response. It is always better to speculatively read multiple files as a batch that are potentially useful.
  > You will regularly be asked to read screenshots. If the user provides a path to a screenshot ALWAYS use this tool to view the file at the path. This tool will work with all temporary file paths like /var/folders/123/abc/T/TemporaryItems/NSIRD_screencaptureui_ZfB1tD/Screenshot.png

### Tool: SlashCommand

#### ➖ Removed
- Lines 1031-1033: Removed explanation of how slash commands work

#### 🔄 Modified
- Lines 1036-1044: Reverted to simpler usage restrictions format

  **Changed from (v2.0.2):**
  > IMPORTANT: Only use this tool for custom slash commands that appear in the Available Commands list below. Do NOT use for:
  > - Built-in CLI commands (like /help, /clear, etc.)
  > - Commands not shown in the list
  > - Commands you think might exist but aren't listed
  >
  > Notes:
  > - When a user requests multiple slash commands, execute each one sequentially
  > - Do not invoke a command that is already running

  **Changed to:**
  > Important Notes:
  > - Only available slash commands can be executed.
  > - Some commands may require arguments as shown in the command list above
  > - If command validation fails, list up to 5 available commands, not all of them.
  > - Do not use this tool if you are already processing a slash command with the same name as indicated by <command-message>{name_of_command} is running…</command-message>

---

## v2.0.3 • 2025-10-02

**Summary:** No changes from v2.0.2

---

## v2.0.2 • 2025-09-30

**Summary:** Refined parallel execution guidance across multiple tools

**Analysis:** Comprehensive update to clarify when to use parallel vs sequential tool calls. Changes wording from "batch your tool calls" to more explicit "run multiple tool calls in parallel" throughout Bash, Glob, Read, and SlashCommand tools. Adds clarification about dependencies and sequential execution.

**Changes:** 5 tools modified • 98.2% similar

### Tool: Bash

#### 🔄 Modified
- Lines 160-161: Enhanced parallel/sequential execution guidance

  **Changed from:**
  > If the commands are independent and can run in parallel, make multiple Bash tool calls in a single message
  > If the commands depend on each other and must run sequentially, use a single Bash call with '&&' to chain them together

  **Changed to:**
  > If the commands are independent and can run in parallel, make multiple Bash tool calls in a single message. For example, if you need to run "git status" and "git diff", send a single message with two Bash tool calls in parallel.
  > If the commands depend on each other and must run sequentially, use a single Bash call with '&&' to chain them together (e.g., `git add . && git commit -m "message" && git push`). For instance, if one operation must complete before another starts (like mkdir before cp, Write before Bash for git operations, or git add before git commit), run these operations sequentially instead.

#### 🔄 Modified
- Lines 185, 194, 230: Changed wording for consistency

  **Changed from:**
  > You have the capability to call multiple tools in a single response. When multiple independent pieces of information are requested and all commands are likely to succeed, batch your tool calls together for optimal performance.

  **Changed to:**
  > You can call multiple tools in a single response. When multiple independent pieces of information are requested and all commands are likely to succeed, run multiple tool calls in parallel for optimal performance.

#### ➕ Added
- Lines 200-201: Added explicit sequential execution note for git status
  > Note: git status depends on the commit completing, so run it sequentially after the commit.

### Tool: Glob

#### 🔄 Modified
- Line 300: Changed batching language to parallel execution

  **Changed from:**
  > You have the capability to call multiple tools in a single response. It is always better to speculatively perform multiple searches as a batch that are potentially useful.

  **Changed to:**
  > You can call multiple tools in a single response. It is always better to speculatively perform multiple searches in parallel if they are potentially useful.

### Tool: Read

#### 🔄 Modified
- Lines 457-458: Clarified parallel reading and screenshot handling

  **Changed from:**
  > You have the capability to call multiple tools in a single response. It is always better to speculatively read multiple files as a batch that are potentially useful.
  > You will regularly be asked to read screenshots. If the user provides a path to a screenshot ALWAYS use this tool to view the file at the path. This tool will work with all temporary file paths like /var/folders/123/abc/T/TemporaryItems/NSIRD_screencaptureui_ZfB1tD/Screenshot.png

  **Changed to:**
  > You can call multiple tools in a single response. It is always better to speculatively read multiple potentially useful files in parallel.
  > You will regularly be asked to read screenshots. If the user provides a path to a screenshot, ALWAYS use this tool to view the file at the path. This tool will work with all temporary file paths.

### Tool: SlashCommand

#### ➕ Added
- Lines 1031-1033: Added explanation of how slash commands work
  > How slash commands work:
  > When you use this tool or when a user types a slash command, you will see <command-message>{name} is running…</command-message> followed by the expanded prompt. For example, if .claude/commands/foo.md contains "Print today's date", then /foo expands to that prompt in the next message.

#### 🔄 Modified
- Lines 1039-1049: Reorganized and clarified usage restrictions

  **Changed from:**
  > Important Notes:
  > - Only available slash commands can be executed.
  > - Some commands may require arguments as shown in the command list above
  > - If command validation fails, list up to 5 available commands, not all of them.
  > - Do not use this tool if you are already processing a slash command

  **Changed to:**
  > IMPORTANT: Only use this tool for custom slash commands that appear in the Available Commands list below. Do NOT use for:
  > - Built-in CLI commands (like /help, /clear, etc.)
  > - Commands not shown in the list
  > - Commands you think might exist but aren't listed

#### ➕ Added
- Lines 1046-1049: Added notes about sequential execution and command invocation
  > Notes:
  > - When a user requests multiple slash commands, execute each one sequentially and check for <command-message>
  > - Do not invoke a command that is already running
  > - Only custom slash commands with descriptions are listed in Available Commands

---

## v2.0.1 • 2025-09-30

**Summary:** No changes from v2.0.0

---

## v2.0.0 • 2025-09-29

**Summary:** Baseline version - 15 core tools

---
