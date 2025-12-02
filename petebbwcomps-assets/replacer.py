#!/usr/bin/env python3
"""
replacer.py

Usage:
  python replacer.py --temp temp.txt --videos videos.json

What it does:
- Reads `temp.txt` lines containing Mega file links like:
  https://mega.nz/file/ZJxnSSJD#lgR17tK_4c34...
- Parses out file id and token from each temp line.
- Loads `videos.json` (an array of objects) and for each entry whose
  `category` is not `Thumbnails`, replaces `url` with
  `https://mega.nz/embed/<fileid>#<token>` using the next temp URL.
- Writes a backup `videos.json.bak` before modifying and reports a summary.

It will not change entries with `category` == "Thumbnails".
"""

import re
import json
import argparse
from pathlib import Path

MEGA_RE = re.compile(r"https?://mega\.nz/(?:file|embed)/([^#/?]+)#(.+)$")


def normalize_token(token: str) -> str:
    """Normalize token for matching:
    - strip trailing '=' signs
    - convert '+' -> '-' and '/' -> '_' so temp and json forms match
    """
    if token is None:
        return ""
    t = token.rstrip("=")
    return t.replace("+", "-").replace("/", "_")


def parse_temp_file(temp_path):
    """Return a mapping normalized_token -> (fileid, original_token)
    This lets us match tokens from `videos.json` (which may use different
    characters like '+' or '/') to the temp file tokens (which use '-' and '_').
    """
    mapping = {}
    with open(temp_path, "r", encoding="utf-8") as f:
        for i, raw in enumerate(f, 1):
            line = raw.strip()
            if not line:
                continue
            m = MEGA_RE.search(line)
            if not m:
                print(f"[WARN] line {i}: couldn't parse Mega url: {line}")
                continue
            fileid, token = m.group(1), m.group(2)
            norm = normalize_token(token)
            mapping[norm] = (fileid, token)
    return mapping


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def replace_urls(videos, temp_map):
    """Replace only the file id on video entries whose token (after '#')
    matches a temp entry's token after normalization.

    temp_map: dict mapping normalized_token -> (fileid, original_token)
    """
    replaced = 0
    total_to_replace = 0

    for entry in videos:
        cat = entry.get("category", "")
        if isinstance(cat, str) and cat.lower() == "thumbnails":
            continue
        total_to_replace += 1

    for entry in videos:
        cat = entry.get("category", "")
        if isinstance(cat, str) and cat.lower() == "thumbnails":
            continue
        url = entry.get("url", "")
        m = MEGA_RE.search(url)
        if not m:
            continue
        vid_token = m.group(2)
        norm = normalize_token(vid_token)
        if norm in temp_map:
            fileid, token = temp_map[norm]
            entry["url"] = f"https://mega.nz/embed/{fileid}#{token}"
            replaced += 1
        else:
            # no matching temp entry for this token; leave unchanged
            continue

    return replaced, total_to_replace


def main():
    p = argparse.ArgumentParser(description="Replace video URLs in videos.json using temp.txt mappings")
    p.add_argument("--temp", default="temp.txt", help="Path to temp.txt with mega.nz/file links")
    p.add_argument("--videos", default="videos.json", help="Path to videos.json to update")
    p.add_argument("--backup", action="store_true", help="Create a backup copy videos.json.bak")
    args = p.parse_args()

    temp_path = Path(args.temp)
    videos_path = Path(args.videos)

    if not temp_path.exists():
        print(f"[ERROR] temp file not found: {temp_path}")
        return 2
    if not videos_path.exists():
        print(f"[ERROR] videos file not found: {videos_path}")
        return 2

    pairs = parse_temp_file(temp_path)
    if not pairs:
        print("[ERROR] no valid links parsed from temp file")
        return 3

    videos = load_json(videos_path)

    if args.backup:
        bak = videos_path.with_suffix(videos_path.suffix + ".bak")
        write_json(bak, videos)
        print(f"[INFO] backup written to: {bak}")

    replaced, total = replace_urls(videos, pairs)

    write_json(videos_path, videos)

    print(f"[DONE] replaced {replaced} URLs of {total} non-thumbnail entries using {len(pairs)} temp entries")
    if replaced < total:
        print("[WARN] not enough temp entries to replace all video URLs; remaining entries unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
