#!/usr/bin/env python3
"""
Extract tool definitions from Claude Code trace files.

This script:
1. Accepts specific trace file(s) as arguments OR --extract-all flag
2. Extracts tool definitions from the first Sonnet message with tools
3. Saves each version's tools to output/tool_definitions/ directory
4. Generates metadata about tool counts and extraction details

Usage:
    python extract_tools.py <trace_file> [<trace_file> ...]
    python extract_tools.py --extract-all

Examples:
    python extract_tools.py .claude-trace/log-2025-10-31-21-48-26_2.0.5.jsonl
    python extract_tools.py .claude-trace/log-*_2.0.30.jsonl .claude-trace/log-*_2.0.31.jsonl
    python extract_tools.py --extract-all
"""

import sys
import json
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


def extract_tools(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract tool definitions from the "Hi, what is your name?" prompt.

    This corresponds to the SIMPLE PROMPT from INSTRUCTIONS.md which should
    contain the full tool set for the version.

    Returns dict with:
    - entry_idx: Index of the entry
    - user_msg: User message that triggered this
    - tools: List of tool definitions
    - tool_count: Number of tools
    - tool_names: List of tool names
    """
    for idx, entry in enumerate(entries):
        url = entry.get('request', {}).get('url', '')
        body = entry.get('request', {}).get('body')

        if '/v1/messages' in url and body and isinstance(body, dict):
            model = body.get('model', '')
            tools = body.get('tools')
            messages = body.get('messages', [])

            if not tools:
                continue

            # Get user message
            user_msg = ''
            for msg in messages:
                if msg.get('role') == 'user':
                    content = msg.get('content', '')
                    if isinstance(content, str):
                        user_msg = content
                    elif isinstance(content, list):
                        for block in content:
                            if block.get('type') == 'text':
                                text = block.get('text', '')
                                # Look for the SIMPLE PROMPT
                                if 'what is your name' in text.lower():
                                    user_msg = text
                                    break
                    break

            # Look for Sonnet request with "Hi, what is your name?" prompt
            if 'sonnet' in model.lower() and tools and 'what is your name' in user_msg.lower():
                tool_names = [tool.get('name', 'unknown') for tool in tools]
                return {
                    'entry_idx': idx,
                    'user_msg': user_msg,
                    'tools': tools,
                    'tool_count': len(tools),
                    'tool_names': tool_names
                }

    return None


def save_tools(version: str, tools_data: Dict[str, Any], output_dir: Path):
    """Save tool definitions to structured file."""
    output_file = output_dir / f"tools_{version}.txt"

    lines = []
    lines.append("=" * 120)
    lines.append(f"TOOL DEFINITIONS - Claude Code v{version}")
    lines.append("=" * 120)
    lines.append("")
    lines.append(f"Tool Count: {tools_data['tool_count']}")
    lines.append("")
    lines.append("Tool Names:")
    for name in tools_data['tool_names']:
        lines.append(f"  - {name}")
    lines.append("")

    for idx, tool in enumerate(tools_data['tools']):
        tool_name = tool.get('name', 'unknown')
        tool_desc = tool.get('description', '')
        tool_schema = tool.get('input_schema', {})

        lines.append("=" * 120)
        lines.append(f"TOOL {idx + 1}: {tool_name}")
        lines.append("=" * 120)
        lines.append("")

        # Description
        lines.append("DESCRIPTION:")
        lines.append("-" * 120)
        lines.append(tool_desc)
        lines.append("")

        # Input Schema
        lines.append("INPUT SCHEMA:")
        lines.append("-" * 120)
        lines.append(json.dumps(tool_schema, indent=2))
        lines.append("")

    lines.append("=" * 120)
    lines.append("END OF TOOL DEFINITIONS")
    lines.append("=" * 120)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return output_file


def save_tools_json(version: str, tools_data: Dict[str, Any], output_dir: Path):
    """Save tool definitions as JSON for easier programmatic access."""
    output_file = output_dir / f"tools_{version}.json"

    # Create a clean structure for JSON output
    tools_json = {
        'version': version,
        'tool_count': tools_data['tool_count'],
        'extracted_from_entry': tools_data['entry_idx'],
        'tools': tools_data['tools']
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tools_json, f, indent=2)

    return output_file


def save_tools_no_mcp(version: str, tools_data: Dict[str, Any], output_dir: Path):
    """Save tool definitions excluding MCP tools to text file."""
    output_file = output_dir / f"tools_no_mcp_{version}.txt"

    # Filter out MCP tools
    filtered_tools = [
        tool for tool in tools_data['tools']
        if not tool.get('name', '').startswith('mcp__')
    ]

    lines = []
    lines.append("=" * 120)
    lines.append(f"TOOL DEFINITIONS (CORE TOOLS ONLY) - Claude Code v{version}")
    lines.append("=" * 120)
    lines.append("")
    lines.append(f"Tool Count: {len(filtered_tools)} (MCP tools excluded)")
    lines.append("")
    lines.append("Tool Names:")
    for tool in filtered_tools:
        lines.append(f"  - {tool.get('name', 'unknown')}")
    lines.append("")

    for idx, tool in enumerate(filtered_tools):
        tool_name = tool.get('name', 'unknown')
        tool_desc = tool.get('description', '')
        tool_schema = tool.get('input_schema', {})

        lines.append("=" * 120)
        lines.append(f"TOOL {idx + 1}: {tool_name}")
        lines.append("=" * 120)
        lines.append("")

        # Description
        lines.append("DESCRIPTION:")
        lines.append("-" * 120)
        lines.append(tool_desc)
        lines.append("")

        # Input Schema
        lines.append("INPUT SCHEMA:")
        lines.append("-" * 120)
        lines.append(json.dumps(tool_schema, indent=2))
        lines.append("")

    lines.append("=" * 120)
    lines.append("END OF TOOL DEFINITIONS")
    lines.append("=" * 120)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return output_file


def save_tools_no_mcp_json(version: str, tools_data: Dict[str, Any], output_dir: Path):
    """Save tool definitions excluding MCP tools as JSON."""
    output_file = output_dir / f"tools_no_mcp_{version}.json"

    # Filter out MCP tools (tools starting with "mcp__")
    filtered_tools = [
        tool for tool in tools_data['tools']
        if not tool.get('name', '').startswith('mcp__')
    ]

    # Create a clean structure for JSON output
    tools_json = {
        'version': version,
        'tool_count': len(filtered_tools),
        'extracted_from_entry': tools_data['entry_idx'],
        'tools': filtered_tools,
        'note': 'MCP tools excluded'
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tools_json, f, indent=2)

    return output_file


def save_metadata(versions_info: Dict[str, Any], output_dir: Path):
    """Save metadata about all extracted versions."""
    metadata = {
        'versions': {},
        'extraction_order': []
    }

    for version, info in sorted(versions_info.items()):
        metadata['versions'][version] = {
            'trace_file': info['trace_file'],
            'tool_count': info['tool_count'],
            'tool_count_no_mcp': info['tool_count_no_mcp'],
            'tool_names': info['tool_names'],
            'entry_idx': info['entry_idx']
        }
        metadata['extraction_order'].append(version)

    metadata_file = output_dir / 'metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    return metadata_file


def main():
    # Setup
    output_dir = Path('output/tool_definitions')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Error: No trace files specified")
        print("")
        print("Usage:")
        print("  python extract_tools.py <trace_file> [<trace_file> ...]")
        print("  python extract_tools.py --extract-all")
        print("")
        print("Examples:")
        print("  python extract_tools.py .claude-trace/log-2025-10-31-21-48-26_2.0.5.jsonl")
        print("  python extract_tools.py .claude-trace/log-*_2.0.30.jsonl")
        print("  python extract_tools.py --extract-all")
        return

    # Determine which files to process
    trace_files = []

    if sys.argv[1] == '--extract-all':
        trace_dir = Path('.claude-trace')
        if not trace_dir.exists():
            print(f"Error: {trace_dir} directory not found")
            return
        trace_files = sorted(trace_dir.glob('*.jsonl'))
        if not trace_files:
            print(f"Error: No .jsonl files found in {trace_dir}")
            return
        print(f"Found {len(trace_files)} trace files")
    else:
        # Process specific files from arguments
        for arg in sys.argv[1:]:
            path = Path(arg)
            if path.exists() and path.is_file():
                trace_files.append(path)
            else:
                print(f"Warning: File not found or not a file: {arg}")

        if not trace_files:
            print("Error: No valid trace files found")
            return

        print(f"Processing {len(trace_files)} trace file(s)")

    print("")

    # Extract from each file
    versions_info = {}

    for trace_file in trace_files:
        # Extract version from filename (last part after underscore)
        version = trace_file.stem.split('_')[-1]

        # Skip duplicates (keep first occurrence)
        if version in versions_info:
            print(f"⊘ Skipping {trace_file.name} - version {version} already extracted")
            continue

        print(f"Processing {trace_file.name}...")
        entries = load_jsonl(trace_file)
        tools_data = extract_tools(entries)

        if tools_data:
            # Save all formats: text, JSON, no-MCP text, and no-MCP JSON
            txt_file = save_tools(version, tools_data, output_dir)
            json_file = save_tools_json(version, tools_data, output_dir)
            no_mcp_txt_file = save_tools_no_mcp(version, tools_data, output_dir)
            no_mcp_json_file = save_tools_no_mcp_json(version, tools_data, output_dir)

            # Count tools excluding MCP
            non_mcp_count = len([t for t in tools_data['tools'] if not t.get('name', '').startswith('mcp__')])

            versions_info[version] = {
                'trace_file': trace_file.name,
                'tool_count': tools_data['tool_count'],
                'tool_count_no_mcp': non_mcp_count,
                'tool_names': tools_data['tool_names'],
                'entry_idx': tools_data['entry_idx']
            }
            print(f"  ✓ Extracted {tools_data['tool_count']} tools ({non_mcp_count} core, {tools_data['tool_count'] - non_mcp_count} MCP)")
            print(f"  ✓ Saved 4 files: {txt_file.name}, {json_file.name}, {no_mcp_txt_file.name}, {no_mcp_json_file.name}")
        else:
            print(f"  ✗ No tools found")

        print("")

    # Save metadata
    if versions_info:
        metadata_file = save_metadata(versions_info, output_dir)
        print(f"✓ Saved metadata to {metadata_file.name}")
        print("")
        print("=" * 80)
        print("EXTRACTION SUMMARY")
        print("=" * 80)
        for version in sorted(versions_info.keys()):
            info = versions_info[version]
            mcp_count = info['tool_count'] - info['tool_count_no_mcp']
            print(f"  v{version}: {info['tool_count']} tools ({info['tool_count_no_mcp']} core, {mcp_count} MCP) - {info['trace_file']}")
            print(f"    Tools: {', '.join(info['tool_names'][:5])}" +
                  (f"... +{len(info['tool_names'])-5} more" if len(info['tool_names']) > 5 else ""))
        print("")
    else:
        print("No tools extracted")


if __name__ == '__main__':
    main()
