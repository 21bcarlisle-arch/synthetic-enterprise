**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0

# The superseded panel prints a size now, and `no_sign` was carried — but not structurally

**Filed** 2026-09-21 · autonomous worker · scheduled tick
**Claim** `the-panel-beside-the-refusal-still-signs-the-choosing`
**Proved through the page's own JavaScript against the published feed. Four mutations run and reverted.**

> The drawn item asked two things. The first is done: `#arms-split` no longer states a direction
> for the choosing. The second asked me to decide whether `no_sign` needed wiring or was already
> carried by `verdict_withheld_because` — and **the answer is both**, which is why the honest
> remedy is a guard rather than a comment. It is carried today. It is not carried by construction,
> and the branch where it is dropped is reachable.

---

## 1. What the panel said, and what the panel beside it said

One page, one quantity, two answers:

| region | the choosing | what it stated |
|---|---|---|
| `#arms-legs-first` | `current_world.selection_leg` | **NO DIRECTION IS STATED FOR THIS LEG** — 9 seeds, family straddles zero, centre on the other side of zero from the published draw |
| `#arms-split` | `provisioned.selection_gbp` | **−£1,904** — a signed pounds figure, with a trailing clause saying the words *"not a direction"* |

The trailing clause was true and it was not the refusal. A reader met a minus sign in bold and a
qualification in running prose at the end of the same sentence. The control over that panel,
`test_the_selection_leg_reaches_the_reader_with_its_own_sign`, **required** the signed figure to be
present and was satisfied by the phrase *"not a direction"* appearing anywhere in the panel. It was
the thing holding the defect in place, and it went red the moment the page became more honest —
which is this project's named shape for a control pinned to today's answer.

## 2. What is on the page now

- **The size, from the feed.** `provisioned.selection_magnitude_gbp` is a new published field.
  The door does **not** call `Math.abs()`: a number the page strips a sign off is a number the page
  produced, sitting where no control over the feed can see it. `selection_gbp` keeps its sign in the
  feed so the magnitude stays auditable against the run.
- **The refusal as a heading, not a footnote.** *"NO DIRECTION IS STATED FOR THE CHOOSING ON THIS
  CLOCK"* — amber, own block, the same vocabulary `legVerdict` uses one panel along.
- **The back door, named and closed.** Removing the sign is not the whole repair. The two arm
  advantages in that panel keep theirs and their difference **is** the size, so the direction is one
  subtraction away. A page that stripped the sign and said nothing about that arithmetic would be
  hiding the recovery rather than refusing the claim — the *reader does the addition* shape this
  site already records against the population-repair bias clause. The new feed clause
  `and_subtracting_the_arms_does_not_restore_it` disqualifies the subtraction on the same ground:
  both arms are single draws on a clock no seed family has ever graded.
- **Fail closed on an older feed.** A publish predating `selection_magnitude_gbp` renders a named
  absence. It does **not** fall back to the signed figure.

## 3. The `no_sign` question, and why "it is already carried" is only half true

`_leg_in_this_world` composes `no_sign` and then either assigns it to `verdict_withheld_because` or
appends it. On the published feed `selection_leg.no_sign` (497 chars) **is** a substring of
`selection_leg.verdict_withheld_because` (1,019 chars), so the sentence does reach a reader today.
That containment is now asserted rather than assumed.

**It is not structural.** Both folding branches are gated on `resolved is not None`:

```
if resolved is not None and stability.get("checked") and not stability.get("stable"):   # branch 1
if resolved is not None and stability.get("sign_determined") is False:                  # branch 2
elif verdict_withheld_because and no_sign:                                              # append
```

`_resolvable` returns `None` when the point estimate is `None`, and `_verdict_stability` is computed
from the floor family and does not need the point. So a leg with **no figure but a read floor
family that straddles zero** publishes a non-empty `no_sign` beside `verdict_withheld_because: None`
— and the old door fell through to *"AND NO DIRECTION IS STATED FOR THIS LEG, AND NO REASON IS
GIVEN"* with the reason sitting unread one field away. The page told the reader no reason existed
while holding the stronger of the two.

`withheldReason()` now concatenates when `no_sign` is not already inside the withheld reason. On the
ordinary feed it changes nothing; in the gap it is the only thing that puts the sentence on screen.
The `indexOf` guard is the other half — an unconditional concatenation gives every ordinary reader
the same paragraph twice, and that is its own rung.

## 4. R15 — the mutations, each run against the INDEX copy and reverted

| poison | result |
|---|---|
| restore `signed(sp.selection_gbp)` in the door (the relapse, one line) | `..._as_a_SIZE_and_never_as_a_SIGN` **and** the MUTATION rung red |
| drop the amber refusal block, keep the size and the muted clause | three rungs red, including the feed-bytes rung |
| `legVerdict` reads `leg.verdict_withheld_because` only | `..._whichever_field_the_feed_puts_it_in` red on the orphaned-reason leg |
| `withheldReason` concatenates unconditionally | the same rung red on the duplication leg (count == 2) |

The MUTATION rung poisons **feeds**, never the door — a test may not edit production — and carries
its own reachability leg: the live feed must still satisfy everything the poisons broke, so a page
that always printed the missing-reason branch would fail it.

## 5. Attribution of the reds that are not mine

`site/` plus the two value-arms suites ran 1,151 passed / 5 failed in the shared worktree. One
(`test_every_tied_here_relative_pointer_is_true_from_the_region_it_lands_in`) is in
`HEAD_RED_REGISTER.md`, standing since 2026-09-20. The other four name `site/data/delivery.json`
pointers and a `discrimination_across_the_family` registry row — none of which this diff reaches.
Isolated by swapping the three changed source files into a `git archive HEAD` extract and
regenerating the feed there: **all four green**, so they are other lanes' dirty artefacts in the
shared tree and not this change. `site/test_the_baseline_comparison_reaches_the_reader.py` is
173 passed / 1 skipped.

The static-quality ratchet is red at `I001: 1306 != 1307` — one violation **fewer** than the
baseline, from another lane's dirty file. The baseline is not lowered; `surgical_land`'s
HEAD-plus-paths extract is what gates this landing.

## 6. What is still owed

Nothing on this claim. The superseded panel's own figures — the two arm advantages — keep their
signs and are now explicitly disqualified as a route to the choosing's direction, but they are
themselves ungraded single draws against the control. **Whether a panel may sign an arm advantage on
a clock with no seed family at all is the wider question**, and it is not this item's. It is one
floor run on the settled-provisioned clock away from being answerable rather than arguable, and
`no_spread_on_this_clock` already says so in the words that make it conditional.
