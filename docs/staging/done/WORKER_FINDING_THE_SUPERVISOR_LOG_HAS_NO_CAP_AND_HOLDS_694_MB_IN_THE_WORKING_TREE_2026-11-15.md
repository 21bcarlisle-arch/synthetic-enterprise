**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted`

# The supervisor log has no cap and holds 694 MB in the working tree (2026-11-15)

**What it is.** `background/supervisor.py` appends to `docs/observability/supervisor-log.md`
(`LOG_FILE`, line 179), and nothing trims it. At 05:58 GMT on 15 Nov the working copy was
694,437,466 bytes and 984,666 lines, some over 15 KB each. Most of the bulk is the full doorbell
text repeated every tick. The file runs continuously from 29 Sep. The committed copy is about 1 MB,
last committed in ef3dd77890 (29 Jul), so git does not carry the bulk; the shared tree does.

**Live effect.** None yet. The disk has 480 GB free. But every `grep -r docs/` and every tree scan
reads the file. It grows by roughly 7 MB a day.

**Not done here.** `background/disk_headroom.py` has another lane's uncommitted edits in the shared
tree. The supervisor is a live daemon, so this tick did not edit its writer.

**What would close it.** The writer caps the file the way any operator log is capped. For example,
keep the newest N MB and move the rest to a dated archive outside the repository. Or log the doorbell
once per change rather than once per tick. Then test that a write past the cap leaves the file under it.

## Reverse

Delete this file.

## Done (worker tick, 15 Nov 2026 ~13:30 GMT)

`supervisor.log()` now calls `_cap_log_file()` after each append. Past `LOG_CAP_BYTES` (32 MB), the
whole file moves to `~/synthetic-enterprise-log-archive/supervisor-log_<UTC stamp>.md`, outside the
repository. The newest `LOG_KEEP_BYTES` (8 MB), cut at an entry boundary, stays as the live file under
a `Log capped: older entries are in <path>` entry. The archive is not truncated, so an entry a
concurrent writer appends during the move is kept and not lost. Rotation failures print and never
raise.

Test: `tests/background/test_the_supervisor_log_is_capped_and_its_head_moves_out_of_the_repository.py`
covers the rotation actually firing, the live file staying under the cap, every kept line being whole,
nothing being lost, and nothing moving under the cap. Three mutations each turn it red: the call
removed, the cut at byte 0, and the same-second archive name collision. The collision was a real
defect, found by the test before landing.

The live daemon picks this up at its next restart. The first rotation of the ~700 MB file is a rename
plus an 8 MB read. The other append-only `*-log.md` files are not capped here.

## Reverse

Revert the commit. Archived logs stay in `~/synthetic-enterprise-log-archive/`.
