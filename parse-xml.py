#!/usr/bin/env python3
"""Parse WordPress XML export and extract posts with categories and tags."""

import xml.etree.ElementTree as ET
import json
import html
import sys

INPUT = "/Users/jdemaat/Downloads/bagcdcommunityresourceslist.WordPress.2026-03-30.xml"
OUTPUT = "/Users/jdemaat/Desktop/CRL2026/data.json"

# WordPress XML namespaces
NS = {
    'wp': 'http://wordpress.org/export/1.2/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
}

# Pathway category nicenames (these are the structural groupings, like "Platforms")
PATHWAY_NICENAMES = {
    'p1-experience-environment', 'p2-experience-environment',
    'u7-experience-environment', 'p2-experience-environment-unit-7',
    'p1-information-systems', 'p2-information-systems', 'u7-information-systems',
    'p1-tm', 'p1tm', 'p2-tm',
    'p1-nv', 'p1-nv-unit-6', 'p2-nv', 'p2-nv-unit-6',
    'p1-si-unit-7', 'p1-si-unit-6', 'p2-si',
    'u5-core-reading', 'u6-core-reading-list', 'u7-core-reading-list',
    'lectures-debates',
}

# Unit category nicenames
UNIT_NICENAMES = {
    'unit1', 'unit2', 'unit3', 'unit4',
    'u5', 'unit-6', 'unit-7',
}

# Stage nicenames (we'll track but not use as primary grouping)
STAGE_NICENAMES = {'stage1', 'stage-2', 'stage-3'}

tree = ET.parse(INPUT)
root = tree.getroot()
channel = root.find('channel')

posts = []
all_tags = set()
all_pathways = set()
all_units = set()

for item in channel.findall('item'):
    post_type = item.find('wp:post_type', NS)
    if post_type is None or post_type.text != 'post':
        continue

    title_el = item.find('title')
    title = title_el.text if title_el is not None and title_el.text else ''
    title = html.unescape(title).strip()
    if not title:
        continue

    creator = item.find('dc:creator', NS)
    author = creator.text if creator is not None and creator.text else ''

    status = item.find('wp:status', NS)
    status_text = status.text if status is not None else 'draft'

    tags = []
    pathways = []
    units = []

    for cat in item.findall('category'):
        domain = cat.get('domain', '')
        nicename = cat.get('nicename', '')
        label = html.unescape(cat.text or '').strip()

        if domain == 'post_tag':
            tags.append(label)
            all_tags.add(label)
        elif domain == 'category':
            if nicename in PATHWAY_NICENAMES:
                # Normalize: strip unit prefix (U6P1-E&E → P1-E&E)
                import re as _re
                norm = _re.sub(r'^U\d+', '', label)
                # Ensure dash after P1/P2 (P1T&M → P1-T&M)
                norm = _re.sub(r'^(P[12])([^-])', r'\1-\2', norm)
                pathways.append(norm)
                all_pathways.add(norm)
            elif nicename in UNIT_NICENAMES:
                units.append(label)
                all_units.add(label)
            # Ignore stage categories

    # Include both published and draft posts that have at least a title
    posts.append({
        'id': f"post-{item.find('wp:post_id', NS).text}",
        'title': title,
        'author': author,
        'status': status_text,
        'tags': tags,
        'pathways': pathways,
        'units': units,
    })

# Build output
output = {
    'posts': posts,
    'allTags': sorted(all_tags),
    'allPathways': sorted(all_pathways),
    'allUnits': sorted(all_units),
    'stats': {
        'totalPosts': len(posts),
        'publishedPosts': sum(1 for p in posts if p['status'] == 'publish'),
        'postsWithTags': sum(1 for p in posts if p['tags']),
        'postsWithPathways': sum(1 for p in posts if p['pathways']),
        'postsWithUnits': sum(1 for p in posts if p['units']),
        'uniqueTags': len(all_tags),
        'uniquePathways': len(all_pathways),
        'uniqueUnits': len(all_units),
    }
}

with open(OUTPUT, 'w') as f:
    json.dump(output, f, indent=2)

print(f"Extracted {len(posts)} posts")
print(f"  Published: {output['stats']['publishedPosts']}")
print(f"  With tags: {output['stats']['postsWithTags']}")
print(f"  With pathways: {output['stats']['postsWithPathways']}")
print(f"  With units: {output['stats']['postsWithUnits']}")
print(f"  Unique tags: {output['stats']['uniqueTags']}")
print(f"  Unique pathways: {output['stats']['uniquePathways']}")
print(f"  Unique units: {output['stats']['uniqueUnits']}")
print(f"\nPathways: {sorted(all_pathways)}")
print(f"Units: {sorted(all_units)}")
print(f"\nTop tags:")
from collections import Counter
tag_counts = Counter()
for p in posts:
    for t in p['tags']:
        tag_counts[t] += 1
for tag, count in tag_counts.most_common(30):
    print(f"  {tag}: {count}")
