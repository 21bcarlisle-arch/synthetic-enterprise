<!-- DISCOVER artefact — GAP-Q (deliverable 4 of DIRECTOR_RULING_GAP_TRIAGE_RATIFIED). Answers the
two triage questions the director left to the agent's judgement. Answer (a) is AUTONOMOUS (no taxonomy
change — a read-time filter, not a fifth bucket). Answer (b) is DESCRIPTIVE/AUTONOMOUS (risk is folded,
and stays folded). Neither self-extends the ratified taxonomy. -->
# Gap-Triage Open Questions — Staleness Disposition & Blast-Radius-as-Risk (GAP-Q, one report)

**Serves:** `DIRECTOR_RULING_GAP_TRIAGE_RATIFIED_2026-07-28` §3(a) + §3(b) — the two questions posed as
*"your judgement, not prescriptions"*. Closes the two open judgement calls so the ratified taxonomy has
total coverage (no undisposed class) and a stated risk treatment.
**Mint:** `PLANNER_MINTED_staleness_blastradius_answers_2026-07-28`.
**Method it reasons over:** `docs/design/GAP_TRIAGE_AND_RANKING.md` (GAP2, ratified) +
`docs/design/GAP_REGISTER_MINT_SOURCE_CONTRACT.md` (GAP1 reader contract).

> **R12 up front:** neither answer introduces a gap-count target. The count of stale / minted / folded
> rows is a diagnostic on the enumeration line only — never a score, target, or headline.

---
## (a) Staleness disposition — a register entry that is no longer true

**The question.** A published register can hold a row that is *no longer true*: a simplification whose
component was since removed, a board-spec row already reconciled, a claim-status placeholder already
wired, a sanity finding already remediated. It fits **none** of the four ratified buckets — `mint`,
`deliberate-and-staying`, `blocked-on-director`, `not-worth-the-complexity` all presuppose a *real,
still-open* gap. Does it need a **fifth disposition** (`stale`/`superseded`), or is it handled by a
**read-time staleness filter** in GAP1's reader?

**Answer: a read-time filter in GAP1's reader — NOT a fifth taxonomy bucket. AUTONOMOUS (no taxonomy
change → no return-for-ratification).**

**Argument.**
1. **A stale row is not a gap; it is a bookkeeping error in the register.** The four GAP2 buckets are
   *dispositions of a gap that exists*: close it, keep it (argued), escalate it, or accept it (bounded).
   A stale row has no gap to dispose of — the thing it describes is gone or already fixed. It has no
   business competing for a *ranking* alongside real gaps; that is a category error, not a fifth choice.
2. **A fifth bucket opens a laundering door.** The §2 amendment already guards the one scope-drift
   direction — retiring an honest red as "deliberate" — by making *into*-`deliberate-and-staying` moves
   return for ratification. A `stale` **bucket inside the taxonomy** would be a *second* door to the
   same place: reclassify an awkward real gap as "stale" and it vanishes from the ranked list with no
   ratification, because staleness reads as "not a gap" rather than "a scope choice". Keeping staleness
   as a **read-time drop, evidence-gated and logged**, keeps that move auditable and out of the bucket
   the amendment protects.
3. **Ordering: the staleness filter runs FIRST, the taxonomy second.** GAP1's reader asks *"is this row
   still true?"* before any row reaches GAP2's *"what do we do about this gap?"*. Only rows that pass
   (still true) enter the taxonomy. This is the clean seam: GAP1 (enumerate the *true* open residue) →
   GAP2 (dispose of it). Staleness belongs to the reader, with the reader's existing fail-safe contract.

**The evidence test (named either way, per exit criterion).** A row is `stale`/`superseded` — and only
then dropped at read time — iff **at least one** holds, each machine-checkable:
- **(E1) Removed component:** a git commit provably removed the component the row describes (the file /
  symbol / atom named in the row no longer exists in HEAD). Provenance: `git log --diff-filter=D` /
  symbol absence.
- **(E2) Passing test over the described gap:** a live test asserts the exact condition the row flags is
  now satisfied (the simplification's error is now bounded/closed; the board-spec row now reconciles;
  the placeholder is now wired to a live consumer per R11).
- **(E3) Explicit supersedence pointer:** the row carries, or another row carries, a `superseded_by:`
  pointer to the atom/commit/row that replaced it (an auditable redirect, not a silent delete).

**Interaction with `ambiguous-defaults-to-mint` (the phantom-work guard).** Staleness is **not**
ambiguity, and the two must not be conflated:
- *Ambiguous* = "we cannot tell whether this true gap is worth closing" → **`mint`** (measure it). GAP2
  register-1 already routes an unmeasured-but-true simplification to `mint`.
- *Stale* = "this gap provably no longer exists" (E1/E2/E3) → **read-time drop** (never enters the
  taxonomy, never becomes phantom mint work).
- **The burden of proof is on `stale`.** A row that *might* be dead but shows none of E1–E3 is **not
  dropped** — it stays in the enumeration and, if unmeasured, defaults to `mint`. This asymmetry is the
  point: it preserves reds. Unproven-stale = alive = mint (measure it, or discover it is dead);
  proven-stale = dropped (with its evidence cited). A dead gap does **not** become phantom mint work
  (E1–E3 catch it first); a suspected-dead-but-unproven gap does **not** silently vanish (it fails the
  test, stays alive). Both failure directions are closed.

**Why this is autonomous but still constrained.** No fifth bucket → the ratified GAP2 taxonomy is
unchanged → this answer does **not** return for ratification. **But** the read-time drop *is* a move in
the "retire a red" direction, so it inherits the §2-amendment spirit at the reader layer: every drop
**cites its E1/E2/E3 evidence and is logged** (the enumeration diagnostic line records "N rows dropped
stale, each with evidence"), never a silent omission. Implementing the staleness filter is a change to
GAP1's **reader (BUILD half)**, which is `blocked_on: director_build_open` (R16) — so this is a **design
constraint recorded against GAP1's BUILD half, not enacted now**. Until that reader ships, GAP3
enumerates conservatively: a row it cannot *prove* stale (E1–E3) is carried as a live gap.

---
## (b) Blast-radius as risk — scored separately, or deliberately folded?

**The question.** GAP2's ranking dimension **blast radius** is defined as *"how many surfaces/consumers
the closure touches (a proxy for both value and risk)"*. Is risk scored **separately** anywhere in the
ordering, or **deliberately folded** into blast-radius?

**Answer: deliberately FOLDED into blast-radius, and it stays folded. DESCRIPTIVE → AUTONOMOUS.**

**Argument.**
1. **For these gaps, value and risk ride the same quantity.** The gaps here are fidelity/credibility
   gaps in a simulation under version control. The measure that drives *value* — how many
   surfaces/consumers a closure touches — is the *same* measure that drives *risk* (more consumers
   touched ⇒ more that can regress). They are one axis measured once; a separate risk score would
   re-measure the same consumer graph and call it a second number.
2. **Risk is bounded structurally, so there is little residual risk for a score to price.** Under
   `PROCEED_BY_DEFAULT` + everything-reversible, a wrong reversible change costs ~1 hour of compute and
   `git` reverts it. The only *irreversible* risk is the one-way-door list — and those gaps are already
   routed **categorically** to the `blocked-on-director` bucket, **not** priced in a ranking score. So
   the risk a ranking dimension would need to capture is (residual, reversible) = small, and the
   irreversible remainder is bucketed out before ranking ever runs.
3. **A separate risk dimension would be a mechanism buying almost nothing** — extra per-gap scoring and
   rationale, to price a downside the reversibility floor already caps and the `blocked-on-director`
   bucket already removes. Per the director's own steer (*"if the honest answer is folded for
   simplicity, say so and leave it — not worth a mechanism"*): **folded, left as-is.**

**The one honest caveat, recorded (not a mechanism — a named trigger).** Blast-radius currently *adds*
to the composite (`… + blast_radius − cost_to_close`): the **value** reading (bigger blast ⇒ higher
rank). A pure **risk** reading would *subtract*. Folding both into one additive term therefore encodes
an assumption — *value dominates risk on these gaps* — which is true **only because the reversibility
floor caps the downside**. That floor is a property of *pre-go-live* life (no real customers, no real
money, everything in `git`). **Un-fold trigger:** at the go-live seam — the first real, irreversible
consumer (real customer / real market / real money, the one-way-door frontier) — the reversibility floor
is gone, risk stops being reversible, and blast-radius must **split** into a value term (`+`) and a risk
term (`−`). Until then: folded, correct, and cheaper. This trigger is descriptive; it changes nothing
now and returns nothing for ratification.

---
## Coverage check (why these two answers complete the method)
- **(a)** removes the one coverage hole the ratified four-bucket taxonomy had — a row that is *no longer
  true* now has a defined disposition (read-time drop, evidence-gated) that is provably *not* a route to
  silently retire a live red.
- **(b)** makes the value/risk folding **explicit** rather than implicit, with a named condition under
  which it must be revisited — so a future reader knows it is a deliberate simplification, not an
  oversight (the exact standard §3 sets for `deliberate-and-staying`: argued, bounded, and its trigger
  stated).

## Walls untouched
- **No R13 / curriculum / generator move:** this report reasons about triage bookkeeping only; it reads
  no baseline and moves no difficulty value.
- **No self-extension of the taxonomy:** answer (a) is a *reader* filter, not a fifth GAP2 bucket — the
  ratified taxonomy is unchanged. Had the answer been a fifth bucket, it would have been HELD for
  ratification; it is not, so it is autonomous.
- **R12:** neither answer introduces a gap-count target; the count stays a diagnostic.
