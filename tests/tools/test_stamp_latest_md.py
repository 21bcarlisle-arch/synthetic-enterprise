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


def test_stamp_preserves_rest_of_file(tmp_path, monkeypatch):
    latest_md = tmp_path / "LATEST.md"
    content = "# Title\n\nLast updated: 2020-01-01T00:00:00Z\n\nTrailing paragraph.\n"
    latest_md.write_text(content, encoding="utf-8")
    monkeypatch.setattr(stamp_latest_md, "LATEST_MD", latest_md)
    stamp_latest_md.stamp()
    text = latest_md.read_text(encoding="utf-8")
    assert "# Title" in text
    assert "Trailing paragraph." in text


def test_stamp_only_replaces_one_line(tmp_path, monkeypatch):
    """Two 'Last updated:' lines — only first is replaced (count=1)."""
    latest_md = tmp_path / "LATEST.md"
    latest_md.write_text(
        "Last updated: 2020-01-01T00:00:00Z\n\nLast updated: 2019-01-01T00:00:00Z\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(stamp_latest_md, "LATEST_MD", latest_md)
    stamp_latest_md.stamp()
    text = latest_md.read_text(encoding="utf-8")
    # Original second line is untouched
    assert "2019-01-01T00:00:00Z" in text


def test_stamp_timestamp_is_utc_zulu(tmp_path, monkeypatch):
    """Generated timestamp ends with Z (Zulu / UTC)."""
    latest_md = tmp_path / "LATEST.md"
    latest_md.write_text("Last updated: 2020-01-01T00:00:00Z\n", encoding="utf-8")
    monkeypatch.setattr(stamp_latest_md, "LATEST_MD", latest_md)
    stamp_latest_md.stamp()
    text = latest_md.read_text(encoding="utf-8")
    import re
    match = re.search(r"Last updated: (.+)", text)
    assert match.group(1).endswith("Z")


def test_stamp_raises_on_empty_file(tmp_path, monkeypatch):
    latest_md = tmp_path / "LATEST.md"
    latest_md.write_text("", encoding="utf-8")
    monkeypatch.setattr(stamp_latest_md, "LATEST_MD", latest_md)
    raised = False
    try:
        stamp_latest_md.stamp()
    except ValueError:
        raised = True
    assert raised


def test_stamp_latest_md_module_has_correct_path():
    from pathlib import Path
    p = stamp_latest_md.LATEST_MD
    assert str(p).endswith("LATEST.md")
    assert "docs" in str(p) or "status" in str(p)


def test_stamp_writes_utc_not_local(tmp_path, monkeypatch):
    """Timestamp produced by stamp() uses UTC, not local time."""
    import re
    from datetime import UTC, datetime
    latest_md = tmp_path / "LATEST.md"
    latest_md.write_text("Last updated: 2000-01-01T00:00:00Z\n", encoding="utf-8")
    monkeypatch.setattr(stamp_latest_md, "LATEST_MD", latest_md)
    from datetime import timedelta
    before = datetime.now(UTC).replace(microsecond=0)
    stamp_latest_md.stamp()
    after = datetime.now(UTC).replace(microsecond=0) + timedelta(seconds=1)
    text = latest_md.read_text(encoding="utf-8")
    match = re.search(r"Last updated: (.+)", text)
    ts = datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    assert before <= ts <= after
