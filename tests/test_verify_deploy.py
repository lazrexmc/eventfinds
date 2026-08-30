import verify_deploy as vd


def test_compare_verdicts():
    assert vd.compare(b"a\nb", b"a\nb") == "DEPLOYED"
    assert vd.compare(b"a\nb", b"a\r\nb") == "DEPLOYED"          # line endings are not drift
    assert vd.compare(b"a\nb", None) == "MISSING"
    assert vd.compare(b"a\nb", b"a\nc") == "STALE"
    injected = b"<html><script defer src=\"https://static.cloudflareinsights.com/beacon.min.js\" data-cf-beacon='{}'></script>\n</html>"
    assert vd.compare(b"<html>\n</html>", injected) == "DEPLOYED"  # edge-injected analytics tag is not drift


def test_markers_walks_a_temp_tree_and_skips_headers(tmp_path):
    site = tmp_path / "some_dir_name"
    site.mkdir()
    (site / "index.html").write_text("<html></html>", encoding="utf-8")
    (site / "_headers").write_text("/*\n", encoding="utf-8")
    (site / "js").mkdir()
    (site / "js" / "app.js").write_text("export {};", encoding="utf-8")
    (site / "data").mkdir()
    (site / "data" / "events.json").write_text("{}", encoding="utf-8")

    assert vd.markers(site) == [
        ("site/data/events.json", "/data/events.json"),
        ("site/index.html", "/"),
        ("site/js/app.js", "/js/app.js"),
    ]


def test_markers_cover_the_publication_and_the_page():
    files = [m[0] for m in vd.markers(vd.ROOT / "site")]
    assert "site/data/events.json" in files and "site/data/meta.json" in files
    assert "site/js/app.js" in files
    assert "site/assets/vendor/leaflet/leaflet.markercluster.js" in files
    assert vd.ORIGIN == "https://eventfinds.pages.dev"


def test_local_bytes_is_none_for_a_missing_marker(tmp_path):
    assert vd.local_bytes(tmp_path / "nope.js") is None
    f = tmp_path / "x.js"
    f.write_bytes(b"abc")
    assert vd.local_bytes(f) == b"abc"
