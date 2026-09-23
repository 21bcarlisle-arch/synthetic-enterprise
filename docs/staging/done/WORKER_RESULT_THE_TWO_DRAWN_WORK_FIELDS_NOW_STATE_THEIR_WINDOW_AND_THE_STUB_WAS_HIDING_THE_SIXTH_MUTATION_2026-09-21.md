**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the two drawn-work fields state their window now, and the control's own stub was hiding the mutation it claimed to catch

**Filed:** 2026-09-21, 19:55 local. Drawn as Lane 0 delivery,
`the-seats-own-ledger-field-names-a-population-it-does-not-hold` (fifth listing).

---

## The headline

**Both drawn-work fields in the orientation brief now state what they were measured over, in the
text a reader sees, and the misnamed one is called `lane_0_drawn_never_landed`.** A control over
the whole partition pulls both window statements out of ONE rendered prompt and requires them to
exist, to be two, and to be the two the code actually measured over. Six mutations, all fired.

## What was wrong, restated from the code rather than from the brief

`build_brief` carried `focus_drawn_never_landed`, built from `_drawn_never_landed(now)` →
`delivery_lane.drawn_without_landing()`, which reads the claims ledger over
`DRAWN_WITHOUT_LANDING_HORIZON_SECONDS` (a day) and returns **every** Lane 0 item handed out in
that horizon whose window closed empty. Nothing on that path filters to the focus — the `focus_`
in the name was false, and it was the only statement of population the reader had.

Inches away sat `previous_focus_drawn`, fed `focus_drawn_since(since)`: the previous focus alone,
over the **stretch**. Two windows, two populations, neither stated, both read side by side by a
bounded session that will not open `delivery_lane.py`. The absence of a window statement was read
as "the stretch", because every other key in the brief is.

## What changed

| | before | after |
|---|---|---|
| key name | `focus_drawn_never_landed` | `lane_0_drawn_never_landed` |
| its window in the prompt | unstated (the empty branch said "in the last day") | `MEASURED OVER THE LAST 24.0h OF THE DRAW LEDGER`, on **both** branches, read from the constant |
| steer verdict's window | unstated | `window=` passed at the call site, on the verdict **and** welded to the `note` that gets quoted |
| the steer verdict in the prompt | JSON only, 21 keys down | its own sentence, next to the other block, saying it is neither the same window nor the same population |
| a caller that does not state a window | silent | `AN UNSTATED WINDOW` on the face of the verdict |

No stored record needed migrating: `decisions.jsonl` and the delivery page read
`previous_focus_drawn` only, and no Python outside the tests read the old key name.

## The finding inside the finding — a stub hid the mutation the control claimed

The brief-level legs monkeypatch `_drawn_never_landed` to hand the brief two known populations.
That is what makes them a control on the **brief** — and exactly what makes them blind to a focus
filter inside the function they stubbed. The mutation *"filter `_drawn_never_landed` to the
focus"* was listed in the docstring as caught; it ran **silently** against all three legs. The
repair is a fourth leg that drives the real reader against a real temp ledger with a live focus
that does not contain the drawn id.

**The class:** *a control that stubs the function whose behaviour its claim is about proves the
stub.* This is the R15 catalogue's shape, arrived at from a new door — not "the mutation was
caught by a different leg", but "the mutation could not reach any leg".

## The second finding — a killed mutation sweep left its mutation in the shared tree

The first sweep ran under a 2-minute Bash timeout, was killed mid-run, and its `finally: restore`
never executed. I then checked the tree was clean by grepping for **three literals from the other
mutations** and concluded it was. It was not: mutation (d) was live in `background/delivery_seat.py`
for the next ~20 minutes, and the second sweep read it as the base — so five "FIRED" verdicts were
measured against a contaminated original. All six were re-run on the clean base afterwards and all
six fire.

**The class:** *a check keyed to today's three answers, not to the property.* The property is "the
file equals its pre-sweep bytes"; the check asked "are these three strings absent". Cheap remedy
for any future sweep: hash the file before and after, and assert the hash, not the greps.

## Mutation evidence (clean base)

```
FIRED  (a) key renamed back to focus_drawn_never_landed
FIRED  (b) steer block drops MEASURED OVER
FIRED  (c) both blocks state the same window
FIRED  (d) never-landed filtered to focus          <- only the unstubbed leg sees this
FIRED  (e) call site drops window=
FIRED  (f) horizon hand-typed instead of read from the constant
```

## Landing

Landed with `python3 -m tools.surgical_land`. The shared working tree carries another lane's I001
fix, so `test_static_quality_ratchet` reads 1306 against a frozen 1307 and reds **every** lane; a
HEAD extract measures 1307, and the four paths landed here are I001-clean, so the tree this commit
creates sits at the baseline. The baseline was **not** lowered — the fix is not this lane's to bank.

## What is NOT done

The ratchet's stale I001 entry is still open in the shared tree and will red the next lane that
commits by pathspec. It belongs to whichever lane is holding the dirty file that fixed it, and
lowering it from here would bank another lane's work under this one's name.
