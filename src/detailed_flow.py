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
        ('/api/hello', 'HEALTH', 'Health check / phase delimiter'),
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


def analyze_detailed_flow(entries: List[Dict[str, Any]], version: str) -> str:
    """Generate detailed flow showing all requests with full context."""

    lines = []
    lines.append("=" * 120)
    lines.append(f"DETAILED API FLOW - Claude Code v{version}")
    lines.append("=" * 120)
    lines.append("")
    lines.append("NOTE: This analysis auto-detects request types and handles unknowns gracefully.")
    lines.append("      Health checks (GET /api/hello) are used as phase delimiters.")
    lines.append("")
    lines.append("=" * 120)

    # Track phases and unknown patterns
    health_check_count = 0
    unknown_endpoints = []
    unknown_message_types = []

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

        # Handle health checks as phase delimiters
        if req_type == "HEALTH":
            health_check_count += 1
            lines.append("")
            lines.append("  " + "─" * 116)
            lines.append(f"  ⬇️  Phase {health_check_count} completed - Health check")
            lines.append("  " + "─" * 116)
            lines.append("")

        # Handle message requests with full detail
        elif req_type == "MESSAGE" and body:
            user_msg = extract_user_message(body)
            model = body.get('model', 'unknown')
            has_system = bool(body.get('system'))
            has_tools = bool(body.get('tools'))
            msg_count = len(body.get('messages', []))

            purpose = classify_message_purpose(body, user_msg, response_raw)

            # Track unknown patterns
            if "unknown pattern" in purpose.lower() or "unknown model" in purpose.lower():
                unknown_message_types.append((model, user_msg[:50]))

            # Extract response info
            tool_calls = extract_tool_calls(response_raw)
            response_text = extract_response_text(response_raw)

            details.append(f"Model: {model}")
            details.append(f"Msgs: {msg_count}, System: {has_system}, Tools: {has_tools}")

            if user_msg and user_msg.strip() and len(user_msg) < 200:
                details.append(f"📥 User: {user_msg[:150]}")
            elif user_msg and len(user_msg) >= 200:
                details.append(f"📥 User: {user_msg[:100]}... [{len(user_msg)} chars]")

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
    lines.append(f"Health check phases: {health_check_count}")

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

    report = analyze_detailed_flow(entries, version)
    print(report)


if __name__ == '__main__':
    main()
