#!/usr/bin/env python3
"""Stage 1: Extract tags from WordPress XML export, clean, and output tags.json"""

import xml.etree.ElementTree as ET
import json
import re
from collections import Counter

XML_PATH = "/Users/jdemaat/Downloads/bagcdcommunityresourceslist.WordPress.2026-03-30.xml"

# WordPress namespace
NS = {"wp": "http://wordpress.org/export/1.2/"}

tree = ET.parse(XML_PATH)
root = tree.getroot()
channel = root.find("channel")

# 1. Extract tag definitions (slug -> name)
tag_defs = {}
for tag_el in channel.findall("wp:tag", NS):
    slug = tag_el.find("wp:tag_slug", NS).text
    name = tag_el.find("wp:tag_name", NS).text
    if slug and name:
        tag_defs[slug] = name

print(f"Tag definitions found: {len(tag_defs)}")

# 2. Count how many published posts use each tag
tag_counts = Counter()
items = channel.findall("item")
print(f"Total items in export: {len(items)}")

for item in items:
    # Only count published posts
    status = item.find("wp:status", NS)
    post_type = item.find("wp:post_type", NS)
    if status is not None and status.text != "publish":
        continue
    if post_type is not None and post_type.text not in ("post", "page"):
        continue

    for cat in item.findall("category"):
        if cat.get("domain") == "post_tag":
            slug = cat.get("nicename")
            if slug:
                tag_counts[slug] += 1

print(f"Tags actually used in posts: {len(tag_counts)}")

# 3. Clean: normalise names, merge duplicates
def clean_name(name):
    """Remove leading # and normalise whitespace"""
    name = name.strip()
    if name.startswith("#"):
        name = name[1:]
    return name

# Build slug -> clean_name mapping, merging case variants
# Group by lowercased clean name
from collections import defaultdict
name_groups = defaultdict(list)

all_slugs = set(tag_defs.keys()) | set(tag_counts.keys())
for slug in all_slugs:
    name = tag_defs.get(slug, slug.replace("-", " "))
    clean = clean_name(name)
    key = clean.lower().strip()
    name_groups[key].append((slug, clean))

# Merge: pick the best name (most common capitalisation or longest), sum counts
tags = []
for key, entries in name_groups.items():
    # Sum counts across all slugs for this normalised name
    total_count = sum(tag_counts.get(slug, 0) for slug, _ in entries)

    # Pick the best label: prefer the one with highest count, then longest
    best_name = max(entries, key=lambda x: (tag_counts.get(x[0], 0), len(x[1])))[1]

    # Use the normalised key as ID (safe for JSON keys)
    tag_id = key.replace(" ", "-")

    tags.append({
        "id": tag_id,
        "label": best_name,
        "count": total_count,
        "slugs": [s for s, _ in entries]  # track originals for debugging
    })

print(f"After normalisation/merge: {len(tags)} unique tags")

# 4. Remove tags used only once
tags_filtered = [t for t in tags if t["count"] >= 2]
removed = len(tags) - len(tags_filtered)
print(f"Removed {removed} tags with count < 2, keeping {len(tags_filtered)}")

# Sort by count descending
tags_filtered.sort(key=lambda t: -t["count"])

# Remove internal slugs field for output
tags_out = [{"id": t["id"], "label": t["label"], "count": t["count"]} for t in tags_filtered]

# 5. Summary stats
counts = [t["count"] for t in tags_out]
print(f"\n=== STAGE 1 SUMMARY ===")
print(f"Total unique tags (after cleaning): {len(tags_out)}")
print(f"Min post count: {min(counts)}")
print(f"Max post count: {max(counts)}")
print(f"Avg post count: {sum(counts)/len(counts):.1f}")
print(f"Median post count: {sorted(counts)[len(counts)//2]}")
print(f"\nTop 20 tags:")
for t in tags_out[:20]:
    print(f"  {t['count']:4d}  {t['label']}")

# 6. Save
with open("tags.json", "w") as f:
    json.dump(tags_out, f, indent=2)

print(f"\nSaved tags.json with {len(tags_out)} tags")
