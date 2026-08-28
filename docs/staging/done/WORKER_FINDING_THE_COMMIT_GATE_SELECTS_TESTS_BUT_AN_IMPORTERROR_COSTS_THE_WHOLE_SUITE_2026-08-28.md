**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `AO1_capability_index`

# The commit gate selects a few test files, but an ImportError in any one of them costs the whole suite — so the gate's blast radius and its subject are different sizes

`tools/pre_commit_test_gate.py` runs a *selection*: `select_targets(staged)` maps the staged paths
to test files by filename stem, import graph and a handful of curated surface lists, then runs
exactly those. That is a deliberate and well-argued design — the module carries several hundred
lines explaining why a whole-suite run on every commit is the wrong trade, and it is right about
that.

It is unsound for exactly one failure mode, and that mode is the cheapest one to create.

**pytest aborts collection globally.** One test module that raises on import produces
`Interrupted: N error during collection` and **no tests run at all** — not the module's, not the
rest of the suite's, not the marker-selected subset some daemon depends on. So the cost of an
unimportable test file is not scoped to that file. The gate's subject is a handful of files; the
damage a refused import does is the entire tree.

## Observed, today, with the bill attached

Commit `0850eadcd` deleted `RESI_OFFER_COST_GBP` and `IC_OFFER_COST_GBP` from
`company/analytics/counterfactual_retention.py`. The deletion was correct and well evidenced. It
updated two of the three consumers.

The third was `tests/tools/test_phase_rx_track_record.py`. Its stem names a *phase*, not either
changed module, so `select_targets` did not select it and the gate was green on a commit that made
the tree uncollectable.

**What that cost:** the independent-cadence operational-layer signal runs hourly with a marker
expression. From `19:26 UTC` to `22:26 UTC` it returned `rc=2` five consecutive times, because the
marker never selected anything. The operational layer was **unmonitored for three hours**, and the
alarm that eventually escalated had to spend its first paragraph telling the reader it was *not* a
daemon-lifecycle regression — because the symptom is indistinguishable from one.

That is the second cost and it is worth naming separately: a collection abort **presents as
whatever the caller was trying to measure**, so it misdirects the diagnosis of every consumer
downstream of it.

## Why the obvious repairs are the wrong ones

**Not "widen the selection."** No stem or import-graph rule connects
`counterfactual_retention.py` to `test_phase_rx_track_record.py` without connecting a great deal
else; the module already documents a case where widening took one commit past twenty minutes. The
selection is not too narrow. It is the wrong *instrument* for this one property.

**Not "run the whole suite."** That is the trade the gate exists to refuse, and it costs fifteen
minutes an edit.

## The one leg, measured

`python3 -m pytest tests/ -q --collect-only` over the whole tree: **9.97 s**, 31,052 tests, on a
warm cache. Against a gate that already takes more than ten minutes that is under 2%.

Collection is the only thing that has to be whole-tree, because collection is the only thing whose
failure is whole-tree. Everything else the gate does can stay selected. The proposed leg is one
`--collect-only` run, gating on a non-zero return, placed **before** the targeted run — a
collection error makes the targeted result meaningless anyway.

## What must be true of it before it lands, and why this is filed rather than shipped

Three things, none of them free, which is why this is a finding and not a commit:

1. **It must run against the tree the commit would create, not the working tree.** The ruff
   ratchet already reads the whole working tree and duly wedges one lane when another lane is
   dirty. A whole-tree collect-only has exactly that failure mode and a bigger surface. Under
   `python3 -m tools.surgical_land` the subject is correct by construction; under a plain
   `git commit` on this shared tree it is not, and that difference has to be settled before the
   leg goes in — not discovered by wedging four lanes at once.
2. **It needs its own mutation proof.** A control that cannot fail is the house rule. The proof is
   cheap and obvious: stage a test module importing a name that does not exist, assert the gate
   refuses, assert it passes once the import is repaired.
3. **It fails closed, loudly.** If pytest itself cannot be invoked, that is a refusal, not a pass.
   A collection gate that silently no-ops when its checker is unavailable is the FAIL-SILENT shape
   and would be worse than no gate, because it would be *believed*.

## Reversal

Delete the leg and its test. No data, no schema, no published surface — one gate step and one test
file.

---

*Filed by the worker tick that repaired the instance
(`tests/tools/test_phase_rx_track_record.py`, signal recovered `green: true, rc: 0,
episode_closed: true`). The instance is fixed; the class is not, and the class is what put the
operational layer in the dark. Nothing here is blocked — this is drawable as it stands.*
