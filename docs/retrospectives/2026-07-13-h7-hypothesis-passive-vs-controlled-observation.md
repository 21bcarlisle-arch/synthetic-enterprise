# 2026-07-13 — H7's "dedup-per-context-boundary" hypothesis was wrong; passive log observation isn't a controlled test

**Claim discipline (R9): everything below is observed-with-evidence.** The log-line counts, tool-call
sequence, and timestamps quoted below are read directly from `docs/observability/
instructions_loaded_log.jsonl` and this session's own tool-call transcript (Bash sed/grep calls vs.
Read-tool calls), not inferred or reconstructed from memory.

## What happened

`H7_skills_and_rules` (harness skills/`.claude/rules/` adoption) needed to verify that the path-scoped
epistemic-wall rules (`.claude/rules/epistemic-wall-company.md`/`-sim.md`) actually fire when a matching
file is read. A hook (`background/hooks/log_instructions_loaded.py`) logs every real load event.

Across three earlier self-refill turns (2026-07-12 21:05, 22:25, and three further sim-rule entries at
00:12/00:23/00:38 the following day), the log grew only sporadically — sometimes a session would touch
many `company/**` files with no new log line appearing at all. The registered hypothesis, entered into
`docs/design/maturity_map.yaml` as real progress, was: **the rule injection deduplicates within a
rebuilt context** — it fires once per compaction/context-rebuild boundary, not per matching read. This
was treated as "real, honest, more nuanced" progress and left as the standing explanation across two
separate simplification entries.

It was wrong. This turn, a controlled test (not a passive observation) disproved it directly:
1. Captured the exact log line count (7).
2. Made a genuine **Read-tool** call on `company/crm/vulnerability_register.py` — a file only ever
   touched via `Bash sed -n`/`grep` earlier in this same session, never via the Read tool. The rule
   fired immediately (visible as a system-reminder in the same tool result), and the log grew to 8
   lines in the same turn, with no context-rebuild boundary anywhere nearby.
2. Made a genuine Read-tool call on `tests/company/governance/test_decision_rights.py` (a deliberate
   near-miss — the glob `company/**/*.py` should not match a `tests/company/` prefix). No rule fired,
   log stayed at 8.

Checking back: every file this session had been "missing" a fire for — `company/crm/home_registry.py`,
`property_model.py`, `energy_profile.py`, `company/compliance/domain_invariants.py` — had been read
via Bash (`sed -n`/`grep`), never via the Read tool. The real mechanism is **Read/Edit-tool-triggered
path matching**; a `Bash cat`/`sed`/`grep` of a wall-scoped file does not get the reminder injected at
all. This has nothing to do with context-rebuild boundaries.

## Root cause, not the instance

The dedup-per-boundary hypothesis wasn't a wild guess — it was a real inference from real data. But it
was built from **passive, incidental observation**: noting the log's growth (or non-growth) across a
session where many different variables were changing at once (which tool touched the file, how long ago
the last compaction was, which specific files were read). With multiple uncontrolled variables moving
together, a plausible story fit the data without being the true cause. The confound (tool type) was
never isolated because it was never deliberately varied — every "missing fire" happened to be a Bash
read, and every session boundary happened to coincide with heavy Bash-based investigation work, so the
two explanations looked observationally identical until a real controlled test held one variable fixed
(read the same class of file, vary only the tool) and checked the other in isolation.

**The general lesson:** correlational observation across an uncontrolled, naturally-varying session is
not equivalent to a controlled experiment, even when it's repeated multiple times and each repetition
is honestly logged as "further supported." A hypothesis earns "confirmed" only once a deliberate test
isolates the one variable in question — not once a pattern has been observed to persist across several
incidental checks. This project's own maturity-map discipline already distinguishes DISCOVER (research)
from VERIFY (deliberate testing) as different rungs on the ladder; this incident is a concrete case of
prose in a simplifications entry claiming VERIFY-grade confidence ("further supported... not just
consistent with it") on DISCOVER-grade (passive-observation) evidence.

## The fix, verified not asserted

Already done, this same turn, not deferred: the controlled Read-tool positive-match and near-miss tests
above were run directly, with the log file checked before and after each, and the results are what
closed `H7_skills_and_rules` to level 3 (see that atom's own 2026-07-13 simplifications entry,
commit `5264f145`). This retro records the methodological lesson; the technical fix already landed.

## The class-level lesson (R10)

This is a real, generalisable measurement-discipline gap, not a one-off wrong guess about one hook.
Any future atom investigation that infers a mechanism's behaviour from **observing logs/outputs across
multiple incidental actions within a live working session** (rather than a single deliberately-designed
before/after test) should label that inference as a **hypothesis (DISCOVER-grade)**, not a **finding
(VERIFY-grade)** — regardless of how many times it has "held up" under further incidental observation.
Repeated incidental consistency is not the same evidentiary class as one controlled test, and conflating
the two lets a wrong causal story accumulate false confidence turn over turn (exactly what happened
here across three separate self-refill passes).

## What was NOT lost / genuine scope of harm

No harm beyond wasted investigation time across roughly three self-refill turns spent narrating and
re-confirming a wrong hypothesis instead of running the one controlled test that would have settled it
in a single turn. No incorrect BUILD code shipped, no external-facing claim was ever made from this
finding (it stayed inside `docs/design/maturity_map.yaml`'s own simplifications trail), and the eventual
correction was clean and complete — H7 is now honestly at level 3 with real, controlled evidence behind
it.

## Follow-up (done inline)

Audited whether any other atom's simplifications entries this session made a similarly VERIFY-grade
claim ("confirmed", "further supported", "resolved") from passive/incidental observation rather than a
deliberate controlled test. The other atoms touched this session (W1_reveal_over_time's EWMA-weighting
quantification, W2_2/W2_4/W2_8/C4/B4/A3's architecture FRAME findings) are all grounded in direct code
reads and grep-confirmed absence/presence of call sites — a different, sounder evidentiary class (static
inspection of the actual current source, not inference from a live process's intermittent behaviour
over time) — so this specific gap is not currently repeated elsewhere in this session's own work.
