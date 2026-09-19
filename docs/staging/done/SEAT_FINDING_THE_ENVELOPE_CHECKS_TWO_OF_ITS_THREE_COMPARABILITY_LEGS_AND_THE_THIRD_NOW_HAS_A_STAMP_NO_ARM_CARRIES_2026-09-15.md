**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the window leg of the blind envelope, split out of the stamp that made it checkable)

# The envelope refuses on two of its three comparability legs, and the third now has a stamp that no filed arm carries

**Filed 2026-09-15, delivery seat, immediately after landing `7b278dda0`** (the run output now stamps
`execution_mode.window`). Split out rather than folded in, because the stamp was measured and
mutation-proven on its own and this is a different change to a different file with a different risk.

---

## The three legs, and which of them can refuse

`_blind_envelope` in the value-arms generator withholds or excludes on two preconditions:

1. **same world** — `world_identity.digest`, and since 2026-09-15 the home digest beside it, because
   the departure level does not move when the housing stock is re-drawn.
2. **same machine** — `execution_mode.risk_committee`, evidenced for the four first-hand arms since
   `331c4958f` and still an unfalsifiable assertion for ARM C'.
3. **same window** — *nothing*. Every headline figure in a run output is an accumulation over the
   window, so a run stopped at 2020 and a run stopped at 2025 disagree on treasury, net margin and
   bad debt for a reason that is not about the company.

Leg 3 now has a stamp. **No arm carries it**, because all four first-hand arms ran before it existed.

## What is measurable today, and it is not nothing

Measured 2026-09-15 on the four cached artefacts the arms record names in their own `read_from`,
each identified by its `generated_at` matching the filed `producing_commit.resolved_at` to the
second, and each confirmed as the filed arm by summing its per-year figures to the filed line:

| arm | years | span | filed gross reproduced from its own years |
|---|---|---|---|
| A_cull | 10 | 2016–2025 | yes, exactly |
| C_cull83 | 10 | 2016–2025 | yes, exactly |
| D_tenure | 10 | 2016–2025 | yes, exactly |
| B_chosen | 10 | 2016–2025 | yes, exactly |

So the third leg **holds** for the four, on the delivered span. The boundary they were *asked* for is
unstamped in those artefacts and cannot be recovered. ARM C' has no run output on this box and can
satisfy nothing — the same shape as its missing home digest, and it must be excluded by name rather
than allowed to withhold the block, which is the branch that lane already learned to write.

## What must NOT be done with this

Adding a window precondition to `_blind_envelope` **before** the arms carry the field sets the bar
with a missing mechanism instead of with evidence: every arm would fail closed and the envelope would
withhold on account of a field none of them could ever have had. That is the shape a sibling finding
named at HEAD this week. The order is: write the measured span onto each arm first (it is a fact
about the artefact the arm was read from, not a derived figure — the derived-figure rule is why the
spans are not to be filed as a comparability *verdict*), then key the check to it.

## What done looks like

* each first-hand arm in the arms record carries the span read off its own artefact, with C' carrying
  a named absence;
* `_blind_envelope` excludes an arm whose span disagrees with the rest, the way it already excludes
  one that cannot be placed in the housing stock, and says so on the page;
* a control that goes red when two arms of different lengths are compared as equals — keyed to the
  property, not to today's four-out-of-four agreement, which would pass with the check deleted.
