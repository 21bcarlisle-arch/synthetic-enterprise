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


def test_stamp_latest_md_is_path_object():
    from pathlib import Path
    assert isinstance(stamp_latest_md.LATEST_MD, Path)


def test_stamp_second_call_advances_or_holds_timestamp(tmp_path, monkeypatch):
    import re, time
    from datetime import UTC, datetime
    latest_md = tmp_path / "LATEST.md"
    latest_md.write_text("Last updated: 2000-01-01T00:00:00Z\n", encoding="utf-8")
    monkeypatch.setattr(stamp_latest_md, "LATEST_MD", latest_md)
    stamp_latest_md.stamp()
    ts1_text = re.search(r"Last updated: (.+)", latest_md.read_text()).group(1)
    stamp_latest_md.stamp()
    ts2_text = re.search(r"Last updated: (.+)", latest_md.read_text()).group(1)
    ts1 = datetime.strptime(ts1_text, "%Y-%m-%dT%H:%M:%SZ")
    ts2 = datetime.strptime(ts2_text, "%Y-%m-%dT%H:%M:%SZ")
    assert ts2 >= ts1


def test_stamp_replaces_arbitrary_old_timestamp(tmp_path, monkeypatch):
    import re
    latest_md = tmp_path / "LATEST.md"
    latest_md.write_text("Last updated: 1990-06-15T12:34:56Z\n", encoding="utf-8")
    monkeypatch.setattr(stamp_latest_md, "LATEST_MD", latest_md)
    stamp_latest_md.stamp()
    text = latest_md.read_text(encoding="utf-8")
    assert "1990-06-15T12:34:56Z" not in text
    assert re.search(r"Last updated: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", text)


def test_stamp_preserves_non_updated_lines(tmp_path, monkeypatch):
    md = tmp_path / "LATEST.md"
    md.write_text("header\nLast updated: 2020-01-01T00:00:00Z\nbody line\n")
    monkeypatch.setattr(stamp_latest_md, "LATEST_MD", md)
    stamp_latest_md.stamp()
    assert "header" in md.read_text()
    assert "body line" in md.read_text()


def test_stamp_updates_last_updated_to_today(tmp_path, monkeypatch):
    import datetime
    md = tmp_path / "LATEST.md"
    md.write_text("Last updated: 2020-01-01T00:00:00Z\n")
    monkeypatch.setattr(stamp_latest_md, "LATEST_MD", md)
    stamp_latest_md.stamp()
    today = datetime.date.today().isoformat()
    assert today in md.read_text()


def test_stamp_function_returns_none(tmp_path, monkeypatch):
    md = tmp_path / "LATEST.md"
    md.write_text("Last updated: 2020-01-01T00:00:00Z\n")
    monkeypatch.setattr(stamp_latest_md, "LATEST_MD", md)
    result = stamp_latest_md.stamp()
    assert result is None
