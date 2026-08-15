# EP19 — the qualification acts, and the wall that was supposed to stop them

**Atom:** `EP19_counterparty_qualification_paths` · lane `F_risk_compliance` · epoch 5 · level 1 → 2 target · `loop_stage: idle`
**Draw:** 2026-08-15 worker tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written for this atom** —
its `file_scope` is `[]` and stays `[]`. The repair below is to `background/one_way_door.py`, a HARNESS
wall, not to any counterparty adapter; epoch-5 BUILD gating is untouched.
**Level this pass:** **1 → 1 (held).** See [§ The level](#the-level-held-at-1-and-why).
**Severity:** BLOCKING — a reserved-class wall read PROCEED on its whole population.
**Lane:** `F_risk_compliance`
**Discharged:** `tests/background/test_one_way_door.py::test_every_gated_counterparty_qualification_act_is_a_door`, `tests/background/test_one_way_door.py::test_the_open_counterparties_and_the_register_work_itself_still_proceed`, `background/one_way_door.py` — the defect is repaired and mutation-proven in both directions in this same commit; the severity states what this pass FOUND, not what it left.

## What this pass was drawn to do, and what it found instead

The previous pass (2026-08-13) produced `docs/design/EP19_COUNTERPARTY_QUALIFICATION_REGISTER.md` and
named its own L2 blocker: the atom's `gain` promises *"named qualifications **with owners**"* and the
register had none. The obvious next move was to derive owners. Deriving an owner means asking, per row,
*who is allowed to perform this act* — and in this project that question has a mechanical answer:
`background/one_way_door.py`, which CLAUDE.md names as **the SOLE enumeration** of what is reserved.

So the acts were put through it. `observed-with-evidence`, 2026-08-15, by running `classify_action`
against one plain-English description of each register row's qualifying act:

| row | act | verdict, before |
|---|---|---|
| B1 | Submit a Smart Energy Code accession application to the SEC Panel and pay the accession fee | `door=False` |
| B1 | Apply for SMKI certificates and book CIO/UIT entry-process testing with the DCC | `door=False` |
| B2 | Contact the REC Code Manager to confirm our REC eligibility | `door=False` |
| B3 | Sign the Data Services Contract / UK Link User Agreement with Xoserve as CDSP | `door=False` |
| B4 | Accede to the Uniform Network Code as a gas shipper and sign transportation agreements | `door=False` |
| B5 | Open a sponsoring bank relationship and apply for a Bacs Service User Number | `door=False` |
| B7 | Accede to the Balancing and Settlement Code and appoint an ECVN agent | `door=False` |

**Seven of seven read PROCEED** — including signing a contract with a real company and opening a real
bank relationship, which are the *textbook* instances of reserved classes 1 and 2.

Meanwhile the atom's own `block_reason` — the *sentence describing* the boundary, which contains the
words *"spending real money"* — classifies `door=True, category=real_money`. The wall fired on the prose
about the population and not on the population.

That is the R15 **fail-open** pattern with a **wrong-subject** twist, and it is the sharpest form of the
`MAKE_IT_STICK` failure this project keeps rediscovering: *the rule lived in prose that named a
mechanism, and the mechanism did not implement the prose.* EP19's `block_reason` says the ceiling is
"the register, never the application", and cites classes 1 and 2 by name. Nothing enforced it.

**Fair reading of the previous pass.** The 2026-08-13 register wrote *"THE RESERVED BOUNDARY IS HELD, not
just cited"*. That was true of the **document** — no row carries an apply/contact/submit action, by
construction, and that is still true. It was not true of the **mechanism** the atom points at. The defect
is in the wall, not in the register's discipline; but the register's sentence invites the stronger reading,
and the stronger reading was false.

## Why it missed — near-misses of shape, not of intent

The patterns were not absent-minded; each miss is one narrow inch away from a hit.

1. **`\bsign(ed|ing)? (a |the )?contract\b`** requires that literal word pair. Every real instrument
   carries a **name between the article and the noun** — "sign the *Data Services* Contract", "sign the
   *UK Link User* Agreement" — so the toy phrasing was caught and every actual one fell through.
2. **`\bsubmit(ted)? to ofgem\b`** names exactly one of the eight real bodies this project would ever
   write to. Xoserve, the SEC Panel, RECCo, the REC Code Manager, the DCC, Elexon, NESO and a sponsoring
   bank were all outside the wall.
3. **Accession** — the actual verb of every UK energy code — appeared in no pattern at all.
4. **The money side of a code accession is a *fee***, not a subscription and not a card. The REAL_MONEY
   list had been widened twice before (2026-07-29 for "approve spend", 2026-08-03 for "card payment"),
   each time by the shape that had just been missed; "pay the accession fee" is the third shape.

## The repair, and the two directions it is pinned in

`background/one_way_door.py`, six added patterns. Widening detection is **safety-INCREASING**, which the
module's own two prior widenings establish needs no authorisation (the console convention governs
safety-REDUCING changes). After: **7 of 7 gated acts gate**, B1 as `real_money`, the rest as
`real_world_commitment`.

The harder half was **not jamming the lane that writes the register**. A control that false-fires on the
loop's own routine draw is its own defect (the 2026-07-16 epoch-adjective precedent, where a false match
re-escalated open-build every draw). Two first cuts of these patterns did exactly that:

- pairing `accession` with `apply`/`file`/`register` fired on *"apply the filename convention to the
  accession register doc"* and *"file the accession notes"* — this atom's own documentation work;
- `register` as a verb fired on *"write the counterparty qualification **register**"* — this repo names
  roughly fifty registers.

So the final patterns require something no *description* carries: an acting verb next to a **named real
body**, or an instrument with no documentary sense (`SMKI`, `CIO/UIT`, `Service User Number`). The bare
word `accession` is deliberately **not** a trigger. `call` is deliberately absent from the verb list —
*"call the Elexon Insights API"* is the commonest sentence in this repo, and B6/B8 of the register are
**OPEN** counterparties whose data qualifies nobody.

**R15, both directions, surgically** (`tests/background/test_one_way_door.py`, three new tests):

- Remove exactly the six new patterns at runtime and **7 of 7 gated acts flip back to PROCEED**; nothing
  else in the file moves. The control fires on a real, named defect — it is not passed by construction.
- Twelve open/descriptive actions stay PROCEED, including all three OPEN register rows, this atom's own
  register-writing work, and the simulated-domain phrasings (`"paying an early exit fee"`, `"sign the
  commit"`) that a lazier pattern would have caught.

**Blast radius checked, not assumed.** Every `block_reason` / `blocked_on` string in
`docs/design/maturity_map.yaml` was classified with and without the new patterns to confirm no atom
newly gates and silently leaves the draw. Both supervisor call sites
(`supervisor.py:557`, `:3408`) are in any case reached only for reasons that already name an abolished
permission token.

## What this gives the register: owners, derived rather than guessed

The atom's `gain` wants *qualifications with owners*. The previous pass looked for owners in the external
source and correctly found none. **The owner was never an external fact.** In this company there are
exactly two parties who can perform anything, and which one owns an act is decided by the reserved-class
enumeration:

- act classifies **RESERVED** → the owner is **the director**, necessarily and permanently. The agent can
  never own it, at any epoch, however open the curriculum gets.
- act classifies **PROCEED** → the owner is **the company/agent lane** named in the row.

That column is now added to Part B of the register, and it is *derived by running the classifier*, not
asserted — which is only meaningful because of the repair above. Derived from the pre-repair classifier,
every gated row would have been labelled "agent-owned".

## The level: held at 1, and why

The 2026-08-13 pass named the L2 blocker as **owners + costs + lead times**. This pass closes **owners**,
and closes it mechanically. It does not close costs or lead times, and it cannot: both are live external
facts (accession fees, SEC/REC processing times, Bacs sponsorship lead time) and autonomous runs have no
network. Nothing was inferred into those columns to make a level move look available.

So the level stays at **1**, with the remaining L2 gap now precisely two columns wide instead of three,
and with the next step named: **one networked DISCOVER pass to price the five gated paths and record
their published lead times.** Moving to L2 on a third of the blocker would be greening a criterion by
redefining it.

## Open items carried forward (R10 — named, not dropped)

1. **Costs and lead times** for B1–B5 and B7 — the whole remaining L2 gap. Needs network.
2. Items 2–5 of the register's own open list are **unchanged** by this pass: B7's qualification path is
   still `inferred`; B1/B5 still rest on `~` markers; MRA/DCUSA subsumption still unknown; 2026-08-05 is
   still the freshness ceiling on every `✓` row.
3. **The wall's population is bigger than this register.** These seven acts are the ones EP19 names. The
   same fail-open shape plausibly covers other real-world engagement this project has never written down
   (an auditor, a hosting provider, a data vendor). This pass repaired the shapes it could demonstrate a
   defect for and did **not** speculatively widen beyond them — the untested half is registered here as
   the honest residue, not claimed as covered.
4. **The classifier is keyword-shaped and always will be leaky at the edges.** `provably_irreversible=True`
   remains the inverted-burden escape hatch for an act the keywords never anticipated.

## Cross-references

- `docs/design/EP19_COUNTERPARTY_QUALIFICATION_REGISTER.md` — Part B of the register; gained the
  **Owner** column this pass.
- `docs/design/F5_LICENCE_READINESS_REGISTER.md` — Part A (the licence itself). Its own rows are
  qualification acts of the same class and inherit this repair.
- `background/one_way_door.py` — the wall; the six patterns carry this doc's path in their comment.
- `tests/background/test_one_way_door.py` — the three tests and the mutation note.
- `docs/design/maturity_map.yaml` — `EP19_counterparty_qualification_paths` (level held at 1).
