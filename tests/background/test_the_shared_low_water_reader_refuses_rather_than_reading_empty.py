"""THE SHARED LOW-WATER READER'S OWN CONTRACTS — proved here, not through one caller's suite.

WHY THIS FILE EXISTS, and it is a measurement rather than a tidying instinct.
`background/register_low_water.py` is one mechanism with four callers (the alarm census, the class
register, the maturity map, the canon). Its closing paragraph already records that mutating
`keys_at_head`'s `return None` to `return frozenset()` SURVIVED all four suites while the canon
still held a hand-rolled copy of the reader — the contract existed, and the only test of it was
pointed at the copy.

Convergence landed (`fc950dda6`, `029c21452`) and nobody re-asked the question. Re-asked on
2026-09-05 with a seven-mutation battery, each mutation applied alone and each of the four suites
run SEPARATELY so the answer is per-caller rather than a single pass/fail. Pre-registered in
`docs/staging/SEAT_PREREG_WHICH_CALLERS_PROVE_THE_CONVERGED_LOW_WATER_CONTRACTS_2026-09-05.md`;
result written up beside it. What it found:

  M1  `except (OSError, SubprocessError): return None` -> `frozenset()`   SURVIVED ALL FOUR
  M2  `if proc.returncode != 0: return None`           -> `frozenset()`   died in canon ONLY
  M3  `except Exception: return None` (extractor threw)-> `frozenset()`   died in class + canon
  M4  `if keys is None: return None`                   -> `frozenset()`   died in canon ONLY
  M5  unestablishable baseline -> `[]` instead of refusal                 died in all four
  M6  `str(ret.get(key) or "")` -> `str(ret.get(key, ""))`                died in all four
  M7  drop `.strip()` from the reason check                               died in census + canon

M5 and M6 are genuinely proved by every caller and need nothing here. The rest are the finding:
**M1's contract is held in place by nothing, and M2/M3/M4/M7 are each load-bearing on one or two
caller suites** — a canon test edited in good faith would silently un-prove three contracts for
four registers, and every suite would stay green.

SAID PRECISELY: the shipped code is CORRECT and always was. `keys_at_head` does return `None` on a
git that cannot run, no control is mis-reporting, and none of this is a live fault. What the
battery establishes is that nothing would NOTICE if that stopped being true.

THE BRANCH IS REACHABLE, which is why the gap is worth closing rather than theoretical.
`subprocess.run(["git", ...])` raises `FileNotFoundError` (an `OSError`) where git is not on PATH
and `TimeoutExpired` (a `SubprocessError`) when the 30s cap trips on a loaded machine — this one,
under a full gate run. Were the contract broken, both would become "HEAD's register was empty", so
nothing can have been removed, and ALL FOUR registers would report clean — precisely the
fail-silent shape the module's own header says it exists to refuse.

WHAT THIS FILE DELIBERATELY IS NOT. Not a per-caller routing test asserting "this rung calls
`removed_rows`". Three of those would be a control guarding a control. The contract lives on the
shared reader, so the proof of it belongs on the shared reader, and the callers are left alone.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from background import register_low_water as rlw  # noqa: E402

#: A register that really is committed at HEAD, so the SUCCESS leg is a real `git show`.
_LIVE_REGISTER = "docs/design/self_clearing_alarm_dispositions.json"


def _keys(text: str) -> list[str]:
    """A trivially successful extractor: the reader's failure legs are the subject here, not
    anybody's parser."""
    return ["a", "b"]


def test_the_reader_CAN_succeed_before_any_leg_asserts_that_it_refuses():
    """THE PARTITION CONTROL, written first on purpose. Every other test here asserts the reader
    returns None. A reader that returned None unconditionally — the exact fail-closed-everywhere
    mutation — would pass all of them, so one leg has to prove the success branch is reachable at
    all. This project has entered that trap three times through three different doors."""
    out = rlw.keys_at_head(_LIVE_REGISTER, _keys)
    assert out == frozenset({"a", "b"}), (
        "the reader could not read a register that IS committed at HEAD, so every refusal leg "
        "below is vacuous"
    )


@pytest.mark.parametrize("boom", [
    OSError("git is not on PATH"),
    FileNotFoundError("git"),
    subprocess.TimeoutExpired(cmd="git show", timeout=30),
    subprocess.SubprocessError("something else went wrong"),
])
def test_A_GIT_THAT_CANNOT_RUN_IS_UNESTABLISHABLE_AND_NEVER_AN_EMPTY_BASELINE(monkeypatch, boom):
    """THE MUTATION THAT SURVIVED ALL FOUR SUITES (M1), and the reason this file exists.

    `frozenset()` and `None` are opposite claims. The empty set says "HEAD's register held no
    rows, so nothing can have been removed" — which reports CLEAN, on all four registers at once,
    on any machine where git cannot be invoked or the 30-second cap trips under load. `None` says
    "I cannot answer", and `removed_rows` turns that into a refusal that names itself.

    Driven by making `subprocess.run` actually raise rather than by passing `baseline=None`: the
    latter tests the caller's handling and says nothing about what the reader returns, which is
    the exact gap that let this survive.

    MUTATION: `except (OSError, subprocess.SubprocessError): return frozenset()` and this fires.
    """
    def _raise(*_a, **_k):
        raise boom

    monkeypatch.setattr(rlw.subprocess, "run", _raise)
    assert rlw.keys_at_head(_LIVE_REGISTER, _keys) is None, (
        f"a git that raised {type(boom).__name__} left the baseline UNESTABLISHED; returning an "
        f"empty set reports every register clean and is the fail-silent this module refuses"
    )


def test_a_register_ABSENT_at_head_is_unestablishable_rather_than_empty():
    """M2 — the non-zero-returncode leg, which died only in the canon's suite. An in-repo path
    HEAD does not carry makes `git show` exit non-zero for real, no patching needed.

    MUTATION: `if proc.returncode != 0: return frozenset()` and this fires.
    """
    assert rlw.keys_at_head("docs/design/__no_such_register_at_all__.json", _keys) is None


def test_an_extractor_that_RAISES_leaves_the_baseline_unestablished():
    """M3 — died in the class and canon suites only. An extractor that throws on HEAD's bytes has
    established nothing; swallowing the exception into an empty set is the fail-silent one level
    below the caller.

    MUTATION: `except Exception: return frozenset()` and this fires.
    """
    def _explode(_text: str):
        raise RuntimeError("HEAD's copy is not what this parser expects")

    assert rlw.keys_at_head(_LIVE_REGISTER, _explode) is None


def test_an_extractor_that_RETURNS_NONE_has_its_verdict_carried_not_discarded():
    """M4 — died in the canon's suite only, and it is a DIFFERENT subject from the leg above.

    An extractor signals "HEAD's copy parsed, but is unusable as a baseline" by returning None
    rather than raising — `_disposition_keys_in_register` and `class_ids_in_source` both do this
    for a shape that is not a mapping. The reader must carry that verdict out. Turning it into
    `frozenset()` overrules the one component that actually looked at the bytes.

    MUTATION: `if keys is None: return frozenset()` and this fires.
    """
    assert rlw.keys_at_head(_LIVE_REGISTER, lambda _text: None) is None


def _rows_kwargs(**over):
    kwargs = dict(register="R", current=[], baseline=frozenset({"gone"}),
                  retired={}, row_is="A row is the only record.",
                  retire_with="`RETIRED[\"{key}\"]`")
    kwargs.update(over)
    return kwargs


@pytest.mark.parametrize("reason", ["   ", "\t", "\n", " \n\t "])
def test_a_WHITESPACE_ONLY_retirement_reason_does_not_open_the_hatch(reason):
    """M7 — died in the census and canon suites only. A reason made of whitespace is not an
    authored sentence, and the escape hatch exists precisely because only an authored sentence
    separates a genuinely retired subject from a derivation gone blind.

    MUTATION: drop `.strip()` from the reason check and this fires.
    """
    out = rlw.removed_rows(**_rows_kwargs(retired={"gone": reason}))
    assert len(out) == 1 and "gone" in out[0], (
        "whitespace cleared the refusal, so the hatch opens without anybody saying why"
    )


def test_a_REAL_reason_still_clears_it_so_the_hatch_is_not_welded_shut():
    """The other side of the partition. A refusal that can never be cleared is not a control, it
    is a wall, and every test above would pass against one."""
    assert rlw.removed_rows(
        **_rows_kwargs(retired={"gone": "the carrier was deleted in abc1234"})) == []
