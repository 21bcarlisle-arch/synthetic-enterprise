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

## Done (worker tick, 16 Nov 2026 ~03:45 GMT)

**Filed after the map, so the count stands: W1 is refuted at 6 of 20.** 72c936d313's predictions were
pre-registered at 22:24 GMT on 11 Nov, ten hours after 18285bfa11. The predictions 3159a16f2c graded are
s.7 of the 11 Nov map itself, which landed in 72c936d313. Each was written inside the map, so each sits on
it by construction. On the older map (a454d03fcc) it was refuted sooner: 4 of 14 on e58699ec9c, which
18285bfa11 said in its message and nowhere else.

Recorded beside W1's prediction in `docs/institutional/ways_of_working.md`, with the split the total
hides. Code misses were 1 of 20, against 18 of 80 before. Reader misses were 5 of 20, against 8 of 80.
At 20 the intervals overlap. The stop condition is unchanged. The level-DD area has no fix in hand: the
BLOCKING finding waits only on the 16 Nov publish's grade. The next level-DD fix should be preceded by a
map that traces the readers. That is stated on W1 as a suggestion, not a new rule, and W1's 24 Nov review
decides it.
