#!/usr/bin/env python3
"""rebuild-index.py — Rebuild wiki/index.md from actual wiki content.
Usage: python3 rebuild-index.py [wiki_dir]
"""
import os, sys, glob, re

wiki_dir = sys.argv[1] if len(sys.argv) > 1 else "."
index_path = os.path.join(wiki_dir, "wiki", "index.md")

ingested = sorted(glob.glob(f"{wiki_dir}/raw/ingested/**/*.md", recursive=True))
concepts = sorted(glob.glob(f"{wiki_dir}/wiki/concepts/**/*.md", recursive=True))
sources_md = sorted(glob.glob(f"{wiki_dir}/wiki/sources/**/*.md", recursive=True))
entities = sorted(glob.glob(f"{wiki_dir}/wiki/entities/**/*.md", recursive=True))

lines = [
    "# Wiki Index\n",
    "Auto-generated index. Rebuilt by rebuild-index.py\n",
    "\n## Sources\n"
]

for p in ingested:
    aid = os.path.basename(p).replace('.md', '')
    lines.append(f"- **{aid}**\n")

if sources_md:
    lines.append(f"\n## Detailed Sources\n")
    for p in sources_md:
        name = os.path.basename(p).replace('.md', '')
        content = open(p).read()
        title = ''
        for l in content.split('\n')[:5]:
            if l.startswith('**Title:**') or l.startswith('# '):
                title = l.replace('**Title:**', '').replace('# ', '').strip()
                break
        lines.append(f"- [[{name}]]" + (f" — {title}" if title else '') + "\n")

lines.append(f"\n## Concepts ({len(concepts)} concepts)\n")
for p in concepts:
    name = os.path.basename(p).replace('.md', '')
    content = open(p).read()
    first_para = ''
    for l in content.split('\n'):
        stripped = l.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('['):
            first_para = stripped[:120]
            break
    lines.append(f"- [[{name}]]" + (f" — {first_para}" if first_para else '') + "\n")

if entities:
    lines.append(f"\n## Entities\n")
    for p in entities:
        name = os.path.basename(p).replace('.md', '')
        lines.append(f"- [[{name}]]\n")

with open(index_path, 'w') as f:
    f.write(''.join(lines))

print(f"Index rebuilt: {len(ingested)} sources, {len(concepts)} concepts, {len(entities)} entities")
