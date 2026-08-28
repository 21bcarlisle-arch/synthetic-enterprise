# Held work — built, tested, and deliberately not in the tree

Work that is **finished enough to run** and is being kept out of the shared working tree because
landing it would leave other lanes red. Each entry says what blocks it and what restores it.

A held patch is not a shelf. It is a claim that the work is done and the *decision* is not.

---

## `founder_book_*` — the 80-founder book (director, 2026-08-28: "take the 80 founders")

**Files:** `founder_book_live_population.patch`, `FOUNDER_BOOK.yaml.held`,
`test_founder_book.py.held`

**Restore:**
```
git apply docs/design/held/founder_book_live_population.patch
cp docs/design/held/FOUNDER_BOOK.yaml.held      docs/design/FOUNDER_BOOK.yaml
cp docs/design/held/test_founder_book.py.held   tests/simulation/test_founder_book.py
```

**What blocks it:** applying it turns four tests in
`tests/simulation/test_net_new_acquisition.py` red, and the reason is a question rather than a
stale fixture — with 800 of the 1,200 customer-year budget spent on founders, the campaign keeps
issuing paid quotes (1,066 → 1,707) after the budget can no longer convert them into wins
(211 → 45). Re-baselining those numbers before ruling on that behaviour would be changing a
figure to fit a run.

**Why it is HELD rather than committed:** the gates read the whole tree, so the change sitting in
the working tree makes *every lane's* commit red, not just mine. Holding it keeps the tree
green for everyone while the ruling is outstanding.

**The ruling it waits on, and the rest of the evidence:**
`docs/staging/WORKER_FINDING_THE_FOUNDER_BOOK_EXPOSES_A_CAMPAIGN_THAT_KEEPS_QUOTING_AFTER_THE_BUDGET_STOPS_2026-08-28.md`
