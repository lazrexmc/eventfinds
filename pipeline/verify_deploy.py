#!/usr/bin/env python
"""verify_deploy.py - does the origin serve what git holds?

Copied 2026-08-30 from the RapidForge `verify-deploy` code candidate (reference implementation:
the reference project's tools/verify_deploy.py, stdlib, 2026-08-29). EventFinds is its second
consumer. Only ORIGIN, the markers() walk, HEADER_MARKERS, the User-Agent and the hint text differ.

WHY. "Auto-deploys on push" is a sentence with no check; a Pages integration can die silently and
every push then "succeeds" into git only. Run this after every push that touches site/.

  python pipeline/verify_deploy.py
  python pipeline/verify_deploy.py --origin https://eventfinds.pages.dev
  python pipeline/verify_deploy.py --json

Exit 0 only when every marker is DEPLOYED. STALE = origin serves different bytes; MISSING = 404;
NO-LOCAL = the marker file is missing from the repo itself. Not in CI on purpose: a push is not yet a deploy, so CI would race it.
ASCII only in this file.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = "https://eventfinds.pages.dev"
# _headers is not served as a file; its effect is checked separately, via HEADER_MARKERS.
SKIP = {"_headers"}
HEADER_MARKERS = ["content-security-policy", "x-content-type-options", "referrer-policy"]


def markers(site_dir):
    """Every file under site_dir except the names in SKIP, sorted by relative path - so a fresh
    file under site/ is covered automatically instead of waiting on a hand-maintained list.
    Returns (local_rel, url_path) pairs; local_rel is always "site/<relpath>" (this tool's own
    on-disk naming), regardless of what site_dir itself is actually named, so a test can point
    this at a temp tree and still get back the site/... strings the rest of the script expects.
    index.html maps to the root URL "/"; every other file maps to "/<relpath>"."""
    site_dir = Path(site_dir)
    relpaths = sorted(
        p.relative_to(site_dir).as_posix()
        for p in site_dir.rglob("*")
        if p.is_file() and p.name not in SKIP
    )
    return [
        ("site/" + rel, "/" if rel == "index.html" else "/" + rel)
        for rel in relpaths
    ]


# Cloudflare Web Analytics injects exactly this tag into HTML responses at the edge (a zone setting,
# not a file in git). It is the one difference between git and the origin that is not drift.
_CF_BEACON = re.compile(rb"<script[^>]*static\.cloudflareinsights\.com/beacon\.min\.js[^>]*></script>")


def compare(local, remote):
    """DEPLOYED when the origin's bytes equal git's, ignoring line endings, whitespace runs and the
    edge-injected analytics tag (which also leaves a stray newline behind). Any other byte is STALE."""
    if remote is None:
        return "MISSING"
    norm = lambda b: re.sub(rb"\s+", b" ", _CF_BEACON.sub(b"", b.replace(b"\r\n", b"\n"))).strip()
    return "DEPLOYED" if norm(local) == norm(remote) else "STALE"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "eventfinds-verify-deploy/1.0",
                                               "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read(), {k.lower(): v for k, v in r.headers.items()}
    except urllib.error.HTTPError as e:
        return e.code, None, {}
    except Exception as e:
        return 0, None, {"error": "%s: %s" % (type(e).__name__, e)}


def local_bytes(path):
    """The repo's bytes for a marker, or None when the file does not exist locally - a verdict, not a crash."""
    p = Path(path)
    return p.read_bytes() if p.is_file() else None


def main():
    ap = argparse.ArgumentParser(description="compare local site/ files with what the origin serves")
    ap.add_argument("--origin", default=ORIGIN)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    origin = a.origin.rstrip("/")

    results = []
    for local_rel, path in markers(ROOT / "site"):
        local = local_bytes(ROOT / local_rel)
        if local is None:
            results.append({"file": local_rel, "url": origin + path, "http": None, "verdict": "NO-LOCAL"})
            continue
        status, body, _ = fetch(origin + path)
        verdict = compare(local, body if status == 200 else None)
        results.append({"file": local_rel, "url": origin + path, "http": status, "verdict": verdict})

    status, _, headers = fetch(origin + "/")
    for h in HEADER_MARKERS:
        present = h in headers
        results.append({"file": "site/_headers", "url": origin + "/", "http": status,
                        "verdict": "DEPLOYED" if present else "MISSING", "header": h})

    bad = [r for r in results if r["verdict"] != "DEPLOYED"]
    if a.json:
        print(json.dumps({"origin": origin, "results": results, "failed": len(bad)}, indent=2))
        return 1 if bad else 0

    print("\nDeploy check - local site/ vs %s\n" % origin)
    for r in results:
        label = r.get("header", r["file"])
        mark = "PASS" if r["verdict"] == "DEPLOYED" else "FAIL"
        print("  %s  %-44s %-9s HTTP %s" % (mark, label, r["verdict"], r["http"]))
    if bad:
        print("\n  %d marker(s) not deployed. The origin is NOT serving the pushed site/ - check" % len(bad))
        print("  Cloudflare Dashboard -> Workers & Pages -> eventfinds -> Deployments (failed build? integration gone?).\n")
        return 1
    print("\n  ALL DEPLOYED - the origin serves exactly what git holds.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
