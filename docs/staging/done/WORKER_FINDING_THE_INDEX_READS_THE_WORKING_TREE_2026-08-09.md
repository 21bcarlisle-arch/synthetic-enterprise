# [WORKER-FINDING] The capability index reads the WORKING TREE, so a module that exists on one machine reads as `wired` — and G6 refused an honest record for a second time (2026-08-09)

**Severity:** BLOCKING · **Lane:** H_harness

**Found during:** DIRECTOR_STEER_SECOND_PUBLISH_WEDGE_2026-08-09 DO-NEXT #2 — getting
`tools/run_annual_report.py` into version control (landed `83a55b750`).

**Advances:** AO1_capability_index, AO2_write_time_reuse_gate — the index's population question and
the G6 phrasing sensitivity are both properties of the write-time pair.

---

## Finding 1 — the index cannot distinguish "in the repo" from "on this machine"

**Observed, with evidence.** While `tools/run_annual_report.py`, `tools/run_segment_report.py` and
`tools/run_phase4c_pipeline.py` were all untracked (`git ls-files` empty for each, HEAD carrying
none of them), the live index reported:

```
$ python3 tools/capability_index.py --find "composition root"
tools.run_annual_report      wired   Composition root — run the simulated world, then report on it.
    2 test file(s) ... | 5 caller(s) | see it: test run, command
tools.run_segment_report     wired   Composition root — run the segment simulation, then report on it.
```

`wired`, with five callers, for a module a fresh checkout does not have. `build_rows` walks the
filesystem, so an untracked file is indistinguishable from a committed one.

**Why this is the fail-open shape and not a nitpick.** The index's whole purpose is to answer
"do we already have this?" before someone writes it again. On a fresh checkout — the cloud seat, the
designated destination — the honest answer for these three was **no**, and the index said yes with
five callers. It is the same single-point-of-failure the steer was about, seen from the index side:
the artefact that is supposed to tell you what the repo contains was reading one working tree.
`--check` therefore also cannot notice that a `wired` row has no committed file behind it.

**Not fixed on sight (SELF_INTERRUPT_DISCIPLINE).** The candidate shape, for whoever draws it: a row
whose path is absent from `git ls-files` is reported in a distinct state (`untracked`, not `wired`),
and `--check` fails on one — because "wired" claiming an untracked module is a claim the index
cannot support. Watch the vacuity direction: on a clean tree there are zero untracked capability
modules, so the guard must be proven against a seeded one rather than assumed live.

## Finding 2 — G6 refused an honest record on a bare word, second instance

`_NOTHING_CLAIMED = re.compile(r"\b(none|nothing|no (existing|current|prior|other)|not? (existing )?match)", re.I)`

The refused INDEX line said, in one sentence, *both* what the index returned **and** that nothing
else composes the same thing:

> `INDEX: searched "run annual report", "composition root" -- the only rows returned are these three
> modules themselves ...; nothing else in the index composes "run the world, then describe it".`

G6 read the bare `nothing`, put the terms back through the live index, got 3 rows, and refused with
*"the record says the index found nothing … Finding something is not a refusal — say what you found
and why new code anyway."* The record **had** said what it found, by name, in the same clause.

**The honest reading, and it matters for the steer's reserved case.** This is a refusal of a
PHRASING, not of a disclosure: rewriting the identical fact without a nothing-word passed on the
next attempt, and no truthful statement was found that the gate would not accept. So the steer's
"if the gate blocks a truthful provenance disclosure, that is its own finding" condition was **not**
met, and this is not being reported as though it were.

**It is still a real defect, and now a class with two instances** — the earlier one refused an
honest REUSE record on the word "none". The guard is a regex over free prose deciding whether a
sentence makes a claim; a record that names its matches and *then* says "nothing else" is the most
informative form of the record and the one most likely to trip. Candidate shape: evaluate G6 against
the *structure* — refuse only when the record names no match at all — rather than against the
presence of a negation word anywhere in the note. The wall to preserve while doing it: G6 is the one
guard that can contradict the record from an independent source (R15), so weakening it into
never-fires is the worse failure. Prove both directions.

---

**Filed by:** the scheduled worker tick that actioned the steer. Registered, not built.
