import csv
import re

from assign_ids import assign_ids
from model import COLUMNS, UUID4_RE

HEADER = ",".join(COLUMNS)


def test_blank_ids_get_uuid4_and_existing_ids_survive(tmp_path):
    p = tmp_path / "events.csv"
    p.write_text(
        HEADER + "\n"
        + "11111111-1111-4111-8111-111111111111,Keep Me,festival,annual,Columbia,MO,,,,,,,,,,,draft,\n"
        + ",New One,festival,annual,Columbia,MO,,,,,,,,,,,draft,\n",
        encoding="utf-8")
    assert assign_ids(p) == 1
    with open(p, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["id"] == "11111111-1111-4111-8111-111111111111"
    assert UUID4_RE.match(rows[1]["id"])
    assert rows[1]["name"] == "New One"
    assert p.read_bytes().count(b"\r\n") == 0
    assert assign_ids(p) == 0            # idempotent


def test_header_only_file_is_left_alone(tmp_path):
    p = tmp_path / "events.csv"
    p.write_text(HEADER + "\n", encoding="utf-8")
    assert assign_ids(p) == 0
    assert p.read_text(encoding="utf-8") == HEADER + "\n"
