**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# FINDING — the level anchor's new guard is green at HEAD and red in the tree the world actually runs from, and the block that reddens it is in no commit

**Found 2026-09-01 ~20:20Z, delivery seat, Lane 0, on the drawn Lane 0 item.** The drawn item's own
"done means" was discharged before this tick opened — the capture ran to completion, the five
predictions are graded at `68ec6825b` / `39967d018` / `83cdb7dd4`, the stale docstring was corrected
at `342d72159` and `7cb667126`, and the whole-book fit emitted. That is established in
`WORKER_PREREGISTRATION_WHAT_A_NATIVE_SVT_CAPTURE_MUST_SHOW_2026-09-01.md` and is not re-derived
here. **This stretch followed the interconnection instead**, which is what the seat is for: of what
landed since the last orientation, what else assumes it, and does that assumption still hold.

It does not.

---

## The finding, measured

`9fd700366` (2026-09-01 20:44:18 +0100 = **19:44Z**) landed a fail-closed guard on
`simulation/departure_level_anchor.year_level_anchor`: a year **inside** the published record with no
fitted anchor now raises instead of silently taking the reference year's value. It landed with a new
control, `tests/simulation/test_departure_risks.py::test_a_year_inside_the_published_record_with_no_fitted_anchor_refuses_instead_of_falling_back`,
and that control was mutation-proven. All of that is sound and none of it is in question.

**The control is green at HEAD and red in this working tree, and has been from the instant it
landed.**

```
$ cd /tmp/headchk && git archive HEAD | tar -x   # clean extract of HEAD
$ python3 -B -m pytest tests/simulation/test_departure_risks.py -k no_fitted_anchor -q
1 passed, 21 deselected

$ cd /home/rich/synthetic-enterprise    # the shared tree
$ python3 -B -m pytest tests/simulation/test_departure_risks.py -k no_fitted_anchor -q
>           assert year_level_anchor(y) == YEAR_LEVEL_ANCHOR[y]
E           KeyError: 2016
1 failed, 1 passed, 20 deselected
```

The cause is not the guard and not the control. It is that this tree carries an **uncommitted
seven-year `YEAR_LEVEL_ANCHOR` block** where HEAD carries the committed ten-year one:

| | years | source |
|---|---|---|
| HEAD (`0e316d3e9`) | 2016–2025, all ten | committed since `71242c941` |
| this working tree | 2017–2021, 2023, 2024 — **2016, 2022, 2025 absent** | in **no commit** |

Checked, not assumed: `git log --all -S'4.547299' -- simulation/departure_level_anchor.py` and the
same for `0.364038` both return **nothing**, and a scan of every commit touching the file finds none
whose content matches the working tree's sha256 `1ece30c4…`. The block exists only here.

## Why nobody saw it, and why the grading could not have

**The tree was never written by the landing.**

```
$ stat -c '%y' simulation/departure_level_anchor.py
2026-08-31 20:14:35   # the guard landed 2026-09-01 19:44Z, twenty-three hours later
$ git worktree list
/home/rich/synthetic-enterprise   0e316d3e9 [main]
/var/tmp/se-ladder                2eeaa69ea (detached HEAD)      ... and five more
```

The landing lane worked in one of the sibling worktrees. HEAD moved out from under this checkout and
this checkout's copy of the file has not been touched since **2026-08-31 20:14:35** — which is also,
exactly, the content the native capture ran at 17:31Z: the working tree's sha256 is
`1ece30c41f3cec3c7a91f00e432b55013b4a7a92df82971f6b04034d1f117236`, byte-identical to
`PROVENANCE.txt`'s as-run entry. So this is **old content that HEAD has since superseded**, not new
work by a live lane.

**The grading's own constraint check therefore ran against a different tree than this one.** That
prereg certifies constraint 1 — *"no constant pasted, edited or deleted"* — with *"`git diff -U0`
filtered to `YEAR_LEVEL_ANCHOR` and any year line returns empty"*, and explicitly contrasts itself
with its two predecessors, which certified the same constraint *"by recalling what their author had
not done"*. Reading the artefact was the right instinct and it is the reason that grading is better
than the two before it. **But in this tree that check cannot return empty** — ten year-lines differ
from HEAD. The certification is true of the tree it was run in and false of the tree the world runs
from, and nothing in its wording says which tree it meant.

This is the catalogued class *a green test in the shared worktree measures several lanes, not your
change* — running the other way round. The usual failure is a tree that is greener than HEAD. Here
HEAD is greener than the tree, and a change proven correct at HEAD is red where the work happens.
**`G4`'s stated refuter, *"any red that is not present at clean HEAD"*, is exactly blind to this**:
it is the right refuter for a pre-existing red, and it cannot see a red that the change creates only
in composition with uncommitted work. G4 was named as the prediction its author was least sure of,
and it was refuted-shaped for a reason one step past the one it braced for.

## The forward hazard, which is worse than the red

The two halves are individually defensible and jointly fatal. Measured by composing HEAD's function
with this tree's block:

```
2016 -> ValueError: no fitted level anchor for 2016, which is INSIDE the published switching record (2016-2025)…
2022 -> ValueError: …
2025 -> ValueError: …
2024 -> 3.053619      # fitted, fine
2030 -> 3.053619      # outside the record, fallback preserved, fine
```

`year_level_anchor` is called on the **hot path of the run**, not in a report:
`simulation/customer_events.py:610`, and `simulation/run_phase2b.py:1634`, `:1667`, `:1719`, each on
`int(term_start_str[:4])`. The window is 2016–2025, so 2016, 2022 and 2025 term starts all occur.
**If the seven-year block is landed on top of the guard, `run_phase2b` raises mid-run on three of
the ten record years.**

And the two texts disagree in prose, which is how you can tell this is a real collision and not a
merge artefact. HEAD's docstring says a missing in-record year is *"a refusal and not a fallback"*.
The tree's docstring says *"TWO KINDS OF YEAR REACH THAT FALLBACK NOW … 2016, 2022 and 2025 are IN
the record and still land here"*. Each is internally consistent; they are opposite answers to one
question, and whichever lands second silently decides it.

## What I did NOT do, and why

**I did not touch `simulation/departure_level_anchor.py`.** The drawn pathspec for this stretch
nominally covers `simulation/`, and that is precisely the catalogued class *a drawn pathspec can be
the careless pathspec it warns about*. Three specific restraints:

1. **No `git checkout` and no `git show HEAD: >` over the file.** The seven-year block is in no
   commit; overwriting it destroys it irrecoverably. The red is reversible and visible, the deletion
   would not be. The house rule against `git stash`/`git checkout <path>` on this tree exists for
   exactly this.
2. **No reconciliation.** Keeping both halves — the guard plus the seven-year block — is the
   crashing state above. Choosing between them is a design decision belonging to the lane that fitted
   the block, on evidence about which capture the block should come from, and it is not mine to take
   by pathspec accident at 20:20Z.
3. **No constant adopted into `YEAR_LEVEL_ANCHOR`.** The standing constraint from all three preregs
   on this file is honoured by not touching the table, discharged by reading the artefact:
   `git status --porcelain simulation/departure_level_anchor.py` is ` M` (unstaged, unchanged by me)
   and it is excluded from this stretch's commit.

**So this stretch's pathspec is narrowed to this document alone**, and the narrowing is the finding's
point rather than an omission from it.

## What is owed next

1. **Decide the collision deliberately, in the lane that owns the fit.** Either the seven-year block
   is superseded — in which case this tree's copy should be brought to HEAD *by the lane that knows
   it is dead*, not by whoever commits `simulation/` next — or the block is live, in which case
   landing it requires answering what `year_level_anchor(2016 | 2022 | 2025)` should do, because the
   guard now makes that a crash rather than a silent 1.98x. **Until then every lane that commits a
   file selecting `tests/simulation/test_departure_risks.py` from this checkout is wedged on a red
   it did not cause.**
2. **A guard that a sibling worktree can arm is a shape, not an incident.** `9fd700366` is correct,
   proven, and made this tree red without touching it. Six worktrees share this repository and HEAD
   moves under all of them; a control keyed to agreement between a committed table and a committed
   record is silently keyed to *whichever copy of the table the runner has*. Whether that is worth a
   mechanism or only a habit is a separate judgement — filed here, not built here, because a control
   that only guards our own controls is usually not worth having.
3. **Unchanged from the two preregs and not re-derived:** the band control's emptied subject (7 years,
   not 8) is still red at HEAD and is still the only thing holding the level anchor accountable; and
   `tools/population_anchor.py`'s five 2022 consumers still resolve `.get("sim_churn_rate", 0.0)` to
   a published measured zero. Both remain outside this pathspec.

---

# CORRECTION 2026-09-01 ~20:55Z, same seat, later tick. THE TWO BLOCKS ARE NOT RIVAL DRAFTS — THEY ARE CONSECUTIVE ITERATES, AND THIS FINDING HAS THE DIRECTION BACKWARDS.

*Kept above rather than revised. The restraint this finding exercised was right; the reason it gave
for it was wrong, and the two had to be separated before the collision could be decided.*

The finding above reads the working tree's copy as **"old content that HEAD has since superseded"**,
on the strength of its mtime (`2026-08-31 20:14:35`) being older than the guard's landing
(`2026-09-01 19:44Z`). That inference does not hold: an mtime older than *one* commit to a file says
nothing about which *table* came first, because the guard commit changed the accessor, not the block.

**The direction is measurable, and no docstring or mtime is needed to measure it.** Every capture
records, per row, the anchor the run actually executed under — the `sim_level_anchor` column. That
column identifies the block that produced the capture, independently of anything anyone wrote about
it. Read across every capture on disk:

| artefact | mtime | `sim_level_anchor` column | ⇒ ran under |
|---|---|---|---|
| ten-year block | committed `71242c941`, 08-30 20:15 | — | — |
| `docs/reports/c3_shown_price_departure_factors.json` | 08-31 02:17 | 2016:4.597312 … 2022:1.524110 … 2025:2.118624 | **ten-year** |
| `docs/reports/ladder_churn_factors.json` | 08-31 16:44 | matches the ten-year block in **all nine** years present | **ten-year** |
| seven-year block (this tree) | 08-31 20:14 | — | — |
| `docs/reports/c2_departure_factors.json` | 08-31 20:54 | 2017:4.547299 … 2023:0.364038; **2016 and 2025 both 3.053619** | **seven-year** |
| `/tmp/svtcap/c2_marketterm.json` (native capture) | 09-01 17:31 | identical to `c2` above | **seven-year** |

`3.053619` is 2024's anchor and `MULTIPLIER_REFERENCE_YEAR` is 2024, so 2016 and 2025 reading
`3.053619` is precisely the reference-year fallback firing under a block that omits them. That is
the seven-year block's signature and nothing else produces it.

**So the order is: ten-year block → `ladder` capture → seven-year block → `c2` capture → native
capture.** The tree's block is the fit **of** the capture that HEAD's block **produced**. It is
HEAD's *successor*, not its predecessor, and the tree's own docstring claim — *"this capture's
`sim_level_anchor` column was checked row by row against the block it replaced and matches it in all
nine years"* — is **independently true**, re-measured here rather than taken from the file asserting it.

## What this changes, and the second defect it exposes

**HEAD's ten-year block cites an artefact it cannot have been fitted on.** Its docstring says
*"Fitted by `tools/fit_year_level_anchor.py` on `docs/reports/c2_departure_factors.json`"*. The file
carrying that name today ran under the **seven-year** block and is dated a **day after** the ten-year
table landed. The capture the ten-year block was actually fitted on was overwritten **in place, under
the same filename**, and the overwrite is itself committed — `b46318106`, 09-01 16:35, *"the capture
the published departure figures were already produced from lands"*. The citation is therefore
unfollowable: it resolves, at HEAD, to a capture produced two steps later by its own successor. This
is an instance of `figures_on_a_superseded_clock` — the file path was stable and the run behind it
was not.

**And that is what makes the wedge the shape it is.** `9fd700366`'s control was written and
mutation-proven against the **predecessor** table, in which all ten record years are fitted. Its leg
(b) requires that every in-record year be present in the block — its own docstring says so in
advance: *"adding 2026 to the record and not to the fit must turn this red, and re-fitting must turn
it green."* The successor fit deliberately refuses three in-record years, with a named cause each.

**So this is not "a stale tree against a fresh HEAD". It is HEAD's control requiring a property that
HEAD's own successor fit abandons on purpose, and both positions are argued.** That is the decision,
it is a real one, and it is still the fit lane's to take — for a sharper reason than this finding
originally gave.

## Two further corrections to claims resting on the same reading

**(1) The crash is reachable, not hypothetical — confirmed by counting the calls.** Composing HEAD's
guard with this block raises on 2016 and 2025, and those years occur in every capture on disk: 2016
carries 1 renewal row and 2025 carries 15–18, in `c2`, `ladder` and the native capture alike. The
forward hazard this finding named is real and it fires on the first affected term start.

**(2) "2022 has zero renewal decisions" is CAPTURE-SCOPED and is being read as a property of the
world.** True of the `c2`/`ladder`/native family (0 rows each). **False of
`c3_shown_price_departure_factors.json`, which carries 53 renewal rows in 2022** under the ten-year
block. The tree's docstring is correctly scoped — it says *"zero renewal decisions **here**"* — but
the native capture's grading is not: `WORKER_PREREGISTRATION_WHAT_A_NATIVE_SVT_CAPTURE_MUST_SHOW_2026-09-01.md`'s
unpredicted finding (a) argues from *"this capture establishes 2022 has zero renewal decisions over
55 accounts"* to a standing conclusion about `population_anchor`'s published zero. The premise holds
for that capture; the conclusion is owed the scope. Recorded here, beside the collision it bears on,
and **not** edited into that grading by this tick.

## What I did NOT do, and one thing I considered and rejected

**I did not touch `simulation/departure_level_anchor.py`**, and I did not pick a fit.

**I considered repairing leg (b) of the control and decided against it.** The tempting reading is
that leg (b) is keyed to today's answer — the catalogued *a control pinned to the current state goes
red when the code becomes more honest*. It would have un-wedged the tree without deciding anything,
which is exactly the shape a bounded tick wants. **It is the wrong reading.** The control's docstring
states the requirement in advance, before this collision existed, and leg (c) already drives the
guard's refusal branch independently. Narrowing leg (b) would delete a deliberate accountability
requirement on the *fit* in order to relieve a symptom, which is the catalogued
*a guard narrowed for one subject class permanently severs the other*. The red is the control working.

**What I did instead: removed the irreversibility, so the decision has no deadline.** The block was
in no commit and no reflog — verified with `git log --all --reflog`, where `--all` alone would not
have settled it, because six sibling worktrees share this object store on detached HEADs that `--all`
does not enumerate. It is now preserved byte-exact, sha256 `1ece30c4…` matching `PROVENANCE.txt`'s
as-run entry, at **`docs/design/UNLANDED_WHOLE_BOOK_LEVEL_ANCHOR_BLOCK_2026-09-01.md`**, with a
verified round-trip. Until this tick, one `git checkout <path>` destroyed it with no route back —
which meant whoever took the decision was working against a hazard as well as a question.

## What is owed next, restated

1. **The collision decision, unchanged in ownership and sharpened in content:** does an in-record
   year that the whole-book fit honestly cannot identify refuse (crashing the run on 2016 and 2025)
   or fall back? Landing either half alone is safe; landing both is the crash. **Neither table is
   stale — the newer one is in this tree and the older one is at HEAD.**
2. **Re-cite HEAD's block, or re-fit it.** Its stated fit input no longer resolves to the run it was
   fitted on, so at HEAD the ten-year table is a set of numbers whose provenance cannot be followed.
3. Unchanged and not re-derived: the band control's emptied subject; `population_anchor`'s five 2022
   consumers, now also owed the scope correction in (2) above.
