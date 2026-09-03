**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# What the undecomposed floor leg must return in the live world

*Delivery seat, 2026-09-03, lane-0, claim `the-baseline-was-beaten-in-a-world-that-no-longer-exists`.
Filed while `se-noise-floor-all-20260903b` is queued and has produced nothing. §1 is measured; §2 is
the prediction and its answer is not in hand.*

---

## 1. Measured — the two decomposition legs, like-for-like, same mode, two worlds

Both 2026-09-03 legs carry `world_identity.digest` **`39a192ce04c1eda8`**, which is the live world
and the same world as the three-arm run published under `/capabilities/`. Same seed family
(11111 / 22222 / 33333) on all four.

| leg | 2026-08-31 (old world) | 2026-09-03 (live world) | move |
|---|---|---|---|
| `only` — redraw the priced roster only | stdev **3,776.27**, range 7,547.97 | stdev **5,923.04**, range 10,983.77 | **+56.85%** |
| `except` — redraw everything but the roster | stdev **0.00**, range 0.00 | stdev **0.00**, range 0.00 | unchanged |

The `except` leg returns three byte-identical seeds in both worlds: redrawing every household
outside the hand-authored roster moves the selection figure by exactly nothing. That is the
decomposition's attribution — essentially all of the floor's variance sits on the priced side —
reproduced independently in the live world rather than carried over from the old one.

**P4 is NOT graded by this.** P4 was written about `selection_gbp_spread.stdev` on
`value_cycle_ab_s1_noise_floor.json`, which is the **`all`** leg, and that leg was OOM-killed at
11:27Z (`ExecMainStatus=9`) and wrote nothing. `only` and `all` are different modes and grading one
against the other's prediction is the leg-swap this claim exists to stop. P4 stays pending. What §1
establishes is that the floor's direction of travel on the mode that *can* be compared is **wider**,
which is P4's direction on a different leg.

## 2. The prediction, filed before the `all` leg returns

In the **old** world the `all` and `only` legs returned the *same* selection spread to every digit
printed — stdev 3,776.2691398368634 and range 7,547.969953000022 on both — while `except` returned
zero. That is not a coincidence: `only` redraws exactly the households that produce priced
decisions, `except` redraws the rest, and the rest contribute no variance, so the undecomposed leg
has nothing to add to the priced one. If that structure is a property of the instrument rather than
of the old world's particular numbers, it must hold again.

> **P6 — the undecomposed leg reproduces the `only` leg.**
> **Predicted:** `value_cycle_ab_s1_noise_floor_20260903.json` returns
> `selection_gbp_spread.stdev` of **5,923.04 ± 5%**, and `range` near **10,983.77**.
> **Refuted if:** it lands outside 5,600–6,250, or if `except` and `all` stop reconciling to
> `only` the way they did in the old world.
> **If refuted**, the reading is about the INSTRUMENT and not about the world: it would mean the
> decomposition's premise — that the unpriced side contributes no variance — is a fact about the
> old world's draw and not a property of the book, and the decomposition would need re-deriving
> rather than re-running.

> **P7 — the current contrast still cannot be resolved, and now by a wider margin.**
> The live-world `value_advantage_gbp` is **£2,335.87**. Against a live-world floor near £5,923 that
> is 0.39× — comfortably inside.
> **Predicted:** `selection_distinguishable_from_zero` stays **false** in the live world.
> **Refuted if:** the re-run resolves it, which on a floor that widened would need explaining.

**Neither figure may be published until the `all` leg lands.** £2,335.87 over £5,923.04 is a ratio
between a contrast from the live world and a spread from the live world, so it *would* be a
quantity — but it is the wrong leg. The `only` leg's spread does not bound the published figure;
`redraw_scope` on the `all` artefact says so in its own words: *"every household re-drawn — the
undecomposed floor, and the only mode whose spread bounds the published figure directly."* Quoting
the `only` leg because it is the one that finished is the same move as quoting the old world's floor
because it is the one on disk.

`tools/generate_value_arms_data._current_world_contrast` refuses the verdict in code until a floor
naming this world is on the page, and it will keep refusing after these two legs land, correctly,
because neither is the undecomposed one.

## 3. What is owed next

`se-noise-floor-all-20260903b` — queued behind the two legs above, ~2h24, started after they exited
at 12:23Z. When it lands with digest `39a192ce04c1eda8`: grade P4, P6 and P7 here; re-run
`decompose_floor` (which needs all three legs and refuses any that do not share one world); wire the
live-world floor into `_current_world_contrast` so the page states a verdict; and grade P5's
substantive clause on the digests, not on the `producing_commit` proxy §4 of the sibling
pre-registration already flagged as the worse test.
