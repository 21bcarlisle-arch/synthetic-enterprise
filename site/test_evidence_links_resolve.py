"""Cross-door control: every data/state evidence link a door renders MUST resolve.

SITE_CONSTITUTION DoD (per door): "evidence links resolve". The per-door render
harnesses (test_company_door.py, test_proof_door.py, ...) execute each page's JS
against the live JSON and assert the *rendered value*; this control closes the
complementary gap they do NOT cover -- that every `../data/*.json` / `../state/*.json`
the page fetches or links as evidence actually EXISTS on disk. A door that renders
clean can still cite a data file a generator has since renamed or dropped; that
dangling evidence link is a silent DoD violation until a visitor clicks it.

MAKE_IT_STICK: this converts the constitution's "evidence links resolve" policy
into a standing mechanism rather than an ad-hoc phase-close check.

R15 (a control must be able to FAIL): `test_a_fabricated_reference_is_flagged`
mutates in a reference to a non-existent data file and asserts the resolver marks
it missing -- proving the control fires on its own named defect (a dangling
evidence link), not just passing vacuously.

R3 (the site is a rendering, never an author): the reference set is read from the
page source; nothing here hardcodes the expected file list -- add a new data-backed
panel and its link is checked automatically.
"""
import re
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent

# DERIVED, 2026-08-20. This was a hand-kept list of eleven doors, and it named "project" --
# a page that had 301'd to /proof/ on 2026-07-23 and was deleted on 2026-08-20, which took
# this control down with it and made the tree unwritable for every lane.
#
# The literal was wrong in both directions, which is the usual shape: it went STALE (a door
# that no longer existed) and it was INCOMPLETE (the five-tab fold added /explore/ and
# /harness/, and neither was ever added here, so a dangling evidence link on either would
# have gone unseen). Every built page is scanned now -- reachable or not, since a broken link
# on a retained page is still a broken link -- and doors coming and going needs no edit here.
def _doors():
    pages = sorted(SITE.rglob("index.html"))
    out = []
    for p in pages:
        rel = p.parent.relative_to(SITE).as_posix()
        out.append(("home" if rel == "." else rel.replace("/", "-"), rel))
    assert len(out) >= 10, (
        f"only {len(out)} built page(s) found under {SITE} -- treating that as a broken scan "
        "rather than a shrunken site, since a short list here makes this control vacuous"
    )
    return out


DOORS = _doors()

# Matches a relative reference to a JSON evidence file under data/ or state/, as
# an ACTUAL link/fetch URL -- i.e. opened by a quote, the way a static href or a
# JS fetch()/template string writes it:
#   href="../data/company.json"   fetch("./data/dashboard.json")
#   "../state/track_record_scorecard.json"
# The opening-quote anchor deliberately excludes unquoted prose/comment mentions
# (`// rendered off site/data/regulatory.json`, `<code>site/data/x.json</code>`)
# that are documentation, not evidence links -- those are not links a visitor
# clicks, so a `site/`-prefixed or comment mention must not red the control.
_REF = re.compile(r'["\']((?:\.\./|\./)?(?:data|state)/[A-Za-z0-9_./-]+\.json)')


def _refs(page_dir: str) -> set[str]:
    html = (SITE / page_dir / "index.html").read_text(encoding="utf-8")
    return {m.group(1) for m in _REF.finditer(html)}


def _resolve(page_dir: str, ref: str) -> Path:
    # Strip cache-busting query (?t=...) and any fragment before resolving.
    clean = ref.split("?", 1)[0].split("#", 1)[0]
    return (SITE / page_dir / clean).resolve()


@pytest.mark.parametrize("door,page_dir", DOORS, ids=[d for d, _ in DOORS])
def test_every_evidence_link_resolves(door, page_dir):
    """Every data/state file a door cites as evidence exists on disk."""
    refs = _refs(page_dir)
    if not refs:
        pytest.skip(f"{door}: cites no data/state evidence files")
    missing = sorted(r for r in refs if not _resolve(page_dir, r).exists())
    assert not missing, f"{door}: dangling evidence link(s): {missing}"


def test_at_least_one_door_cites_evidence():
    """Guards the control against a vacuous pass if the regex ever silently
    stops matching (a fail-silent regression): the site as a whole MUST cite
    data-file evidence somewhere."""
    total = sum(len(_refs(pd)) for _, pd in DOORS)
    assert total > 0, "no door cites any data/state evidence file -- regex broke?"


def test_a_fabricated_reference_is_flagged():
    """R15: the resolver marks a non-existent evidence file as missing. Proves the
    control can fail on its own named defect (a dangling evidence link) rather
    than passing vacuously."""
    # DERIVED. This named "company", a page deleted on 2026-08-20 -- the same stale-literal
    # defect that took three other controls down with it. The door is now whichever built page
    # actually cites evidence, so the proof survives any future fold.
    door = next(d for _id, d in DOORS if _refs(d))
    fake = "../data/__this_file_does_not_exist__.json"
    assert not _resolve(door, fake).exists()
    # And a real one still resolves (independence -- not always-false).
    real = next(iter(_refs(door)))
    assert _resolve(door, real).exists(), real
