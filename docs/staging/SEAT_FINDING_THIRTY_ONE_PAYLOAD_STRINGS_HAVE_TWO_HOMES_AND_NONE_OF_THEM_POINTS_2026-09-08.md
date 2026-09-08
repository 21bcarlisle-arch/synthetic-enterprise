**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — thirty-one payload strings have more than one home, up to seven, and not one of them points

LATENT, and lower than the parent: **no live falsehood was found.** The sweep this documents is the
generalisation of
`SEAT_FINDING_A_POINTER_SENTENCE_WITH_TWO_HOMES_IS_FALSE_IN_ONE_OF_THEM_2026-09-08.md` across the
whole published site, and the site is currently clean of the defect. What it is NOT clean of is the
*shape*: three separate producers compose one payload string into two or more page regions, and one
of them writes here-relative prose ("the row above", "the figure above") into a neighbouring field
of the same feed. The gap between "true today" and "false the next time a sentence moves fields" is
one edit by someone who cannot see the second home.

**Filed:** 2026-09-08, delivery seat (isolated worktree).
**Pre-registration:** `SEAT_PREREGISTRATION_THE_MULTI_HOME_PAYLOAD_STRING_SWEEP_2026-09-08.md`,
written before the sweep ran.

---

## The predictions, against what came back

| | Predicted | Measured | |
|---|---|---|---|
| **Q1** multi-home payload strings (≥40 chars) | 20–200 | **31**, of 654 rendered | HELD |
| **Q2** of those, carrying here-relative prose | 0 or 1 | **0** | HELD |
| **Q3** a live falsehood outside value_arms | NO (~0.6) | **NO** | HELD |
| **Q4** cheap enough to stand up as a control | YES | **2.7s for 22 doors** | HELD |

Q3 is the one worth reading as evidence rather than as a tick: the prediction was filed at 0.6, so
holding it is weak evidence, and the reason the answer is NO is partly that the parent finding had
already converted the only instance to a landmark four hours earlier.

## Method — homes derived, never declared

Every door on disk (`site/**/index.html`, 22 of them) driven through its own boot path with
`site/_live_harness.mjs` against the **local** `site/data/*.json` feeds. A payload string's HOMES
are the `door#element` regions whose rendered content contains it, after one normal form applied to
both sides. Composition needs no model: a sentence a producer folds into a headline is found in the
headline's region because it is there.

**The door population is `site/**/index.html`, NOT `live_pixel_verify.all_doors()`, and that is a
second finding.** `all_doors()` is the sitemap plus `ia_register.INTERNAL_DOORS`; the sitemap
deliberately omits the sixteen `/knowledge/` topic pages and `INTERNAL_DOORS` is currently empty, so
it returns **6 doors of the 22 deployed**. Sweeping the advertised set would have reported a clean
site while missing the widest-shared payload strings on it — the knowledge sidebar. Whether the R11
live-pixel gate should be reading 6 of 22 is not this item's question and is left in "what is next".

## What has two homes

| Producer field | Homes | |
|---|---|---|
| `knowledge_wholesale.json .topics[].blurb` / `.title` | up to **7** | `#sidebar` of seven knowledge doors |
| `delivery.json .what_it_decided.focus[].what` / `.why` | 2 | `/harness/#delivery-decided` **and** `/harness/#delivery-next` |
| `value_arms.json .realised.arms[].what` == `.provisioned.arms[].what` | 2 | `/capabilities/#arms-realised` and `#arms-split` |

The `delivery.json` row is the live hazard. The same feed's
`what_it_got_wrong.entries[].what` already says *"the successor to the row above"* and *"every
figure above was read from the tree"* — both single-homed, both true, both written by the same
producer in the same voice as the focus items, which are not. Nothing distinguishes the two fields
to a writer. That is the parent defect's exact precondition, sitting one field away.

## What was built

`site/test_a_here_relative_pointer_has_one_home.py` — five rungs.

**The rule.** A payload sentence carrying a registered `here`-relative phrase ("higher up", "the
table above", "shown below", "beside this") and naming no landmark may render in **at most one**
region. A one-home sentence is left alone whatever it says: the page that owns it can check it. A
two-home sentence is a defect however true it is in both today, because nothing that edits either
home is looking at the other and the producer that wrote it can see neither. Keyed to the property
— no position, no wording, no page is pinned.

**The landmark exemption, and why it is not a hole.** "Under the headline figure" names what the
direction is measured from, so it is true from anywhere and cannot rot by gaining a third home.
That is the repair the parent finding shipped, so the rule must not red on it — and the detector
rung is what stops the exemption widening into a blanket one.

**Three legs against passing on blindness:** a door that rendered nothing is a red, not a clean
page; some string must reach two regions or the "at most one" quantifier is never exercised; and
some *rendered* string must still carry a registered phrase, or the vocabulary has gone stale
against how the site writes now.

**R15 — the mutations, run against the real tree and reverted:**

| Poison | Result |
|---|---|
| plant `"higher up this section"` into `delivery.json` `focus[0].why` (two homes) | RED on the rule, naming both homes and the field; nothing else reds |
| plant the landmark `"directly below this headline"` into the same two-home field | all five GREEN — the judge does not refuse its own partition |
| `_homes` returns the empty set | RED on witness + detector — a blind matcher cannot report a clean site |
| `_LANDMARK` widened to match every sentence | RED on the detector — an exemption nothing measures excuses everything |
| every rendered region dropped | RED on the blindness leg, before the rule waves the site through |

## What this control cannot see, said on the surface

Homes are derived from a real render against the **published** feeds, so a producer branch today's
data does not drive renders nowhere and is judged nowhere. **The parent defect lived on exactly such
a branch** — with the level leg sign-stable, `composition.why_not_readable` never carries the
pointer at all, and this sweep would have passed over the defect it generalises. Twelve
here-relative payload strings currently render in zero regions and this file says nothing about
them.

That is not a hole to paper over with an allowlist. It is the boundary between the two rung shapes:
the value_arms rung runs the **composers** and so sees every branch of one page; this sweep reads
the **feed** and so sees every page on one branch. Both are needed and neither subsumes the other.

## What is next

1. **The branch half, generalised.** Drive each producer's branches rather than the published feed,
   the way `_every_pointer_this_page_can_publish` does for value_arms. That is a per-producer job
   and it is the follow-on this turn did not do.
2. **`live_pixel_verify` reads 6 of 22 deployed doors.** The R11 live-pixel gate's coverage is
   derived from the sitemap, and the sitemap advertises the door set on purpose. "Not advertised"
   is not "not deployed" — the module's own `INTERNAL_DOORS` comment makes exactly that argument
   about `/director/`, and the list it fixed it with is now empty while sixteen noindex knowledge
   pages serve 200. Worth a separate item; it is a coverage claim, not a defect in a page.
3. **Nothing was reworded.** The pre-registration said no single-home sentence would be changed on
   the strength of this, and none was. A landmark rewrite with no measured defect behind it is the
   thing the parent finding's own correction warns against.
