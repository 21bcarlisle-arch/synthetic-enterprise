<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED] — Seed + publish the open-question register (six carried with disposition) (deliverable 2) (2026-07-28)

**Source:** `DIRECTOR_RULING_NO_QUESTION_LEFT_UNANSWERED_2026-07-28.md`, deliverable **2** ("The
register seeded and published, with the six above either answered or carried with a reason.").

**Provenance:** RUNG-7 planner mint from the ruling's WORK THIS CREATES block. grep-confirmed net-new
— no existing mint seeds an open-question register. Distinct from deliverable **4**: this atom SEEDS
and PUBLISHES the register (the six §3 questions present, each with a disposition — answered OR
carried-with-reason so none is silent); deliverable 4 produces the substantive batched ANSWERS. They
couple — 4's answers let 2 flip a row from `carried` to `answered` — and MAY land together, but 2's
acceptance is "the register exists, is published, and no seeded question is silent", not "all six
answered".

**Serves:** the ruling's acceptance test — *"the current open-question set is inspectable from
published artifacts without asking the machine."* Seeding proves the register is real and non-empty;
publishing (an inspectable artefact — the register file itself and/or the daily note per deliverable 3)
makes the open set inspectable.

**Fidelity/robustness gained (one sentence):** the six outstanding director questions §3 stop being
folklore and become published rows, each carrying either an answer or an explicit carry-reason — silence
is eliminated by construction.

---
## The six to seed (verbatim from ruling §3)
1. `merit_order` drawable only from 2026-07-28 — why (epoch gate / dep / scheduling artifact), and *is
   it drawing now* (date is today)? [from `d81197736` §5]
2. Harness exit-criterion counter current reading + cause of last reset; is it wired to primary state
   (could it observe last night's HARDEN-while-unminted)? [`d81197736`, `1494d6160` §4b]
3. Cohort assignment status: done / in flight / blocked / counter-proposed? [`e685eb76d`, `1494d6160` §4a]
4. Stall-set coverage verdict on the four events (console rescue, publish-gate wedge >1h, origin freeze
   >30m, advisor restart-ruling): detected / detector-added / argued-out? [`d81197736` §3]
5. Staleness disposition in the gap taxonomy. [`27271871e` §3a]
6. Blast radius as positive value vs risk. [`27271871e` §3b]

## Lane / level / deps
- **Lane:** `H_harness` (a data/observability seeding task).
- **Target level:** `blocked_on: director_level_up` for any level claim (R16).
- **Deps:** register SHAPE from **deliverable 1** (mechanism). Answer CONTENT from **deliverable 4**
  (a row may seed `carried` immediately and flip to `answered` when 4 lands).

## Exit criteria
- The six §3 questions present as register rows, each `answered` (with the answer) or `carried` (with an
  explicit reason) — **none silent**.
- The register is a **published/inspectable artefact** (fetchable file and/or surfaced per deliverable 3),
  so the open-question set is readable without querying the tick (LAW C: derived from primary state).
- If any of the six was in fact already answered elsewhere, the row **cites where** and closes it (ruling
  §3 invites this).

## Walls untouched
- **R12:** the register is a diagnostic surface; open-count is never a target.
- **No level self-bump (R16):** `blocked_on: director_level_up`.
- **No safety/auth/curriculum move.**
