import re

import tools.stamp_latest_md as stamp_latest_md


def test_stamp_rewrites_last_updated_line(tmp_path, monkeypatch):
    latest_md = tmp_path / "LATEST.md"
    latest_md.write_text(
        "# Latest Status\n\nLast updated: 2020-01-01T00:00:00Z\n\nBody text.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(stamp_latest_md, "LATEST_MD", latest_md)

    stamp_latest_md.stamp()

    text = latest_md.read_text(encoding="utf-8")
    match = re.search(r"^Last updated: (.+)$", text, flags=re.MULTILINE)
    assert match is not None
    assert match.group(1) != "2020-01-01T00:00:00Z"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", match.group(1))
    assert "Body text." in text


def test_stamp_raises_without_last_updated_line(tmp_path, monkeypatch):
    latest_md = tmp_path / "LATEST.md"
    latest_md.write_text("# No timestamp line here\n", encoding="utf-8")
    monkeypatch.setattr(stamp_latest_md, "LATEST_MD", latest_md)

    try:
        stamp_latest_md.stamp()
        raised = False
    except ValueError:
        raised = True
    assert raised
