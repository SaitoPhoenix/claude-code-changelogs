#!/usr/bin/env python3
"""
Detailed flow analysis showing exact mapping of user prompts to API requests.

Shows:
- What requests happen for each phase
- Request purpose and content
- Response content (tool calls, text, etc.)
- Handles unknown request types gracefully
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def load_jsonl(file_path: Path) -> List[Dict[str, Any]]:
    """Load JSONL file into list of parsed entries."""
    entries = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries


def extract_user_message(body: Dict[str, Any]) -> str:
    """Extract the actual user message (not system reminders)."""
    messages = body.get('messages', [])

    for msg in messages:
        if msg.get('role') == 'user':
            content = msg.get('content', '')
            if isinstance(content, str):
                # Skip system reminders
                if not content.strip().startswith('<system-reminder>'):
                    return content
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        text = block.get('text', '')
                        if not text.strip().startswith('<system-reminder>'):
                            return text

    return ""


def extract_all_user_messages(body: Dict[str, Any]) -> List[str]:
    """Extract all user messages in the conversation chain (not system reminders)."""
    messages = body.get('messages', [])
    user_messages = []

    for msg in messages:
        if msg.get('role') == 'user':
            content = msg.get('content', '')
            if isinstance(content, str):
                # Skip system reminders
                if not content.strip().startswith('<system-reminder>'):
                    user_messages.append(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        text = block.get('text', '')
                        if not text.strip().startswith('<system-reminder>'):
                            user_messages.append(text)
                            break  # Only take first text block per message

    return user_messages


def format_message_with_indent(msg: str, prefix: str, max_length: int = 150) -> str:
    """Format a message with proper indentation for multi-line content.

    Args:
        msg: The message text
        prefix: The prefix (e.g., "       [1] User: ")
        max_length: Maximum length before truncating

    Returns:
        Formatted message with proper indentation
    """
    indent = " " * len(prefix)

    if len(msg) >= max_length:
        # Truncate but still apply indentation to newlines within the truncated portion
        truncated = msg[:100]
        lines_in_truncated = truncated.split('\n')
        formatted_truncated = lines_in_truncated[0]
        for line in lines_in_truncated[1:]:
            formatted_truncated += '\n' + indent + line
        return f"{prefix}{formatted_truncated}... [{len(msg)} chars]"

    # Split on newlines and indent continuation lines
    lines_in_msg = msg.split('\n')
    formatted_msg = lines_in_msg[0]
    for line in lines_in_msg[1:]:
        formatted_msg += '\n' + indent + line

    return f"{prefix}{formatted_msg}"


def extract_conversation_chain(body: Dict[str, Any]) -> List[tuple[str, str]]:
    """Extract all messages in the conversation chain with roles.
    Returns list of (role, content) tuples."""
    messages = body.get('messages', [])
    conversation = []

    for msg in messages:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')

        if role == 'user':
            # Extract user text or tool results, skip system reminders
            if isinstance(content, str):
                if not content.strip().startswith('<system-reminder>'):
                    conversation.append(('user', content))
            elif isinstance(content, list):
                text_found = False
                tool_results = []

                for block in content:
                    if isinstance(block, dict):
                        if block.get('type') == 'text':
                            text = block.get('text', '')
                            if not text.strip().startswith('<system-reminder>'):
                                conversation.append(('user', text))
                                text_found = True
                                break
                        elif block.get('type') == 'tool_result':
                            tool_results.append(block.get('tool_use_id', 'unknown'))

                # If no text but has tool results, add a marker
                if not text_found and tool_results:
                    conversation.append(('tool_result', f"[Tool results received: {len(tool_results)} result(s)]"))

        elif role == 'assistant':
            # Extract assistant response
            if isinstance(content, str):
                conversation.append(('assistant', content))
            elif isinstance(content, list):
                # Combine text blocks and note tool uses
                texts = []
                tools = []
                for block in content:
                    if isinstance(block, dict):
                        if block.get('type') == 'text':
                            texts.append(block.get('text', ''))
                        elif block.get('type') == 'tool_use':
                            tools.append(block.get('name', 'unknown'))

                response_parts = []
                if texts:
                    response_parts.append(' '.join(texts))
                if tools:
                    response_parts.append(f"[Called tools: {', '.join(tools)}]")

                if response_parts:
                    conversation.append(('assistant', ' '.join(response_parts)))

    return conversation


def extract_tool_calls(response_body: str) -> List[str]:
    """Extract tool names called in response."""
    try:
        resp = json.loads(response_body)
        content = resp.get('content', [])
        tools = []
        for block in content:
            if block.get('type') == 'tool_use':
                tools.append(block.get('name', 'unknown'))
        return tools
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def extract_response_text(response_body: str) -> str:
    """Extract text response."""
    try:
        resp = json.loads(response_body)
        content = resp.get('content', [])
        texts = []
        for block in content:
            if block.get('type') == 'text':
                texts.append(block.get('text', ''))
        return ' '.join(texts)
    except (json.JSONDecodeError, KeyError, TypeError):
        return ""


def classify_endpoint_type(url: str, method: str) -> tuple[str, str]:
    """
    Classify endpoint type and purpose.
    Returns (type, purpose) tuple.
    Handles unknown endpoints gracefully.
    """
    # Known endpoint patterns
    endpoint_patterns = [
        ('oauth', 'AUTH', 'OAuth authentication'),
        ('organization', 'AUTH', 'Organization access check'),
        ('count_tokens', 'VALIDATE', 'Token count validation'),
        ('/api/hello', 'HEALTH', 'Health check'),
        ('/v1/messages', 'MESSAGE', 'API message request'),
    ]

    for pattern, req_type, purpose in endpoint_patterns:
        if pattern in url:
            return req_type, purpose

    # Unknown endpoint - provide helpful info
    # Extract meaningful part of URL
    url_parts = url.split('/')
    endpoint_name = '/'.join(url_parts[-2:]) if len(url_parts) >= 2 else url
    return "UNKNOWN", f"⚠️  Unknown endpoint: {method} {endpoint_name}"


def classify_message_purpose(body: Dict[str, Any], user_msg: str, response_body: str) -> str:
    """
    Determine message purpose based on content patterns.
    Handles unknown types gracefully with generic but informative labels.
    """
    model = body.get('model', 'unknown')
    tool_calls = extract_tool_calls(response_body)

    # Extract system prompt text for pattern matching
    system = body.get('system', '')
    system_text = ''
    if isinstance(system, str):
        system_text = system.lower()
    elif isinstance(system, list):
        # System is array of content blocks
        texts = []
        for block in system:
            if isinstance(block, dict) and block.get('type') == 'text':
                texts.append(block.get('text', ''))
        system_text = ' '.join(texts).lower()

    # Known patterns to check (order matters - most specific first)
    # Patterns check BOTH user message and system prompt
    haiku_patterns = [
        ('quota', "💰 Check quota limits", 'user'),
        ('warmup', "🔥 Model warmup", 'user'),
        ('title for the following conversation', "📝 Generate conversation title", 'user'),
        ('new conversation topic', "🔍 Detect if new topic", 'system'),
        ('isnewtopic', "🔍 Topic detection (JSON)", 'system'),
        ('command:', "📋 Summarize tool output", 'user'),
    ]

    sonnet_patterns = [
        ('warmup', "🔥 Model warmup (Sonnet)", 'user'),
    ]

    # Check model-specific patterns
    if 'haiku' in model.lower():
        for keyword, purpose, check_location in haiku_patterns:
            if check_location == 'user' and keyword in user_msg.lower():
                return purpose
            elif check_location == 'system' and keyword in system_text:
                return purpose
        # Unknown Haiku usage
        return "⚡ Haiku processing (unknown pattern)"

    elif 'sonnet' in model.lower():
        for keyword, purpose, check_location in sonnet_patterns:
            if check_location == 'user' and keyword in user_msg.lower():
                return purpose
            elif check_location == 'system' and keyword in system_text:
                return purpose
        # Sonnet with tool calls
        if tool_calls:
            return f"🛠️  Sonnet calling: {', '.join(tool_calls)}"
        # Generic Sonnet processing
        msg_count = len(body.get('messages', []))
        has_system = bool(body.get('system'))
        return f"💬 Sonnet turn (msgs:{msg_count}, sys:{has_system})"

    # Unknown model
    return f"❓ Unknown model: {model}"


def analyze_request_flow(entries: List[Dict[str, Any]], version: str) -> str:
    """Generate request flow showing all requests with full context."""

    lines = []
    lines.append("=" * 120)
    lines.append(f"REQUEST FLOW - Claude Code v{version}")
    lines.append("=" * 120)
    lines.append("")
    lines.append("NOTE: This analysis auto-detects request types and handles unknowns gracefully.")
    lines.append("      Turns are marked by 'Detect if new topic' Haiku calls (user interactions).")
    lines.append("")
    lines.append("=" * 120)

    # Track turns and unknown patterns
    turn_number = 0
    unknown_endpoints = []
    unknown_message_types = []

    # Start with Turn 0 - Initialization
    lines.append("")
    lines.append("  " + "─" * 116)
    lines.append(f"  🎬 Turn {turn_number} - Initialization")
    lines.append("  " + "─" * 116)
    lines.append("")

    for idx, entry in enumerate(entries):
        url = entry.get('request', {}).get('url', '')
        method = entry.get('request', {}).get('method', 'UNKNOWN')
        body = entry.get('request', {}).get('body')
        response_raw = entry.get('response', {}).get('body_raw', '')

        # Classify endpoint
        req_type, purpose = classify_endpoint_type(url, method)

        details = []

        # Track unknowns for summary
        if req_type == "UNKNOWN":
            unknown_endpoints.append((method, url))

        # Handle message requests with full detail
        if req_type == "MESSAGE" and body:
            user_msg = extract_user_message(body)
            all_user_msgs = extract_all_user_messages(body)
            model = body.get('model', 'unknown')
            has_system = bool(body.get('system'))
            has_tools = bool(body.get('tools'))
            msg_count = len(body.get('messages', []))

            purpose = classify_message_purpose(body, user_msg, response_raw)

            # Check if this is a "Detect if new topic" message - marks a new turn
            if "Detect if new topic" in purpose:
                turn_number += 1
                # Get the actual user prompt - strip newlines for single-line display
                prompt_single_line = user_msg.replace('\n', ' ').replace('\r', ' ')
                next_prompt = prompt_single_line if len(prompt_single_line) <= 80 else prompt_single_line[:77] + "..."
                lines.append("")
                lines.append("  " + "─" * 116)
                lines.append(f"  💬 Turn {turn_number} - {next_prompt}")
                lines.append("  " + "─" * 116)
                lines.append("")

            # Track unknown patterns
            if "unknown pattern" in purpose.lower() or "unknown model" in purpose.lower():
                unknown_message_types.append((model, user_msg[:50]))

            # Extract response info
            tool_calls = extract_tool_calls(response_raw)
            response_text = extract_response_text(response_raw)

            details.append(f"Model: {model}")
            details.append(f"Msgs: {msg_count}, System: {has_system}, Tools: {has_tools}")

            # Display full conversation chain
            conversation = extract_conversation_chain(body)
            if conversation:
                if len(conversation) == 1:
                    # Single message - show it inline with proper indentation
                    role, msg = conversation[0]
                    if role == "tool_result":
                        emoji = "🔧"
                        role_label = "Tool"
                    elif role == "user":
                        emoji = "📥"
                        role_label = "User"
                    else:
                        emoji = "💬"
                        role_label = "Assistant"

                    prefix = f"{emoji} {role_label}: "
                    formatted = format_message_with_indent(msg, prefix, max_length=200)
                    details.append(formatted)
                else:
                    # Multiple messages - show full conversation with proper indentation
                    details.append(f"💬 Conversation ({len(conversation)} messages in chain):")
                    for i, (role, msg) in enumerate(conversation, 1):
                        if role == "tool_result":
                            role_label = "Tool"
                        elif role == "user":
                            role_label = "User"
                        else:
                            role_label = "Assistant"

                        prefix = f"       [{i}] {role_label}: "
                        formatted = format_message_with_indent(msg, prefix, max_length=150)
                        details.append(formatted)

            if tool_calls:
                details.append(f"🔧 Tools called: {', '.join(tool_calls)}")

            if response_text and len(response_text) < 150:
                details.append(f"💭 Response: {response_text}")
            elif response_text:
                details.append(f"💭 Response: {response_text[:100]}... [{len(response_text)} chars]")

        # Print request
        lines.append(f"  [{idx:2d}] {req_type:10s} | {purpose}")
        for detail in details:
            lines.append(f"       {detail}")
        lines.append("")

    # Summary section showing any unknowns detected
    lines.append("=" * 120)
    lines.append("ANALYSIS SUMMARY")
    lines.append("=" * 120)
    lines.append(f"Total requests: {len(entries)}")
    lines.append(f"Total turns: {turn_number}")

    if unknown_endpoints:
        lines.append("")
        lines.append("⚠️  UNKNOWN ENDPOINTS DETECTED:")
        for method, url in set(unknown_endpoints):
            lines.append(f"   - {method} {url}")
        lines.append("   (These are new and not yet categorized)")

    if unknown_message_types:
        lines.append("")
        lines.append("⚠️  UNKNOWN MESSAGE PATTERNS DETECTED:")
        for model, msg_preview in unknown_message_types:
            lines.append(f"   - {model}: {msg_preview}...")
        lines.append("   (These may be new features or usage patterns)")

    if not unknown_endpoints and not unknown_message_types:
        lines.append("")
        lines.append("✅ All request types recognized")

    lines.append("")
    lines.append("=" * 120)
    lines.append("END OF FLOW")
    lines.append("=" * 120)

    return '\n'.join(lines)


def main():
    if len(sys.argv) != 2:
        print("Usage: python detailed_flow.py <trace.jsonl>")
        print("")
        print("This script analyzes Claude Code API traces and shows:")
        print("  - All requests in chronological order")
        print("  - Request types and purposes")
        print("  - User messages and responses")
        print("  - Tool calls and outputs")
        print("  - Detection of unknown/new request types")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist")
        sys.exit(1)

    version = file_path.stem.split('_')[-1] if '_' in file_path.stem else file_path.stem

    print(f"Analyzing {file_path.name}...")
    entries = load_jsonl(file_path)

    report = analyze_request_flow(entries, version)
    print(report)


if __name__ == '__main__':
    main()
