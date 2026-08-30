"""config.py - the per-deployment settings. ONE home per deployment (spec decision 5)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVENTS_CSV = ROOT / "data" / "events.csv"
PLACES_CSV = ROOT / "data" / "places.csv"
SITE_DIR = ROOT / "site"
SITE_DATA = SITE_DIR / "data"

HOME = {"name": "Columbia, MO", "lat": 38.9517, "lng": -92.3341}
STALE_DAYS = 60          # a published row dated further in the past than this is WARNED about
PIPELINE_VERSION = "1"   # bump when the export contract changes
