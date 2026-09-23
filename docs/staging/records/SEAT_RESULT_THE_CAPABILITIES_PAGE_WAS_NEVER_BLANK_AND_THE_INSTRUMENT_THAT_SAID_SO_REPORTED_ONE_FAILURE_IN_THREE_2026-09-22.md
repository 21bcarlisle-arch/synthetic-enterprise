**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The capabilities page was never blank, and the instrument that said so reported one failure in three

**Severity note:** this document DOWNGRADES a BLOCKING finding to refuted, and the evidence is a
sweep every reader can re-run. It also fixes a real fail-silent in the instrument that produced
the false reading. Nothing in this area is left untrustworthy: the page is healthy at every
committed base, the whole `site/` tree is green, and the harness now reports every failure it sees.
**Filed:** 2026-09-22, delivery seat.
**Claim:** `the-unbounded-quotient-six-remaining-debt-sites-and-the-page-that-renders-empty`
**Pre-registration:** `docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_EMPTY_CAPABILITIES_PAGE_WAS_A_WITHHELD_FEED_IN_THE_HARNESS_CALL_2026-09-22.md`
**Corrects:** `docs/staging/SEAT_FINDING_THE_CAPABILITIES_PAGE_RENDERS_ALMOST_ENTIRELY_EMPTY_ON_THE_CURRENT_BASE_AND_NO_SCRIPT_ERROR_IS_RAISED_2026-09-22.md`

---

## The finding is REFUTED, and the drawn item's second half with it

The item asked me to "diagnose why the capabilities door renders 36 of 37 elements empty with
scriptError null". It does not, and it did not.

Driving `site/capabilities/index.html` through its own harness with every feed it requests,
supplied from that commit's own `site/data/`:

| base | result |
|---|---|
| `d3b420cbb` — the commit the finding blamed | **42 of 42 render**, 0 empty, scriptError null |
| `72f04cc3e` | 42 of 42, 0 empty |
| `852fd2854` | 42 of 42, 0 empty |
| `d93b8fb88` | 42 of 42, 0 empty |
| `08c696269` | 42 of 42, 0 empty |
| `5973f923b` — the finding's own "current base" | **42 of 42**, 0 empty |
| `869483fd1` — this turn's landing | 42 of 42, 0 empty |
| `d3a18954a` — the trunk after it moved MID-TURN | **42 of 42**, 0 empty |

Each row is a clean `git archive` extract, page and feeds both from that commit, so no
working-tree copy of anything reaches it. **The page is blank at no base in this range.**

The last row is the one that earns its place. `origin/main` advanced by six commits while I was
working, and `54aaedd20` moved **`site/capabilities/index.html` and `site/data/value_arms.json`** —
the page under investigation and its largest feed. A verdict measured before that and reported
after it would have been a stale claim about a file that had moved underneath it, which is the
shape this seat is supposed to catch rather than commit. Re-measured on the merged base: unchanged.

The finding's second-order claim — "the site lane is red for every lane that touches `site/`" — is
also false: `python3 -m pytest site/` is **893 passed, 37 skipped, 0 failed**.

## My own prediction was REFUTED, and here it is beside the answer

I pre-registered that withholding `../data/capabilities_door.json` from the harness call would
reproduce the 36-of-37 signature, because the finding's account named the other feeds and not that
one. **Wrong, and wrong in a way that was informative.** Withholding any single feed does not
produce empty elements at all — it produces FEWER elements:

| feed withheld | elements reported | empty |
|---|---|---|
| none | 42 | 0 |
| `capabilities_door.json` | 33 | 0 |
| `book_growth.json` | 38 | 0 |
| `value_arms.json` | 25 | 0 |
| `dd_opening_arms.json` | 35 | 0 |

The harness only reports elements the page actually asked for by id. A feed that never arrives
means the render that would have grabbed those handles never runs, so they are **absent, not
empty** — which is the same distinction the page itself makes in its refusal text, and I walked
straight past it when writing the prediction.

## What the page actually does when it cannot read its feed, and it is the OPPOSITE of silent

Supplying all four feeds as `{}` — present, readable, structurally useless — is the nearest thing
to the finding's scenario I could construct. The page renders this:

```
stamp        This page could not load its data (TypeError: Cannot read properties of
             undefined (reading 'entries')). Nothing below is trustworthy; the figures
             are absent, not zero.
growth-note  No campaign record is available, so this table is absent rather than empty.
arms-note    The arm comparison is not available, so it is absent rather than empty.
ddopen-note  The opening direct-debit comparison is not available, so it is absent
             rather than empty.
```

Four named refusals, on the surface, each distinguishing absent from zero. That is exactly what
`CLAUDE.md` requires of a business surface and the page does it correctly. **`scriptError: null`
is the RIGHT answer here** — there is no unhandled script error, because the page caught its own
failure and told the reader. The finding read that null as the door being unable to report itself.
It was the door reporting itself, into elements the finding counted rather than read.

## The real defect is in the INSTRUMENT, and the finding's own pointer found it

The finding's "Where to start" was right even though its headline was not: `_live_harness.mjs`
recorded only the first error and continued. That is a live fail-silent, and it is reachable:

```
three breaks in one door  ->  scriptError: "FIRST BLOCK BROKE"
                              (SECOND BLOCK BROKE and READY LISTENER BROKE are LOST)
```

And the worse half, which nobody had named: **an unhandled promise rejection killed the harness
process.** No stdout at all — so which elements had rendered, and which feeds were unresolved, were
destroyed along with the failure. That is the evidence a reader needs most, thrown away at exactly
the moment it is produced. It is also how a caller ends up guessing: my own sweep script above had
to carry a "harness produced no JSON" fallback branch to survive it.

This matters beyond one page. Every `*_reaches_the_reader` control in `site/` reads this harness,
and most assert `scriptError is None`. An instrument that loses failures weakens all of them at
once, and **none of them can see it** — a door with two breaks repaired down to one reports one
message either way, and the suite reads identically before and after.

## What landed

* `scriptErrors: [{where, message}, ...]` — every failure, each naming the channel that produced
  it (`script[0]`, `script[1]`, `DOMContentLoaded`, `unhandledRejection`). A block that throws and
  a ready-listener that throws are different repairs and can carry identical text.
* An unhandled rejection is **reported instead of fatal**. The run finishes and prints, so
  `unresolved` and the partial render survive.
* `scriptError` is KEPT, now derived as the first message. Renaming it would have been a large
  diff whose only content is a rename, across controls that would have gone **fail-open** if the
  field silently vanished — `test_scriptError_still_carries_the_FIRST_message` pins that.
* Whole `site/` tree re-run against the changed harness: **893 passed**, unchanged.

## Mutation-proven: 7 run, 7 killed

Including M1, which restores the exact original defect (first-error-only), and M6, the fail-closed
mirror — a channel that reports an error unconditionally. M6 is the one that matters most: without
`test_the_partition_is_WHOLE` asserting a healthy door reports `[]`, every other leg here would be
satisfied by an instrument that screamed on every run.

| mutation | verdict |
|---|---|
| revert to first-error-only | KILLED |
| `unhandledRejection` handler removed | KILLED |
| `where` dropped from the record | KILLED |
| `scriptError` compat field nulled | KILLED |
| DOM-ready listener errors dropped | KILLED |
| errors reported unconditionally | KILLED |
| static path loses the field | KILLED |

## Filed, not fixed

**I cannot reproduce the finding's exact 36-of-37, and I will not invent a cause for it.** No base
in the range produces it and no single-feed withholding produces it. The signature — handles
grabbed, then empty — needs a call that supplied feeds the page could partly read, and the finding
does not record the feed table it used. The honest statement is that the measurement is not
reproducible from what was written down, and **the harness call's inputs should have been recorded
with it**. That is the thing to carry forward, and it is now cheap: `_meta` already reports
`requested` and `unresolved`, and a caller filing a blankness claim should paste `_meta` verbatim.

**`tests/tools/test_every_leg_of_the_advantage_reaches_a_sentence.py` is 7 red and is NOT this.**
`_legs_on_one_bar` returns an honest `available: false` naming its reason: the error bar was
measured on the run of 2026-09-10 and the point estimate on the run of 2026-09-18, and the two did
not measure the same BOOK (70–73 accounts against 52–55). The refusal is CORRECT; the tests are
pinned to a state where the artefacts agreed, which is the "keyed to today's answer rather than to
the property" shape. The repair is either a re-run of the noise floor on the point estimate's own
run — which that reason string already calls owed work — or re-pointing those controls at the
refusal. Both are a different piece of work from this one and neither is blocked on it.
