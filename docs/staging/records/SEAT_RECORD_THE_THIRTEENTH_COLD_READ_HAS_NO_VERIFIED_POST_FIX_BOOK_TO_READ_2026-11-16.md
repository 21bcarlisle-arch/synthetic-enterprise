**Severity:** RECORDED · **Lane:** delivery · **Epoch:** 2 · **Atom:** none (direction: cold-read exit, leg three)

# The thirteenth cold read has no verified post-fix book to read, so it was not run (2026-11-16)

*Claim `thirteenth-cold-read`. The draw asked for the thirteenth cold read "on the first publisher-verified post-fix
book". 57158c97c says that read waits on publication. This checks whether publication has happened.*

**It has not.** `site/data/publish_provenance.json` on origin/main (78a387afe3, written 2026-11-16T17:48:08Z) shows:

- `verification_state: paused` since 2026-11-16T04:26:22Z, on git=f7e17b1316.
- `last_verified` / `showing_run`: still **6fe7827ab2** (run_output_6fe7827ab2_20261111T140730Z). The twelfth read
  already used that book, and it is the pre-fix book.
- `paused_reason`: INV_OVERDUE_WITHIN_BALANCE 4, INV_OVERDUE_WITHIN_PAGE_BALANCE 7,
  INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR 5 (the exception allows at most 1).

**Why no read was run on a substitute book.** There are two other books, and both fail leg three:
- A read on 6fe7827ab2 would repeat the twelfth read on a book that does not carry the N30 fix.
- A read on the unverified f7e17b1316 book would read figures the publisher refuses to show. The exit asks for a
  *verified* book. Lowering the bar to "the book on disk" would key the exit to what is available today rather than
  to the property it tests.

**What unblocks it.** Other lanes already own the refusal. The next-book D5 row needs the debit half switched on
(78a387afe3). The 16 Nov book's seventh re-grade was refused on the same rows, and D5's world half has not been
relaunched (9e82aa2bb0). sim-runner now builds the next book only on a commit that carries those fixes (d20c70aec5).
Nothing here is new work. Re-draw this item when `publish_provenance.json` shows `verification_state` not `paused` and a
`last_verified.git_commit` that descends from ee2fa6b7a (N30's fix).

**The thirteenth read's trade, chosen now so it is not picked after the book is seen:** a vulnerability and
Priority Services Register specialist (SLC 0 Standards of Conduct, SLC 26 PSR, SLC 27 ability to pay and
self-disconnection). Trades the earlier records already used: generalist; GB metering and settlement; Ofgem price-cap and
tariff analyst; consumer-protection and collections practitioner; Energy Ombudsman case investigator; revenue-assurance
and billing-operations auditor; billing-systems test analyst; supply-point registration and meter data-quality analyst.
The overlap with collections is ability-to-pay, so the brief should point this reader at outcomes for households with a
vulnerability, not at the dunning ladder.
