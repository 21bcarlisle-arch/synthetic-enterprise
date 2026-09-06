**Severity:** BLOCKING · **Lane:** E_finance_treasury · **Epoch:** 2 · **Atom:** EP5_settlement_true_ups

**Discharged:** 2026-09-06. The four implementations are one.
`company/regulatory/settlement_reconciliation.py::ELEXON_RUN_MONTHS` is now the single sourced
definition; `company/market/bsc_settlement_run_register.py` and `tools/generate_world_data.py`
READ it (defects (b) and (c)); `simulation/settlement_timetable.py`'s docstring is corrected
beside its own constants (defect (a)); `site/data/world.json` is regenerated and now serves
Elexon's SF 1 / R1 2 / R2 4 / R3 7 / RF 14. Controls, each poison-proven below:
`tests/tools/test_the_published_settlement_timetable_is_the_sourced_one.py` (three legs over the
seam that reaches the site) and
`tests/company/market/test_bsc_settlement_run_register.py::TestSettlementRunRecord::test_the_register_holds_NO_timetable_of_its_own`.

**Poison rounds run before this discharge was written** (R15: "survived" means two opposite
things, so reachability is proven, not assumed):

| poison | what it simulates | result |
|---|---|---|
| `ELEXON_RUN_MONTHS["RF"] = 28` | the DF figure re-attached to RF at source | published-ladder leg **RED** |
| generator re-types `months=28` for RF, feed regenerated | defect (c) exactly, re-committed | published-ladder leg **RED**, prose/number leg **RED** |
| register re-types its own `_SETTLEMENT_RUN_MONTHS` map | defect (b) exactly, re-committed | both register legs **RED** |

**Item 2, the deletion recommendation, was NOT taken, and here is why.** The finding recommended
deleting `bsc_settlement_run_register.py` outright on the grounds that it has no non-test
importers and no citation. It now has a citation and holds no timetable of its own, which removes
the liability the recommendation was made against — a module that cannot disagree with the source
is not a second timetable. Deleting a live module with a passing suite is a larger, less
reversible act than making it read the truth, and the seat's call is the smaller one. Its *reach*
finding (zero non-test importers) stands and is untouched by this turn; if the lane that owns it
wants it gone, nothing here obstructs that.

**What is NOT claimed.** The variance bands (`±0.5%` HH / `±4%` non-HH) remain unverified and are
still named as such in `docs/market_research/elexon_settlement_run_timetable_verified.md` — this
turn did not touch them. And the control is one leg over the published seam, not a census of every
settlement timetable in the tree: a fifth copy that reaches neither the register nor the feed would
still be invisible. That was a deliberate scoping call (the direction: *"do not build a register of
implementations; one leg over the seam that actually reaches the site"*), and it is the honest bound
on this discharge.

# One Elexon settlement timetable has four implementations, the sourced correction reached two, and the published feed carries an uncorrected one

**Found:** 2026-09-06 scheduled tick, LANE 3 DISCOVER/FRAME draw on `EP5_settlement_true_ups`, asking
the interconnection question — what landed since the last pass, and does what assumed it still hold?
**Measured at:** HEAD `fdfa0c94f`. Every file read on disk; `site/data/world.json` parsed in full.
**Severity reasoning:** BLOCKING by construction (DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE
clause 2) — a figure in a published artefact is wrong against a primary source this repo already holds.
Not self-downgraded to LATENT.

---

## The established answer

`docs/market_research/elexon_settlement_run_timetable_verified.md` (2026-08-29) transcribes an
Elexon-authored primary document (Priestley, *Settlement Timetable*, 16 June 2014, hosted on
ofgem.gov.uk, slide 2 read directly):

| Run | II | SF | R1 | R2 | R3 | **RF** | DF |
|---|---|---|---|---|---|---|---|
| after settlement date | 1 wk | 1 mo | 2 mo | 4 mo | 7 mo | **14 mo — LAST SCHEDULED RUN** | 28 mo — **disputes only** |

## What the tree carries

| # | file | R1 | R2 | R3 | RF | state |
|---|---|---|---|---|---|---|
| 1 | `company/regulatory/settlement_reconciliation.py` L59–62 | 2 | 4 | 7 | **14** | CORRECTED |
| 2 | `simulation/settlement_timetable.py` L72–75 | 2 | 4 | 7 | **14** | constants CORRECTED, **docstring not** |
| 3 | `company/market/bsc_settlement_run_register.py` L48–53 | 5 | 14 | 26 | **28** | UNCORRECTED |
| 4 | `tools/generate_world_data.py` L194–200 | 5 | 14 | 26 | **28** | UNCORRECTED, **published** |

Four implementations of one published legal timetable. The correction reached two.

## The three live defects, by line

**(a) `simulation/settlement_timetable.py` L3–7 and L21–22 — prose refuted by its own constants.**
The module docstring states *"R1 (~1 month post-delivery), R2 (~3 months), R3 (~5 months), and RF
(Final Reconciliation, ~28 months) ... (60% / 25% / 12% / 3% respectively)"*. Sixty lines below, the
constants say 2 / 4 / 7 / **14** with a different share curve. The correction edited the constants and
left the first paragraph — the thing a reader reads first — asserting the numbers the primary source
refuted, **inside the file where they were refuted**. No control catches it: every control reads the
constants; none reads the prose.

**(b) `company/market/bsc_settlement_run_register.py` — wrong on every run, uncited, unwired.**
It states the timetable as fact in three places inside one file (docstring L6–10, enum comments L36–39,
`_SETTLEMENT_RUN_MONTHS` L48–53) with **no citation on any of them**. It is the same RF/DF conflation
pass 2 diagnosed, one rung deeper: Elexon's R2 figure (4) is absent entirely, Elexon's RF figure (14)
is attached here to **R2**, and Elexon's DF figure (28, disputes only) is attached here to **RF**.

Reach, measured by `grep` over all `*.py`: **zero non-test importers.** `tools/generate_world_data.py`
(L25, L193, L222), `company/market/bsc_settlement_dispute_register.py` (L15) and
`company/regulatory/network_code_modification_register.py` (L29) name it in prose only. The sole
importer is `tests/company/market/test_bsc_settlement_run_register.py`. Being unwired is what has kept
it wrong; being *cited* is what makes that matter — see (c).

**(c) `tools/generate_world_data.py` L194–200 — a hand copy of (b) that reaches the published feed.**
Five literal dicts, not a read of any constant. Its `mechanism` string (L219) tells the reader
settlement *"progressively swaps estimates for actuals over ~28 months"*, and its `evidence` field
(L222) cites `company/market/bsc_settlement_run_register.py` — a module it does not import, which is
itself uncited, and which is wrong. **A wrong module is named as the evidence for a wrong published
figure, and the citation is the only thing connecting them.**

`site/data/world.json` (`generated_at` `2026-09-06T08:53:08Z`, `git_commit` `b01b1dbe3`), under
`wall.crossings[id=meter_reads]`, carries:

```
SF Initial Settlement    T + 14 days     R1 First Reconciliation  T + 5 months
R2 Second Reconciliation T + 14 months   R3 Third Reconciliation  T + 26 months
RF Final Reconciliation  T + 28 months   "final, no further runs"
```

## The honest bound on (c)

**`settlement_ladder` and `mechanism` are written into the served feed but no page renders either.**
`grep` for `settlement_ladder` across `site/**` returns `site/data/world.json` and nothing else; the
wall crossings rendered by `site/harness/index.html` and `site/capabilities/index.html` do not read
`mechanism`. So a reader must open the JSON to be misled rather than being shown it. That is the whole
of the mitigation and it does not make the figure right — the artefact is public and it is wrong.

## Why this is the class and not three tidy-ups

CLAUDE.md names it by hand: *one legal requirement, five implementations, a defect fixed in one of them
in July and still live in another in August, and nothing anywhere able to notice.* This is that, with
the interval measured: **nineteen days** between the sourced correction landing (2026-08-29) and
anything noticing that two of its four subjects were untouched — and it was noticed only because a
DISCOVER draw on the coupled atom asked what had moved. There is no control anywhere in the tree that
can observe two settlement timetables disagreeing.

## Recommended disposition — not applied here, and why

This was found on a **LANE 3 DISCOVER/FRAME draw on a BUILD-gated atom** (`EPOCH_GATING_AND_ATOM_
AUTHORSHIP` Rule 1 forbids BUILD), so all three are queued with their lines named rather than fixed in
the finding turn. In order:

1. **(a) now** — correct `simulation/settlement_timetable.py` L3–7 and L21–22 to match its own
   constants and cite `elexon_settlement_run_timetable_verified.md`. Zero behaviour change; it is a
   record correction beside the claim.
2. **(b) — correct or delete, and the recommendation is delete.** It has no importers and no citation.
   A second uncited company-side timetable beside the corrected one is a liability, not an asset; if
   its run-adjustment machinery is wanted later, it should be rebuilt importing `settlement_timetable`.
   *This is a live-module deletion and therefore a call for the lane that owns it, made with the reach
   measurement above in hand.*
3. **(c)** — have `generate_world_data` derive the ladder from the single sourced module instead of
   hardcoding it, fix the `~28 months` prose, repoint `evidence` at the sourced research document, and
   regenerate `site/data/world.json`.
4. **The control that stops the fifth copy** — a test that fails when any two settlement timetables in
   the tree disagree. Keyed to the **property** ("the tree holds one settlement timetable"), never to
   today's numbers: it must stay green when Elexon changes the timetable and go red when a fifth copy
   appears. Pinning 2/4/7/14 would be the control-that-cannot-fail shape — it would go green on
   exactly the day the tree became wrong in a new way.

Item 4 is the one that matters. Items 1–3 fix instances; 4 is the only one that fixes the class, and
without it this finding will be re-derived by a sixth DISCOVER pass in another nineteen days.

## Where the full derivation lives

`docs/design/EP5_SETTLEMENT_TRUE_UPS_DISCOVER_PASS3_2026-09-06.md` (this tick's DISCOVER output),
which also records EP5-P0: the four timetables must become one before EP5 BUILD writes a single
restating ledger entry, because a ledger that restates on the real timetable, built beside three copies
that disagree about what the real timetable is, will be correct and unbelievable.
