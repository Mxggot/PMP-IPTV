#!/usr/bin/env python3
"""
build_playlist.py
-----------------
this reads ph.m3u.template, substitutes all {{PLACEHOLDER}} tokens
using CDN_URL env var and CHANNEL_MAP env var (JSON string) then
writes the final playlist to dist/ph.m3u
"""

import os
import re
import json
import sys

def main():
    cdn_url = os.environ.get("CDN_URL", "").rstrip("/")
    channel_map_raw = os.environ.get("CHANNEL_MAP", "")

    if not cdn_url:
        print("ERROR: CDN_URL environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    if not channel_map_raw:
        print("ERROR: CHANNEL_MAP environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    try:
        channel_map = json.loads(channel_map_raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: CHANNEL_MAP is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    template_path = os.path.join(os.path.dirname(__file__), "..", "ph.m3u")
    output_dir    = os.path.join(os.path.dirname(__file__), "..", "dist")
    output_path   = os.path.join(output_dir, "ph.m3u")

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # replace {{CDN}}
    content = content.replace("{{CDN}}", cdn_url)

    # replace all {{CHANNEL_KEY}} tokens
    def replacer(match):
        key = match.group(1)
        if key not in channel_map:
            print(f"WARNING: No mapping found for placeholder {{{{{key}}}}}", file=sys.stderr)
            return match.group(0)
        return channel_map[key]

    content = re.sub(r"\{\{([A-Z0-9_]+)\}\}", replacer, content)

    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✓ Built playlist → {output_path}")

if __name__ == "__main__":
    main()
