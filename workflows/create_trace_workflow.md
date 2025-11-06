Run `npx @mariozechner/claude-trace` to start up claude with a log that captures raw calls to Anthropic. (Visit https://github.com/badlogic/lemmy/tree/main/apps/claude-trace for more details on using this tool.)

Once the session starts, input these prompts in order.  The content doesn't matter much, but these 3 prompts are increasing levels of complexity and helps capture more of the raw calls.  Extraction of tool definitions is based on the simple prompt, so make sure to input that exactly as written:

1. SIMPLE PROMPT: Hi, what is your name?
2. TOOLUSE PROMPT: Run the following command: `ls -1 | wc -l` and tell me how many files are in the current directory.
3. AGENT PROMPT: Use the Task tool to execute the following steps exactly as written: 
  1. Read fixtures/TEST.md 
  2. Reverse the order of the numbers in the DATA field.

In rare instances, the agent prompt may fail.  If it does, just start over with a new session and input the prompts again.  If it is successful, the subagent should only use 2 tools (Read and Edit).

You also need to make sure to update the version_dates.md file with the publish date for the version of Claude Code you are testing.