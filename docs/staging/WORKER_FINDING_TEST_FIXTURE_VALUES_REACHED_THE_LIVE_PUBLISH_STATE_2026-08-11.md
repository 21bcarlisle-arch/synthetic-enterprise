# [WORKER-FINDING] Test fixture values reached the live publish state and were published to origin (2026-08-11)

**Severity:** BLOCKING · **Lane:** H_harness

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
