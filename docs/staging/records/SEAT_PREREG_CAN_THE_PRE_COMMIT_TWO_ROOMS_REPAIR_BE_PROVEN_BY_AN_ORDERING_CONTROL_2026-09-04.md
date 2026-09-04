**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# PREREG: can the pre-commit two-rooms repair be proven by an ordering control?

Filed 2026-09-04 13:2xZ by the delivery seat, working the Lane 0 direction *"the figures stopped
reaching the reader and no direction ever named the path"*. Written BEFORE the test was attempted.

## What I already know, and am therefore not predicting

Established by measurement before this was written, so none of it is a prediction:

* The live wedge was `finding_classes --check` reporting TWO ROOMS on two preregistrations, not
  the test named in `.publish_gate_state.json`'s `blocking_tests`.
* `background/staging_two_rooms_repair.py` classifies **both** pairs `redundant` (SAFE) and would
  have cleared them. Its room-list blindness was already fixed at 45ba3df6d (10:10 local).
* The worker ran that repair at the top of its cycle (~12:30), and the duplicates were written at
  13:01 and 13:06 — after the sweep, during the publish it launched.

## The prediction

**P1.** `git_commit_push` is drivable in a unit test by the monkeypatch set the existing
`_refresh_published_liveness_on_skip` tests already use (`PROJECT_DIR` → `tmp_path`, `tree_lock` →
`nullcontext`, `subprocess.run` → fake, plus `_divergence_refusal` and `_git_add_or_refuse`
stubbed), so an ordering control can be written against the REAL call site rather than against
source text.

**P2.** The ordering control will discriminate. A fake `git commit` that records whether the root
duplicate still exists **at commit time** will report ABSENT with the repair wired in, and PRESENT
with it stubbed to a no-op. Both legs are asserted, because a control over an ordering must make
the two orders produce different answers — asserting only the ABSENT leg would pass just as well
against a fixture that never had a duplicate in it.

**What would refute P1:** `git_commit_push` needs collaborators the harness cannot cheaply supply,
and the honest fallback is a source-order control that says in its own docstring that it reads
text and not behaviour.

**What would refute P2:** the no-op leg also reports ABSENT — which would mean something else in
the path is removing the duplicate and the new call is not what clears it.

## Why this is worth pre-registering

The claim I am about to make is "the repair now runs at the point of use". The tempting control
asserts only that the duplicate is gone by commit time, and that control passes on a fixture where
no duplicate was ever created — the reachability trap this project has entered repeatedly. Naming
the discriminating leg before running it is the only way the result is evidence.

## Graded

To be graded beside the result in the finding that reports it. Not revised after the fact.
