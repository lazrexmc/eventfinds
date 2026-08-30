import verify_deploy as vd


def test_compare_verdicts():
    assert vd.compare(b"a\nb", b"a\nb") == "DEPLOYED"
    assert vd.compare(b"a\nb", b"a\r\nb") == "DEPLOYED"          # line endings are not drift
    assert vd.compare(b"a\nb", None) == "MISSING"
    assert vd.compare(b"a\nb", b"a\nc") == "STALE"
    injected = b"<html><script defer src=\"https://static.cloudflareinsights.com/beacon.min.js\" data-cf-beacon='{}'></script>\n</html>"
    assert vd.compare(b"<html>\n</html>", injected) == "DEPLOYED"  # edge-injected analytics tag is not drift


def test_markers_cover_the_publication_and_the_page():
    files = [m[0] for m in vd.MARKERS if m[1] is not None]
    assert "site/data/events.json" in files and "site/data/meta.json" in files
    assert "site/index.html" in files and "site/js/app.js" in files
    assert vd.ORIGIN == "https://eventfinds.pages.dev"
