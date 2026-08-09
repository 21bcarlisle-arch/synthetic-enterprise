# The scale-constraint checks — making C-S1..C-S5 executable

**Atom:** `AO4_scale_constraints_executable` (lane `H_harness`, L0→L2, `depends_on: AO3_join_test_tier`)
**Constraints:** `docs/staging/done/PRODUCTION_READINESS_SCALE_ADDENDUM.md` (director-decided 2026-07-13)
**Sources:** `docs/staging/DIRECTOR_PROGRAMME_ARCHITECTED_OUT_2026-08-05.md`,
`docs/staging/ADVISOR_FINDINGS_STRUCTURAL_AUDIT_2026-08-04.md`
**Built:** 2026-08-09

---

## 0. Purpose, guarantee, why — before any mechanism

**Purpose.** Five standing design constraints have governed this codebase since 2026-07-13
as *prose in CLAUDE.md*. Prose-only rules decay — that is this project's most repeatedly
proven finding (MAKE_IT_STICK: every rule that held was a mechanism; every rule that
evaporated was an exhortation). This turns each of the five into something that can fail.

**Guarantee.** For each of C-S1..C-S5 there is a check that (a) runs against **real
production functions or real repository state**, never a restatement of them, and (b) is
**mutation-proven to fire** on that constraint's own named defect. Where a constraint is
only partly mechanisable, the residual is written down in §3 rather than left silent.

**Why now, and why not more.** The addendum's own words: *"the constraints that make logic
scale-safe are cheap today and brutal to retrofit."* Every one of these defects is invisible
to the simulation by construction — sim-time hands a whole period's events to the code at
once, so nothing is ever late, duplicated, out of order, or slow. **The sim cannot surface
this class. Only a check can.** And per the addendum's own SIMPLICITY GUARD (amendment A3),
this adds 13 standing checks, 22 R15 proofs and one YAML register — no abstraction layers, no adapters, no
infrastructure-shaped code with no infrastructure behind it.

---

## 1. The five constraints and their checks

All in `tests/system/`. Probes and assertions live in `scale_constraints.py`; the standing
checks are `test_scale_constraints.py`; the R15 proofs are `test_scale_constraint_mutation.py`.

| # | Constraint | Check | What it runs against |
|---|---|---|---|
| **C-S1** | Event-arrival tolerance | the same settlement records, permuted, must produce the same bill; a late-arriving fact must resolve by transaction time, not append order | `saas.bill_generator.generate_bill`, `company.interfaces.bitemporal_event_log` |
| **C-S2(a)** | Idempotency / replay | delivering the same event twice, and re-running the same valuation, must not change the answer | the real log + the real bill generator |
| **C-S2(b)** | RNG substream discipline (A1) | no module in `simulation/`, `sim/`, `company/`, `saas/` draws from the **process-global** `random` stream; and burning 500 draws on one named substream leaves another **bit-identical** | AST scan of 620 modules + `simulation.population_draw._substream` |
| **C-S3** | Asynchronous wall contracts | a request must be observable as **pending** while unanswered, and the answer's latency must be the **measured** gap, never the SLA | `company.governance.decision_rights` submit/resolve/pending |
| **C-S4** | Persistence behind an interface | every **declared** derived copy of durable state must agree with its source **as published**, and no durable state may be duplicated **outside** the register | `tools.mirror_github_pages._STATE_JSON_FILES` + the blobs at `HEAD` |
| **C-S5** | Time-scale invariance declaration | every company-side atom at L3+ must be declared, excepted, or in the frozen landing amnesty | `docs/design/maturity_map.yaml` × `docs/design/TIME_SCALE_INVARIANCE_REGISTER.yaml` |

**C-S2(b) closes the addendum's own open DoD item 4** — *"RNG substream discipline implemented
and proven: adding a draw to one subsystem leaves all other subsystems' streams bit-identical
(test it)"* — which had been deliberately deferred since 2026-07-13 as too risky to rush. The
audit it was waiting for turns out to be **already done**: the scan finds **zero** modules
drawing from the shared stream across all four packages. The named-substream pattern the
addendum wanted generalised (`life_events.py`'s rng/econ_rng split) is present in
`population_draw.py`, `household_segments.py` and `demand_model.py`, and the property is now
asserted rather than asserted-about. What remains open is the *sub-item's other half*: this
guard prevents a regression, it does not prove every existing substream is seeded from a
genuinely independent salt.

---

## 2. Report-only landing — same terms as the join tier, sharper reason

`scale_report_only` is registered in `tests/conftest.py`, and
`background/process_run_complete.py::PUBLISH_GATE_MARKER_EXPR` is
`"not operational and not join_report_only and not scale_report_only"`.

The join tier's reason was brittleness. **This tier's reason is stronger**: these checks
*measure the repository as it is*, so a check can go red because the codebase is genuinely in
breach — and the atom's own registration says so in advance (*"one of the five is already
breached and the check should fail on landing. That is the correct outcome, not a reason to
soften the check"*). The only two responses to a truthful red are *fix it* or *soften it*, and
softening a measurement because you dislike the reading is R12. Deselecting it is how a
truthful red **alarms without wedging the live site**.

(As it landed, only C-S3's residual is outstanding — see §3. The breach the registration
predicted, C-S4, turned out on correct measurement not to be one, which is itself the answer
to a finding that had been open since 2026-08-04.)

Three things keep that honest:

1. **Its own marker, not the join tier's.** One shared marker would mean promoting either
   tier out of report-only promotes both. They earn their stable weeks separately.
2. **The complement widened with it.** `OPERATIONAL_LAYER_MARKER_EXPR` is now
   `"operational or join_report_only or scale_report_only"`, so the tier is deselected from
   the content gate and **covered by the independent-cadence signal** — deselected must never
   mean *covered by no gate* (R11; `feedback_deselecting_a_marker_orphans_the_tier`).
   Persistent-red paging (≥2 consecutive hourly checks) means a transient mid-publish lag
   cannot page, but a standing breach does.
3. **Containment.** No module outside `tests/system/` may carry either marker, and every
   module inside it must carry **exactly one** — enforced and mutation-proven in
   `test_report_only_landing.py`.

**Promotion condition (a stable week).** Drop `not scale_report_only` from
`PUBLISH_GATE_MARKER_EXPR` once the tier has run a full week without a false red, and drop the
matching disjunct from the complement. Do not shorten it because day one is green.

---

## 3. What is red today, and what is not mechanised

The atom requires each constraint to get a standing check **or be listed as not-mechanisable
rather than dropped**. All five got a check. What follows is the honest residual — the part of
each constraint the check does **not** reach. An index that under-reports its own gaps
authorises the thing it was built to prevent (`feedback_index_is_a_fail_open_control`).

### C-S3 — a same-instant answer is still writable (KNOWN RED, registered)

`resolve_decision_request()` accepts `resolved_at == submitted_at` and records a `0.0s`
latency. The mechanism **represents** the pending interval but does not **require** one, so
A4's named exemplar — the DD-mandate submit-and-resolve-in-the-same-step bug — is still
writable against the very mechanism built to replace it.

Carried as `test_cs3_a_same_instant_answer_is_rejected`, `xfail(strict=True)`: it records the
gap without crying wolf, and it **fails the day the mechanism is fixed**, forcing the xfail
off rather than leaving a green lie behind. The fix is out of this atom's `file_scope`
(`tests/system/` + this doc), so it is queued, not fixed on sight
(SELF_INTERRUPT_DISCIPLINE — the supply of findings is infinite).

### C-S4 — FINDING 2 answered: legitimate publish-time snapshots

The structural audit asked a question the advisor could not answer from outside: *"are these
publish-time snapshots (legitimate) or genuine forks (not)? You can [tell]."*

**Measured answer: snapshots, and the finding closes.** `site/state/` (and `site/data/`) are
written by the generators; `docs/state/` is a pure copy step declared in
`tools/mirror_github_pages.py::_STATE_JSON_FILES` and run at the end of the same publish
pass. At HEAD, all four declared pairs — `billing_ledger.json`, `customer_sample.json`,
`population_anchoring.json`, `sim_data.json` — agree exactly. One source, one declared derived
copy, no fork.

**The measurement mistake that produced this check's final shape is worth recording**, because
it is a shape that will recur. The first version compared the two copies **in the working
tree** and went red on all three, which reads exactly like the fork the finding feared. It is
not. A publish pass writes `site/state/` at line ~935 of `process_run_complete.py` and copies
it to `docs/state/` at line ~1269, so for a window in **every single pass** the two disagree
on disk and *nobody is wrong* — the copy step has not run yet. Timestamps caught it: the
source was 36 seconds newer than the copy, with a publish pass still running.

So the check reads the **committed blob** (`git show HEAD:<path>`), not the working tree.
That is not a tolerance or a fudge — it is the more correct measurement on its own terms:
`docs/state/` is served by GitHub Pages straight from this repo on every push, so the commit
*is* what the consumer fetches (R11), and a publish pass commits both sides together, which
means a disagreement there has no benign explanation. The generalisable lesson: **a control
over a multi-step pipeline must be sampled at a point where the pipeline is quiescent**, or it
measures the pipeline running rather than the property. A control that reds during normal
operation gets ignored, and an ignored control is worse than none.

`_read_published` therefore has its own non-vacuity test proving it reads HEAD and does *not*
fall back to the working tree — a silent fallback would reintroduce the window while every
other test kept passing.

### C-S1 — the check covers ORDER and LATENESS, not PARTIALITY

"No company-side logic may assume batch completeness" has a third failure mode the checks do
not reach: logic that is correct under any *order* of a complete set but wrong on an
*incomplete* one (a month billed from 40 of its 48 periods). Mechanising that means deciding,
per surface, what an incomplete set should DO — refuse, estimate, or wait — which is a design
question per call site, not a property assertable over the codebase. **Listed as
not-mechanisable at the class level**; it belongs in each surface's own atom.

### C-S2 — replay is proven at the SUBSYSTEM level, not the RUN level

"Replaying an event history must reproduce identical state" is checked as *no shared stream*
and *substream independence*. Full-run replay determinism (the same 2016-2025 replay twice,
byte-identical) is a whole-run harness property, not a unit assertion, and the existing
`process_run_complete` output gate already covers the instance that bit (the 01:09Z
incident). **Not duplicated here** — a second copy of that check would drift from the first.

### C-S5 — a declaration is a judgement, and 23 of them are outstanding

The check enforces that the question has been *answered*, not that the answer is *true*. It
cannot: time-scale invariance is a property of intent, so only the atom's owner can state it.

Twenty-three company-side atoms were already at L3+ when this landed and owe a declaration.
They are written down in `TIME_SCALE_INVARIANCE_REGISTER.yaml` under `undeclared_at_landing`
and pinned **exactly** by `FROZEN_CS5_BASELINE` in the test — a new undeclared L3+ atom fails,
and so does an atom that gets declared but is left in the amnesty. Clearing them is
remediation-on-touch (canon's own ruling on retroactive application), not a sweep.

The register is seeded with one real exception: `W5_1_banking_payment_rails`, the DD-mandate
same-step simplification, per the addendum's amendment A4.

---

## 4. R15 — the fail-open shape to hunt here

> *A constraint check that passes when the constraint is broken.*

Every check carries a proof that it fires on its own defect, in
`test_scale_constraint_mutation.py`. The discipline:

- **The assertion that ships is the assertion that gets proven.** Probe and assertion live in
  `scale_constraints.py` and are imported verbatim by both modules. A mutation test with its
  own copy of the assertion proves something about the copy
  (`feedback_tautology_reappears_inside_r15_tests`).
- **The cut is in the production source**, monkeypatched at the module attribute the probe
  actually calls — except where the check's subject *is* a file population, where the
  population is mutated and handed to the same shipped assertion.
- **Both directions where it matters.** C-S4 is a check that was red on arrival, so it is
  also proven to go **green** on a clean fixture — a control that can only fail is not a
  control, it is a wedge with a diagnostic message
  (`feedback_control_that_can_only_fail_wedges`). Same for C-S3's residual, and for the
  RNG scan, which is proven **not** to fire on `random.Random(seed)` — the compliant
  construct — because a false-positive guard jams the pipeline against correct code.
- **Vacuity and fail-silence are proven, not assumed.** Every check that reads a population
  asserts its own non-emptiness, and the mutation suite proves each one *fails* when pointed
  at a package that does not exist or a map that parses to nothing. An unavailable check is a
  FAILED check.
- **The probes assert their own premises.** The permutation must genuinely permute; the three
  facts must genuinely differ; the two substreams must genuinely be different streams. A
  comparison whose inputs are identical passes for reasons that have nothing to do with the
  constraint (`feedback_population_control_needs_a_vacuity_guard`).

One R15 note the mutation work turned up and is worth keeping: `BitemporalRecord` is a
**frozen** dataclass, so the obvious "just mutate the stored value" cut is not available and
the mutation has to replace the entry. That is the append-only constraint holding at the type
level, not the test being awkward.
