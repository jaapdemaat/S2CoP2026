#!/usr/bin/env python3
"""Stage 2 & 3: Cluster tags via Anthropic API and build graph.json"""

import json
import os
import sys
import getpass
import anthropic
import math
import colorsys

# Load tags
with open("tags.json") as f:
    tags = json.load(f)

print(f"Loaded {len(tags)} tags")

# Get API key: env var, command-line arg, or prompt
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key and len(sys.argv) > 1:
    api_key = sys.argv[1]
if not api_key:
    api_key = getpass.getpass("Enter your Anthropic API key: ")

client = anthropic.Anthropic(api_key=api_key)

# Stage 2: Batch clustering
BATCH_SIZE = 80
batches = [tags[i:i+BATCH_SIZE] for i in range(0, len(tags), BATCH_SIZE)]
print(f"Split into {len(batches)} batches of up to {BATCH_SIZE}")

all_batch_clusters = []

for i, batch in enumerate(batches):
    tag_list = "\n".join(f"- {t['id']}: {t['label']}" for t in batch)

    prompt = f"""You are helping organise tags from a graphic design/communication design community resources list into semantic clusters.

Here are {len(batch)} tags (id: label):

{tag_list}

Group these tags into semantic clusters based on meaning and topic similarity.
Aim for 8-15 clusters per batch. Each tag must appear in exactly one cluster.
Give each cluster a short descriptive label.

Return ONLY valid JSON — no markdown, no explanation. Format:
[
  {{"cluster_id": "media-film", "cluster_label": "Film & Moving Image", "tags": ["film", "documentary", "animation"]}},
  ...
]"""

    print(f"  Batch {i+1}/{len(batches)} ({len(batch)} tags)...")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]

    batch_clusters = json.loads(text)
    all_batch_clusters.append(batch_clusters)
    print(f"    Got {len(batch_clusters)} clusters")

# Flatten all batch clusters
flat_clusters = []
for bc in all_batch_clusters:
    flat_clusters.extend(bc)

print(f"\nTotal clusters before merge: {len(flat_clusters)}")

# Stage 2b: Merge/reconcile clusters across batches
cluster_summary = json.dumps([
    {"cluster_id": c["cluster_id"], "cluster_label": c["cluster_label"], "tag_count": len(c["tags"]), "sample_tags": c["tags"][:5]}
    for c in flat_clusters
], indent=2)

merge_prompt = f"""You have {len(flat_clusters)} semantic clusters of design/art tags that were created in separate batches.
Many clusters overlap or are duplicates. Merge them into a final coherent set of 15-25 clusters.

Current clusters:
{cluster_summary}

For each final cluster, provide:
- A unique cluster_id (lowercase, hyphenated)
- A descriptive cluster_label
- A list of source cluster_ids to merge into this one

Return ONLY valid JSON:
[
  {{"cluster_id": "film-moving-image", "cluster_label": "Film & Moving Image", "source_ids": ["media-film", "video-animation", ...]}},
  ...
]

Make sure EVERY source cluster_id from the input is assigned to exactly one final cluster."""

print("Reconciling clusters across batches...")
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=[{"role": "user", "content": merge_prompt}]
)

text = response.content[0].text.strip()
if text.startswith("```"):
    text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

merge_plan = json.loads(text)
print(f"Merge plan: {len(merge_plan)} final clusters")

# Build source_id -> final_cluster mapping
source_to_final = {}
for final in merge_plan:
    for src_id in final["source_ids"]:
        source_to_final[src_id] = final["cluster_id"]

# Build final clusters with actual tag lists
final_clusters = {}
for final in merge_plan:
    final_clusters[final["cluster_id"]] = {
        "cluster_id": final["cluster_id"],
        "cluster_label": final["cluster_label"],
        "tags": []
    }

# Map tags from source clusters to final clusters
unmapped_tags = []
for src_cluster in flat_clusters:
    src_id = src_cluster["cluster_id"]
    final_id = source_to_final.get(src_id)
    if final_id and final_id in final_clusters:
        final_clusters[final_id]["tags"].extend(src_cluster["tags"])
    else:
        # Source cluster wasn't mapped - put tags in unmapped
        unmapped_tags.extend(src_cluster["tags"])
        print(f"  Warning: source cluster '{src_id}' not mapped to any final cluster")

if unmapped_tags:
    # Add unmapped to a misc cluster
    if "miscellaneous" not in final_clusters:
        final_clusters["miscellaneous"] = {
            "cluster_id": "miscellaneous",
            "cluster_label": "Miscellaneous",
            "tags": []
        }
    final_clusters["miscellaneous"]["tags"].extend(unmapped_tags)
    print(f"  {len(unmapped_tags)} unmapped tags added to 'miscellaneous'")

# Deduplicate tags within each cluster
for c in final_clusters.values():
    c["tags"] = list(dict.fromkeys(c["tags"]))  # preserve order, remove dupes

clusters_list = list(final_clusters.values())

# Save clusters.json
with open("clusters.json", "w") as f:
    json.dump(clusters_list, f, indent=2)

print(f"\nSaved clusters.json with {len(clusters_list)} clusters")
for c in clusters_list:
    print(f"  {c['cluster_label']}: {len(c['tags'])} tags")

# Stage 3: Build graph.json
print("\n=== STAGE 3: Building graph.json ===")

# Assign colours - one hue per cluster
n_clusters = len(clusters_list)
cluster_colours = {}
for i, c in enumerate(clusters_list):
    hue = i / n_clusters
    r, g, b = colorsys.hls_to_rgb(hue, 0.5, 0.7)
    colour = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    cluster_colours[c["cluster_id"]] = colour

# Build tag -> cluster mapping
tag_to_cluster = {}
for c in clusters_list:
    for tag_id in c["tags"]:
        tag_to_cluster[tag_id] = c["cluster_id"]

# Build nodes
tag_lookup = {t["id"]: t for t in tags}
nodes = []
for t in tags:
    cid = tag_to_cluster.get(t["id"], "miscellaneous")
    nodes.append({
        "id": t["id"],
        "label": t["label"],
        "count": t["count"],
        "cluster_id": cid,
        "cluster_label": next((c["cluster_label"] for c in clusters_list if c["cluster_id"] == cid), "Miscellaneous"),
        "colour": cluster_colours.get(cid, "#999999")
    })

# Build edges: connect tags within same cluster
links = []
for c in clusters_list:
    cluster_tags = [tid for tid in c["tags"] if tid in tag_lookup]
    for i in range(len(cluster_tags)):
        for j in range(i+1, len(cluster_tags)):
            links.append({
                "source": cluster_tags[i],
                "target": cluster_tags[j],
                "weight": 1
            })

graph = {"nodes": nodes, "links": links}

with open("graph.json", "w") as f:
    json.dump(graph, f, indent=2)

print(f"Saved graph.json: {len(nodes)} nodes, {len(links)} links")

# Check for tags not assigned to any cluster
unassigned = [t["id"] for t in tags if t["id"] not in tag_to_cluster]
if unassigned:
    print(f"\nWarning: {len(unassigned)} tags not assigned to any cluster:")
    for tid in unassigned[:10]:
        print(f"  - {tid}")
    if len(unassigned) > 10:
        print(f"  ... and {len(unassigned)-10} more")
