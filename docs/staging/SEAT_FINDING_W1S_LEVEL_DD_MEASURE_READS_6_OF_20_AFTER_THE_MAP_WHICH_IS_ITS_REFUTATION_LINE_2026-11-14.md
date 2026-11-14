**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# W1's level-DD measure reads 6 of 20 after the map, exactly its refutation line (2026-11-14)

**What was found.** The learning-loop line now prints what each landed map has had to answer since
it landed (`background/learning_loop.py` `area_map`, rendered by `delivery_seat._render_learning_loop`).
On origin at d7b9f0d321:

- level-dd: map `LEVEL_DD_AREA_MAP_2026-11-11.md` landed 18285bfa11; since it, 7 code-or-reader misses
  of 23 graded predictions.
- repayment-posting: map landed ad48737415; since it, 3 of 8.

W1 (`docs/institutional/ways_of_working.md`) filed: over the next 20 graded level-DD predictions after
the map lands, code-or-reader misses are **at most 3 of 20**; **refuted if 6 or more**. Oldest first,
the grades after 18285bfa11 are 72c936d313 (7 graded, 3 misses), 3159a16f2c (7, 3), b2f8e23fc0 (3, 0),
f5d1203024 (3, 0). That is 6 of the first 20. On the face of it, the measure is refuted.

**Why I cannot yet say it is refuted.** W1 counts predictions filed *after* the map lands. A `Graded:`
trailer records when a prediction was graded, not when it was filed. 72c936d313 graded the day the map
landed, so its predictions may have been filed before the map existed. Two more open questions: the
older `LEVEL_DD_AREA_MAP.md` (a454d03fcc, 10 Nov) is also on origin, and `area_map` takes the newest
one added. Also, did the misses' predictions name a state on the map, as W1 requires?

**Next step.** Read the prediction files behind 72c936d313 and 3159a16f2c for their filing dates.
If they were filed after 18285bfa11, record W1's measure as refuted, beside its prediction, and
re-map level DD before its next fix. If they were filed earlier, the count starts at b2f8e23fc0,
and so far it reads 1 of 9.
