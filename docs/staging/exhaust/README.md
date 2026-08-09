# Staging exhaust — the machine's heartbeat, filed away from the record

This tree holds the sim pipeline's own lifecycle markers (`run_complete_*.md`,
`run_pending_*.md`), partitioned by the month in the marker's own stamp.

It exists because on 2026-08-09 `docs/staging/done/` held 4,962 files, of which
4,345 were these markers. The instruction record — director rulings, advisor
briefs, worker findings, `from_rich_*` messages — is the part anyone ever needs
to read, and it was buried nine-to-one under machine exhaust. The volume was
never the problem; the filing was. (Atom `AO10_exhaust_separated_from_record`,
from `ADVISOR_PROPOSAL_CAPABILITY_INDEX_AND_DEMO_2026-08-04` §4.)

## The policy

`background/staging_archive_policy.py` **is** the policy — it is mechanised, not
described here. This file only tells a human what they are looking at.

- **RECORD** stays in `docs/staging/done/`: anything a person wrote or must be
  able to find again. Never touched by the policy.
- **EXHAUST** moves here: a file must carry a marker prefix **and** read like a
  marker **and** carry no record marker in its body. Every uncertain case —
  unreadable file, unparseable name, unfamiliar body — stays in the record,
  because an instruction filed as exhaust is the harmful direction.

## Retention

**Indefinite. Nothing here is ever deleted.** Every move is recorded in the
append-only `MANIFEST.jsonl` (old path → new path → when), destination
collisions are reported rather than overwritten, and the file count is proven
equal before and after each sweep.

Growth is handled by a review trigger, not by an unattended deletion rule: a
partition over 2,000 files is named by `retention_review_due()` so a compaction
atom gets minted deliberately. As of the first sweep, `2026-07` (3,165 files)
is over that line and is queued, not swept.

## Finding things

```
python3 -m background.staging_archive_policy --find run_complete_20260618T052611Z.md
python3 -m background.staging_archive_policy --report     # counts per partition
python3 -m background.staging_archive_policy --verify      # prove nothing was lost
python3 -m background.staging_archive_policy --sweep       # dry run; add --apply
```

Code must never glob `done/run_complete_*.md`. Use
`staging_archive_policy.iter_marker_paths()` (the union view over `done/` and
this tree) or `locate(name)`. A glob that silently returns nothing turns
`background_worker`'s supersession frontier into "no run was ever published",
which would republish a stale snapshot over current figures.
