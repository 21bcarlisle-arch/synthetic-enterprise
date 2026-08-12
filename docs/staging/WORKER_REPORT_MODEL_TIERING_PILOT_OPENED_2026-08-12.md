# WORKER REPORT — the tick's model is now a property of the work, and a 7-day pilot is open

**Severity:** INFO · **Lane:** H_harness · **Answers:** director console 2026-08-12
("every scheduled tick runs Opus, including mechanical work… pilot a tier rather than switching
wholesale")

---

## 1. What was actually wrong

`background/worker_tick.py` held `MODEL = "claude-opus-5"` as a module constant and passed it to
every `claude -p` it spawned. **The model was a property of the transport, not of the work.** A tick
that re-runs a measurement tool and commits the row paid exactly what a tick diagnosing a wedged
publish gate paid.

`docs/staging/done/MODEL_SELECTION_POLICY.md` (2026-07-12) had already decided the right thing —
*"model choice is a per-ROLE decision, not a per-session preference"* — and had already filed
site-surface build and the auto-process pipeline as SONNET-tier. It then said, of itself:

> *"Encode the assignment in the harness config… so the right model is used BY CONSTRUCTION, not by
> the agent remembering to switch. A model policy that depends on memory is a model policy with an
> expiry date."*

It was never encoded for the tick. The policy expired exactly as it predicted. That is the same
failure the CLAUDE.md decay audit ran into on the same day, in a different file.

## 2. What the tick draws, and which of it is mechanical

`find_work()` returns one doorbell string of the form `primary; ALSO -- refill`, assembled from a
rung ladder in `supervisor.py`. Each rung emits a stable, unique prefix. Read off the source:

| Rung | Emitted marker | Class | Tier |
|---|---|---|---|
| 1 | `PUBLISH-GATE WEDGE self-refill` | diagnosis | **Opus** |
| 1b | `OPERATIONAL-LAYER PERSISTENT-RED self-refill` | diagnosis | **Opus** |
| Lane 1 | `LANE 1 BUILD` / `self-refill from maturity map (dial-weighted)` | level_move | **Opus** |
| Lane 2 | `LANE 2 SITE` | site_surface | *Sonnet (pilot)* |
| Lane 3 | `LANE 3 DISCOVER/FRAME` | science | **Opus** |
| 7th | `OPEN-CAMPAIGN self-refill` | campaign | **Opus** |
| 4 | `DECLARED-DEFECT self-refill` | science | **Opus** |
| 4b | `STALE-GAP-ROW self-refill` | stale_gap_row | *Sonnet (pilot)* |
| — | `PROPOSE-HALF` / `FORWARD-DISCOVERY` / `RUNG 7 PLANNER` | science | **Opus** |
| floor | `RULE 0 self-refill` (HARDEN) | level_move | **Opus** |
| primary | `unprocessed staging`, receipts only | receipt_archival | *Sonnet (pilot)* |
| primary | `unprocessed staging`, anything else | finding_disposition | **Opus** |
| primary | `urgent from_rich` / `agenda open` | director_input / agenda | **Opus** |

Wall decisions are matched on **content** (`epistemic wall`, `wall_crossing`, `KNIFE`) rather than
on a rung, because a crossing can ride in on any lane.

**Three classes in the pilot.** `stale_gap_row` (re-run a named tool, commit the row, show it
reading CURRENT — the acceptance test is stated in the doorbell itself), `site_surface` (site/**
build to a settled design, disjoint by construction, pixel-verified per R11), `receipt_archival`
(a staging draw whose every item is a report/receipt marker).

**Two considered and declined, recorded so nobody re-opens them by accident.** The RULE-0 HARDEN
floor asks the turn to *"mutation-re-test a control, red-team its invariants"* — findings-quality
work, precisely what the director said he would rather pay for. Open-campaign surfaces land
Expert-Hour-reviewed as scored rubric rows; the scoring is the judgment.

## 3. The safety property, and why it is shaped this way

The director's rule is an asymmetric loss function — *"I'd rather spend the tokens than get
shallower work"* — so the code is built around the asymmetry rather than around accuracy:

- **Opus is the default and every fallback.** Sonnet is reachable only through an enumerated,
  currently-enabled pilot class.
- **Any reserved marker anywhere forces Opus**, even alongside pilot markers. The tick spawns ONE
  process for a doorbell that may combine several drawn items, so the tier is the **maximum** over
  everything drawn — never a first match, never a majority.
- **Unrecognised is Opus.** A rung added next month is unclassified, and unclassified costs tokens.
- **A broken, missing or expired pilot config is Opus.** The pilot cannot fail open into cheapness.

Sonnet's failure mode here is not red, it is *shallow* — which is invisible until it shows up as
rework. So R15 is applied with the directions reversed: what is proven able to fail is **cheapness**.
`tests/background/test_model_tier.py` (41 tests) mutation-proves each direction, including a
table-driven pass over every reserved marker, a check that every marker is a string `supervisor.py`
actually emits (so a reworded rung fails loudly instead of drifting into "unclassified"), and the
mixed-doorbell case in its real shape.

The staging segment is **parsed, not substring-matched**: nine receipts and one `WORKER_FINDING_`
is judgment work. "Contains a receipt" must never be mistaken for "is only receipts".

## 4. The pilot is data, and it closes itself

`docs/observability/model_tier_pilot.yaml` — committed, readable, per-class `enabled`, IaC rule
satisfied (no behaviour-determining state outside the repo).

- **Revert one class:** set `enabled: false`. Next tick, no restart.
- **Revert everything:** all false, or delete the file. Both restore pre-pilot behaviour exactly.
- **Automatic:** `ends: "2026-08-19"` is enforced in `_load_enabled_classes`. Past that date every
  class is off with no edit and nobody needing to remember. A defined period is only defined if
  something ends it.

## 5. The measurement, and the baseline it will be judged against

`python3 -m tools.model_tier_report` attributes commits to tiers by invocation interval
(worker-tick.service is `Type=oneshot` and blocks, so invocations do not overlap).

**The Opus baseline, computed over the 7 days before the pilot opened, when every draw ran Opus:**

```
$ python3 -m tools.model_tier_report --baseline 7
OPUS BASELINE — 2026-08-04 → 2026-08-11 (7d before the pilot, everything on Opus)
  commits  526
  REWORK — broad / narrow
     526 commits   broad 298 (57%)   narrow 178 (34%)
  FINDINGS RAISED  110  (15.7/day)
```

Two rework measures are printed and deliberately never reconciled: **broad** (a path was touched
again) over-counts, because iteration looks like rework; **narrow** (touched again by a commit
reading like a repair) under-counts, and the report says so — a repair titled *"the self-refill
doorbell was replaying the mint-time first step"* matches nothing and is missed. Narrow is a floor,
not an estimate. Where the two disagree, the disagreement is the finding.

Three limits are stated in the tool rather than glossed: the newest interval is open-ended and
flagged; interactive commits land in the same tree and the residual is reported as `unattributable`
rather than folded into a tier; and rework is a proxy, not a verdict.

**Honest caveat on the baseline.** It is an all-work figure. The pre-pilot log recorded no work
class, so a *per-class* Opus baseline cannot be recovered retrospectively — it can only accumulate
forward, from the `opus` rows the pilot itself writes whenever a reserved marker or a disabled class
sends a would-be pilot draw to Opus.

## 6. What to expect, stated now rather than explained away later

**The firing rate will be low at first, and the reason is not the router.** Every tick's doorbell
currently begins `unprocessed staging -- ` followed by **~90 staged documents**, most of them
`WORKER_FINDING_*` needing disposition. One finding in that list makes the whole draw judgment work
and forces Opus — correctly. So while the staging backlog stands, nearly every tick stays on Opus
no matter what the pilot enables.

That is the right answer from the router and the wrong state for the machine. If the pilot reports
zero Sonnet ticks at the end of the window, **the finding is the backlog, not the tiering** — and
the report is built to say exactly that rather than print empty Sonnet rows that read as "no harm
found":

> `VERDICT: the pilot has not fired yet. No Sonnet ticks means no comparison is possible — report
> the firing rate, never an absence of harm.`

Flagged, not fixed: draining ~90 staged findings is its own work, and doing it silently inside a
tiering change is the accretion `DON'T ACCRETE` forbids.

## 7. Landed

| | |
|---|---|
| `background/model_tier.py` | the classifier — reserved/pilot marker tables, max-tier rule, fail-closed config, decision log |
| `background/worker_tick.py` | `choose_model()`; the spawn takes the chosen model; falls back to Opus on any classifier error |
| `docs/observability/model_tier_pilot.yaml` | the live pilot declaration, 2026-08-12 → 2026-08-19 |
| `tools/model_tier_report.py` | coverage, rework (broad/narrow), findings, gate failures, `--baseline N` |
| `tests/background/test_model_tier.py` | 41 tests |
| `tests/tools/test_model_tier_report.py` | 14 tests |

**Also fixed in passing:** CLAUDE.md's model-routing paragraph pointed at
`session_watchdog.py::MAIN_SESSION_MODEL` — a module deleted on 2026-07-17 in the OPS1 collapse.
Repointed at `worker_seat.py::MODEL`, the live seat manager. One of five stale facts the same day's
decay audit found (`docs/observability/CLAUDE_MD_DECAY_AUDIT_2026-08-12.md`).

**Residual, not fixed:** `background/process_manifest.yaml:46` still describes the interactive
session as `--model claude-opus-4-8`. It is a descriptive `command:` string used for process
matching, not a live pin, so it changes no behaviour — but it is stale against the 2026-07-29 move
to Opus 5 and should be corrected on the next touch of that file.
