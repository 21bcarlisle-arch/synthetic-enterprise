**Severity:** RECORDED · **Lane:** E_finance_treasury · **Epoch:** unassigned · **Atom:** `unminted`

# The growth campaign's 2022-24 wins owe GBP 1,331.99 of Market Stabilisation Charge over 40 legs; the patch that books it is built and waits for msc8

Found by the delivery seat, 23 Nov 2026, on claim `campaign-wins-pay-the-market-stabilisation-charge`.

**Duplicate check.** The live claim `the-first-term-strike-gap-to-the-cheapest-fix-is-attributed` shares
`company/interfaces/growth_desk.py` with this one. That claim is about the first-term strike's cost
components, which is different work. This one is not a duplicate, and both proceed.

**Built, not landed, by direction.** `/var/tmp/se-msc-keep/msc9-campaign.patch`, with its message in
`msg9-campaign.txt`, applies on top of `msc8.patch`. Both apply cleanly on origin/main `03bd1213a2`.
The patch is built in the locked worktree `/var/tmp/se-msc9-wt`.

What it does: `run_phase2b.campaign_market_stabilisation_charge_events` charges each served
`net_new_won` leg on its own fuel. The volume is the leg's registered `eac_kwh` or `aq_kwh`, the
charge date is its contract start, and it books through `growth_desk.book_market_stabilisation_charge`.

msc8 is not on origin. Its landing script (`land7.sh`) has never been launched: there is no log and no
end-file. Until it lands, msc9 has nothing to stand on.

**Measured at the run's seed** (shipped config, pre-registered in `/var/tmp/se-msc-keep/msc9_prereg.txt`):

| | |
|---|---|
| Served campaign legs | 388 (219 electricity, 169 gas) |
| MSC events, 14 Apr 2022 – 31 Mar 2024 | **40** |
| Total charged | **GBP 1,331.99** |
| Paid by the four Jan–Feb 2023 legs | GBP 714.40 |

**What this changes in msg8's claim.** msg8 said the campaign's wins are most of 2022-24's wins, so
leaving them uncharged overstates 2022-24 margin "in exactly the years the thesis is hardest".

- That is true by count.
- By money it is small. The rate is zero through 2022. The campaign won no 2022 home at this seed.
  After spring 2023 the rate is under GBP 16/MWh for electricity and GBP 3/MWh for gas.
- Pre-registration P2 (GBP 5k–25k) is **refuted**.
- The 2023-24 first-term attribution should not expect the MSC to close much of its unattributed gap.
  This agrees with `e9744505f`'s reading that the MSC is a minority of the gap.

**Not yet read:** the replacement path's own 2022-24 MSC total. It needs a full run, and the first
book carrying msc8 and msc9 is that reading.
