# Agent report: Extract rulings: Sept-Oct

## Brief given

Read the brief at /tmp/claude-0/canon/brief.md and follow it exactly. Your batch list is /tmp/claude-0/canon/batches/D_sept_oct.txt (25 files, paths relative to /tmp/claude-0/canon/repo/). Your batch code is D. Write your extract to /tmp/claude-0/canon/extracts/D_sept_oct.md. These are the most recent director documents, so for each ruling also note explicitly in the "note" field whether it changes or supersedes an earlier ruling you can see referenced in the text. Read every file in full. Reply with only the batch summary section.

## Report


## Batch summary
- files read: 25 (all read in full; none unreadable). Snapshot is a sparse checkout, so code existence was checked via the git object store at HEAD `81f3d21`; DIRECTOR_CANON.md is frozen at v3 (2026-07-18).
- rulings extracted: 91
- most important / most likely forgotten (by id, one line each why):
  - R-D-29/R-D-30 — the product/machinery standing rule and floor: built, but on 2026-09-16 product share was 5–7% against a 25% floor and "none of them can fail"; the director had to ask why the canon isn't holding; neither standing page carries the definition or the rule.
  - R-D-23/R-D-42 — the 10-05 order supersedes the 09-04 arc but silently drops R3 (the £/tCO₂e score) and the "never greener" argument; R5 (book depth) was to be returned to the director with its cost and never was.
  - R-D-34 vs R-D-53/55 — physical-layer-first (demand-vector canon, 09-07) contradicts commercial-first (merit-order amendment, 09-05) for people phase 1; the amendment's order is what is actually running while W2_19 sits at L0.
  - R-D-54 — the four practice books: a director instruction with no atom, no file and no mention outside its two rulings, flagged as a GAP on 09-07 and still absent 10-12.
  - R-D-64 — the parked-documents audit: H48 at L0, `in_progress/` grown from 121 to 123, condition (HadUK pull) met in September; never reported to him.
  - R-D-62 — the four-things window (world / supplier / one customer / CO₂ as running state): "Not sure — I'll look later", never re-homed, never asked again; the L2 ruling is the same idea arriving by another door.
  - R-D-87 — "a session that takes director input without capturing it is a finding": console records stop at 2026-09-19 while October console instructions are quoted in the stretch log; the capture appears to have lapsed a second time.
  - R-D-48 — the few-thousand-customer book: discharged as a duplicate on 10-06, corrected 10-07 ("the director caught this"), the 10-08 finding still open in the staging root; live book still 80 founders.
  - R-D-70/R-D-73 — the use-case register was to be published to Capabilities (A50 L0) with a plain-English report and the risk-envelope decision brought to him (A51 L0); five weeks, nothing.
  - R-D-59 — effort as the mission's "time" currency, stated in physical units per rung: the only operational definition of the third currency, while CLAUDE.md says time "does not exist here at all" and a 10-04 director row on scoring time stays open.
  - R-D-22 — the bill validator's shared-assumption residual risk: "a second reconstruction by a different route... is not started" — and still isn't.
  - R-D-35 — the weighted distributional acceptance test supersedes the "99% of variance" targets, but the housing and people rulings sit in `done/` with the old target uncorrected.
- contradictions between documents in this batch (one line each):
  - 09-05 amendment puts collections, vulnerability and moves (commercial layer) into people phase 1 as rung 1; 09-07 demand-vector canon says stage 1 is the physical layer and "the commercial layer follows" (R-D-34 vs R-D-53).
  - 09-05 amendment's fidelity order puts payment/collections first and bill accuracy third; 10-05 priority order puts unbilled energy/billing accuracy before debt "because debt rests on knowing what was billed" — and names only the 09-04 canon as superseded (R-D-55 vs R-D-42).
  - 09-02 08:28 "Reconcile-on-the-deadman-cadence is a better design... Take it" vs 09-02 18:00 "reconcile... never on a cadence, and never while a gate is running" (R-D-17 vs R-D-18; the later governs).
  - 09-05 housing: "Coverage is a property of the ensemble of runs... not every house in every geography in one run" and "fresh draw per life, never a fixed library" vs 10-07 "the book needs to reach a few thousand customers" in one run for holdout power, and a live 80-founder `FOUNDER_BOOK.yaml` (R-D-57/60 vs R-D-48).
  - 09-05 housing/people "99% of variance including tails" vs 09-07 "a chosen percentage is not a test" (R-D-58/68 vs R-D-35; the later supersedes and says so).
  - 09-05 weather "the answer is a curve... the recommended cell count" vs 09-07 "the weather cell count is derived, not designed" (R-D-74 vs R-D-36).
  - 09-04 R3 "the score... the number the whole project exists to produce" vs 10-05 order with no carbon score step (R-D-23 vs R-D-42).
  - 09-05 "the website is presentation... should mostly be quiet" vs 10-09 a new harness-diagnostic page on the site, regenerated weekly (R-D-28 vs R-D-49) — reconcilable, but unreconciled.
  - 10-11 advisor trial runs code-editing worker ticks on Sonnet 5.5 vs CLAUDE.md "code edits and anything weighing evidence stay on Opus" (R-D-80).
  - Across the two standing pages: CLAUDE.md "The permission machinery stays deleted" vs DIRECTOR_CANON.md v3 "the twin is the standing approver... the builder never sits waiting on the real director again" and "Epoch 2 is the current open epoch" — DIRECTOR_CANON.md contradicts every Epoch-3 document in this batch and reflects none of them.
agentId: a2f33576e9be26c64 (use SendMessage with to: 'a2f33576e9be26c64', summary: '<5-10 word recap>' to continue this agent)
<usage>subagent_tokens: 292193
tool_uses: 58
duration_ms: 1555847</usage>
