**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

*Filed BLOCKING and downgraded to LATENT in the same turn, deliberately: it WAS blocking — the map
was over its ceiling and every lane's next commit was refused — and the rehome below cleared that.
What is left is the unfixed structural cause, which is latent by definition. The severity tracks the
condition, not the alarm it caused.*

# The spine ratchet refilled in eleven days, because the narrative moved into the one field the store does not hold

**Found:** 2026-09-06, delivery seat, while actioning the phase-2/3 registration deliverable named by
three director rulings (weather, housing, people). The registration could not be written: the map had
1,060 bytes of headroom and six rows need roughly six thousand.

---

## The measurement

`tests/design/test_simplifications_store.py::test_map_within_size_ratchet_when_store_populated`
measures **both halves** of the map against a 409,600-byte ceiling. At the start of this turn:

```
  live    docs/design/maturity_map.yaml         188,272
  closed  docs/design/maturity_map_closed.yaml  220,268
  total                                         408,540   /  409,600     99.74% FULL
```

**The map could not accept a new atom.** Not "should not" — could not. Any lane minting anything
would be refused, and the mint demand is the standing top item on the staging doorbell.

## Why it refilled, and it is not accretion

H32 moved the note class (`build_note`, `origin_note`, `harden_note`, `level_hold_note`, …) out of
the spine into `docs/design/simplifications/<atom_id>.yaml`. That migration took the map from
**521,770 → 393,692 bytes** and its own docstring records the ceiling coming back down to 400K on
the strength of it. Eleven days later the map was at 408,540.

The bytes did not come back as notes. Measured by field over the 99 live atoms:

```
  gain             48,858      <-- largest class in the spine
  real_world_twin  14,089
  expert_hour      13,528
  file_scope       11,946
  block_reason      7,109
```

**`gain` is not a store tenant.** `simplifications_store.NOTE_FIELDS` is
`(build_note, discover_note, harden_note, level_hold_note, level_note, name, notes, origin_note)` —
every one of them `*_note` or an explicit member, and the class control in
`test_atom_notes_store.py` is keyed to the `*_note` suffix precisely so a future `frame_note` is
caught by construction. A field called `gain` is invisible to it.

So the narrative did not stop being written. It was written into the one narrative field the
migration did not cover, and the suffix-keyed class control could not see it. **The control worked
exactly as designed and the prose routed around it.** The single largest example is
`W2_19_who_lives_where_money_and_composition` at 4,459 bytes of `gain` — one atom carrying more
spine than the ceiling's entire remaining headroom.

## The aggravation: nothing reads `gain`

Searched `tools/`, `background/`, `tests/design/`, `site/` for a consumer of the atom `gain` field.
**There is none** — no publisher, no gate, no renderer. It is pure spine narrative with no reader,
which is the exact profile the store exists to hold.

## And the wedge was live, not theoretical

Mid-turn, a concurrent lane landed four weather atoms (`W1_19`–`W1_22`) into the shared tree, taking
the map to **411,294 — over the ceiling.** Every lane's next commit was refused by a control none of
them had touched, and the cause was in neither lane's diff.

## What changed

`gain` was rehomed to the store as `origin_note` for **21 live atoms** (every one over 900 bytes,
excluding the four rows the other lane held uncommitted and the three phase-1 parents under active
amendment). The spine keeps the **first sentence verbatim** and declares `notes_rehomed:
[origin_note]`; the store holds the full original text.

It is a MOVE, not an edit, and it carries H32's own three-layer proof: a **round-trip hash** (the
text taken from the map must equal the text the store's independent read path returns) and a
**remainder proof** (every non-`gain` field of all 99 atoms byte-identical before and after). Both
ran green before the write was accepted.

```
  408,540  ->  391,892      (21 gains rehomed)
  401,168                   (+ the six phase-2/3 registration rows this deliverable needed)
```

## What would close this, and this is NOT it

**This finding is a reprieve, not a fix.** Twenty-one atoms were rehomed by hand under a deadline;
the twenty-second oversized `gain` written tomorrow is invisible to every control in the repo, and
the map is one busy day from 409,600 again.

The structural fix is the one H32 already proved: **make `gain` a tenant of the store**, with the
class control widened from the `*_note` suffix to the narrative class it was always trying to name.
That is an atom, not a commit — it needs the migration, the declaration contract in both directions,
and an R15 mutation proving the widened class control fires on a `gain` left inline.

The falsifier meanwhile is the ratchet itself, and it should be watched rather than trusted: it went
from 23% headroom to 0.3% in eleven days without one line of it being wrong.
