**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The maturity map is 185 bytes under its size ratchet, so the next row that explains itself in a comment turns `tests/design/` red for every lane

**Filed 2026-09-17 by the delivery seat (lane 0), while recording the two levels that
`SEAT_FINDING_THE_HOLDER_WORK_RULE_COUNTS_NAMES_...` and
`SEAT_FINDING_THE_R1_COPYS_MISSING_PARTNER_...` had frozen since 2026-09-08. Found by hitting it.**

## What happened

Recording `SITE4_ia_register_and_nav` L0→L2 and `H47_the_orientation_header_states_a_figure_it_computes`
L0→L2 meant writing two provenance comments into `docs/design/maturity_map.yaml` — the ordinary
shape, and the shape most rows in that file already use. The two comments came to roughly 1,130
bytes and put the map over `MAP_SIZE_CEILING`:

    maturity_map.yaml is 410453 bytes, over the 409600-byte spine ratchet

`tests/design/test_simplifications_store.py::test_map_within_size_ratchet_when_store_populated`
is a pre-commit gate, so that is not a note — it refuses **every lane's commit**, not just the one
that wrote the comment.

I cut both comments to the load-bearing sentence and the ratchet went green again. The measured
state now:

| | bytes |
|---|---|
| `map_store.map_text()` (both halves, which is what the ratchet measures) | 409,415 |
| `MAP_SIZE_CEILING` | 409,600 |
| **headroom** | **185** |

## Why this is a finding and not a note in a commit message

**185 bytes is under two lines of comment.** The next lane to record a level, park a row, or
explain a `blocked_on` will write more than that, and what it will see is `tests/design/` red with
a message about the simplifications register — which is not what it did and not where it is. It
will then be choosing, under time pressure and about someone else's subject, between trimming a
row it did not write and raising a ratchet. The ratchet is the right control and raising it is the
wrong move, so the pressure points at the wrong door.

That this cost me a full commit cycle to discover is the evidence: the gate fires at commit time,
after the nine cheap gates, and names a file the author did not touch.

## What I did NOT do, and why it is the next lane's call rather than mine

I did not raise `MAP_SIZE_CEILING` and I did not drain the map. Raising it is the move the control
exists to refuse. Draining it is real work with a real judgement in it — the ratchet's own docstring
says the register belongs in the store and not the map, and deciding which of ~100 rows' comments
are provenance worth keeping and which are recitation is not a thing to do in passing while
recording somebody else's level.

## The remedy, cheapest first

1. **Make the refusal reach the author before the commit gate does.** The cheap-gate list in
   `CLAUDE.md` is the pre-run set; this ratchet is not in it and takes under a second. Adding it
   costs nothing and converts a full refused cycle into a line of output.
2. **Say the headroom on the surface, not just the breach.** The assertion prints the size and the
   ceiling only when it has already failed. A row-moving tool that printed *"the map has 185 bytes
   of headroom"* while the write still succeeded is the difference between a warning and a wedge.
3. **Then drain**, as its own piece of work with its own judgement: the comments in that file are a
   mix of genuine provenance (why a row is short of its target, what a park is waiting on) and
   recitation of rules that live in `MATURITY_MAP.md`. Only the first kind earns map bytes.

## The falsifier for anyone checking this is still live

    python3 -c "from tests.design.test_simplifications_store import _map_bytes, MAP_SIZE_CEILING; \
                print(MAP_SIZE_CEILING - _map_bytes())"

If that prints a number larger than a couple of hundred, someone has drained the map and this
finding is spent. If it prints a negative number, the gate is already wedged for every lane.
