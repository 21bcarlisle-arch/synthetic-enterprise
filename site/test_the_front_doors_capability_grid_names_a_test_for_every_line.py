"""Every line of the front door's capability grid names a test that exists, and links somewhere.

Director steer of 22 Oct 2026: the front door shows "a complete supplier, shown as a capability
grid", each line stated as what the supplier does, and "check every claim in the capability grid
against a test or record that exists". A grid line is a public claim that a function exists and
works. Its `data-test` names the tests that hold it. This reds when a line names none, or names a
test that has since been deleted or renamed, which would leave the claim with no evidence behind it.
"""
import re
from pathlib import Path

from test_the_published_bytes_reader import published_blob, refuse_working_tree_reads

REPO = Path(__file__).resolve().parents[1]
INDEX_REL = "site/index.html"


def _grid_lines(html: str):
    m = re.search(r'<dl class="fidelity capgrid">(.*?)</dl>', html, re.S)
    assert m, "the front door has lost its capability grid"
    return re.findall(r'<dt><a href="([^"]+)">([^<]+)</a></dt>\s*<dd( data-test="[^"]*")?>', m.group(1))


def _missing(lines):
    out = []
    for href, name, attr in lines:
        tests = attr[len(' data-test="'):-1].split() if attr else []
        if not tests:
            out.append((name, "names no test"))
        for rel in tests:
            if not (REPO / rel).is_file():
                out.append((name, f"names {rel}, which does not exist"))
        if not href:
            out.append((name, "links nowhere"))
    return out


def test_every_grid_line_names_a_test_that_exists():
    lines = _grid_lines(published_blob(INDEX_REL))
    # The partition can be taken at all: the grid is the whole supplier, not one line.
    assert len(lines) >= 8, f"the grid holds {len(lines)} lines, not a whole supplier"
    assert _missing(lines) == []


def test_the_check_can_fail():
    html = published_blob(INDEX_REL)
    lines = _grid_lines(html)
    href, name, attr = lines[0]
    gone = [(href, name, ' data-test="tests/no_such_dir/no_such_test"')] + lines[1:]
    assert _missing(gone) == [(name, "names tests/no_such_dir/no_such_test, which does not exist")]
    bare = [(href, name, "")] + lines[1:]
    assert _missing(bare) == [(name, "names no test")]


def test_no_subject_of_this_file_is_read_from_the_working_tree():
    refuse_working_tree_reads(__file__, (INDEX_REL,))
