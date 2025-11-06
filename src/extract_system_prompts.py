#!/usr/bin/env python3
"""
Extract system prompts from Claude Code trace files.

This script:
1. Extracts the system prompt from the first real user interaction (Sonnet)
2. Saves each version's system prompt to output/system_prompts/ directory
3. Updates metadata about block structure

Usage:
    python extract_system_prompts.py trace_file1.jsonl [trace_file2.jsonl ...]
    python extract_system_prompts.py --all  # Extract all traces in .claude-trace/
"""

import argparse
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


def extract_system_prompt(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract system prompt from the first Sonnet message after warmup.

    Returns dict with:
    - entry_idx: Index of the entry
    - user_msg: User message that triggered this
    - system: List of system blocks
    - block_count: Number of blocks
    """
    for idx, entry in enumerate(entries):
        url = entry.get('request', {}).get('url', '')
        body = entry.get('request', {}).get('body')

        if '/v1/messages' in url and body:
            model = body.get('model', '')
            system = body.get('system', [])
            messages = body.get('messages', [])

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
                                user_msg = block.get('text', '')
                                break
                    break

            # Skip warmup, look for first real prompt
            if 'sonnet' in model.lower() and system and 'Warmup' not in user_msg:
                return {
                    'entry_idx': idx,
                    'user_msg': user_msg,
                    'system': system,
                    'block_count': len(system)
                }

    return None


def save_system_prompt(version: str, prompt_data: Dict[str, Any], output_dir: Path):
    """Save system prompt to structured file."""
    output_file = output_dir / f"system_prompt_{version}.txt"

    lines = []
    lines.append("=" * 120)
    lines.append(f"SYSTEM PROMPT - Claude Code v{version}")
    lines.append("=" * 120)
    lines.append("")
    lines.append(f"Block Count: {prompt_data['block_count']}")
    lines.append(f"Extracted from entry: {prompt_data['entry_idx']}")
    lines.append("")

    for idx, block in enumerate(prompt_data['system']):
        block_type = block.get('type', 'unknown')
        lines.append("=" * 120)
        lines.append(f"BLOCK {idx + 1} - TYPE: {block_type.upper()}")
        lines.append("=" * 120)
        lines.append("")

        if block_type == 'text':
            text = block.get('text', '')
            lines.append(text)
        else:
            # Other block types (JSON dump)
            lines.append(json.dumps(block, indent=2))

        lines.append("")

    lines.append("=" * 120)
    lines.append("END OF SYSTEM PROMPT")
    lines.append("=" * 120)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return output_file


def save_metadata(versions_info: Dict[str, Any], output_dir: Path):
    """Update metadata about all extracted versions."""
    metadata_file = output_dir / 'metadata.json'

    # Load existing metadata if it exists
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        metadata = {
            'versions': {},
            'extraction_order': []
        }

    # Update with new versions
    for version, info in versions_info.items():
        metadata['versions'][version] = {
            'trace_file': info['trace_file'],
            'block_count': info['block_count'],
            'entry_idx': info['entry_idx']
        }
        if version not in metadata['extraction_order']:
            metadata['extraction_order'].append(version)

    # Sort extraction order
    metadata['extraction_order'] = sorted(metadata['extraction_order'])

    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    return metadata_file


def main():
    # Argument parsing
    parser = argparse.ArgumentParser(
        description='Extract system prompts from Claude Code trace files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s trace_2025-01-05_2.0.29.jsonl
  %(prog)s trace1.jsonl trace2.jsonl trace3.jsonl
  %(prog)s --all
        """
    )
    parser.add_argument(
        'trace_files',
        nargs='*',
        help='Trace file(s) to extract from'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Extract from all trace files in .claude-trace/ directory'
    )

    args = parser.parse_args()

    # Setup
    trace_dir = Path('.claude-trace')
    output_dir = Path('output/system_prompts')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine which files to process
    if args.all:
        if not trace_dir.exists():
            print(f"Error: {trace_dir} directory not found")
            return
        trace_files = sorted(trace_dir.glob('*.jsonl'))
        if not trace_files:
            print(f"Error: No .jsonl files found in {trace_dir}")
            return
        print(f"Found {len(trace_files)} trace files")
        print("")
    elif args.trace_files:
        # Convert provided filenames to Path objects
        trace_files = []
        for filename in args.trace_files:
            filepath = trace_dir / filename
            if not filepath.exists():
                print(f"Error: {filepath} not found")
                return
            trace_files.append(filepath)
    else:
        parser.print_help()
        print("\nError: Please provide at least one trace file or use --all flag")
        return

    # Extract from each file
    versions_info = {}

    for trace_file in trace_files:
        # Extract version from filename (last part after underscore)
        version = trace_file.stem.split('_')[-1]

        # Skip duplicates (keep first occurrence)
        if version in versions_info:
            print(f"⊘ Skipping {trace_file.name} - version {version} already extracted in this run")
            continue

        print(f"Processing {trace_file.name}...")
        entries = load_jsonl(trace_file)
        prompt_data = extract_system_prompt(entries)

        if prompt_data:
            output_file = save_system_prompt(version, prompt_data, output_dir)
            versions_info[version] = {
                'trace_file': trace_file.name,
                'block_count': prompt_data['block_count'],
                'entry_idx': prompt_data['entry_idx']
            }
            print(f"  ✓ Extracted {prompt_data['block_count']} blocks")
            print(f"  ✓ Saved to {output_file.name}")
        else:
            print(f"  ✗ No system prompt found")

        print("")

    # Save metadata
    if versions_info:
        metadata_file = save_metadata(versions_info, output_dir)
        print(f"✓ Updated metadata in {metadata_file.name}")
        print("")
        print("=" * 80)
        print("EXTRACTION SUMMARY")
        print("=" * 80)
        for version in sorted(versions_info.keys()):
            info = versions_info[version]
            print(f"  v{version}: {info['block_count']} blocks (from {info['trace_file']})")
        print("")
    else:
        print("No system prompts extracted")


if __name__ == '__main__':
    main()
