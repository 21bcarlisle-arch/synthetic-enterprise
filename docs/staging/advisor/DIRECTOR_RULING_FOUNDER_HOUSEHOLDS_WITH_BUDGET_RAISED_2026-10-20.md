**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] Founders are 400 households, and the settlement budget rises to about 7,800 customer-years (2026-10-20)

**Type:** RULING, through the advisor channel. It answers `for_the_director` row `your-400-household-founder-ruling-fits-in`, which recommended "households with the budget raised" (`019924a7`). The advisor told the director:

> Recommendation: households, budget raised to about 7,800 customer-years; meanwhile it holds 400 meter points. My view: agree, with one caveat — about 0.5 GB of memory headroom is thin, so I'd ask it to watch peak memory on the first few runs. Runs will also take longer, roughly in proportion to the extra customer-years.

The director's words, from chat on Tue 20 Oct:

- 17:40 BST: "Great, agree with all you said."

## What to do

1. **Switch the unit.** Set `founder_unit: households` with `founder_accounts: 400` in `docs/design/FOUNDER_BOOK.yaml`. Raise the settlement budget to the figure your measurement gives for 400 households plus a campaign that can still win, about 7,800 customer-years. Record the derived figure, not a typed guess. Trailer: `Director-doc: his-words -- founders are 400 households, budget raised, director 20 Oct 17:40`.
2. **Close the row** `your-400-household-founder-ruling-fits-in` with this ruling.
3. **His caveat binds.** Watch peak memory on the first production runs at the new shape, at least the first three, against the 6,008 MB allowance. Record each peak in the stretch log. If a run comes within 5% of the allowance, or the reaper fires, go back to 400 supply points for production. Then bring a proposal that closes the gap (streaming per R8, or index-once per R6). Do not trim headroom elsewhere to make room.
4. **Re-run the checks on the change.** Run `tools/world_claims.py` over the new book. Record before and after on the same seed: homes, supply points, dual share, wins per year, run time. Record this as the new held draw (EP17).
5. **Report** in one stretch-log entry: the budget figure and how it was derived, the census before and after, peak memory and wall time for each of the first runs, and the published figures it moves.

— Director ruling, 20 Oct 2026, his words above; the drafting is the advisor's.
