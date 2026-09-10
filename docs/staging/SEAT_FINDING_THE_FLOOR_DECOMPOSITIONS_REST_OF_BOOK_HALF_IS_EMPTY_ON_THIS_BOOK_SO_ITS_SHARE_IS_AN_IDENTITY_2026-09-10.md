**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — the floor decomposition's "rest of the book" half is EMPTY on this book, so its 100% priced share is an identity and not a measurement

The direction was to run the two missing noise-floor legs (`only`, `except`) at nine seeds on the
book `value_cycle_ab_s1_three_arm_20260908.json` publishes, and replace the `V_rest = 0` corner the
page states with the measured split.

**On this book that measurement has an empty half, and `V_rest = 0` is not a corner — it is what the
instrument is built to return.**

**Filed:** 2026-09-10, delivery seat (isolated worktree).
**Pre-registration (written before, refuted by this):**
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_THE_TWO_MISSING_FLOOR_LEGS_WILL_SAY_ON_THIS_BOOK_2026-09-10.md`

---

## What was measured

One instrumented full-window pass at `c066c114b` — the `all` leg's own tree — with
`price_elasticity_for_customer` wrapped in a **pass-through** recorder, so the run is byte-identical
to an unpatched one and only the call sites are counted. `/var/tmp/se-floor-legs-20260910/probe_partition.json`:

| | |
|---|---|
| elasticity calls in the whole run | **298** |
| distinct accounts that drew one | **67** |
| the priced roster the cut is made along | **100 accounts** |
| roster accounts that drew | **67** |
| roster accounts that **never** drew | **33** |
| accounts that drew **outside** the roster | **0** |
| calls outside the roster | **0** |

**Every elasticity draw the run makes belongs to a household the value arm priced.** The `except`
side of the cut is not small. It is empty.

## What that does to the two legs

Both refuse, correctly, for opposite reasons — `noise_floor`'s own guards, quoted:

* `except`: `calls["redrawn"] == 0` → *"its 100 roster entries matched none of the 298 elasticity
  calls this run made, so its 'spread' would be zero by construction."*
* `only`: `calls["held"] == 0` → *"the `only` leg held NO household fixed, so it is the undecomposed
  floor wearing a decomposed label."*

Those two guards were built for exactly this and they work. **The direction's measurement is not
unmeasured on this book; it is undefined on it.**

A truncated smoke run (`--end-year 2016`, `only` mode) hit the second refusal in 76 seconds, which is
what sent me to the probe rather than into a six-hour leg.

## Why `V_rest = 0` is then an identity and not a result

`V_rest` is the variance of `selection_gbp` under re-drawing the elasticity of everybody outside the
priced roster. If nobody outside it ever draws one, re-drawing them changes no byte of the run, and
`V_rest = 0` exactly — for every seed, in every world, at any book size. It carries no information
about the world.

`docs/observability/value_cycle_ab_floor_decomposition.json` publishes
`rest_of_book_sd_gbp: 0.0`, `priced_share_of_variance: 1.0`, `share_is_decisive: true` and a
`reconciliation_ratio` of `0.99999998`, and the page renders them. **A reconciliation ratio of one
between a quantity and itself is not a control passing.**

**The old book was not quite this, and the difference matters.** On the 2026-09-03 book the roster
was 67 accounts and **5** accounts drawing **15** of 350 calls fell outside it. So the `except` leg
there was a real measurement — over five households, returning the identical `selection_gbp` for all
three seeds. Near-powerless, but not vacuous. The arm has since priced a **larger** roster (100
accounts against 67) and swallowed the remainder whole. **The instrument got worse as the arm got
better, and nothing was watching that direction.**

## What this does and does not settle about the page's claim

`site/data/value_arms.json → current_world.selection_leg.what_would_settle_the_sign` publishes
**44.90×** this book for the published draw and **2.82×** for the nine-seed mean, and states that
both are **lower bounds** because they sit at the unmeasured `V_rest = 0` corner and *"the real books
are larger"*.

**On this instrument they are not lower bounds. They are the answer, exactly.** `V_rest = 0` holds
identically, so `m = (V − V_rest)/(c² − V_rest) = V/c²` with nothing left to increase it.

And the verdict the direction hoped for — *whether the rest-of-book cascade alone already exceeds
either contrast, the "no book of this shape can" finding* — **does not hold via this route.** The
cascade's contribution here is zero and exceeds nothing.

**But the reason is not a fact about the world, and the page must not be allowed to read as though
it were.** It is that `price_elasticity_for_customer` is only reached on the paths of households the
arm priced. The published `±£1,810.50` is a **within-priced-book** spread. It is a defensible error
bar on the *selection mechanism* — which is what the leg is about — and it is **not** an error bar
that has ever varied the rest of the book, because on this book it cannot. Nothing on the page says
so.

## The remedy, in the order it should be done

1. **Correct the page's own sentence.** `what_would_settle_the_sign` must stop saying the real books
   are larger, and say instead: on this instrument `V_rest` is identically zero because the
   `except` half of the cut is empty, so these multipliers are exact — and the instrument has never
   varied the rest of the book.
2. **Make the decomposition say when its own half is empty.** `decompose_floor` should carry the
   `except` leg's `accounts_redrawn` and refuse to publish `priced_share_of_variance: 1.0` as a
   measurement when it is zero. A share of one over an empty complement is the same shape as a
   reconciliation of one between a quantity and itself.
3. **Only then ask the real question**, which this instrument cannot: does the rest of the book's
   churn cascade move `selection_gbp` at all? That needs a floor keyed to something the rest of the
   book *has* — not the elasticity draw, which it never reaches.

**Item 1 is the one that is live on a public surface**, and it is the one the running leg is about to
turn from a derivation into an observation.

## What is still running, and why it was launched anyway

`longjob-floor-legs-20260910` (own cgroup, locked worktree at `c066c114b`, artefact
`/var/tmp/se-floor-legs-20260910/driver.rc`) is running the **`except` leg first**, nine seeds.

The probe is **one pass at the base seed**, and the elasticity feeds the churn decision, so a
re-drawn seed can move which households are offered a renewal — the `all` leg's own rows show
`accounts_redrawn` moving between 66 and 67 across seeds. So the empty half is a **derivation**, and
this run is what makes it an observation. Either outcome is the answer:

* it refuses on seed 11111 (~40 min) → the empty half is observed, and the `only` leg is skipped by
  the driver because with nothing held it is the `all` leg already on disk;
* it does **not** refuse → a handful of outside calls exist on some seed and it produces the
  measurement the direction asked for, at ~4 hours.

## Severity: why LATENT and not BLOCKING

No published figure is demonstrably wrong. A lower bound that turns out to be tight is still a
correct lower bound, and the error runs the conservative way — the page asks for a bigger book than
it needs. No verdict flips. What is wrong is that a `priced_share_of_variance` of 1.0 is rendered as
a finding about where the noise comes from, when on this book it could not have come out any other
way.

## An unrelated number this pass happened to reproduce

The probe's pass returned `selection_gbp = £319.10` at `c066c114b`. The three-arm artefact the page
publishes returns **£270.21** for the same call in the same world at `04361d6c7` — a difference of
**+£48.89**, which lands inside the **+£38.96 to +£61.38** band this project had already measured
between those two trees, from a completely different comparison. That band had one witness. It now
has two, and the second was drawn for another purpose entirely. Recorded here because it bears on
`SEAT_FINDING_THE_FLOOR_DECOMPOSITION_CHECKS_THE_WORLD_AND_NOT_THE_TREE_2026-09-10.md`, landed
earlier today.
