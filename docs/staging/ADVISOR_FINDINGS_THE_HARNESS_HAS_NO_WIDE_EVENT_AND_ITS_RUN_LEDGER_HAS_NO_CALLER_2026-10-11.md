# ADVISOR FINDINGS — this project against the observability literature, and the one instrument it is missing
**Knowledge:** none -- a director or advisor ruling, steer or record, not domain research

**Fate (2026-10-13, clear-the-decks):** ATOM -- n/a No banner. P3 -- wide-event-style structured logging / a caller for the run ledger, per advisor's observability-engineering reading; explicitly "nothing here is urgent."

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` — header added by the scale lane: the file landed without one (the second advisor-staged file to, after 67ab788e5) and the severity gate refused every lane's merge of origin

Staged by the advisor on the director's behalf, 2026-10-11, at his request.
**Report and rank.** Nothing here is urgent. Rank it against the current
direction rather than ahead of it.

## Provenance

Source: *Observability Engineering*, 2nd edition (Majors, Fong-Jones, Miranda,
with Parker; O'Reilly, June 2026). The advisor read chapters 1, 17, 25, 27 and
28 directly from the PDF, and chapters 8, 9, 10, 11, 12 and 21 through
subagents reporting verbatim. The second edition is substantially about AI
systems, which is why it is worth this project's attention at all.

Every claim below about **this repository** was verified against origin at
`a1d5ec9` this morning, not recalled. Where the advisor could not establish
something, it says so.

## The frame worth taking

The book's spine is a distinction between **two feedback loops**:

- the **operational** loop — alert, investigate, fix — which protects stability
- the **developer learning** loop — deploy, observe, learn — which is where
  value is actually created

Its argument is that most organisations have only the first, that operational
loops are "the longest, lossiest, and most expensive kind", and that the gap
between the two is "where velocity goes to die". Its memorable form: operations
should be your goalie, and if your goalie is making fifty saves a game your
defence is not working.

Applied here, the shape is unusual and worth naming, because it is not the
failure the book expects:

- On the **simulation**, the learning loop runs extremely well. The last
  twenty commits are pre-registered prediction followed by graded result, in
  pairs. That is better than the book asks for — it never requires
  pre-registration.
- On the **harness**, the operational loop runs well. The dead-man's switch,
  the reconcilers, the alarm-to-work escalation.
- The gap is the **learning loop about the harness itself**. This project
  measures whether the machine is alive. It does not measure whether the
  machine is getting better at its job. `trust_ledger.json` — the nearest
  instrument — has five rows.

## What the book would say this project already does better than its own advice

Stated not as flattery but so none of it is traded away while closing the gaps
below.

1. **Signal independence.** `deadmans_switch.py` refuses any input the stack it
   watches can corrupt, using only git commit timestamps, after learning that
   `docs/observability/` mtime — written by every daemon's own log — masked a
   six-hour blackout. The book has no equivalent concept anywhere.
2. **Controls must be provably failable.** The book's chapter 17 layers three
   CI gates and never once tests whether a gate can go red. R15 is a stronger
   discipline than anything in the literature here.
3. **Observability of the observability.** `self_clearing_alarm_census.py` —
   5,004 functions scanned, 211 state paths, finding controls whose failure
   path writes the state their own alarm reads. Second-order. The book only
   gestures at this, and means cost attribution when it does.
4. **A repeating alarm becomes work.** After three identical firings the alarm
   is filed as a document rather than re-sent; five such documents are on disk.
   The book devotes a chapter to alert fatigue and answers it with SLOs. This
   answer handles a case theirs does not.
5. **Invariants as a semantic firewall.** Chapter 17 builds its whole worked
   example on an energy billing system — interval series, tariff, bill set —
   with coverage, arithmetic and determinism invariants, and an architecture
   that sandwiches a nondeterministic agent between deterministic validation.
   This project arrived at the same place independently and in more depth.

## The gaps, with evidence

### 1. This project cannot answer an arbitrary question about its own history

The book's sharpest diagnostic is the **arbitrary question test**: give the
system a question nobody preconfigured for, and see whether it can be answered
in under a minute. "Show me every run where bad debt moved more than five per
cent under crisis-replay" has no answer here.

The reason is structural, and the book names it: **pre-aggregation is a one-way
trip.** Self-telemetry is 160 JSON files, 64 markdown files and 18 JSONL files,
seven of which have twelve lines or fewer. These are *derived registers* — the
conclusion was stored and the event was discarded. The commit SHA is doing the
work of a correlation key across the whole system.

This matters more than it sounds. Every other gap below is downstream of it,
and so is the automated half of the book's core analysis loop — diff every
dimension inside an anomaly against the baseline and rank by association —
which cannot be built on registers.

**What the repository already holds, verified this morning:**

- `background/run_manifest.py` line 60 declares
  `LEDGER_PATH = docs/observability/run_ledger.jsonl`
- line 233 builds a real run identity from SHA, world scenario, seed and
  generation time
- line 276 defines `append_to_ledger()`
- **that function's only callers are in its own test file**
  (`tests/background/test_run_manifest.py`, lines 97–98)
- `background/run_rotation.py` line 57 imports `RunManifest`, `RunOutcomes` and
  `build_manifest` — and **not** `append_to_ledger`. The manifest is built
  each run and never written.
- `docs/observability/run_ledger.jsonl` **does not exist** (404 on origin,
  absent from a fresh clone, not gitignored)

**And it is not an orphan by neglect.** Both
`DIRECTOR_RULING_GENERATOR_ACTIVATION_AND_RUN_LEDGER_2026-07-25.md` and its
twin sit in `docs/staging/in_progress/`, marked `SUPERVISOR_DRAW: blocked`.
Their own blocked-on note records that the ledger infrastructure **is built and
tested** (21 tests, epistemic PASS) and that the whole ruling is walled on one
director decision: the ruling's N=200 against the director-signed λ=1.0
trickle, escalated on 25 July and not since answered.

So the single most valuable missing instrument in this system is finished code
with no caller, parked behind a question for the director that has been open 78
days. **That is a director item, not a machine item, and it is being raised
with him separately.**

What is worth the machine's judgement is narrower: whether a per-run ledger row
is worth having **independently** of that activation decision — the run
happens either way, and the row would be comparable across runs whatever
population it drew.

### 2. Instruments die and nothing notices

Verified content timestamps, not git metadata:

| Instrument | Last content |
|---|---|
| `token-usage-log.jsonl` | 25 June |
| `edge_traffic.jsonl` | 20 August |
| `decision_log.jsonl` | 22 August |
| `health-check-log.md` | 16 July |
| `deadmans-switch-log.md` | 17 July |
| `daily-self-note.md` | 22 July |
| `head_red_baseline.json` | still `known_red: []` |
| `resource_headroom.py` | 1,041 lines; recorded by its own sibling as never having executed once |

This project has liveness checks for publishing (`publish_freshness.py`) and
for launches (`launch_liveness.py`), and an orphan ratchet for code with no
caller. It has nothing equivalent for its own instruments. The problem to solve
is that **a measurement that quietly stopped is indistinguishable from a
measurement that is reporting nothing to report** — and the system currently
cannot tell those apart about itself.

### 3. The alarm runbook has decayed exactly as the literature predicts

`docs/design/ALARM_RESPONSE_RUNBOOK.md` is dated 2026-07-13, says of itself
"This table is a snapshot, not a living index", and assigns two of its ten rows
to `session_watchdog` — a daemon `background/README.md` records as replaced.

The book is unusually direct here: *"wrong documentation is perhaps more
dangerous than no documentation"*, and *"in fast-changing systems,
instrumentation itself is often the best possible documentation."* It does
carve out an exception worth keeping — ownership, escalation path and entry
points are worth writing down; the attempt to enumerate every failure is not.

The problem is that this table is hand-maintained while the thing it describes
is declared in machine-readable form elsewhere.

### 4. The register directory is a semantic failure in the book's own sense

`docs/observability/` holds 317 files with no README and no index, and roughly
90 of its 160 JSONs are simulation experiment output rather than telemetry —
one location, two meanings.

Chapter 17's whole thesis is that semantic failures are invisible to
conventional monitoring because nothing is broken, only ambiguous. The book
tells the same story twice — in chapters 8 and 21 — of an agent that misread a
field named `is_slow` as a feature flag because nothing described what it was,
and went "off on a wild goose chase". **The fix was adding a description.**

A fresh session reading this directory is in precisely that agent's position.
The project already has `background/derived_artefact_register.py`, so the
concept exists; the question is whether it reaches the registers.

### 5. No service level indicator — and the textbook version would be wrong here

`H4_GO_LIVE_NFR_REGISTER.md` line 17 states plainly that no formal SLO or
availability target has ever been set. `PRODUCTION_READINESS_PARTS_BC.md` row
B3 states that alerting fires on process and build transitions, "not on service
SLIs (because no SLI/SLO exists)". `G9_error_budget_toil_tracking` is fully
specified, has zero implementing code, and sits at level 1, `loop_stage: idle`,
in the **closed** map.

The book's argument is that threshold alerting is only ever a tool for
known-unknowns, and that thresholds on internal state are "potential-cause
indicators" that fuse symptom with cause. Every alarm here is a hand-set
constant about the machine's own internals — 45 minutes, 90 minutes, 6 hours,
7 days plus 24 hours of grace. None is derived from a measured distribution.

**But the textbook remedy does not transfer.** The book's own case study is
explicit that SLOs need "actual users depending on the systems you've built"
and "real scale". This system has one user and a weekly publish. A literal SLO
programme here would be cargo cult, and the existing G9 guardrail already
anticipates the trap: *"a 0 toil target would incentivise HIDING self-caught
failures."*

The adapted question, which is a real one: **the director is the user.** The
service he receives is *learning what he needs to, when he needs to*. That is
measurable as an event-based rate over the notification channel — of the things
that warranted his attention, what share reached him; of the pages sent, what
share were real. The transition records and the five filed repeating-alarm
documents are most of the raw material already.

Related, and the single best candidate metric this project could adopt: the
no-caller census found **eight of thirteen instances were found by accident.**
The book's own test of whether a learning investment is working is *"issues
found internally before customers escalate"*. The local form is *found by a
control, before the director notices* — and it is countable from the staging
corpus today without building anything.

## Decided, and open

**Decided (director):** this is worth the machine's attention, ranked by it,
not ahead of the current direction. The five gaps are accepted as real; the
advisor verified each against origin.

**Open (machine's judgement):** whether any of them is worth closing now, in
what order, and by what mechanism. The advisor has deliberately not specified
mechanisms, file formats, cadences or thresholds — several of these have
obvious-looking answers that are probably wrong, and the machine knows the
environment.

**Open (director, raised separately):** the 25 July N-versus-λ call that walls
the activation ruling.

## Reserved — not authorised by this document

- No OpenTelemetry, no tracing SDK, no metrics collector, no agent. The book
  advocates these for distributed services under real traffic; this is a
  single-machine build loop and the advice does not transfer.
- No SLO or error-budget build. G9 stays where it is.
- Nothing that touches the epistemic wall.
- No change to any existing alarm threshold on the strength of this document.

## Risk

**Touches:** at most `docs/observability/` layout, one or two registers, and a
design document. Nothing in the simulation, nothing on the wall, nothing
published.

**Blast radius:** narrow. The largest item — a per-run ledger row — is additive
and append-only; it changes no existing figure.

**Probable failure mode:** this document is itself an instrument with no
caller. It describes a class of problem (things that stop and nobody notices)
and could join that class. The second risk is the opposite: that it reads as
five tasks and gets built as five mechanisms, when the honest answer may be
that only one earns its place.

**Inline mitigation:** report-and-rank, not build. If the ranking says none of
it is worth doing now, that is a legitimate outcome and should be recorded as
one rather than leaving the document to drift.

**Proportionality:** reversible and narrow — just do it, at whatever rank it
earns.

## Epoch arc

Epoch 1 — the governance and evidence substrate, not company machinery. The
subject throughout is the harness's knowledge of itself, never the simulated
company's knowledge of its customers.
