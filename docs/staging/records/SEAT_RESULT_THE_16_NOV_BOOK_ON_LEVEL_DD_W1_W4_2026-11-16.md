**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# Result: the 16 Nov book on LEVEL_DD s.9.8's W1–W4, the world's final-bill net (2026-11-16)

Grades `docs/design/LEVEL_DD_AREA_MAP_2026-11-11.md` s.9.8 W1–W4 (filed 12 Nov, W4 12 Nov 23:30Z, two 14 Nov
amendments), all before this book existed.

**The book.** `docs/reports/run_output_8a300fa561_20261116T031305Z.json`, `producing_commit` 8a300fa561, which
carries 37d934286 (the world net). Page chain: `/var/tmp/fab-ab2/chain_full.py` (the publisher's five steps in its
order) at origin/main 61d8c871d4, in an isolated worktree. Readers: `/var/tmp/repay-truth/desk.py` (unchanged since
s.9.7) and `/var/tmp/w14/read_w.py`. Outputs: `/var/tmp/w14/`.

| | predicted (as amended 14 Nov) | read | verdict |
|---|---|---|---|
| W1 world final-bill nettings on level legs | 168–213 legs, GBP 4,030–4,990 | **not readable on this book** (below) | ungraded |
| W2 class F, with the 5 credit-bill accounts clear | 0–3; 5 of 5 clear | **27** (all F-shaped, s.9.8); **2 of 5 clear** (SYN-2016-037, -333). -225 owes 159.20 (unchanged to the penny), -444 24.88 (was 71.45), -482 33.23 (unchanged) | **refuted** |
| W3 R5 desk-written-off accounts printing owed | 0–3 | **27, GBP 674.59** | **refuted** |
| W4 reverse-F; SYN-2016-244's final bill asked | 0–3; GBP 30–45 | **not readable on this book** (below) | ungraded |

**W3 reads exactly what the 14 Nov A/B's e17ebc596 arm read**: 27, GBP 674.59, the same 27 accounts, none in or out
(`/var/tmp/fab-ab2/desk_new.json`). 159 commits lie between them, including S6b, ceeefa5960 and the moratoria.
Against s.9.8's F set on the 6fe7827ab2 book: 9 left (PROS-2016-0067, PROS-2017-0038 and PROS-2017-0249 because they
are off the book) and 12 joined.

## Why W1 and W4 cannot be read

The book does not record what the world asked on any bill. `triad_log` is empty. The world payment-truth rows
carry each month's outcome and the settlement amounts only. The page ledger builds every paid bill's payment from
the printed face (`tools/generate_billing_ledger.py`, `"amount_gbp": round(payer_face - scheme_applied, 2)`), then
nets credit-bill credit alone. **Correction beside the 14 Nov record:** the A/B's "SYN-2016-244 final bill asked
77.82 at both commits" read the page's payment, which is the face. It was not the world's ask, so it could not
have moved. Its W1 proxy (`credit_applied_gbp`) is page-side too. Here it reads 245 legs, GBP 8,593.49.

**SYN-2016-244, reconstructed from the book's own inputs (a read, not a grade).** Bills May–Dec 2016 total GBP
316.97, and the world's settlements on them GBP 359.09. So the leg's ledger holds about GBP 42.12 of credit before
its final bill. If 37d934286's branch fires, the world asks 77.82 − 42.12 = **GBP 35.70**, inside W4's band. But
the refund log, the page side, still refunds **GBP 42.14** on 2 Feb 2018, after the 21 Jan final bill. If the world
netted, that household is credited twice: this is reverse-F by construction. The same could hold on any ever-level
leaver the page refunds without netting its final bill. That is at most **151 refunds, GBP 17,873.94**, an upper
bound on reverse-F, not a count.

## What the misses say, and what they cannot

**I cannot yet say why W2 and W3 missed.** No book that lacks 37d934286 shares this population: both A/B arms
carried it. So nothing has yet measured, one variable at a time, whether the world net moves R5.

The hypotheses, ranked by evidence:

1. **Our model of our own code was wrong. The page balance R5 reads cannot see the world's ask.** The page posts
   paid bills at face (above). The world's net can reach the page only through the desk's write-off. Evidence:
   SYN-2016-225 owes 159.20 and SYN-2016-482 33.23, the same to the penny as on the 6fe7827ab2 book, where the world
   still collected at face.
2. **The branch does not fire on these legs.** Possible causes: `final_month` is not detected, or the leg's ledger
   credit is not on `_leg_balance_on`'s remittance keys. The 4-case unit test exercises the branch on a fixture,
   not on a book.
3. Both are true. H1 would mask H2.

**The discriminator is one instrument. It also unblocks W1 and W4.** Serialise the triad's final-month net per leg
(face, ledger credit, ask) into the run JSON as world-side observability. The next book then reads W1, W4 and
whether the branch fired (H2). Comparing that with the page closing balance settles H1. The ask is a world
quantity, so this is observability the harness reads; nothing crosses to `company/`.

**Reverse.** Delete this file and the s.9.8 grade paragraph. No code changed.
