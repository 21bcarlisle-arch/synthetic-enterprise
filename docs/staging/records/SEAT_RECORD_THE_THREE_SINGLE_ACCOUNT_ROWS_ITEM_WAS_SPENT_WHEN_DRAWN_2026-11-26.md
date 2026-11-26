# The three-single-account-rows item was spent when drawn: each row is fixed or carried on origin

**Severity:** low. This record closes a duplicate item. Nothing is built here.

`the-three-single-account-invariant-rows-refusing-the-publish` was drawn on 2026-11-26. It was written
2.6 h earlier, and since then all three of its rows have been answered on origin/main:

- **(1) SYN-2016-099, INV_OVERDUE_WITHIN_PAGE_BALANCE 8.** 470513f81b traced the allocation and
  found the desk's 1.30 is right. The page prints a final-bill payment the world never asked for.
  It was fixed at the world in d688a224a: a leg's bills are now issued in period order, so the stub
  final bill no longer goes out before the February bill. 1eefc88d58 closed the finding. The page-side
  shape that fix does not reach breaches nothing, and it is filed LATENT as SYN-2016-244.
- **(2) SYN-2016-107, INV_OVERDUE_WITHIN_BALANCE 1.** The world was wrong: the gas credit note was
  paying the electricity scheme debit. 91c32797b3 fixed it by making a credit bill's note its own leg's
  cash, and 68cc1baa67 closed the item. 945306b995 filed the prediction for that book on origin.
- **(3) PROS-2023-0338g, the closing refund of 30.68 with no class.** It now has a class.
  c9245cd038 shows it is a double ask, not N29: a leg that left level DD while still supplied was
  asked the level debit again at its final bill. The fix is recommended there and carried by the
  live continuation `a-leg-that-left-level-on-supply-is-not-asked-the-level-debit-at-its-final-bill`.
  That continuation is not duplicated here.

The gas-repeat row stays with the 4df2b4f892 / 9ed3dc9787 thread, as the item said.

What would show this record wrong: the first book on a commit at or after d688a224a still refuses on
SYN-2016-099 or SYN-2016-107. Grading that book is the job of the continuation
`grade-the-first-book-carrying-91c32797b3-and-9ed3dc9787`. This turn does not grade it.
