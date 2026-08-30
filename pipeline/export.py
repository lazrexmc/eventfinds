"""export.py - data/events.csv -> site/data/events.json + meta.json.

THE PUBLISH GATE LIVES HERE, ONCE: is_published(). The page carries no copy of it (gate G6).
Failure is not emptiness: any defect exits 1 naming the row; a genuinely empty directory exports
honestly as event_count 0. Deterministic: same inputs -> byte-identical output except generated_at.
ASCII only in this file.
"""
import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config                                              # noqa: E402
from geocode import UnknownPlace, geocode, load_places     # noqa: E402
from model import ValidationError, slugify, validate_header, validate_row  # noqa: E402

EVENT_KEYS = (
    "id", "slug", "name", "event_type", "cadence", "city", "state", "county", "lat", "lng",
    "start_date", "end_date", "months", "dates_text", "attendance_text", "homepage_url",
    "source_url", "description", "last_verified", "featured",
)


def is_published(row):
    """THE publish gate. A row is public iff a human set visibility to published."""
    return row["visibility"] == "published"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_rows(csv_path):
    """Validate every row; add slug; enforce unique id and unique slug. Raises ValidationError."""
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        validate_header(reader.fieldnames)
        rows = [validate_row(raw, n) for n, raw in enumerate(reader, start=2)]
    seen_id, seen_slug = {}, {}
    for n, r in enumerate(rows, start=2):
        r["slug"] = slugify(r["name"], r["city"], r["state"])
        if r["id"] in seen_id:
            raise ValidationError("line %d: duplicate id %s (also line %d)" % (n, r["id"], seen_id[r["id"]]))
        if r["slug"] in seen_slug:
            raise ValidationError("line %d: duplicate slug %s (also line %d)" % (n, r["slug"], seen_slug[r["slug"]]))
        seen_id[r["id"]] = n
        seen_slug[r["slug"]] = n
    return rows


def build(rows, places, home, generated_at, source_sha256, today):
    """Returns (events_doc, meta, stale_warnings). Raises UnknownPlace for a published row whose
    (city, state) the places table lacks. Only published rows are geocoded or exported."""
    published = [r for r in rows if is_published(r)]
    coords = geocode(published, places)
    events = []
    for r in published:
        lat, lng = coords[r["id"]]
        e = {k: r[k] for k in EVENT_KEYS if k not in ("lat", "lng")}
        e["lat"], e["lng"] = lat, lng
        events.append(e)
    events.sort(key=lambda e: e["slug"])
    stale = []
    for e in events:
        last = e["end_date"] or e["start_date"]
        if last and (today - date.fromisoformat(last)).days > config.STALE_DAYS:
            stale.append((e["slug"], last))
    verified = [e["last_verified"] for e in events if e["last_verified"]]
    meta = {
        "generated_at": generated_at,
        "as_of": max(verified) if verified else None,
        "event_count": len(events),
        "home": dict(home),
        "event_types": sorted({e["event_type"] for e in events}),
        "source_sha256": source_sha256,
        "pipeline_version": config.PIPELINE_VERSION,
    }
    return {"events": events}, meta, stale


def _dump_atomic(path, obj):
    """Write to <name>.tmp in the same directory, then os.replace() it into place - a crash or a
    later failure in this same run never leaves a half-written file at the real path."""
    text = json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)
    return len(text.encode("utf-8"))


def write_publication(out_dir, events_doc, meta):
    """meta.json FIRST, then events.json - so a failure partway through never leaves a new events
    list published beside an old meta (or vice versa) as a mismatched pair."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    _dump_atomic(out_dir / "meta.json", meta)
    _dump_atomic(out_dir / "events.json", events_doc)


def main(argv=None):
    ap = argparse.ArgumentParser(description="export the events CSV to static JSON")
    ap.add_argument("--csv", default=str(config.EVENTS_CSV))
    ap.add_argument("--places", default=str(config.PLACES_CSV))
    ap.add_argument("--out", default=str(config.SITE_DATA))
    ap.add_argument("--today", default=None, help="YYYY-MM-DD; default = today (for the stale warning)")
    a = ap.parse_args(argv)
    try:
        today = date.fromisoformat(a.today) if a.today else date.today()
        rows = read_rows(a.csv)
        places = load_places(a.places)
        events_doc, meta, stale = build(
            rows, places, config.HOME,
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
            sha256_file(a.csv), today)
        write_publication(a.out, events_doc, meta)
    except (ValidationError, UnknownPlace, ValueError, OSError) as e:
        print("ERROR: %s" % e)
        return 1
    for slug, last in stale:
        print("WARN stale: %s (%s)" % (slug, last))
    print("exported %d event(s) -> %s  (as_of=%s, types=%d)"
          % (meta["event_count"], a.out, meta["as_of"], len(meta["event_types"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
