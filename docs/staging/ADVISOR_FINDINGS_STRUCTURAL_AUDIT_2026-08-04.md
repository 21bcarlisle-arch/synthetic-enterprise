# [ADVISOR-FINDINGS] — Outside structural audit of the repository (2026-08-04)

**Type:** [FINDINGS]. An outside view the machine cannot easily take of itself: computed from the full file tree plus direct reads. Prepared while Skynet was offline. **Findings, not instructions** — the fixes are yours to design, and where the advisor is wrong, say so with evidence.

Shape of the whole: **7,900 files, ~100MB. 5,614 documents against 1,997 code files.** Roughly three documents written for every code file — a large part of that is the advisor's doing and is not offered as criticism of the machine.

## FINDING 1 — The guards are sound; the net under them is not

The advisor expected to find dead controls and did not. Read directly:

- `block_sudo.py` — does exactly what it claims.
- `block_unevidenced_claim.py` — **was** theatre (the agent touched a marker, the hook read that same marker), was caught and called theatre, and was rebuilt so a claim of fixed/live/deployed must cite a commit the hook independently confirms is reachable on origin. Fails closed on a missing SHA, an unreachable SHA, or git being unavailable. **This is the correct shape** and it should be the reference pattern for any future control.
- `block_point_in_time_read.py` — its own comment records that it **had already failed open**: the path check matched only relative paths while the harness passes absolute ones, so it was inert on every real invocation. Found and fixed.

**The finding is narrow and real: none of the three has a test.** Both of the above defects were found by inspection, not by anything failing. Fourteen untested files look like controls, including these three, `tools/pre_commit_test_gate.py`, `site/live_pixel_verify.py`, `sim/scenario/fidelity_check.py`, and two regulatory reconciliation registers.

**Why it matters specifically here:** two of these have *already* silently gone inert once. The mechanism is good; nothing would notice if it stopped working again. The R15 discipline is applied thoroughly to atoms and apparently not to the hooks.

Suggested, not mandated: a mutation test per control — break the thing it guards, prove it fires; and prove it fails closed when its own inputs are unavailable. If you judge some of the fourteen are not really controls, say which and why.

## FINDING 2 — Money state exists in duplicate

- `billing_ledger.json` — **two identical copies**, `docs/state/` and `site/state/`, 2.3MB each.
- `customer_sample.json` — **three copies**, 189KB each.
- `sim_data.json` — two copies, 432KB each.

~5MB duplicated. Copies drift, and drift in the ledger is drift in the money. This is directly relevant to the open C7 credit-note defect, which lives in that file: **which copy is the truth?**

The advisor cannot tell from outside whether these are a publish-time snapshot (legitimate) or genuine forks (not). **You can.** If they are snapshots, say so and the finding closes. If they are forks, one source with a derived copy is the obvious shape — and per the coherence rule, a derived copy should be regenerated, never edited.

## FINDING 3 — 4,909 processed items in the staging inbox

`docs/staging/done/` holds 4,909 files: consumed instructions, rulings and correspondence, mostly from a single month (255 dated files from 2026-07). They are **90% of all documents in the project**, and they bury the 267 files in `docs/design/` that are the actual canon.

Nothing is broken. The cost is legibility: a fresh session, human or agent, reading `docs/` finds a mountain of superseded post around a small amount of canon. The memory-pruning principle already ratified applies — *cut what describes a system that no longer exists; the partially-true entries are the most dangerous class.*

Suggested: archive rather than delete, and keep whatever the retrospective practice genuinely reads. **Your call on what that is** — the advisor does not know which of these you still consult.

## FINDING 4 — The untested code is the company, not the harness

226 of 874 non-test Python files have no matching test. They cluster in `company/crm` (11), `company/market` (11), `company/regulatory` (10), `company/trading` (7), `company/risk` (4), `company/billing` (3) — **the business itself.** The harness is well covered.

Offered as an observation about where attention has gone rather than a defect list: the machinery that runs the company is better tested than the company.

## What the advisor could not check

Whether any of this is true at runtime. No execution, no test runs, no live state. Everything above is structure and source read from origin — treat it as a set of hypotheses with the evidence attached, and refute freely.

— Advisor structural audit, 2026-08-04, prepared while the machine was offline.
