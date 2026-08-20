# WORKER FINDING — twenty-one door tests point at a directory that is in no tree, and they wedge the file they live in

**Severity:** BLOCKING · **Lane:** H_harness

rank: after-current-EP6-pass
found_by: EP6_wall_protocol_typing pass 42 (a refused `surgical_land`)
found_at: 2026-08-20

## The observation (observed-with-evidence, R9)

`tests/tools/test_couple_w2_11_d5.py` has 21 tests that error before reaching an
assertion:

```
RuntimeError: door harness failed: Error: Cannot find module
  '/home/rich/synthetic-enterprise/site/proof/_render_harness.mjs'
```

The two constants they resolve through are `tools/couple_w2_11_d5.py:9005-9006`:

```python
_DOOR_HARNESS = Path(__file__).resolve().parent.parent / "site" / "proof" / "_render_harness.mjs"
_DOOR_INDEX   = Path(__file__).resolve().parent.parent / "site" / "proof" / "index.html"
```

`site/proof/` does not exist in the working tree, and it is in **no tree**:

```
$ git ls-tree -r HEAD --name-only | grep -c 'site/proof/'
0
```

A sibling harness of the same name DOES exist and is tracked —
`site/knowledge/electricity-wholesale/_render_harness.mjs` — so this is a path
that moved (or a door that was never committed), not a tool that was deleted.
Which of the two it is has **not** been established here and must not be
asserted: that is the first job of whoever takes this.

## Why it is blocking, not cosmetic

The pre-commit gate selects tests by filename stem, so **any** commit touching
`tools/couple_w2_11_d5.py` or `tests/tools/test_couple_w2_11_d5.py` re-runs this
file and is REFUSED. That is not hypothetical: it refused EP6 pass 42's first
landing after a 15m51s gate cycle (`21 failed, 1236 passed`), and the pass had
to re-home a live-caller wiring onto a different module to land at all.

`tools/couple_w2_11_d5.py` is the W2_11 ↔ D5 coupling harness and appears in the
`file_scope` of at least nine maturity-map atoms. All of them are currently
unable to land anything in it.

## What this is NOT

Not caused by EP6 pass 42. The failures reproduce with that pass's changes fully
reverted, because the missing path is a property of HEAD.

## What would close it

Either the door is restored (`site/proof/index.html` + `_render_harness.mjs`
committed), or the constants are re-pointed at wherever the door actually lives
now, or the 21 tests are retired with a stated reason. Whichever it is, the
closing evidence is a green `tests/tools/test_couple_w2_11_d5.py` at HEAD — and,
per R11, a check that the door those tests are about is reachable on the live
site, since a green suite achieved by deleting the subject is the failure mode
these tests exist to catch.

Filed rather than fixed on sight (SELF_INTERRUPT_DISCIPLINE): the machine is not
blocked — EP6 pass 42 landed by re-homing — and the repair is a site-lane
question about a door this pass has no standing to retire.

---

## The answer to this finding's own first question (established 2026-08-21)

The two possibilities named above — a path that moved, or a door never committed
— are both wrong. `site/proof/` was deleted **deliberately, by director ruling**
(observed-with-evidence):

```
$ git log -1 --format='%H %ad %s' --date=iso 03dd8c49e
03dd8c49e4a7ab94b67215cfc33cd3e437b2a39f 2026-08-20 09:40:53 +0100 The five tabs
are the site now: eleven pages deleted, their content moved, and 25,700 lines of
surface nobody could reach are gone
```

That commit's body quotes the ruling — *"I don't want hidden pages, and I don't
want the maintenance and link burden that comes with them... no permanent limbo,
no page kept because deleting it feels risky"* — and records `proof, evidence ->
Harness`. The same ruling deleted the redirect apparatus with it: `site/_redirects`
keeps two rules and `/proof` is not one of them. The door was retired on purpose,
and restoring it would cross the ruling.

**The content moved; the surface these tests walk did not.** `/harness/` carries
`renderGaps`, `gap-kpis` and `gap-note`, fed from `data/proof.json` — but it
renders four aggregate counts and prose. Searching all of `site/` for
`renderCoupledGaps|coupled-gaps|gap-row|gap-basis|classifyGap` matches only two
stale data blobs (`site/data/simplified.json`, `site/data/tours.json`) and **no
HTML**. So the four regions `_DOOR_REGIONS` names — `gap-val`, `note`,
`components`, `basis` — reach no reader as rendered pixels anywhere on the site.

## The R11 live check this finding demanded — and the trap in its answer

Fetched 2026-08-21: `https://poesys.net/proof/` answers **200**, serves the
retired door, still carries `renderCoupledGaps`/`coupled-gaps`/`gap-row`/
`gap-basis`/`classifyGap`, and still fetches `../data/proof.json`. By the letter
of the closing condition above, "the door those tests are about is reachable on
the live site."

**It must not be read as a subject to re-point at.** It is a ghost, and this repo
already knows: `docs/observability/retired_paths_served.json` records `/proof/`
as `still_served: true`, note *"served from a cache the deployment no longer
backs"*, and `tools/retired_paths_still_served.py` exists to notice when it
clears. Nine paths that ruling deleted answer 200 for the same reason
(`/proof/`, `/world/`, `/company/`, `/customers/`, `/now/`, `/glossary/`,
`/director/`, `/shadow/`, `/evidence/`); the pages retired in earlier passes
(`/method/`, `/simplified/`, `/project/`, `/tours/`, `/platform/`, `/supplier/`,
`/sim/`) now answer 404. The live `/harness/` is byte-identical to
`site/harness/index.html`, so the ruling's additions deployed cleanly — what
persists is cache, not a deployment. A control re-pointed at a cached object
would go green against something no tree can rebuild and that vanishes without
notice.

## Why re-pointing cannot honestly green the suite either

The checks are working, not broken. `check_reader_render_sites` fires on
`available is not True`, and `check_door_row_surfaces` refuses to score a census
that did not run ("an unavailable check is a failed check"). Nothing here is
fail-open: the control is red because its subject was retired the day before it
noticed. Re-pointed at `/harness/`, it stays red for a second true reason — the
successor does not print the carried note verbatim, and `note_verbatim` failing
is precisely what turns four of the five figures' measured precisions back into
claims about an internal string. Both reds are accurate statements about what the
reader lost.

## What is owed (recommendation, not yet done)

The per-pair figures are **still published — as JSON**: `/data/proof.json`
answers 200 and carries fifteen pairs with `value`, `components`, basis
(`baseline_g0`/`raw_gap`) and `note`. What was lost is the *rendered* surface,
not the publication. So the repair is a withdrawal, and it has to be a loud one:

1. Teach the module the door was **RETIRED** (naming `03dd8c49e`), distinctly
   from unreachable. `RuntimeError: Cannot find module` asserts something is
   broken, which is false, and is what wedges the file.
2. **Withdraw** the reader-surface claims that rested on the door — the
   `door:coupled-gaps` regions, and the `renderer:` sites that counted as reader
   surfaces only because the door concatenated the note verbatim — rather than
   deleting the assertions. A withdrawal that returns no violations is the
   fail-silent pattern R15 names.
3. **Guard the withdrawal so it can fail**: any door that renders coupled-gap
   rows again must bring the walk back. That mutation is what proves the
   retirement is a fact about the site rather than a way of being green.
4. Decide explicitly whether a fetchable JSON artefact counts as a reader surface
   for these figures' declared precision. R11 says the rendered value, and this
   module's whole premise is "the rendered pixel, never the source". If JSON does
   not count, then several `PUBLISHED_GAP_CONSUMERS` entries are claiming a
   reader precision that no longer meets an artefact — and saying so out loud is
   the honest outcome.

Item 4 is a design decision about what a live control asserts of the company's
published output, which is why this pass did not rush it in a bounded tick:
greening this suite by guessing would be exactly the "green suite achieved by
deleting the subject" that this finding was filed to prevent.

**Still BLOCKING — the wedge is NOT cleared.** `tools/couple_w2_11_d5.py` and
`tests/tools/test_couple_w2_11_d5.py` remain unlandable for the atoms that name
them. What this pass removes is the wrong hypothesis: the next taker does not
need to look for a moved path or an uncommitted door, and must not restore the
retired one.
