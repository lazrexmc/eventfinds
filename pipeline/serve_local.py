"""serve_local.py - view site/ locally with production parity.

Correct MIME for .json (Windows registry entries can poison mimetypes into text/plain and serve a
silently blank page), Cache-Control: no-store so a re-export shows on refresh, and EVERY header
from site/_headers on every response - so the CSP is enforced here, not only in production.
Shape follows the EqualShares build's serve_local.py (RapidForge Build 001). Stdlib only.
ASCII only in this file.
"""
import functools
import sys
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

HOST = "127.0.0.1"
PORT = 8765
MIME = {
    ".json": "application/json; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".txt": "text/plain; charset=utf-8",
}


def log(msg=""):
    print("[%s] %s" % (datetime.now().strftime("%H:%M:%S"), msg))


def parse_site_headers(site_dir):
    """The /* block of site/_headers as [(name, value)] - one source of truth, no hand-kept copy."""
    headers = []
    hf = Path(site_dir) / "_headers"
    if not hf.exists():
        log("WARNING: site/_headers not found - serving WITHOUT the production security headers")
        return headers
    in_star = False
    for line in hf.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith((" ", "\t")):
            in_star = (stripped == "/*")
            continue
        if in_star and ":" in stripped:
            name, _, value = stripped.partition(":")
            headers.append((name.strip(), value.strip()))
    return headers


SECURITY_HEADERS = []


class SiteHandler(SimpleHTTPRequestHandler):
    def guess_type(self, path):
        ext = Path(str(path)).suffix.lower()
        return MIME.get(ext) or super().guess_type(path)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        for name, value in SECURITY_HEADERS:
            self.send_header(name, value)
        super().end_headers()

    def log_message(self, fmt, *args):
        log("%s %s" % (self.address_string(), fmt % args))


def main():
    site = config.SITE_DIR
    if not site.is_dir():
        log("ERROR: site directory not found: %s" % site)
        return 1
    if not (site / "data" / "meta.json").exists():
        log("note: site/data/meta.json is missing - the page will show its error box until export.py runs")
    SECURITY_HEADERS.extend(parse_site_headers(site))
    log("serving %d security header(s) from site/_headers on every response" % len(SECURITY_HEADERS))
    handler = functools.partial(SiteHandler, directory=str(site))
    try:
        httpd = ThreadingHTTPServer((HOST, PORT), handler)
    except OSError as e:
        log("ERROR: cannot bind %s:%d (%s) - is another serve_local.py running?" % (HOST, PORT, e))
        return 1
    log("serving %s" % site)
    log("open  http://%s:%d/   (Ctrl+C to stop)" % (HOST, PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        log("stopped")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
