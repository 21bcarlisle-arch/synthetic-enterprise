# WORKER FINDING — the publish-gate wedge two docstrings cite has never existed; an unmapped ledger key is admitted as an extra coupled pair

**Severity:** LATENT · **Lane:** H_harness

**Raised:** 2026-08-18, `D34_the_resolution_floor_covers_two_of_five_figures` worker tick (LANE 3 idle draw, DISCOVER/FRAME)
**Rank requested (P-1):** backlog
**Why this doc exists:** the repair is in `tools/generate_proof_data.py::_coupled_gaps` and
`background/coupled_triad.py`, outside D34's `file_scope`
(`tools/couple_w2_11_d5.py`, `tests/tools/test_couple_w2_11_d5.py`). QUEUED, not fixed on
sight — SELF-INTERRUPT DISCIPLINE. R9 labels throughout.

LATENT rather than BLOCKING is a decision, not a default: no unmapped key is in the live
ledger today, so no published figure is currently wrong. What is wrong is the belief that a
control would stop one, held in two shipped docstrings, which is why this is worth a doc
rather than a silent fix.

---

## The claim, quoted from the tree at HEAD `99f5df61a`

```
background/live_payment_triad.py:748   "NO ::suffixed keys, which the Proof door counts as
                                        unmapped extras and would wedge the publish gate"

tools/couple_w2_11_d5.py:11290        "Do NOT write ::suffixed keys: they are not map-coupled
                                        pairs, so the Proof door counts them as unmapped extras
                                        and wedges the publish gate (the 2026-07-18 lesson)"
```

Both are load-bearing: they are the stated reason the live scorer writes ONE bare-keyed
detection entry and rides the other four dimensions' figures inline in the note.

## What is actually there — `observed-with-evidence`

Measured this tick against the live atoms and the HEAD ledger, in memory, with **nothing
written to `docs/observability/coupled_gap_ledger.json`**: one extra key injected into a copy
of the ledger, then the two shipped consumers called.

**`tools/generate_proof_data.py::_coupled_gaps`** — the Proof-door panel:

| | baseline | with one injected key |
|---|---|---|
| `pair_count` | 14 | **15** |
| `measured` | 14 | **15** |
| `unmeasured`, `blocks_l3_count`, `wall_leak_count`, `basis_finding_count` | 0 / 0 / 0 / 14 | unchanged |

The added row is rendered as a first-class pair:

```
world_atom    'W2_11_payment_behaviour_source::belief'
company_atom  'D5_account_hierarchy_payments'
world_name    ''            world_level  None
chip          'measured'    severity     'blue'
value         0.0833907649896623        blocks_l3  False
```

**`background/sanity_daemon.py::_coupled_gap_digest_line`** — the daily digest, same injection:

```
base:  COUPLED-TRIAD gap (14 pairs; ...) -- ... W2_11<->D5: 0.083; W2_2<->C_cohort_discovery: 1.034; ...
inj:   COUPLED-TRIAD gap (15 pairs; ...) -- ... W2_11<->D5: 0.083; W2_11<->D5: 0.083; W2_2<->...
```

The same pair, the same label, the same number, printed twice.

**Isolated across three key shapes** — `…::belief`, `…::detection_latency`, and a bare
`ZZ_not_a_world_atom_at_all`. All three are admitted identically, `pair_count` 14 → 15,
`world_name ''`, `world_level None`. So the `::` is not what does it: **nothing in either
consumer rejects a ledger key the map does not pair.** There is no unmapped-extras count, no
red, no raise, and no publish gate involved at any point.

## What the cited lesson actually says

Commit `c874a5711` (2026-07-18), the authority both docstrings point at, reads:

> "…writes ONLY the bare headline entry (no ::suffixed proof-door **pollution**)"

*Pollution* is precisely what the measurement above shows — a spurious row and a duplicated
digest line. Somewhere between that commit and now the prose hardened "pollution" into "wedges
the publish gate". `inferred`, not observed: no commit was found that built and then removed
such a gate; the search was over `tools/generate_proof_data.py` and
`background/coupled_triad.py` between 2026-07-17 and 2026-07-20, and the only hits were the
coupling-wiring commit above and an unrelated Proof re-home.

## Why the hardened version is the dangerous one

The two directions are not symmetric. "This pollutes the door" tells a writer to be careful.
"A gate will wedge if you do this" tells a writer the mistake is *already controlled* — so no
control gets built, and the mistake, when it arrives, lands on the public Proof door and in the
director's daily digest with no red anywhere. That is the fail-open shape: the belief in the
control substitutes for the control.

It also has a live consequence for the atom that found it. D34's residue ("publish before
precise" — four of five published dimensions' resolution caveats reach no reader) has an
obvious cheap discharge: give each dimension its own ledger entry. The docstrings say a gate
forbids it. The measurement says nothing forbids it, and that both readers would re-count one
pair's five dimensions as five pairs. Same conclusion, opposite reason, and only one of the two
reasons survives contact with the code.

## The repair, and what would make it R15-real

Not a docstring edit. A docstring is what failed here.

1. **A control on the ledger keyset** — every key in `coupled_gap_ledger.json` is a world atom
   the live coupling pairs, or the check fails. It must be fail-closed on an unreadable/absent
   ledger (an unavailable check is a failed check).
2. **R15 both ways**, with the injections above as the mutations: a `::`-suffixed sibling of a
   real pair, and a bare key naming nothing in the map. Both must red. The null control is the
   live ledger, which must stay green.
3. **The door's own `pair_count` against the map's coupling count** — the panel currently
   derives its count from the ledger it renders, so it cannot notice disagreeing with the map.
4. Only then correct the two docstrings, to what `c874a5711` said and to the control that now
   exists.

## Scope

- `tools/generate_proof_data.py::_coupled_gaps`
- `background/coupled_triad.py` (`build_coupling`, `load_gap_ledger`)
- `background/sanity_daemon.py::_coupled_gap_digest_line`
- docstrings at `background/live_payment_triad.py:748`, `tools/couple_w2_11_d5.py:11290`

No published figure moved and none was tuned (R12). Nothing was written to the live ledger.
