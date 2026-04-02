#!/usr/bin/env python3
"""
Build graph.json with 10 Communities of Practice (COPs).
No API key required — clusters curated by semantic analysis.
"""

import json

# Load tags
with open("tags.json") as f:
    tags = json.load(f)

tag_ids = {t["id"] for t in tags}
print(f"Loaded {len(tags)} tags")

# ── 10 Communities of Practice ────────────────────────────────────────────────

cops_raw = {
    "cop01": {
        "label": "COP 01 — Film & Moving Image",
        "short": "Film & Moving Image",
        "tags": [
            "film", "documentary", "animation", "cinematography", "video",
            "music-video", "short-film", "stop-motion", "cinema", "fashion-film",
            "experimental-film", "16mm-film", "celluloid-film", "film-making",
            "filmmaking", "directing", "title-sequences", "video-essay", "editing",
            "montage", "documentary-style-cinematography", "visual-effects",
            "effects", "cinematic", "visual-storytelling", "anime",
            # merged: photography & image-making
            "photography", "film-photography", "image-making", "images",
            "portraits", "portrait", "lensless", "black-and-white", "imagery",
            # merged: music & sound
            "music", "sound", "soundtrack", "radio", "album", "sampling",
            "rhythm", "broadcasting", "podcast", "dance",
        ]
    },
    "cop02": {
        "label": "COP 02 — Typography & Publication",
        "short": "Typography & Publication",
        "tags": [
            # typography
            "typography", "kinetic-typography", "typograhy", "type",
            "letterpress", "grids", "layout", "filmtypography",
            # publication & print
            "publication", "book", "books", "magazine", "publishing", "print",
            "posters", "editorial", "printmaking", "essay", "article",
            "manuals", "comics", "risograph", "reading",
        ]
    },
    "cop03": {
        "label": "COP 03 — Branding & Identity Design",
        "short": "Branding & Identity Design",
        "tags": [
            "branding", "brand", "brand-identity", "brand-dsign",
            "brand-ecosystem", "brand-narrtive", "brand-strategy",
            "branding-and-identity", "visual-identity", "visual-identities",
            "identity-design", "dynamic-identity", "spatial-identity",
            "logos", "logo", "corporate", "non-corporate",
            # advertising & marketing
            "advertising", "advert", "advertisement", "marketing",
            "campaign", "commercial", "viral", "influence",
            # flags & symbols
            "flag-design", "flag", "vexillography", "pictogram", "pictograms",
        ]
    },
    "cop04": {
        "label": "COP 04 — Digital & Interactive",
        "short": "Digital & Interactive",
        "tags": [
            # digital & web
            "digital", "website", "website-design", "web-design",
            "digital-design", "digital-age", "internet", "ui", "ux",
            "creative-computing", "social-media",
            # interactive & immersive
            "interactive", "interaction", "immersive", "immersion",
            "game", "game-design", "gaming", "videogame", "play",
            "multisensory", "projection",
            # technology
            "technology", "ai", "glitch",
        ]
    },
    "cop05": {
        "label": "COP 05 — Data & Information Design",
        "short": "Data & Information Design",
        "tags": [
            "data-visualisation", "data", "diagram", "diagramming",
            "information-design", "information", "infographics", "inforgraphic",
            "visualisation", "map", "maps", "mapping",
            "system", "systems", "design-systems",
        ]
    },
    "cop06": {
        "label": "COP 06 — Space, Place & Wayfinding",
        "short": "Space, Place & Wayfinding",
        "tags": [
            "space", "wayfinding", "way-finding", "navigation", "architecture",
            "place", "placeness", "non-place", "signs", "signages",
            "environmental-design", "spatial-design", "city", "cities",
            "cityscape", "transport", "london", "dérive", "psychogeography",
            # packaging & objects
            "packaging", "object", "objects", "boxes", "box",
            "installation", "set-design", "exhibition-design",
            "museum", "museums", "natural-history-museum",
        ]
    },
    "cop07": {
        "label": "COP 07 — Narrative & Storytelling",
        "short": "Narrative & Storytelling",
        "tags": [
            "storytelling", "narrative", "narrative-and-voice", "metaphor",
            "symbolism", "symbols", "semiotics", "writing", "literature",
            "poetry", "drama", "comedy", "horror", "fantasy", "sci-fi",
            "scifi", "coming-of-age", "dystopian", "tragedy", "adventure",
            "action", "world-building", "worldbuilding", "irony", "iconography",
            "folklore", "dreamlike", "surrealism",
        ]
    },
    "cop08": {
        "label": "COP 08 — Culture, History & Society",
        "short": "Culture, History & Society",
        "tags": [
            # culture & history
            "culture", "history", "historical", "art-history", "design-history",
            "heritage", "archive", "collections", "legacy-media",
            "modernism", "vernacular-design", "frutiger-aero", "retro",
            "historical-fiction",
            # society & politics
            "politics", "political", "feminism", "cyberfeminism", "facism",
            "society", "social-structures", "social-commentary", "protest",
            "resistance", "war", "conflict", "power", "capitalism",
            "consumerism", "consumer", "consumer-behaviour", "representation",
            "decolonisation", "design-activism", "ethics", "design-ethics",
            "fake-news", "control",
            # cultural geography
            "japanese", "japan", "middle-east", "food", "fashion",
            "curation",
        ]
    },
    "cop09": {
        "label": "COP 09 — Psychology & Human Experience",
        "short": "Psychology & Human Experience",
        "tags": [
            "psychology", "emotion", "emotional", "emotional-design",
            "color-psychology", "empathy", "perception", "memory", "memories",
            "nostalgia", "consciousness", "the-subconscious", "phenomenology",
            "human-experience", "human-connection", "intimacy", "relationship",
            "relationships", "connection", "connections", "attention-span",
            "functionality-and-emotion", "uncanny", "dreamlike", "reflection",
            "imperfection", "stillness", "focus", "observation",
            # identity & community
            "identity", "community", "people", "humanity", "family",
            "home", "life", "death", "survival", "growth", "perspectives",
            "realities",
            # nature & environment
            "nature", "environment", "environmental", "ecology",
            "climate-change", "sustainability", "animals", "more-than-human",
            "recycle",
        ]
    },
    "cop10": {
        "label": "COP 10 — Design Practice & Theory",
        "short": "Design Practice & Theory",
        "tags": [
            "design", "graphic-design", "design-process", "design-principles",
            "design-philosophy", "design-strategy", "design-approach",
            "contemporary-design", "speculative-design", "speculative",
            "speculativedesign", "experience-design", "functional-design",
            "universal-design", "playful-design", "3d-design", "3d",
            "theory", "philosophy", "critical-thinking", "process",
            "framework", "strategy", "research", "creativity", "collaboration",
            "multidisciplinary", "professional-practice", "techniques",
            "simplicity", "scale", "construction-parameters", "designer-as",
            "project", "participatory-design", "inclusive-design", "visual-design",
            # art & fine art
            "art", "painting", "sculpture", "drawing", "collage",
            "digital-collage", "graffiti", "street-art", "art-direction",
            "art-project", "artist", "artistic-practice", "expressionist",
            "ornament", "mixmedia", "performance",
            # remaining technology & media
            "media", "analogue", "analogue-methods", "physical",
            "physical-process", "material", "pattern", "repetition",
            "colour", "color", "visual", "visuals", "visual-communication",
            "visual-culture",
            # futures
            "future", "futures", "time-and-movement", "motion",
            "science", "scientific",
            # misc
            "communication", "accessibility", "experience", "experimental",
            "illustration", "language",
        ]
    },
}

# ── COP palette (matching alluvial config.js) ─────────────────────────────

cop_colours = {
    "cop01": "#E8763A",   # warm orange
    "cop02": "#3AABE8",   # cool blue
    "cop03": "#E8C93A",   # warm yellow
    "cop04": "#3AE89B",   # cool green
    "cop05": "#C73AE8",   # purple
    "cop06": "#E85A5A",   # red
    "cop07": "#5AE8C4",   # teal
    "cop08": "#E8A63A",   # amber
    "cop09": "#5A8AE8",   # blue
    "cop10": "#D4E85A",   # lime
}

# ── Validate & build clusters ─────────────────────────────────────────────

assigned = set()
clusters_list = []

for cid, cdata in cops_raw.items():
    valid_tags = [t for t in cdata["tags"] if t in tag_ids]
    assigned.update(valid_tags)
    clusters_list.append({
        "cluster_id": cid,
        "cluster_label": cdata["label"],
        "cluster_short": cdata["short"],
        "tags": valid_tags
    })

# Any unassigned → COP 10
unassigned = tag_ids - assigned
if unassigned:
    print(f"Note: {len(unassigned)} tags added to COP 10:")
    for uid in sorted(unassigned):
        print(f"  - {uid}")
    clusters_list[-1]["tags"].extend(sorted(unassigned))

clusters_list = [c for c in clusters_list if len(c["tags"]) > 0]

with open("clusters.json", "w") as f:
    json.dump(clusters_list, f, indent=2)

print(f"\nSaved clusters.json with {len(clusters_list)} COPs")
for c in clusters_list:
    print(f"  {c['cluster_label']:45s} {len(c['tags']):3d} tags")

# ── Build graph.json ──────────────────────────────────────────────────────

tag_to_cluster = {}
for c in clusters_list:
    for tag_id in c["tags"]:
        tag_to_cluster[tag_id] = c["cluster_id"]

cluster_label_lookup = {c["cluster_id"]: c["cluster_label"] for c in clusters_list}
cluster_short_lookup = {c["cluster_id"]: c["cluster_short"] for c in clusters_list}
tag_lookup = {t["id"]: t for t in tags}

nodes = []
for t in tags:
    cid = tag_to_cluster.get(t["id"], "cop10")
    nodes.append({
        "id": t["id"],
        "label": t["label"],
        "count": t["count"],
        "cluster_id": cid,
        "cluster_label": cluster_label_lookup.get(cid, "COP 10"),
        "cluster_short": cluster_short_lookup.get(cid, "Design Practice & Theory"),
        "colour": cop_colours.get(cid, "#999999")
    })

# Build edges — hub + chain topology for large clusters
MAX_HUBS = 3
links = []
for c in clusters_list:
    cluster_tags = [tid for tid in c["tags"] if tid in tag_lookup]
    cluster_tags.sort(key=lambda t: tag_lookup[t]["count"], reverse=True)

    if len(cluster_tags) <= 9:
        for i in range(len(cluster_tags)):
            for j in range(i + 1, len(cluster_tags)):
                links.append({"source": cluster_tags[i], "target": cluster_tags[j], "weight": 1})
    else:
        hubs = cluster_tags[:MAX_HUBS]
        for tag in cluster_tags:
            for hub in hubs:
                if tag != hub:
                    links.append({"source": hub, "target": tag, "weight": 1})
        for i in range(len(cluster_tags) - 1):
            links.append({"source": cluster_tags[i], "target": cluster_tags[i + 1], "weight": 1})

# Deduplicate
seen = set()
unique_links = []
for link in links:
    key = tuple(sorted([link["source"], link["target"]]))
    if key not in seen:
        seen.add(key)
        unique_links.append(link)

graph = {"nodes": nodes, "links": unique_links}

with open("graph.json", "w") as f:
    json.dump(graph, f, indent=2)

print(f"\nSaved graph.json: {len(nodes)} nodes, {len(unique_links)} links")

unassigned_final = [t["id"] for t in tags if t["id"] not in tag_to_cluster]
if unassigned_final:
    print(f"\n⚠ {len(unassigned_final)} tags not in any COP")
else:
    print(f"✓ All {len(tags)} tags assigned")
