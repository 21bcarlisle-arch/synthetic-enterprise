# The write-time gate — AO2, the step that spends the index

**Atom:** `AO2_write_time_reuse_gate` (lane H_harness, L0→L2, 2026-08-08).
**Serves:** `DIRECTOR_PROGRAMME_ARCHITECTED_OUT_2026-08-05.md` step **MAP**, second half, plus the
same-day director amendment adding the ecosystem question and the three part classes.
**Mechanism:** `tools/write_time_gate.py`, wired at `tools/git-hooks/commit-msg`.
**Proof:** `tests/tools/test_write_time_gate.py` — 41 tests, 8 source mutations.
**Depends on:** `AO1_capability_index` (`docs/design/CAPABILITY_INDEX.md`) — reused verbatim, never
re-derived.

---

## Purpose, guarantees, why — before the mechanism

**Purpose.** Make the *look* leave a trace. Before a new capability module lands, the commit records
what the index answered and what the ecosystem answered.

**Why, in the director's own accounting.** The programme names one cause — **write-time blindness**:
each turn's cheapest move is to write fresh, because discovering what exists costs more than
creating it. AO1 changed the price of looking. Nothing yet changed the price of *not* looking, and
the director's framing is blunt: the index is a demo until this exists. §5 names this "the only
immediate behaviour change" in the whole programme.

**Guarantees.**

1. **A new capability module cannot land silently.** A commit adding a tracked `.py` under a
   declared code root either carries a record or is refused.
2. **Both questions are answered, or the gap is visible.** The class *is* the ecosystem answer;
   `CATALOGUE` without a library named and `SUBSYSTEM` without a build-vs-buy note are refusals,
   because the director ruled that silence there is a gap.
3. **One claim is checked against an independent source.** G6 puts the record's "nothing exists"
   claim back through the live index. Every other guard reads the record against itself; this one
   can contradict it.
4. **An ordinary commit pays nothing.** No new code module → exit 0 without reading the message,
   the mode file, or the index.

**What it does not do — the wall.** *"Know, then choose — forced reuse that couples two purposes is
the mirror error of duplication and is equally a defect."* Every refusal is answerable by writing a
truthful record and committing the new module anyway. There is no record this gate accepts for
"reused it" that it refuses for "wrote it fresh". `test_the_wall_holds` pins exactly that property:
same module, same index, two honest records, both pass. If that test ever fails, the gate has
started deciding and has become the mirror defect.

---

## The record

In the commit message, one block per new module:

```
REUSE: company/billing/late_payment_charge.py
CLASS: CUSTOM
INDEX: searched "late payment", "charge" -- nearest is company.billing.dunning,
       which schedules chasing but never prices a charge
```

| Field | Owed by | Meaning |
|---|---|---|
| `REUSE:` | every new module | the path, exactly as staged |
| `CLASS:` | every new module | `CATALOGUE` \| `CUSTOM` \| `SUBSYSTEM` |
| `INDEX:` | every new module | the terms you put through the index, **in quotes**, and what came back |
| `LIBRARY:` | `CATALOGUE` only | the mature library this stands on |
| `EVALUATED:` / `REJECTED:` | `SUBSYSTEM` only | the build-vs-buy note: what was considered, why not |

`python3 tools/write_time_gate.py --explain <path>` prints the block with the live matches already
filled in, so producing a record costs a paste rather than a memory.

### The three part classes (director, 2026-08-05)

- **CATALOGUE** — calendars, timezones, money arithmetic, statistical fitting, solvers. *Always*
  from a mature library. Evidence class the director named by hand: the from-scratch working-day
  calculator of 2026-08-03, written while `holidays`/`workalendar` exist, and the BST/UTC settlement
  block the same day. A new CATALOGUE module must name the library it wraps — hand-rolling one is
  that incident repeating.
- **CUSTOM** — GB market mechanics, licence conditions, behavioural archetypes, the wall, the
  harness. *Always* built: it is the product. No build-vs-buy note owed. Recreating the physics of
  the GB market is the job; recreating the mathematics underneath it is waste.
- **SUBSYSTEM** — dispatch, ledgers and similar. May be custom, but only with the note naming the
  library evaluated and why rejected. Dependency discipline still applies: deterministic decade
  replays mean any new library is pinned and its determinism stated.

---

## Guards, and the defect each one catches

| Guard | Fires when | Mutation that proves it |
|---|---|---|
| G1 | a new module has no `REUSE` block | the append is neutered → a recordless commit passes |
| G2 | `CLASS` absent or not one of the three | `if False:` → an unclassified module passes |
| G3 | `CATALOGUE` names no library | clause disabled → a hand-rolled catalogue part passes |
| G4 | `SUBSYSTEM` missing `EVALUATED`/`REJECTED` | `missing = []` → silence clears the gate |
| G5 | `INDEX` quotes no search term | `if False:` → "I had a look" with no terms passes |
| G6 | record claims emptiness the live index contradicts | early `return []` → a false claim passes |

Two more mutations cover the *detector* rather than the guards: breaking the code-root test makes
new modules invisible (the whole gate silently stops applying), and breaking the test-file exclusion
makes it demand records for test files (the false-positive direction that gets a gate routed
around). Both are proven to go red.

**Vacuity.** The fail-open shape here is a gate whose detector never fires — every test passes while
no commit is ever checked. `test_detection_is_not_vacuous` fails if the fixtures stop producing owed
records, and `evaluate()` reports `owed` even when empty precisely so "nothing to check" stays
distinguishable from "checked and clean".

**Fail-closed** in all four directions (R15: an unavailable check is a failed check): unreadable
message, unbuildable index, unreadable/unknown mode word, and unreadable git state all REFUSE. An
absent mode file means `gate` — strict is the default, so the gate cannot be disabled by deleting
something.

---

## Scope, stated rather than left silent

The director's sentence says "before a new module/**function**". This fires on **modules only**.
That is a deferral with a reason, not a drop:

- a function-level gate fires on nearly every commit, and a gate that fires constantly is one people
  learn to route around with `--no-verify` — worse than no gate, and this project has the
  route-around class on file already (`H19`);
- the module is the unit AO1 has rows for, so the record and the answer share a unit;
- the module is the unit a builder actually reuses (`from company.billing.working_days import …`).

**Revisit if** duplication reappears *inside* modules — that would be evidence this scope is wrong.

Also out of scope by design: `site/**` (the site lane has its own gate), tests, `__init__.py`, and
anything outside the declared code roots.

## Rollout

Lands in `gate` mode, because §5 rules it the immediate behaviour change and
`test_the_live_mode_file_is_gate_or_absent` refuses a de-fanged landing. `tools/write_time_gate.mode`
holding `warn` downgrades refusals to identically-worded warnings — the 3am escape hatch, matching
`tools/moap_coherence_gate.mode`. The flip is a deliberate one-line diff and never automatic; a
warn-mode run reads exactly like the refusal it would be, so findings cannot quietly go to die in it.

## This gate applied to itself

`tools/write_time_gate.py` is a new module, so AO2's own landing commit carries its own record —
`CLASS: CUSTOM` (the harness is the product), index terms `"commit gate"`, `"pre-commit"`,
`"build vs buy"`, nearest `tools.pre_commit_test_gate`, which gates test colour and asks no reuse
question. The commit that adds the gate is the first commit the gate checks.
