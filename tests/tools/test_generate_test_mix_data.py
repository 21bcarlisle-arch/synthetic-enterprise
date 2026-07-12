"""Tests for tools/generate_test_mix_data.py.

Director page comments (/project/, 2026-07-12): "so what... velocity and
depth?" / "show the mix of tests... scope of what we are testing".
"""
import json

import pytest

from tools.generate_test_mix_data import _collect_count, compute_test_mix, generate


def _write_test_file(path, n_tests):
    path.write_text(
        "\n".join("def test_{}():\n    assert True\n".format(i) for i in range(n_tests))
    )


def test_collect_count_real_pytest_collection(tmp_path):
    _write_test_file(tmp_path / "test_sample.py", 5)
    assert _collect_count(tmp_path) == 5


def test_collect_count_zero_for_empty_directory(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    assert _collect_count(empty) == 0


def test_compute_test_mix_expands_company_one_level_deeper(tmp_path, monkeypatch):
    import tools.generate_test_mix_data as mod

    monkeypatch.setattr(mod, "TESTS_DIR", tmp_path)
    (tmp_path / "background").mkdir()
    _write_test_file(tmp_path / "background" / "test_a.py", 3)
    (tmp_path / "company").mkdir()
    (tmp_path / "company" / "billing").mkdir()
    _write_test_file(tmp_path / "company" / "billing" / "test_b.py", 4)
    (tmp_path / "company" / "crm").mkdir()
    _write_test_file(tmp_path / "company" / "crm" / "test_c.py", 2)

    result = compute_test_mix()
    names = {a["name"] for a in result["areas"]}
    assert "background" in names, "non-company top-level dirs stay as one area"
    assert "company/billing" in names, "company/ subdirs are expanded, prefixed with company/"
    assert "company/crm" in names
    assert "company" not in names, "company itself must not ALSO appear as a flat bucket"
    assert result["total"] == 3 + 4 + 2


def test_compute_test_mix_counts_loose_files_inside_expanded_directory(tmp_path, monkeypatch):
    """Real bug found 2026-07-12: loose *.py test files directly inside an
    expanded directory (e.g. tests/company/test_something.py, not in any
    of company/'s own subdirectories) were silently dropped entirely -- not
    counted anywhere, no error. tests/company/ alone has 60+ such files
    (1,927 tests) in the real repo. Caught by cross-checking a whole-tree
    collect-only count against the per-area sum, not by trusting either
    number alone."""
    import tools.generate_test_mix_data as mod

    monkeypatch.setattr(mod, "TESTS_DIR", tmp_path)
    (tmp_path / "company").mkdir()
    (tmp_path / "company" / "billing").mkdir()
    _write_test_file(tmp_path / "company" / "billing" / "test_b.py", 4)
    _write_test_file(tmp_path / "company" / "test_loose.py", 7)

    result = compute_test_mix()
    loose_area = next((a for a in result["areas"] if a["name"] == "company (general)"), None)
    assert loose_area is not None, "loose files directly in company/ must appear as their own area"
    assert loose_area["count"] == 7
    assert result["total"] == 4 + 7


def test_compute_test_mix_skips_pycache(tmp_path, monkeypatch):
    import tools.generate_test_mix_data as mod

    monkeypatch.setattr(mod, "TESTS_DIR", tmp_path)
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "junk.pyc").write_text("not real")
    (tmp_path / "saas").mkdir()
    _write_test_file(tmp_path / "saas" / "test_x.py", 1)

    result = compute_test_mix()
    assert all(a["name"] != "__pycache__" for a in result["areas"])


def test_compute_test_mix_counts_root_level_loose_files(tmp_path, monkeypatch):
    import tools.generate_test_mix_data as mod

    monkeypatch.setattr(mod, "TESTS_DIR", tmp_path)
    (tmp_path / "saas").mkdir()
    _write_test_file(tmp_path / "saas" / "test_x.py", 2)
    _write_test_file(tmp_path / "test_root_level.py", 3)

    result = compute_test_mix()
    root_area = next((a for a in result["areas"] if a["name"] == "top-level (general)"), None)
    assert root_area is not None
    assert root_area["count"] == 3
    assert result["total"] == 2 + 3


def test_compute_test_mix_sorted_descending_by_count(tmp_path, monkeypatch):
    import tools.generate_test_mix_data as mod

    monkeypatch.setattr(mod, "TESTS_DIR", tmp_path)
    (tmp_path / "small").mkdir()
    _write_test_file(tmp_path / "small" / "test_s.py", 1)
    (tmp_path / "big").mkdir()
    _write_test_file(tmp_path / "big" / "test_b.py", 5)

    result = compute_test_mix()
    counts = [a["count"] for a in result["areas"]]
    assert counts == sorted(counts, reverse=True)


def test_generate_writes_valid_json(tmp_path, monkeypatch):
    import tools.generate_test_mix_data as mod

    monkeypatch.setattr(mod, "TESTS_DIR", tmp_path)
    monkeypatch.setattr(mod, "OUT_PATH", tmp_path / "out" / "test_mix.json")
    (tmp_path / "sim").mkdir()
    _write_test_file(tmp_path / "sim" / "test_a.py", 2)

    generate()
    written = json.loads((tmp_path / "out" / "test_mix.json").read_text())
    assert written["total"] == 2
    assert written["areas"][0]["name"] == "sim"
