**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0

# The paired twelve price the population repair at £810.18 ± 32, and the standalone sign got seventeen times harder

**Filed** 2026-09-19 · delivery seat · scheduled tick
**Item** `read-the-twelve-at-18327d977-alone-and-pair-them-only-if-the-world-digest-matches`

> The run landed at 09:10:27Z, within a minute of the 09:10Z projection. The world digest matched,
> so the pairing was admissible and was taken. **It gives this project its first determinate sign
> on anything in the level/selection split — and what carries that sign is the repair, not the
> choosing.** The standalone reading of the twelve moved the other way: `selection_gbp` is now
> closer to zero and therefore FURTHER from a stateable sign than the family it replaces.

---

## 1. The precondition was checked first, and it passed

The pre-registration (`WORKER_RESULT_THE_TWELVE_ARE_BEING_DRAWN_A_SECOND_TIME…_2026-09-19.md` §7)
fixed the order of operations: read `world_identity` before anything else, because
`simulation/run_phase2b.py` differs between the two trees and a moved world would mean the seed ids
no longer label the same households.

| check | result |
|---|---|
| `world_identity` dict, whole, new vs old | **identical** (not just the digest — every anchor) |
| digest | `39a192ce04c1eda8` both |
| seed ids | 3100001–3100012 both, all twelve present |
| `billing_accounts_settled_in_window` per seed | **identical on 12 of 12** (154 ×11, 154; and 66/66 where old was 66) |
| `accounts_redrawn` per seed | identical on 12 of 12 |

The population check is stronger than the digest test the pre-reg asked for and is reported because
it is the one that actually answers the question: the same seed met the same number of settled
billing accounts under both trees. The pairing is a paired design, not two populations differenced.

**The pre-registration's first prediction — "I expect the digests to match" — is confirmed.**

## 2. The twelve at `18327d977`, ALONE, pooled with nothing

`docs/observability/value_cycle_ab_s1_noise_floor_next12_at_18327d977.json`, produced
2026-09-19T09:10:27Z, `producing_commit` `18327d9775c206cc7055b3c3cfee7ef7c70baee2`, clock
`settled-realised`, redraw key `elasticity`, mode `all`.

| | this family (`18327d977`) | the first twelve (`a178b56d6`) |
|---|---|---|
| n | 12 | 12 |
| mean `selection_gbp` | **−£259.29** | −£1,069.48 |
| sd | £5,413.58 | £5,398.31 |
| sem | £1,562.77 | £1,558.36 |
| sems from zero | **0.166** | 0.686 |
| sign stateable? | **no** | no |
| seeds needed for a sign, at this mean and sd | **1,744** | 102 |

They are reported side by side, not in place of each other. This is the **second** twelve-seed
family on these seed ids; the first is not superseded and is not replaced.

**These are two instruments and the fold says so, live.** Run this turn against the real pair,
`tools/fold_noise_floor_family.py` refuses and takes the branch built for it three hours before the
artefact existed:

> REFUSED: seed 3100001 appears in both … They were drawn by DIFFERENT PRICING CODE — `a178b56d6`
> and `18327d977` differ on `company/pricing/renewal_rate_chain.py`,
> `company/pricing/value_based_renewal.py`, `simulation/run_phase2b.py`,
> `tools/run_value_cycle_ab.py` … **Do NOT de-duplicate** … Fold each family alone and report them
> side by side.

No output file was written. The separation is a mechanism and not a document, and it now has a
live application rather than a fixture.

**No `instrument_stamp` key was appended to this artefact.** The first twelve carries one; nothing
in the repository reads it (`grep -rn instrument_stamp` returns one prose line in that family's own
result doc). The fold and `generate_value_arms_data._floor_tree_pairing` both key on
`producing_commit`, which this artefact carries natively from the producer. Every byte here is the
producer's.

## 3. THE RESULT: the paired contrast, and what it actually counts

Same twelve seeds, same world, same households, one bounded change to the objective. Differencing
seed-by-seed:

| quantity | paired mean (new − old) | sd | sem | t (df 11) | 95% CI |
|---|---|---|---|---|---|
| `selection_gbp` | **+£810.18** | £50.24 | £14.50 | **+55.86** | **[+£778.26, +£842.11]** |
| `level_advantage_gbp` | **−£810.18** | £50.24 | £14.50 | −55.86 | — |
| `value_advantage_gbp` | **£0.00** | **£0.00** | — | — | — |

All twelve paired differences are positive (range +£743.09 to +£899.58); sign test p = 4.9e-04
before the t-test is consulted at all.

**Pairing works, and by two orders of magnitude.** sd falls from £5,413.58 unpaired to £50.24
paired — a factor of **107.7**. The pre-registration's second prediction — *"I expect the paired sd
to be far below £5,398"* — is confirmed, and its own falsifier ("if the paired sd comes back near
the unpaired sd, pairing buys nothing here") did not fire.

### And here is the sentence the number must be read with

`value_advantage_gbp` is **bit-identical on every one of the twelve seeds** — maximum absolute
paired difference £0.00, not £0.01. `level_advantage_gbp` and `selection_gbp` move by exactly equal
and opposite amounts on every seed. By the producer's own definitions
(`run_value_cycle_ab.level_vs_selection`, lines 4189–4192):

```
value_advantage = value_net − control_net        ← unchanged, to the penny, 12/12
level_advantage = level_net  − control_net       ← −£810.18
selection_gbp   = value_advantage − level_advantage = value_net − level_net
```

So the change between the trees **moved the LEVEL arm and left the value arm and the control
untouched**. The £810.18 is not value created and it is not value the choosing was worth. It is
**the level arm's net falling by £810.18 because it stopped pricing renewals the value arm had
refused.**

Named at the line: `renewal_rate_chain.py` stopped stamping every decline with `"value_based"` and
now reads `active_policy().renewal_margin_arm`; `value_based_renewal.py` gained
`_no_lawful_predictable_offer` — **one refusal raised by both arms**, so `flat_at_level` now
declines at the same support-bound frontier the value arm declines at. Before the repair the level
arm priced a population the value arm would not, and booked margin on it; the residual called
"selection" carried that difference.

**This is the price of the contamination that
`WORKER_RESULT_THE_SELECTION_LEG_DIFFERENCES_TWO_ARMS_OVER_DIFFERENT_PRICED_POPULATIONS…_2026-09-18.md`
identified qualitatively.** It is now a measured quantity with a 95% interval, on matched seeds.

It accounts for **75.8%** of the first twelve's mean deficit (£810.18 of £1,069.48) — stated once,
with the caveat that the denominator is itself 0.69 sems from zero and therefore a magnitude that
cannot be signed. The numerator can be. They are the same quantity in the same unit over the same
twelve households, so the ratio is a quantity; it is a ratio with one unstable end.

## 4. What this does NOT do, and it is the more important half

**It does not give `selection_gbp` a sign, and it made the standalone route worse.** Moving the
mean from −£1,069.48 to −£259.29 while the sd stood still pushed the family from 0.69 sems from
zero to 0.17. The seeds an unpaired family would need to state a sign — at this mean and this sd —
went from **102 to 1,744, a factor of 17**. A more honest instrument is further from an answer,
which is the expected shape when the old answer was partly an artefact.

**It does not close the contested-width question, and nothing in flight will.** The published
eighteen are `4e7938f673` + `9f0ab066f`, byte-identical on the value arm — one instrument, I1. This
family is 20 paths from I1. The one-variable run the page says is owed — *these twelve seeds at
`4e7938f673`* — is still owed and still unrun. This run holds the seed set fixed and varies the
instrument; that run would hold the instrument fixed and vary the seed set. They are complementary
and neither substitutes for the other.

**It must not be pooled toward the published figure**, and by a stronger argument than the item
gave: there is no tree here of which these twelve are a larger sample. Every candidate is 20 paths
away.

## 5. What is owed

1. **The published `selection_gbp` on the arms page is contaminated in the same direction, and its
   caveat has no magnitude.** `generate_value_arms_data.py` already puts the two-populations warning
   on the surface rather than in a footnote (`same_priced_population`, the `WHO to price` sentence)
   — that is correct and stays. What it cannot say is *how much*. Both I1 trees predate the
   2026-09-18 repair, so the published negative carries a downward bias of this class. **£810.18 is
   an indication of its size, NOT a correction**: it was measured on a different instrument's book
   and transporting it would be exactly the pooling this whole item exists to prevent. The owed
   work is a sentence on the page giving the reader the direction of the bias and one measured
   magnitude from a named other instrument, fail-closed about which book it came from.
2. **The one-variable run at `4e7938f673`** remains the only thing that can separate instrument
   from seed set for the published eighteen.
3. **No top-up run on this family.** The fold refuses to pool it with the first twelve, so a top-up
   would buy an artefact nothing can join. The instruction stands and is now demonstrated rather
   than argued.
4. All thirty-six seed rows in this lineage predate `05684780e`, so **none of them sees the world's
   default-tariff exit.** That caveat carries forward unchanged onto this family.

**What would prove this insufficient:** a paired reading published anywhere without the sentence
that `value_advantage_gbp` did not move. A +£810.18 with t = 55.86 beside a thesis quantity is
exactly the shape that gets quoted as "the selection leg is now positive and significant". It is
not. Total value advantage was unchanged to the penny; £810.18 moved from one side of the
decomposition to the other. Value re-attributed is not value created, and this project's mission
binds that distinction on every decision.

---

**Landed this turn:** `docs/observability/value_cycle_ab_s1_noise_floor_next12_at_18327d977.json`
(producer bytes, unmodified) and this reading. The fold refusal above was run against the real pair
and wrote no output.
