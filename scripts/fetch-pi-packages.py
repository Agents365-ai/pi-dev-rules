#!/usr/bin/env python3
"""Fetch the complete Pi package gallery and write a queryable manifest.

The pi.dev/packages gallery is backed by the npm registry keyword `pi-package`
(pi.dev's own /api routes are disabled). This paginates the npm search API and
writes references/pi-packages.csv (one row per package, sorted by monthly
downloads). Re-run to refresh; the list changes daily.

Usage: python3 scripts/fetch-pi-packages.py [output.csv]
"""

import csv
import json
import os
import sys
import time
import urllib.request

SEARCH = "https://registry.npmjs.org/-/v1/search?text=keywords:pi-package&size={size}&from={frm}"
PAGE = 250  # npm search hard cap per request
OUT = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "references",
        "pi-packages.csv",
    )
)


def classify(keywords, description):
    """Best-effort type from keywords/description (gallery categories:
    extension / skill / theme / prompt / package)."""
    kw = {k.lower() for k in keywords}
    desc = (description or "").lower()
    if "pi-theme" in kw or "theme" in kw:
        return "theme"
    if "pi-skill" in kw or "skill" in kw or "agent-skill" in kw or "skills" in kw:
        return "skill"
    if "pi-prompt" in kw or "prompt-template" in kw or "prompt" in kw:
        return "prompt"
    if "pi-extension" in kw or "extension" in kw:
        return "extension"
    if "skill" in desc and "extension" not in desc:
        return "skill"
    return "package"


def fetch_all():
    rows, total, frm = [], None, 0
    while total is None or frm < total:
        url = SEARCH.format(size=PAGE, frm=frm)
        data = None  # bound by the loop below (always breaks or raises)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url, timeout=30) as r:
                    data = json.load(r)
                break
            except Exception:  # noqa: BLE001 - transient network/registry errors
                if attempt == 3:
                    raise
                time.sleep(2 * (attempt + 1))
        assert data is not None  # loop above always breaks (success) or raises
        total = data["total"]
        objs = data.get("objects", [])
        if not objs:
            break
        for o in objs:
            p = o.get("package", {})
            rows.append(
                {
                    "name": p.get("name", ""),
                    "type": classify(p.get("keywords", []), p.get("description", "")),
                    "downloads_monthly": (o.get("downloads") or {}).get("monthly", 0),
                    "version": p.get("version", ""),
                    "author": (p.get("maintainers") or [{}])[0].get("username", ""),
                    "description": (p.get("description", "") or "")
                    .replace("\n", " ")
                    .strip(),
                    "install": f"pi install npm:{p.get('name', '')}",
                    "repository": (p.get("links") or {}).get("repository", ""),
                    "npm": (p.get("links") or {}).get("npm", ""),
                    "updated": (p.get("date", "") or "")[:10],
                }
            )
        frm += len(objs)
        print(f"  fetched {frm}/{total}", file=sys.stderr)
        time.sleep(0.15)
    # npm search overlaps pages, so dedupe by package name before ranking.
    seen = {}
    for r in rows:
        seen.setdefault(r["name"], r)
    rows = list(seen.values())
    rows.sort(key=lambda r: r["downloads_monthly"], reverse=True)
    return rows, total


def main():
    print(
        "Fetching Pi package gallery from npm (keyword: pi-package)...", file=sys.stderr
    )
    rows, total = fetch_all()
    cols = [
        "name",
        "type",
        "downloads_monthly",
        "version",
        "author",
        "description",
        "install",
        "repository",
        "npm",
        "updated",
    ]
    try:
        with open(OUT, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
    except OSError as e:
        raise SystemExit(f"failed to write {OUT}: {e}")
    from collections import Counter

    by_type = Counter(r["type"] for r in rows)
    print(
        f"\nWrote {len(rows)} packages (registry total: {total}) -> {OUT}",
        file=sys.stderr,
    )
    print(
        "By type: " + ", ".join(f"{k}={v}" for k, v in by_type.most_common()),
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
