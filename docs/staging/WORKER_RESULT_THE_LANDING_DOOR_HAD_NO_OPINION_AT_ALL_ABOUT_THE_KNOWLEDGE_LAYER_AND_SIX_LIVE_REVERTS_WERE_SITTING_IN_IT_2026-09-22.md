**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS_stale_copy_refusal`

# The stale-copy guard already read `.py`; what it could not read was the knowledge layer, and six live reverts were sitting in it

**Claim:** `surgical-land-refuses-a-path-whose-working-copy-predates-the-commit-that-last-touched-it`.

## The item's stated motive is wrong, and measuring it is what found the real gap

The Lane 0 item asked for one leg in `tools/surgical_land`: compare each path's working-copy mtime
against `git log -1 --format=%cI -- <path>` and refuse when the commit is newer. Its reason was that
*"nothing in the landing path asks whether the bytes are OLDER than HEAD"*.

**That is false, and has been since 2026-09-08.** `tools/stale_copy_refusal.py` asks exactly that
question by content, and `surgical_land` calls it in-process on every landing. Re-measured on this
tree on 2026-09-22: **all five** of the stale copies in the HDD pile the item was written from —
`sim/weather_ingestor.py`, `tools/build_weather_world.py`, `tests/sim/test_weather_ingestor.py`,
`simulation/premise_population.py`, `tests/simulation/test_premise_population.py` — are already
refused by `judge`, under rule `predates_landing`. The two lanes that caught them by hand
(`a2145439a`/`ce4a60430` and `7d006dd31`) were doing by hand what the door would have done.

What IS true is narrower and worse. `violations()` skipped every suffix outside `READABLE`
(`.py`, `.html`, `.js`) **in silence** — and that is where the maturity map, the knowledge layer,
the simplification notes and the staging record live.

## The rule as commissioned would have refused 13.1% of the tree, and rule 1 vouches for nineteen of them

Measured over the 358 tracked-modified paths in this working tree:

| | paths | |
|---|---|---|
| commit newer than working copy | **47** | 13.1% — what a clock-only rule refuses |
| …of which the content rules already CATCH | 15 | the leg would be a second opinion |
| …of which the content rules positively VOUCH for | **19** | **honest work a clock-only rule refuses** |
| …of which no content rule has a reader at all | 13 | the real gap |

The nineteen are structural, not incidental, and the reason is this module's own oldest recorded
finding: **`surgical_land` never writes the working tree**, by design — that is what makes it safe
for a file two lanes hold. So every landing leaves every other lane's copy stale *by mtime* while
its content stays perfectly current. Clock-staleness is the normal resting state of a shared
checkout. A clock verdict refuses honest work through the one legal door, which is the pressure
toward `--no-verify` the module exists to remove.

**So the clock is a TRIGGER, not a verdict.** `clock_judge` applies rule 1's line evidence — which
was always suffix-agnostic in mechanism — to the paths rule 1 has no reader for, and only to a copy
whose own mtime predates the commit. The clock is what makes the line evidence safe out there:
widening `READABLE` was considered when this module was written and rejected because a generated
`.json` is rewritten whole on every publish, so "contains not one line of the last commit" is its
ordinary operation. A regenerated artefact has a mtime *newer* than the landing, so it never enters
the rule — the exclusion is now a property of the artefact instead of a suffix list that rots.

## The six live instances, all of them invisible to every control until today

`python3 -m tools.stale_copy_refusal --census` now names these. They are **still uncommitted in
`/home/rich/synthetic-enterprise`**, and until this landed any lane naming them in a pathspec would
have reverted the commits below without reddening anything.

| path | reverts | what the copy deletes |
|---|---|---|
| `docs/design/simplifications/A49_...r3_and_r4.yaml` | `c2af43816` | the whole record of both landed ceiling instruments, the R3/R4 gating decision, and the "THAT CAUSE IS REFUTED" correction — replaced by the pre-correction draft |
| `docs/institutional/knowledge_map.md` | `651454d79` | a landed knowledge row: what a conversion decision at a cap boundary IS |
| `docs/design/ANNUAL_REPORT_IMPORT_DEBT.md` | `9419e2633` | the 88/83/10,900 re-measurement of 2026-09-07 |
| `docs/market_research/domestic_shift_response_arc.json` | `c325d0c53` | four CLOSED-2026-09-07 resolutions, back to open questions |
| `docs/staging/SEAT_RESULT_THE_CEILING_COST_CURVE_IS_CONVEX_..._2026-09-21.md` | `090a5d260` | the `V/c²` interval table and the "we cannot tell" verdict |
| `docs/staging/SEAT_RESULT_THE_CEILING_WAS_PRICING_ONE_CHILD_..._2026-09-22.md` | `f31e3b1cd` | the correction that closed the two-cadence claim |

Seven other unread paths were clock-stale and the line evidence **cleared** them, which is the leg
doing the half it was built for.

## What landed

`tools/stale_copy_refusal.py`: `CLOCK`, `committed_at`, `clock_judge`, its own branch in
`Loss.render` and `Loss.remedy`, `violations()` and `census()` widened to the whole changed set.
Eleven controls in `tests/tools/test_stale_copy_refusal.py`, **eight poison mutations run and each
killed by the control written for it** — the clock condition, the line evidence, the bytes-from-disk
check, the no-evidence guard, the READABLE partition, the `violations()` wiring, the remedy branch,
and the census no-opinion column.

Three things worth carrying:

- **The remedy branch is not cosmetic.** `gains` is `None` for every CLOCK loss (no symbol reader
  can read a `.md`), and the `gains is None` branch says *"cannot tell which door"* — which is false
  here. The clock has established the copy predates the landing, so it cannot be holder work over it
  and `isolate_hunks` has nothing legitimate to select. A refusal naming a door the tool would
  refuse is the bypass pressure again.
- **The bytes must be the bytes on disk.** `surgical_land --content` supplies bytes on no disk
  anywhere; an mtime is a fact about a *file*. Read anyway, the leg would grade a `--content`
  landing by the clock of the file it overwrites. It yields no opinion when the result blob is not
  the working copy, which is narrower than it could be and the only honest width.
- **A CLOCK no-opinion is still reported as one.** This leg takes a bite out of the unread
  population; it does not read it. `--census` keeps the declined paths in the no-opinion section,
  or the census publishes a coverage it has not got.

## What this does NOT close

A lane that has already pulled the landing and then rewrites over it is invisible to every rule
here, clock included — its mtime is fresh. That is the wider half of
`A_REWRITE_DELETED_THE_BINDING_REPAIR`, still open, and this narrows the class rather than closing
it. Binary and unreadable-encoding paths remain no-opinion.
