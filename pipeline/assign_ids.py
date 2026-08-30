"""assign_ids.py - give every row a permanent id, once.

Identity is a UUID4 assigned here and never derived from position (a spreadsheet row inserted in
the middle must not renumber anything). Run after adding rows; the export refuses a blank id.
ASCII only in this file.
"""
import argparse
import csv
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config                      # noqa: E402
from model import validate_header  # noqa: E402


def assign_ids(csv_path):
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        validate_header(reader.fieldnames)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)
    assigned = 0
    for r in rows:
        if r.get("id") is None or r["id"].strip() == "":
            r["id"] = str(uuid.uuid4())
            assigned += 1
    if assigned:
        with open(csv_path, "w", encoding="utf-8", newline="\n") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    return assigned


def main(argv=None):
    ap = argparse.ArgumentParser(description="fill blank id cells in the events CSV with UUID4s")
    ap.add_argument("--csv", default=str(config.EVENTS_CSV))
    a = ap.parse_args(argv)
    n = assign_ids(Path(a.csv))
    print("assigned %d id(s) in %s" % (n, a.csv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
