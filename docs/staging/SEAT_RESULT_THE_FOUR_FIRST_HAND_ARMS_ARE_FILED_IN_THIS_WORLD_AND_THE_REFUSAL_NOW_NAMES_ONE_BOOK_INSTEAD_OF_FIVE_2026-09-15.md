**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the four re-run blind arms are filed with their own home digest and mode)

# The four first-hand arms are filed in this world, and the refusal now names one book instead of five

**Filed 2026-09-15, worker tick (LANE 0 delivery, claim
`file-the-four-re-run-blind-arms-with-their-own-home-digest-and-mode`).** Step 4 of the drawn item,
done — after step 3 had to be done again, which is
`SEAT_FINDING_THE_DRAWN_PREMISE_CHECKED_A_COMMIT_AND_THE_THING_THAT_MATTERED_WAS_FOUR_DEAD_PROCESSES`.

---

## The runs

All four completed under `systemd-run --user --unit=blind-arms-rerun`, `ALL_ARMS_DONE` at
18:58:53Z, unit `Result=success` / `ExecMainStatus=0`. The `setsid` launch of the identical work
died at 8m41s and wrote nothing; this one ran 51m29s and wrote all four.

| arm | key | rc | elapsed | selection |
|---|---|---|---|---|
| A | `cull` | 0 | 726.2s | `uniform_count` |
| C | `cull83` | 0 | 764.7s | `chosen_weighted` |
| D | `tenure` | 0 | 795.1s | `chosen_weighted` |
| B | `chosen` | 0 | 787.9s | `chosen_weighted` |

**Every arm was checked before anything was filed, and the filing asserts rather than assumes.**
All four carry `producing_commit.commit = 331c4958f` (a real sha, not a launch label),
`world_identity.digest = 39a192ce04c1eda8` (unchanged, so they remain four arms of one world), and
`world_identity.homes.digest = 35f8efe8ff02f245` — read back from
`simulation.world_home_identity.home_stock_identity()` in the same breath and equal to it. The
filing script `assert`s all three per arm and would have refused rather than written a mismatch.

## The figures, and how the mapping was established rather than guessed

The five published lines are not the run output's own key names. The mapping was settled by
printing all candidates against the filed 09-11 values, not by reading names that looked right:

| filed line | run-output key | rejected candidate |
|---|---|---|
| `gross_margin_gbp` | `total_gross_gbp` | — |
| `revenue_gbp` | `total_revenue_gbp` | — |
| `bad_debt_gbp` | `total_bad_debt_gbp` | `provisioned_bad_debt_gbp` (31,668 vs a filed 11,676) |
| `net_margin_gbp` | `total_net_gbp` | `provisioned_net_gbp` (126,296 vs a filed 147,954) |
| `net_after_cost_to_serve_gbp` | `net_margin_after_cost_to_serve_gbp` | — |

The `provisioned_*` pair is the trap: both are plausible names for the same line and both are
wrong by 20–170%. The `total_*` values land within 0.4–8% of the 09-11 figures, which is what a
moved code commit and a re-drawn housing stock should do to the same arm.

Re-measured, in this world (£):

| arm | gross | revenue | bad debt | net | net after CTS |
|---|---|---|---|---|---|
| A `cull` | 382,119.50 | 679,554.13 | 10,814.12 | 147,149.45 | 97,948.85 |
| C `cull83` | 378,405.65 | 683,784.59 | 8,331.16 | 144,101.90 | 94,836.00 |
| D `tenure` | 383,215.23 | 690,290.81 | 9,391.27 | 148,282.17 | 96,619.66 |
| B `chosen` | 381,542.41 | 675,945.72 | 8,359.26 | 148,623.22 | 99,380.18 |

No position, span or percentage is stored — all of it is computed at publish time by
`_blind_envelope`, which is the existing rule in this file and the reason it was not broken here.

## THE DRAWN ITEM'S DONE-CONDITION IS NOT REACHED BY THE WORK IT DESCRIBES, AND THAT IS THE FINDING

The drawn item says filing these four is "what puts a baseline back" on the page. **It is not, and
the consumer says so.** `_blind_envelope_homes_refusal` requires **every** arm to carry a
`home_digest` equal to the live stock:

```python
filed = [a.get("home_digest") for a in arms]
unstamped = [... for a, d in zip(arms, filed) if not d]
if unstamped:  return {"available": False, ...}
```

ARM C′ carries none, and the same drawn item correctly forbids re-running it — it has no first-hand
run output on this box. So filing four of five **cannot** flip `available` to true, and the page
still publishes a refusal. Measured before and after:

```
before:  5 of these 5 books carry no record of which HOUSES they ran on (ARM A …; ARM C …; ARM D …; ARM B …; ARM C' …)
after :  1 of these 5 books carry no record of which HOUSES they ran on (ARM C' -- the other seat's blind arm, at matched count, year mix and spend)
```

**That is still the right answer and the work was still worth doing.** What moved is not the
verdict but its subject: what stands between this page and a published baseline is now one named,
un-rerunnable arm rather than a general absence across the whole set. The next decision — whether
to publish a three-arm blind span from first-hand books only, or to keep C′ and keep refusing — is
a real choice that is now visible and costed. **It is not this tick's to make silently**, and
dropping C′ to turn the page green would be fitting the evidence to the conclusion: two of the five
verdicts turn on it, and it is the only arm holding count, year mix *and* spend.

C′ is filed with `home_digest: null` plus a named reason, and with an explicit
`figures_are_from_a_different_home_stock` warning, because the one thing a later reader must not do
is "fix" the refusal by copying a sibling arm's digest onto it. That would assert this book was
measured in houses nobody measured it in.

## Document-level prose corrected, because the re-run falsified it

* `pounds_are_not_publishable` asserted "All five arms ran SIM_FAST_MODE=1, identically". For the
  four it is now **evidenced** — each carries its own `execution_mode` block read from the
  environment of the process that ran the world. For C′ it remains an assertion **nobody on this
  box can falsify**. The sentence now says which is which instead of covering both with one claim.
* `comparable_because` said `world_digest` was "the ONLY reason these are five arms of one world".
  That is the claim the homes refusal was built to correct: the departure level does not move when
  the housing stock is re-drawn. It now names both digests and says which arms carry which.
* `second_hand_caveat` now records that C′ is also the only arm still measured in the 09-11 stock.

## What was NOT landed, and why — the feed is one publish behind

`site/data/value_arms.json` is **not** in this commit. Regenerating it here produced the correct
`1 of 5` block, but it also picked up a newer dashboard run
(`run_output_f4b8d2c6b_20260915T171049Z.json`) that **is not committed** —
`site/data/dashboard.json` and `site/data/publish_provenance.json` are both another lane's
uncommitted work. Landing a feed built from an uncommitted dashboard is exactly what
`test_the_published_supplier_claim_answers_THE_SAME_from_HEADs_committed_bytes` refuses, and it is
red in the working tree for that reason:

```
HEAD:    The published run's net margin (£147,886.78) …
working: The published run's net margin (£148,558.61) …
```

**That red is not this change.** It is driven by the two uncommitted dashboard paths that test
reads; the arms file feeds `blind_envelope` alone and cannot move a published run's net margin. A
clean-extract check could not settle it either way — a `git archive` extract has no `.git`, so this
particular test fails closed there on `site/data/dashboard.json is in no commit`, which is the
wrong harness rather than a result.

So the reader still sees `5 of 5` until the publish lane next regenerates. **This is a lag, not a
wedge**: the producer reads the arms file, so the corrected block appears on the next regeneration
with no further work. The regenerated feed is left in the working tree so that lane carries it.

**A generated file was overwritten in the shared tree in the course of this, and it should not have
been.** `python3 -m tools.generate_value_arms_data --help` is not a help flag — the module has no
argument parser and **ran on import**, writing `site/data/value_arms.json` in place over another
lane's uncommitted regeneration. No authored work was lost: the diff was 10/10 and every line of it
is regeneration drift (`generated_at`, `publishing_tree_commit`, dashboard run ids) from the same
committed producer, so the overwritten bytes are fully regenerable. It was still a write to the
shared tree that was not intended, and the general rule it breaks — probing an unknown module with
`--help` is not a read-only act — is worth more than the instance.

## What is next

1. The C′ decision above: three-arm first-hand span, or keep refusing. Needs the director or the
   seat, not a tick.
2. The publish lane regenerating `site/data/value_arms.json` once the dashboard paths land.
3. Still no shared detached-job launcher — see the companion finding.
