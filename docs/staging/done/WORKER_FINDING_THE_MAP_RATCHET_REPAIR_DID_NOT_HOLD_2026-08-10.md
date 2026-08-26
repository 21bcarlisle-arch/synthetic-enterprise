# WORKER FINDING — the map size ratchet is red again 24h after H32 drained it, and this time it wedges publishing

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-10, during the PW3 build (incidental — not that atom's scope).
**Disposition:** QUEUED as `H41_the_map_ratchet_has_no_ongoing_drain`. NOT fixed on sight.
**Rank:** top of the harness queue while publishing is wedged on it.

## Observed, with evidence

The sixth publish wedge (two atoms numbered H38) is fixed and pushed at `82007ad44`. The gate's
NEXT red, measured under the gate's own argv, is the map size ratchet:

```
$ python3 -m pytest tests/design/test_simplifications_store.py -x -q \
    -m "not operational and not join_report_only and not scale_report_only"
FAILED test_map_within_size_ratchet_when_store_populated
  maturity_map.yaml is 423947 bytes, over the 409600-byte spine ratchet
$ git show HEAD:docs/design/maturity_map.yaml | wc -c
423744          # red on COMMITTED HEAD, not on working-tree dirt
```

This is the same control `WORKER_FINDING_MAP_SIZE_RATCHET_RED_ON_HEAD_2026-08-09` filed and
`H32_map_size_ratchet_red_on_head` closed. H32's rehoming worked and is not in question: it took
the map 464,110 → 393,692 by moving the note class into
`docs/design/simplifications/<atom>.yaml`. **It has regrown 30,255 bytes in one day.**

That earlier finding's own line — *"Not currently blocking: the pre-commit gate does not run
`tests/design/`, so this is a red test rather than a wedged publish"* — is no longer true. The
PUBLISH gate does run `tests/design/`; the sixth wedge's blocking test was
`tests/design/test_maturity_map_contract.py`. So the same red has changed class from backlog to
blocker without anything about it changing.

## The finding: a ratchet with no ongoing drain is a one-time cleanup, not a control

H32 drained the field that was largest **at that moment**. It added nothing that keeps draining, so
the refill rate — ordinary minting — put the map back over the ceiling inside 24 hours. That is the
generalisable shape, and it is the reason this must not be closed a second time by another
one-off migration.

Where the bytes are now, measured (258 atoms, `str(value)` lengths summed by field):

| field | bytes | note |
|---|---:|---|
| `evidence` | 110,036 | path lists, ~426/atom |
| `name` | 67,689 | the mint text; only 2 atoms exceed 1KB, so this is broad, not a few offenders |
| `expert_hour` | 41,588 | ~161/atom, and the overwhelming majority is the literal default `{status: not_attempted, last: null, findings: []}` |
| `real_world_twin` | 25,258 | |
| `file_scope` | 22,117 | |
| `exit_evidence` | 20,592 | |

The overage is 14,347 bytes. The `expert_hour` default alone is worth ~35KB — but note what the
table says: no single field is an anomaly. The map is 258 atoms recording themselves honestly,
which is the behaviour the map exists for. **Any repair that pays the ceiling with the record is
refused in advance**, as H32's own atom text already ruled.

## The candidate answers, and what decides between them

1. **Stop storing defaults.** Omit `expert_hour` where it equals the not-attempted default; readers
   default on read. Mechanical, ~35KB, and it removes a value that carries no information. The one
   real hazard is a PUBLISHED figure: `tools/generate_proof_data.py:359` builds
   `Counter((a.get("expert_hour") or {}).get("status"))` and publishes
   `expert_hour_not_attempted` on the Proof door — omitted atoms would count as `None` and the
   door's number would silently change. That is R11/R14 territory and is exactly why this was not
   slipped into the PW3 tick.
2. **Rehome `evidence`/`file_scope` into the store**, as the note class was. Largest single win;
   also the widest consumer blast radius.
3. **Re-derive the ceiling from what a 258-atom map costs**, with the drain from (1) or (2) landed
   first so the number is derived from a cleaned map rather than from the pressure of a wedge.
   Raising it on its own, while wedged, is the "make the number green" move R12 forbids.

**What would decide it:** whichever option leaves a drain that runs at mint rate. A migration that
does not is this finding again in a fortnight, and the third time it should be treated as R3
(two-strike redesign) — eliminate the fixed-byte ceiling in favour of a per-atom budget the mint
path itself enforces, rather than patching the same control a third time.

## Honest note about this document

Minting `H41` into the map to record this makes the map ~1KB bigger, and this finding archives into
`staging/done/` later, which is the derived-artefact staleness trigger. Both are named rather than
avoided: the record is worth more than the byte, which is the whole argument above.
