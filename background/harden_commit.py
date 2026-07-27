"""Single source of truth: is a git commit a HARDEN re-verification pass?

DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27 §1 (as restated by the same-day
amendment): a HARDEN re-verify "never counts as work for the deadman clock, utilisation, or the
product/machinery split." HARDEN is NOT abolished — it stays available and keeps finding real
defects (it found four on 2026-07-27). This module only lets the ACCOUNTING organs exclude a HARDEN
commit from forward-progress; it never suppresses the HARDEN draw itself (that is the LANDED
draw-ordering half, `supervisor.py::_unconsumed_director_ruling_or_steer`).

The marker is a COMMIT-SUBJECT convention — the two shipped subject forms a Rule-0 HARDEN pass
commits under (see `git log` 2026-07-27 and earlier):
    [HARDEN <atom_id>] ...                         -- a pass that touched code/tests + R15 controls
    chore(harden): / chore(harden-cooldown): ...   -- a cooldown-stamp / no-source re-verify

Note the `chore(harden` form ALREADY matched deadman's broader `chore(` non-progress prefix; the
genuinely-new coverage this module adds is the `[HARDEN <atom>]` form, which touches real code/tests
and therefore, before this, refreshed the deadman clock and counted as a MACHINERY commit — exactly
the busywork-masks-real-work failure §1 forbids.

R15 INDEPENDENCE: the verdict is derived from the ACTUAL commit subject passed in — never from a
constant, a flag, or the same organ's own state. A commit is HARDEN iff its own subject says so.
"""
from __future__ import annotations

# Case-sensitive: the shipped convention writes `[HARDEN` upper-case and `chore(harden` lower-case.
# `[HARDEN` covers `[HARDEN]`, `[HARDEN <atom>]`, `[HARDEN <atom> ...]`; `chore(harden` covers
# `chore(harden):` and `chore(harden-cooldown):`.
_HARDEN_SUBJECT_PREFIXES = ("[HARDEN", "chore(harden")


def is_harden_commit(subject: str) -> bool:
    """True iff `subject` is a HARDEN re-verification commit by the subject convention above."""
    s = subject.strip()
    return any(s.startswith(pfx) for pfx in _HARDEN_SUBJECT_PREFIXES)
