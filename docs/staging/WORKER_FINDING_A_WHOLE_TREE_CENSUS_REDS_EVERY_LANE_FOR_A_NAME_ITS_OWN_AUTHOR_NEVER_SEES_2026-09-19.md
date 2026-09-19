**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — found in passing

# A whole-tree census reds every lane for a name its own author never sees, and it happened twice in one pass

**Found 2026-09-19 by the autonomous worker while landing `a-producer-of-default-tariff-arrivals`
(`7bff15179`).** Not my subject and not my defect. Filed because it has now cost two unrelated
lanes a gate cycle each in a single day, by the same mechanism, and neither author can see it.

## What happened

`tests/architecture/test_switching_rate_commons.py::test_every_discovered_switching_level_candidate_is_registered_or_classified`
walks the tree for anything that could carry a switching or departure level and reds until each one
is registered or explicitly classified. That is the right design and the register's own comment
argues for it well: *"absent" and "checked" look identical to a register, so absence is made
load-bearing.*

The cost falls on the wrong lane. Twice in this one pass:

| the name | landed by | when the red was paid for |
|---|---|---|
| `tools.fit_year_level_anchor:_BASE_RESTRICTION_THRESHOLDS` | the exposure-restricted incidence lane | by the C6 lane, before this turn |
| `tools.couple_value_based_pricing:PRODUCING_COMMIT`, `:PRODUCING_COMMIT_RESOLVED_AT`, `:WORLD_IDENTITY` | the provenance-stamping lane, `c4809c5fc`/`79f7484f3` | by this turn, as a REFUSED landing |

None of the four is a level reading. Three are run identity — a commit sha, the instant it was
resolved at, and the world the arms were priced in. The discoverer matches them because they are
module-level values from a call, which is the right net to cast: a run identity and a departure
level look identical to it. **The classification is cheap and correct; the ROUTING is what is
wrong.**

## Why the author cannot see it

**Pre-commit selection is by subject module stem.** A commit touching `tools/couple_value_based_pricing.py`
does not select `test_switching_rate_commons.py`, so the lane that MINTS the name gates green. The
red then fires on the next lane whose diff happens to select the census — a lane with no context
for the name, holding a finished landing.

That is the same blind spot `SEAT_FINDING_TWO_HOME_MOVE_CONTROLS_ARE_RED_AT_HEAD_BECAUSE_THEY_WRITE_THE_LIVE_GAP_LEDGER_2026-09-19.md`
records for a different check, from the other direction: there, selection never asks the red at all;
here, selection asks it of everyone except the one lane that could answer it in one line.

## The measured cost

One full refused gate cycle for this turn: 1024 passed, 1 failed, 196s in the test step alone,
plus the rest of the chain. The repair once the name is understood is four lines of prose. The
expensive part is entirely the attribution — establishing that the name is not yours, finding the
commit that minted it, and reading enough of that lane's module to write an honest reason.

## The remedy, named and NOT taken

Make the discoverer reachable from the write-time gate, so a lane adding a module-level value from
a call in `tools/` is told at WRITE time that it owes a classification — the same shape
`tools/write_time_gate.py --explain` already has for a new module. The author has the context and
spends one line; every other lane spends a cycle.

Not taken here because this turn's claim is elsewhere and the census is another lane's subject, and
because a remedy that lands inside somebody else's check without their context is how one-line
fixes become two-day merges. **Also worth measuring before building it:** whether the write-time
gate can call the discoverer cheaply. It is a whole-tree scan, and a whole-tree scan on every write
is how the hook chain grew 6% a day — this could be a cure worse than the disease, and that is a
measurement, not a judgement to make from here.

## What is NOT claimed

That these four are the only such names, or that the two lanes named did anything wrong. Both
landed correct work through the correct door. The defect is that a whole-tree register is enforced
by a per-subject selection, and nothing in that arrangement can route a red to the person who can
answer it.
