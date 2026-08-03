# HX2 — Stall-set coverage verdict on the four director-named events

**Atom:** `HX2_stall_set_coverage_verdict` (lane H_harness, dial 3).
**Source:** `docs/staging/done/DIRECTOR_RULING_HARNESS_EXIT_CRITERION_RATIFIED_2026-07-27.md` §3 — the
director ratified the exit criterion and then returned four events that actually happened, asking
whether the proposed stall set covered them. He returned this as a **problem, not a prescription**.
**Mechanism:** `background/stall_class_register.py` — the single enumeration.
**Tests:** `tests/background/test_stall_class_register.py` — 28 passing, 8 mutations below.

---

## Why the question was the right one

The ratified criterion is *"three consecutive product-content advances across a span in which the
STALL-class intervention count is ZERO"*. A count of stalls is only as honest as the **set** of things
called a stall, so a hole in the set does not read as a hole — it reads as a **clean span**. That is the
FAIL-SILENT pattern R15 names, sitting directly under a promotion gate.

The proposal (`docs/design/HARNESS_EXIT_CRITERION_PROPOSAL_2026-07-27.md` §2) listed five classes and
asserted **"Each has an existing detector."** That assertion is false. Checked against real code this
tick, **three of the five have no detector**, and two of them still do not (§6 below). The director's
four events were not the only gap; they were the ones he could see from outside.

---

## The verdicts

### E1 — EMERGENCY CONSOLE RESCUE → **DETECTOR ADDED (as an over-inclusive fallback), with a stated limit**

**Verdict: not directly detectable in this repository, and that is a structural fact, not an omission.**

A granted console turn leaves **no trace in this repo**. `background/director_input_log.py` does tag
console turns (channel `window`), but writes them to the **private** `synthetic-enterprise-ops` repo
(`background/director_input_log.py:4-5`, `:45` — `from background.ops_repo import ...`). So a third party
with repository access — the ruling's own acceptance test — cannot see a console rescue at all. Grep for
a console-rescue detector across `background/` and `tools/` returns **nothing** but this register's own
comments.

What *is* visible is the **silence the rescue ended**. `meaningful_progress_gap` therefore covers E1 by
construction: a rescue implies a gap, so every rescue is inside the detected set. It is deliberately
**over-inclusive** (guarantee G5) — a gap the machine got out of by itself also lands here, and under R17
("the tick never rests while authorized work exists") that *is* a stall. Counting it costs only a delayed
harness decision; missing it would grant an unearned clean span.

**Honest bound, stated not hidden:** this detects *that* the machine went quiet, never *that a human was
summoned to the terminal*. If the director wants the rescue itself counted rather than its shadow, the
console channel has to reach this repo's primary state — that is a change to `director_input_log.py`'s
destination, and it is his call, not the agent's, because the reason it is private is his own privacy
amendment. **Recommendation: leave it private and keep the over-inclusive proxy.** The proxy never
under-counts, and the alternative leaks console content into the public repo to win precision on a
counter that only gates one internal decision (R12).

**Evidence it fires on the real thing.** Run over real git history this tick, the detector recovers the
**4-day publish blackout** with no prompting: a `5907 min` (98.4h) gap, 2026-07-30 01:37 → 2026-08-03
03:05, unattributed to any director input, resumed by `1325f2bb9` *"fix(publish gate): an RNG-derived
literal wedged publishing for 4 days"*. Nothing told it that incident existed.

### E2 — PUBLISH-GATE WEDGE > 1h → **ALREADY DETECTED (adapted, not rebuilt)**

`background/supervisor.py::_publish_gate_wedge_active` already fires at exactly the director's bar:
`PUBLISH_GATE_WEDGE_MIN_AGE_SECONDS == 3600` — verified live this tick. It carries an independent
`.last_tested_hash` cross-check, so it is not reading the wedge state against itself.

`detect_publish_gate_wedge()` is a thin **adapter** that wraps that verdict as a `StallEvent`. No new
predicate was written. Rebuilding it would have created a second definition of "wedged" free to drift
from the one the supervisor actually acts on — the accretion `OPERATIONAL_LAYER_DESIGN` forbids.

**Inherited fail-safe, stated:** an absent or malformed state file yields *no* wedge. That is correct in
the supervisor (a phantom RUNG-1 draw would displace real work) and acceptable here, because this class
is `point`-kind anyway: `.publish_gate_state.json` is overwritten in place and never committed, so past
wedges are **not reconstructible**. HX1 must therefore **sample** this each tick; it cannot audit a span
for it after the fact. That constraint is a property of the state file, and it is why the class carries
`evidence_kind="point"` rather than a false claim of span coverage.

### E3 — ORIGIN FREEZE / PUSH FAILURE > 30 min → **DETECTOR ADDED**

`background/process_run_complete.py::_push_reached_origin` (`:1404`) already makes **one push attempt**
honest — `rc=0` is not enough, `ls-remote` must show origin at local HEAD. What nothing measured was
**duration**. The 3.5h freeze was a run of individually "handled" attempts while real commits stacked up
locally; every single attempt was checked, and the standing condition was still invisible.

`detect_origin_freeze()` measures the standing condition: oldest unpushed commit vs now, threshold
`30 min`. The threshold is not arbitrary — it is exactly `process_run_complete.PUSH_THROTTLE_SECONDS`
(`:80`, `30 * 60`), so a freeze reaching the bar means at least one whole push cycle produced no advance.

**Anti-tautology, deliberately:** the remote head comes from `git ls-remote`, **never** the local
remote-tracking ref. The tracking ref is the very thing that goes stale in this failure — reading it
would be checking the phantom against the phantom. Pinned by
`test_origin_freeze_never_reads_the_local_tracking_ref`.

**Fail-closed:** origin unreachable → `unavailable=True`, never "no freeze". Autonomous runs often have
no network, and an unavailable check is a FAILED check (R15), not a clean one.

### E4 — ADVISOR RULING WHOSE PURPOSE IS RESTARTING STALLED WORK → **DETECTOR ADDED**

`stall_ended_by_director_or_advisor_input`, carrying `channel` so an advisor-bridge ruling (E4) is
distinguishable from an NTFY steer.

This is the part that **binds the advisor**, per the ruling: if the machine must be doorbelled awake by a
staged document, the counter resets. And it is where the **stall/decision split the ruling praises** is
mechanised rather than exhorted:

- An input arriving **while meaningful commits are flowing** produces **no event at all** — there is no
  gap to attribute it to. That is "director DECISION-class touches unrestricted", in code.
- The same input arriving **into a silence**, followed by resumption within an hour, is a **RESCUE**.

**Evidence it fires on the real thing.** Over the 2026-07-24 → 07-28 window the detector independently
recovers the known **42h pending-batch deadlock**: a `1786 min` (29.8h) gap ended `25 min` after the
advisor-bridge input *"[DIRECTOR-RULING][ADVISOR-STAGED] EIGHTH CLASS — pending-batch deadlock"*. Nine
stall events surfaced in that window, seven attributed to the bridge.

**One non-obvious correction this required.** A commit that merely **stages** a director/advisor document
is *input*, not the machine's output, and must not count as progress. Found by running the detector
against the real deadlock: the advisor's own staging commit counted as the machine resuming work and so
**hid the very rescue it was**. Counting a doorbell as progress makes a doorbelled stall undetectable by
construction. Pinned by `test_a_staging_commit_is_input_not_progress`.

---

## R15 — mutation proof (exit criterion 2)

Eight mutations, each firing **exactly its own named test**; baseline restored green (28/28) afterwards.
A register *of stall classes* is itself a control, so this is the acceptance, not decoration.

| # | Mutation | Killer pattern | Test that fired |
|---|---|---|---|
| M1 | staging commit counts as progress | tautology (doorbell = its own answer) | `test_a_staging_commit_is_input_not_progress` |
| M2 | attribution window unbounded | over-attribution | `test_input_long_before_resumption_is_not_credited_as_the_rescue` |
| M3 | git unreadable returns `[]` | FAIL-OPEN | `test_git_unreadable_is_unavailable_not_clean` |
| M4 | vanished detector silently ignored | FAIL-SILENT | `test_registry_fails_loud_when_a_named_detector_vanishes` |
| M5 | origin unreachable reads clean | FAIL-OPEN | `test_origin_unreachable_is_unavailable_not_clean` |
| M6 | freeze threshold ignored | false positive | `test_origin_freeze_quiet_inside_the_push_throttle` |
| M7 | uncovered classes omitted not named | FAIL-SILENT | `test_uncovered_classes_are_named_not_omitted` |
| M8 | wedge adapter always fires | false positive | `test_wedge_adapter_quiet_below_the_bar` (+ `..._when_the_gate_passed_at_head`) |

Both directions are covered per the ruling's demand: each detector **fires** on a synthetic instance of
its named event **and stays quiet** on the benign look-alike — most importantly the legitimate director
DECISION-class touch, which is explicitly unrestricted and must never trip the rescue detector
(`test_quiet_on_a_director_decision_during_healthy_progress`).

---

## The union set (exit criterion 3) — and the two holes it does NOT close

`STALL_CLASSES` in `background/stall_class_register.py` is the **whole set**, in one readable place, so
HX1 cannot silently miss a class. **9 classes, 7 with a live detector.** Every named detector is
import-checked at call time (`resolve_detectors()` raises `StallRegistryError`), so a renamed or deleted
detector fails **loudly** instead of degrading into a quietly smaller stall set.

A class with no detector is listed with `detector=None` and reported as **UNCOVERED** — never omitted.
An omitted class is invisible; a named hole is auditable. The two holes, both inherited from the
proposal's own five and both independently re-verified against real code this tick:

- **`harden_while_content_unminted`** — `supervisor.py:1957 _unconsumed_director_ruling_or_steer` is a
  **suppressor** (it gates the Rule-0 HARDEN tier at `:3575`), and suppression leaves **no event
  record**, so a span cannot be audited for it. Closing this is HX1's scope; HX2's duty was that it is
  not *silently* missing.
- **`act_later_ruled_reversible`** — `action_needed.resolve_item(item_id, answer, ...)` stores the
  director's answer text but **no reversibility verdict**, so "later ruled reversible" is not
  machine-readable. Would need a verdict field at resolve time.

**This is the load-bearing consequence, and it is deliberately not softened:** while either hole is open,
**a zero stall count is not proof of a clean span**, and HX1 must not treat it as one. The daily
self-note publishes that verdict every morning (`coverage_line()` → 🟠 while uncovered), so the hole is
visible each day rather than discovered at the moment someone wants to claim the harness is done.

**R12:** nothing here is a fidelity, maturity or product-quality measure. It gates one decision — may
harness investment resume — and must not appear in any quality claim. A count of stall classes is a
**diagnostic, never a target to drive to zero**.

---

## Provenance note

The mechanism and its tests were written in a fork that **died before committing** and were recovered as
untracked files (`docs/staging/WORKER_FINDING_DEAD_FORK_RESCUE_AUDIT_2026-08-03.md`). They were adopted
rather than rebuilt, but **not merged blind**: every named detector was re-resolved against main's real
code, the two "uncovered" claims were re-verified against `supervisor.py` and `action_needed.py` rather
than taken on the fork's word, all 8 mutations were re-run, and the detectors were run against **real
git history** — where they recovered both the 42h deadlock and the 4-day blackout unprompted. This
verdict document did not exist in the fork; `coverage_line()` cited it as a dangling reference.
