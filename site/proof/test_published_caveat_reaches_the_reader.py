"""The published door serves the sentence the shipped code authors.

BLOCKING 1 of WORKER_FINDING_THE_CORRECTED_SENTENCE_NEVER_REACHED_THE_READER_AND_ITS_
CONTROL_HAS_NO_CALLER_2026-08-15.md -- the falsifier that finding recorded as MISSING,
built here because discharging it required one.

THE DEFECT, observed. Hour #31 corrected a caveat sentence on 2026-08-14. The correction
reached the source register and the working tree and stopped there. For a day
https://poesys.net/data/proof.json served the sentence the repo believed it had corrected,
while docs/design/simplifications/H27_payment_belief_gap.yaml recorded the residuals as
"now published in the sentence a reader meets". Nothing was red.

WHY NOTHING WAS RED, AND WHAT FIXES IT. Every existing assertion on that sentence takes an
IN-PROCESS object as its subject -- `pair.measure(...)["detection"].components`
(tests/tools/test_couple_w2_11_d5.py:4210), or `_live_coupled_gaps()` in
test_coupled_gaps_panel.py. Both RECOMPUTE the sentence, and a recomputation structurally
cannot see this defect, because what went wrong is that the recomputation's output was never
committed. So the two subjects here are the SHIPPED AUTHOR of the sentence
(`tools.couple_w2_11_d5.detection_resolution_caveat`, a pure register-derived function) and
the PUBLISHED FILE the deploy uploads. They are independent: one is code, the other a build
artefact, and the whole defect is the artefact lagging the code.

DELIBERATELY NOT A SUBJECT: docs/observability/coupled_gap_ledger.json. An artefact
regenerated from a stale intermediate agrees with itself, so routing this check through the
ledger would reintroduce the blindness it exists to close. (That ledger is separately
contaminated -- RECORDED 7 of the same finding, a bare pytest run re-publishing a test
fixture's population into it -- which is a second, independent reason not to lean on it.)

R15 BOTH WAYS, PROVEN AGAINST REAL HISTORY RATHER THAN A FIXTURE:
  RED   at 3e4037c1e -- that tree's proof.json serves "RESOLUTION IS WHERE THIS BOOK SITS
        BESIDE THE GRACE LINE" while the same tree's code already authors "RESOLUTION IS
        WHICH CASES THIS HEADLINE COUNTS".
  GREEN at 272e35bb3 -- the commit that published the correction.
The defect this control catches is a commit that actually happened, so the mutation is
history rather than a mock.

WHY THE SITE LANE. `tools/git-hooks/pre-commit`'s site-lane step runs the site suite on a
broad trigger -- site/data, any generate_*_data producer, or a site-consumed ledger -- which
is exactly the change set that can strand a correction. The tests/ publish gate selects test
files by NAME STEM and would not have run this; that stem-selection blindness is the decay
path BLOCKING 3 of the same finding names, and the class shape recorded in
WORKER_FINDING_A_RED_AT_HEAD_IS_INVISIBLE_TO_EVERY_COMMIT_THAT_DOES_NOT_SELECT_ITS_FILE_2026-08-15.md.

A SEPARATE FILE ON PURPOSE: site/proof/test_coupled_gaps_panel.py carries another lane's
uncommitted D44 basis-audit work, so appending here would have landed their tests ahead of
their supplier.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent  # site/proof -> repo root
PUBLISHED_PROOF = PROJECT / "site" / "data" / "proof.json"

SUPERSEDED_OPENER = "RESOLUTION IS WHERE THIS BOOK SITS BESIDE THE GRACE LINE"
CORRECTED_OPENER = "RESOLUTION IS WHICH CASES"


def _published_caveats() -> dict:
    """Every `*_caveat` component in the PUBLISHED proof.json, keyed pair-index -> field.

    R15 FAIL-SILENT: an absent, unreadable or pair-less artefact is a FAILED check, never an
    empty (and therefore agreeing) mapping -- so this raises rather than returning {}.
    """
    payload = json.loads(PUBLISHED_PROOF.read_text(encoding="utf-8"))
    pairs = payload["coupled_gaps"]["pairs"]
    assert pairs, "the published door carries no coupled pairs at all"
    out = {}
    for i, pair in enumerate(pairs):
        for field, text in (pair.get("components") or {}).items():
            if field.endswith("_caveat") and isinstance(text, str):
                out[(i, field)] = text
    assert out, "the published door carries no caveat text at all"
    return out


def test_the_sentence_the_shipped_code_authors_is_the_sentence_the_door_serves():
    """THE CLASS CONTROL: a caveat corrected in the register must reach the published file.

    Comparing the authored string to a recomputation of itself is what every prior
    assertion did, and it cannot fail. The comparison here crosses the code/artefact
    boundary the defect opened.
    """
    sys.path.insert(0, str(PROJECT))
    from tools.couple_w2_11_d5 import detection_resolution_caveat

    authored = detection_resolution_caveat()
    # VACUITY GUARD: a control comparing an empty string to an empty string passes
    # forever, which is how a control stops being one.
    assert authored and authored.strip(), (
        "the shipped caveat author returned nothing -- this control would be vacuous"
    )

    published = _published_caveats()
    served = [key for key, text in published.items() if text == authored]
    if not served:
        # R5: the alarm carries its diagnostic payload rather than a bare "not found".
        candidates = [text[:120] for text in published.values() if "RESOLUTION IS" in text]
        raise AssertionError(
            "the sentence the shipped code authors is on NO published surface -- a "
            "correction that never reached the reader. Regenerate and COMMIT "
            "site/data/proof.json, then re-fetch the live URL and quote the served value; "
            f"code on origin is not the evidence. Published resolution caveats: {candidates}"
        )
    assert len(served) == 1, (
        f"the authored sentence appears {len(served)} times on the door ({served}); a "
        "duplicated caveat means two pairs are sharing one measurement's prose"
    )


def test_the_published_detection_caveat_carries_the_hour31_correction():
    """THE INSTANCE, pinned by its own words.

    The class control above compares code to artefact, so it would still pass if the
    register were emptied of the correction -- both sides would move together. This pins
    the sentence that motivated it, in BOTH directions: the corrected clause present AND
    the superseded one absent. Presence alone would pass on a file that appended the
    correction beside the claim it replaced.
    """
    detection = [text for text in _published_caveats().values()
                 if CORRECTED_OPENER in text or SUPERSEDED_OPENER in text]
    assert len(detection) == 1, (
        "expected exactly one drift-resolution caveat on the published door, found "
        f"{len(detection)}"
    )
    served = detection[0]
    assert "crossing the line is NECESSARY, NOT SUFFICIENT" in served, (
        "the published door does not carry Hour #31's correction -- the reader is being "
        "served the claim the repo believes it corrected"
    )
    assert "DO NOT RUN THAT BACKWARDS" in served, (
        "the correction's second half -- that an unmoved number does NOT mean nothing "
        "crossed -- is not on the published surface"
    )
    assert SUPERSEDED_OPENER not in served, (
        "the superseded headline is still on the published surface"
    )
