"""geocode.py - city-centroid geocoding from data/places.csv, the ONE table.

Pins mark the city, not the venue (the page says so). Same-city rows get a deterministic ring
offset (~300 m) so they do not overlap. A (city, state) the table lacks FAILS the export by name -
it is never silently absent from the map.
ASCII only in this file.
"""
import csv
import math
from collections import OrderedDict

from model import slugify

PLACES_HEADER = ["city", "state", "lat", "lng"]
RING_DEG = 0.0035   # ~300-400 m


class UnknownPlace(Exception):
    """One or more (city, state) pairs are not in the places table. Message names them all."""


def load_places(path):
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if list(reader.fieldnames or []) != PLACES_HEADER:
            raise ValueError("%s: header must be city,state,lat,lng" % path)
        places = {}
        for n, r in enumerate(reader, start=2):
            key = (r["city"].strip(), r["state"].strip())
            if key in places:
                raise ValueError("%s line %d: duplicate place %s, %s" % (path, n, key[0], key[1]))
            try:
                places[key] = (float(r["lat"]), float(r["lng"]))
            except (TypeError, ValueError):
                raise ValueError("%s line %d: lat/lng not numeric for %s, %s"
                                 % (path, n, key[0], key[1]))
    return places


def ring_offset(lat, lng, idx, n):
    if n <= 1:
        return (lat, lng)
    ang = 2.0 * math.pi * idx / n
    return (lat + RING_DEG * math.cos(ang), lng + RING_DEG * math.sin(ang))


def geocode(rows, places):
    """rows: iterable of typed rows (id, name, city, state). Returns {id: (lat, lng)} rounded 5 dp.
    Raises UnknownPlace listing every missing town with its rows' slugs."""
    groups = OrderedDict()
    for r in rows:
        groups.setdefault((r["city"], r["state"]), []).append(r)
    missing = []
    for (city, state), group in groups.items():
        if (city, state) not in places:
            slugs = ", ".join(slugify(r["name"], r["city"], r["state"]) for r in group)
            missing.append("%s, %s (%d row%s: %s)" % (city, state, len(group),
                                                       "" if len(group) == 1 else "s", slugs))
    if missing:
        raise UnknownPlace("unknown place(s) - add them to data/places.csv: "
                           + "; ".join(missing))
    out = {}
    for (city, state), group in groups.items():
        lat0, lng0 = places[(city, state)]
        for idx, r in enumerate(group):
            lat, lng = ring_offset(lat0, lng0, idx, len(group))
            out[r["id"]] = (round(lat, 5), round(lng, 5))
    return out
