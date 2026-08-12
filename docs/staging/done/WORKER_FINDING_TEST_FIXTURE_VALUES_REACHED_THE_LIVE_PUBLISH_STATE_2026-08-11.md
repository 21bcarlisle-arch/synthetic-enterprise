# [WORKER-FINDING] Test fixture values reached the live publish state and were published to origin (2026-08-11)

**Severity:** RECORDED · **Lane:** H_harness — **REPAIRED 2026-08-12, both parts. See
"Disposition" at the foot of this document for what was built, where it is wired, and what
residue is accepted.** The header is RECORDED rather than BLOCKING because no fixture value can
now reach a published surface on any publish path, and the one residue (the mechanism behind a
log-only value) is accepted with its reason stated.

**Found:** reading the publisher log while unwedging the 41-hour publish outage. The outage is
fixed and this is not what caused it — but it is the more dangerous defect, because it puts
fabricated values on a public surface.

**R9 labelling is deliberate throughout: the symptom is `observed-with-evidence`; the mechanism is
`NOT ESTABLISHED`. I am not asserting a cause I have not proven.**

## Observed, with evidence

```
[2026-08-11 08:58 UTC] Provenance banner: Verification paused since 2026-08-11T08:58:57Z
                       · showing run run_verified.json (last verified 2026-08-11T08:58:57Z)
[2026-08-11 08:58 UTC] Provenance banner published to origin.
[2026-08-11 09:01 UTC] Publish gate: run_complete_20260811T090122Z.md exited 0 but no suite PASS
                       is recorded for git=abc1234 -- publishing nothing is not evidence...
```

`run_verified.json` and `abc1234` are **test fixture literals**, not runtime values. The first was
rendered into a freshness banner and **published to origin** — i.e. a fabricated run id was, for a
period, the public claim about how current the site was. That is the ruling's named cardinal sin
(fake-fresh) arriving from an unexpected direction.

## What I checked, and what it rules OUT

* `tests/background/test_publish_decoupling_exit.py` — the obvious suspect, since it is where the
  literal `run_verified.json` lives — **is exonerated**: it both `monkeypatch.setattr(prov,
  "PROVENANCE_FILE", tmp)` and passes `path=p`, so its writes land in `tmp_path`.
* The `conftest.py::_PROTECTED_WRITE_PATHS` guard **does** cover
  `site/data/publish_provenance.json` and **does** fire in the real tree — its own R15 test
  (`test_a_test_cannot_write_the_published_provenance_claim`) passes.
* `_overlay_untracked_data` symlinks only `sim/cache` and `node_modules` into the gate checkout, so
  a test writing inside the checkout **cannot** reach the real file through the overlay. That was my
  first hypothesis and the code refutes it.
* `tests/background/test_publish_provenance.py` never references `PROVENANCE_FILE` (0 occurrences)
  and calls `record_annotation(...)` at line 82 without a `path=`. **This is the strongest
  remaining lead, not a conclusion** — `record_annotation` does not set `showing_run`, so it cannot
  by itself explain a `showing_run` of `run_verified.json`.

**So the mechanism is open.** Something wrote a `record_verified(run_id="run_verified.json")` state
into a provenance file the publisher then read, and none of the paths above accounts for it.

## Why it matters more than the outage it was found beside

The whole decoupling rests on the banner being the one thing a visitor can always trust. A publish
gate that can be wedged is an availability problem; a banner that can state a fabricated run id is
an **integrity** problem, and it publishes silently — nothing in the pipeline flagged either line.
The content I landed at `f65d22b06` was scanned for these markers before committing and is clean,
but that was a manual check by one operator on one occasion, which is not a control.

## Proposed atom (queued, not built — SELF_INTERRUPT_DISCIPLINE)

**`OPS_no_fixture_value_may_be_published`** — two parts, and part 1 does not require knowing the
mechanism, which is why it goes first:

1. **A publish-time assertion on the VALUE, not the writer.** Before any provenance or dashboard
   commit, refuse if `showing_run.run_id` does not match `run_output_<sha>_<stamp>.json`, or if any
   published field matches the fixture vocabulary (`abc1234`, `deadbeef`, `run_verified.json`,
   `v`\*40). A publisher that cannot prove its own values are runtime-derived should not commit.
   This closes the class **whatever** the source turns out to be.
2. **Then find the writer**, with the search narrowed by part 1's refusal logs, which will name the
   cycle and the value.

R15 both ways: mutation — hand a fixture-shaped run id to the publisher and the commit must be
refused (test reds if it publishes); a genuine run id must pass untouched.

**Recommendation: P1.** Not because it is blocking — publishing is healthy as of `f65d22b06` — but
because it is an integrity defect on the public surface with no detector at all, and part 1 is a
value-shape check that costs little and does not depend on completing the diagnosis.

---

## Disposition (2026-08-12, worker tick — RUNG 1c blocking-finding draw)

**Part 1 — the publish-time assertion on the VALUE — was already built and is now wired on
every publish path.** `background/publish_provenance.py` carries `publishable_violations`,
`dashboard_meta_violations` and `assert_publishable`: a run id must match
`run_output_<sha>_<UTC stamp>.json`, a git_commit must be a sha that `git cat-file` finds in
this repo, the named fixture vocabulary is refused by name, and an unavailable git reads as
absent (fail-closed — an unavailable check is a failed check, R15 killer pattern 3).

**What this tick found and fixed: the guard was mounted on the wrong cycle.** It was called
from `_commit_and_push_paths` only — the liveness heartbeat and the RED-cycle banner.
`git_commit_push`, the function that commits `site/data/dashboard.json` and
`site/data/publish_provenance.json` together on every GREEN cycle, never called it. That is
also the path the ESTABLISHED half of this finding actually took: `d4d1a04e6` published
`run_output_abc1234_20260621T104002Z.json` to origin from a content publish, not from a banner.
The checker's own comment — "publishing a false provenance is impossible from here" — was true
of the function it sat in and false of the publisher.

**The class, for the register:** *a control's subject is the set of call sites it is wired
into, never the sentence in its docstring.* A sibling test's docstring asserted in prose that
"every provenance commit — red-cycle banner and green-cycle content alike — passes through
`_commit_and_push_paths`". Nothing checked that sentence, and it was wrong. Corrected in place.

**R15 both ways, driven not asserted** (`tests/background/test_published_provenance_is_real.py`,
28 passed):

* FIRES — `test_the_green_cycle_publish_refuses_a_false_provenance`: a green-cycle tree holding
  `run_verified.json` / `v`×40 reaches **no git call at all**, `git_commit_push` returns False,
  and the refusal log names the offending value so it names the cycle.
* SILENT — `test_the_green_cycle_publish_commits_a_genuine_stamp`: a real run id and a sha that
  names a real commit in a real fixture repo publish exactly as before. Without this half, the
  first is satisfied by a guard that refuses everything — an outage wearing a control's hat.
* MUTATION (in-test) — `test_the_green_cycle_refusal_is_the_guards_doing`: neutralise the
  checker and the same false provenance publishes.
* MUTATION (production) — deleting the two added lines from `git_commit_push` reds the FIRES
  test, with `git add` / `git commit` / `git push` all reached on the fixture provenance. Run
  and observed this tick, not reasoned about.

**Part 2 — the writer — is answered for the value that was published and accepted for the one
that was not.** The ESTABLISHED value (`abc1234`) has an established mechanism: the decoupling
made `_process()` stamp the real provenance file, so ordinary publisher tests driving
`_process()` wrote the live surface. That is closed at the write by
`tests/conftest.py::_PROTECTED_WRITE_PATHS`, which now covers
`site/data/publish_provenance.json` and whose own R15 test passes. The `run_verified.json` line
in this document's own evidence block was **an overstatement, corrected**: every commit that
ever touched the provenance was searched and none carries that value — it reached the LOG (the
banner line renders from in-memory state before the commit) and there is no evidence it reached
origin.

**Accepted residue, stated rather than left implicit:** the in-memory path that produced that
log line is still NOT ESTABLISHED. It is accepted because the guard asks the only question with
a knowable answer — *is what we are about to publish a real run and a real commit?* — so the
class is closed whatever the writer turns out to be, and a shape-valid-but-stale re-stamp is a
different defect already held by the fake-fresh disjoint-write-set property.

**Live surface at disposition (R11):** `site/data/publish_provenance.json` reads
`showing_run.run_id = run_output_5053c2a4b_20260812T151102Z.json`, `git_commit = 5053c2a4b`;
`dashboard.json` `meta.source_file = run_output_3abd6e1df_20260812T163606Z.json`. Both are real
runs against real commits; the guard is silent on both.
