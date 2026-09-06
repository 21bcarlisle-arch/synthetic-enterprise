# Delivery-seat stretch log

*What each stretch of work was about, what it got wrong, and the reasoning behind the calls made in
it. The commits record what changed; this records why. Newest first.*

*Written by `tools/stretch_log.py` as part of finishing a piece of work, not as a separate step.
A stretch that lands commits without an entry here is a finding, raised by `--check`.*

---

## 2026-09-06 — The weather pull sat undrawn for eighteen hours because the atom was a programme, and the first measurement refutes a ruling prediction by a sign

<!-- head: 5f5b8d74ebb8 -->

**What this stretch was about.** The HadUK-Grid weather pull finished on Saturday evening — 318
files, 19.8 GB, zero failures — and for eighteen hours nothing was drawn from it. The cause was the
same one that had already cost two other stretches: `W1_14` is a ruling-sized atom, "derive the
weather cells", and a bounded tick reading that has no first move, so it takes the machinery in
front of it instead.

**The fix, third time of asking.** Four bounded successors, each with a first move: `W1_19` the three
drivers per land cell (needs nothing but the disk), `W1_20` household weights from the censuses,
`W1_21` the clustering and the level coverage curve, `W1_22` cold-spell persistence and cross-cell
synchrony. Then the first one was taken.

**What W1_19 found.** The grid is 1450 × 900 and only 18.8% of it is land — 245,077 cells, matching
the count the pull had already recorded, so the read is independently corroborated. A mean over the
full array is a mean over the Atlantic.

The ruling makes two falsifiable predictions. *"The north–south gradient dominates solar"* is
confirmed, at −0.806 between latitude and sunshine. *"Winter temperature and wind are positively
correlated"* is **refuted as written**: across land cells it is −0.430.

**Both signs are right, and that is the actual finding.** The claim is true in *time* and false in
*space*. This project had already measured the temporal half — winter temp/wind correlation +0.507,
the cold-and-still joint tail with its 2.34× decile lift. In a given winter at a given place, cold
snaps arrive with still air. Across *places*, the windiest cells are northern, upland and exposed,
and those are the cold ones. Deriving cells partitions space, so the spatial figure is the one that
governs there; persistence, synchrony and hedging live in time and take the positive one. Pooling
them would be the definitional failure this project keeps paying for.

The most consequential number was not one of the predictions: **annual temperature and sunshine
correlate at +0.841 across space**, both dominated by the same north–south gradient. So clustering on
three drivers is not clustering on three independent axes, and the coverage curve should be expected
to rise faster than a three-dimensional argument suggests.

**What the tree cost, and it is worth recording.** The mint took seven attempts to land. Two atom-number
collisions with a concurrent lane minting the same ruling's phase-2 and phase-3 rows — they renumbered
and recorded the collision in their own store file, so nothing was lost, and their orphaned files were
removed only after checking their replacements were strict supersets. The map's size ratchet refused
the landing twice: it counts both map halves together and sits close to its ceiling, so any atom
addition can break it, and the long reasoning had to move into the simplifications store where the
control says it belongs. `site/data/` appeared in a file_scope again — the second time, caught by the
same guard both times. And the content file had to be rebuilt once because it was assembled against a
HEAD that moved: `--content` overwrites a whole file, so landing a stale assembly would have reverted
another lane's just-landed work. The gate caught that as a store/map mismatch rather than as a silent
revert, which is the only reason it was visible.

**Where it stands.** `W1_20` is next — household weights from the censuses via postcode, which the
ruling forbids taking from the SIM's own population because that would make the coverage curve a
statement about our draw rather than about Britain. It needs a pull this tree does not hold.

---

## 2026-09-06 — The startup anchors named the stalest documents and omitted every surface holding current reasoning

<!-- head: 66dfc5de04df -->

**What this stretch was about.** The set of documents a fresh session is told to read on startup —
the "anchors" — had stopped describing how to orient. It named PROJECT_OVERVIEW, the annual report
and ASSUMPTIONS: what the project *is*. It named nothing about what the project is currently *doing*
or why, all of which arrived later — the delivery seat's direction record, the decisions log, the
class registers, the stretch log.

**The measurement.** Of the five surfaces named, two had zero commits in fourteen days. Of the
surfaces the machine keeps current, the five most active were named nowhere: `PROJECT_STATE.txt`
(270 modifications in 30 days), `DIRECTION.yaml`, `decisions.jsonl`, `knowledge_map.md`, and the
stretch log. So the anchors pointed at the stalest documents and omitted the freshest.

**Why the obvious fix was the wrong one.** Ranking `docs/` paths by edit frequency and calling the
top ones anchors puts the *retired* `docs/shadow/` mirror pages above `knowledge_map.md`, and it
would never have caught the stretch log — two commits old on the day it was missed. Frequency
measures how busy a file is, not whether a reader needs it.

The structural signal is that **a module declares a path to it**. A surface the machine maintains is
one a reader can be sent to, however new. That finds eight published reader surfaces, five named and
three not — and a landing is now refused while any of them is unnamed. The instance and the class
close together.

**Two exemptions, named rather than papered over.** `DIRECTION.yaml` and `decisions.jsonl` are
assembled in two steps — a directory constant, then the filename — so an AST scan reading
single-expression constants cannot see them. They are listed with that reason, and a control reds if
either becomes discoverable, so the exemption cannot outlive its cause. This is the same shape as
`finding_classes` in the derived-artefact register, handled the same way.

**What the anchors now say.** Each entry carries a sentence saying what the surface is *for* rather
than what it is called — "Assumptions" became "every sourced assumption the world is built on, with
its anchor and its gaps". The rendered freshness table gained that as a column and an opening line
telling a reader to start there. The label is taken from the same line the path came from, so the
table cannot describe one anchor and age another.

**A live defect the new control caught immediately.** `ASSUMPTIONS.md` claimed "Last seeded:
2026-08-10" while another lane had committed rows to it on 2026-09-05 — 26 days out, and blocking
every landing. Its header now states the true date *and* says the line is checked against git, so
the next person adding a row is told what they owe rather than discovering it.

**Where it stands.** Eleven anchors, none unnamed, the check clean. Stage 1 is unchanged and next:
the fitted premise joint, the space-filling sample, and the people joint on small-area geography —
all above billing correctness, which is above the supplier optimising.

---

## 2026-09-06 — Stretch reports became a committed file on the mirror, and the lapse check shipped matching titles instead of paths

<!-- head: 073bb159ec0d -->

**What this stretch was about.** Making the reasoning behind the work durable. The director's
observation was that the prose written at the end of a piece of work — the corrections, the things
stopped short of, why a call went one way — is the most useful thing produced and the only thing not
kept: commits record what changed, and the why lived in a console window that gets cleared.

**What was already there, which is most of it.** The delivery seat writes roughly 3,000 characters
of stretch prose into `docs/direction/DIRECTION.yaml`'s `thesis_read` at every orientation, and
`tools/generate_delivery_page.py` already renders it into `site/data/delivery.json` for the
director's page. Three things were missing, not a mechanism:

1. it is a YAML scalar rather than a document — nobody reads a config field months later;
2. it is overwritten each orientation, so git holds the history and a reader does not;
3. it reaches `site/` (Cloudflare) and never `docs/`, which is the tree the GitHub Pages mirror
   publishes and the channel the advisor actually fetches.

And a fourth the seat could never have covered: an interactive session's reports entered none of it.

**What was built.** One file, `docs/status/SEAT_STRETCH_LOG.md`, newest entry first, published by the
same push as `LATEST.md`. `tools/stretch_log.py` appends entries and checks for lapses. It computes
nothing the existing renderer already computes.

**The two properties, enforced rather than requested.** A lapse is a *finding*, not a refusal:
`--check` counts the commits landed since the newest entry's recorded head and names their subjects,
and it is wired into the publish path as a log line. A gate would be wrong for a structural reason —
a report is written when a piece of work *finishes*, so refusing every commit in between would block
the work it exists to describe. And an entry must stand alone: `append` refuses a subject that leans
on the conversation it was written in ("as discussed", "per your last", "continuing") or one too
short to name its subject, because a reader in six months has none of that context. The phrase check
is on the subject only — a body may legitimately quote a console turn.

**The defect it shipped with, found within the hour.** The exclusion that stops the log counting its
own commit matched a *title* — subjects containing "stretch log". Its own landing commit was called
"the why, kept: stretch reports land in a committed file on the mirror", which says "stretch
reports", so it slipped through and the tool reported itself as owing a report for the commit that
wrote it. That is the same shape as two wrong measurements the day before, where module callers were
counted by text search and docstrings and dict keys counted as calls, and the same shape as a class
register whose title-keyed classifier could not see 92 findings. It is now excluded by *path*: if a
commit touched the log it is the report, whatever it is called.

**One thing worth keeping about the fix.** The control that drives it must answer the two `git log`
shapes differently — the commit range, and the range restricted to the log's path. A stub that
returns the same text for both makes every commit look like it touched the log, so nothing is ever
owed. A sibling test had exactly that stub and went red when the real behaviour arrived, which is how
the gap surfaced at all.

**Where it stands.** The log is live with two entries, published on the mirror, and `--check` is
green. Stage 1 continues: the fitted joint, the space-filling sample and the people joint remain
queued above billing correctness, which is above the supplier optimising.

---

## 2026-09-06 — Stage 1 housing and people anchors from NEED, two budget dials raised for one window, and a corrected sample size

<!-- head: b01b1dbe392e -->

**What this stretch was about.** Stage 1 of the three-stage sequence the director set on
2026-09-05: build a robust end-to-end SIM (weather, houses, people) before billing correctness, and
both before the supplier optimising. Concretely: anchoring the housing joint against published data,
measuring what the premise draw already carries, and sizing the space-filling sample. Plus two
budget dials raised for one allowance window, and the sequencing of a use-case register that arrived
mid-stretch.

**What was established, all from DESNZ NEED `anon2026_50k.csv` (50,000 dwellings, one row each):**

- *Floor area* is anchored from **HMRC** valuation bands via NEED, not the EPC register the housing
  ruling named. EPC needs a GOV.UK account and is the worse source on the ruling's own terms — ~60%
  coverage, transaction-biased, SAP-*modelled* consumption. NEED is open and metered. Median gas runs
  2.56× from the modal 51–100 m² band to >200 m².
- *Bungalows* are a first-class type at 7.9%, with a distribution unlike detached — closing the
  ruling's "folded into detached" gap with a published share.
- *"Off gas" is a fact about a meter, not the grid.* NEED's `MAIN_HEAT_FUEL` is derived: no matched
  meter **or** under 1,000 kWh in three years. 50.3% of flats read as "not gas", which cannot be
  off-grid — it is communal or electric heating with no individual meter. So the attribute drawn is
  `has_mains_gas_supply`, the fact a supplier actually holds. The true off-grid share stays a gap.
- *Independence invents one house in five.* Drawing the axes independently puts 19.6% of houses in
  cells the stock does not contain (1,303 detached under 50 m²; zero exist) while under-producing
  detached >200 m² — the top consumption band — by 5.15×.
- *Rejecting on labels covers 6.1% of the top-1% tail; rejecting on outputs covers 85.4%.* The
  label-based sample reports 92% overall and is nearly blind to the tail.
- *Area deprivation is mostly the house.* Median gas by IMD quintile spreads 1.38× raw and only
  1.09–1.20× within one floor-area band. Supports the housing ruling's H2; narrows the people
  ruling's geography claim to *composition*, not usage-given-the-house.

**The correction that matters most.** I published "N ≈ 100 houses covers 99.6% of the output space",
flagged as a lower bound because shape and gradient were unavailable. That was too generous. Adding
one further dimension the use cases actually need — inter-year consumption volatility, i.e.
bill-shock exposure — takes N=100 from 99.2% coverage to **32.7%**; at 250 it is 87.7% and still
short. The figure was an artefact of measuring the two dimensions that were easiest to obtain. It is
corrected beside the original claim as well as in a new document, because a figure quoted once gets
quoted again from wherever it was found.

**Calls made, and the reasoning.**

- *Source swapped from EPC to NEED* without asking: evidence in hand, reasoning sound, reversal is a
  one-line change.
- *Fork width raised to 2 — but only after refusing to do it myself.* A control asserted the value
  with "if someone widens this without a director decision, this fails". Widening it and then editing
  that guard would have been self-certifying, so it was backed out and the lever reported instead.
  The director then authorised it. The guard now pins its expected value to the window's **own
  clock** — 2 before 02:50Z on 2026-09-07, 1 after — so if the restore never runs the test reds by
  itself and says the timer did not fire. An earlier draft had the restore script edit the guard too;
  driving that on a copy left the tree red, a restore that breaks what it restores.
- *Tick cadence 1800s → 120s.* Duty cycle measured at 47%; the service is `Type=oneshot`, so systemd
  cannot stack activations — the dial's whole ceiling is ~2×, and that was reported rather than
  discovered later.

**Stopped short of, deliberately.**

- *Flow temperature* stays out of phase 1 and is a registered gap. It has zero occurrences anywhere
  in `simulation/`, and the director's reasoning is recorded: the lever only means something once a
  product could turn it down, and inventing hidden state for a ceiling nothing can act on is not
  fidelity. The consequence is written down so it is not rediscovered as an oversight — the
  turn-down lever's ceiling is *unstateable*, not merely uncomputed.
- *The use-case register's use cases* are stage 3 and none is built, however ready the mechanics look.
  Only its second half — the SIM fidelity each use case depends on — is stage 1, folded into the
  housing and people phase-1 atoms rather than minted as new work.
- *A third fork.* There is no third disjoint scope; W2_19 and W2_21 both touch
  `simulation/population_draw.py`, so it would buy contention.

**Mistakes the tree caught, worth keeping.** The map's hygiene control caught a data-asset atom filed
under the default value stream; the fix for it then landed on a *different* atom's identical two
lines, and the stale-id control named that in the same run. Separately, inserting the N correction
split a sentence and left "this is the number it asked for" standing immediately after the retraction
— worse than either alone, since a skimming reader takes the last sentence.

**Where it stands.** Stage 1 continues: the fitted joint (W2_21), the sample (W2_22) and the people
joint (W2_19) are queued and ranked above billing, which is above the supplier optimising. Both
budget dials revert automatically at 02:50Z on 2026-09-07.

---
