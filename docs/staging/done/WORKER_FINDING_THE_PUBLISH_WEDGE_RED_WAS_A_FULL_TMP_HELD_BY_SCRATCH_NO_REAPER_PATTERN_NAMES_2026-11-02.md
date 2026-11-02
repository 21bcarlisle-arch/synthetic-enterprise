**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The publish wedge's last red was a full /tmp, not a test: 8 GB of week-old probe scratch under names no reaper pattern matches (2026-11-02)

**What the doorbell said.** The publish gate had been failing for about 806 minutes. Its last refusal named
`tests/background/test_derived_artefact_register.py::TestSeatGuard::test_the_entrypoint_is_seat_guarded` as an
ERROR in a checkout of 204c76f9f.

**What it was (measured).** Rerun at f73ed3e7a4, the same file errored in a fixture with
`OSError: [Errno 28] No space left on device` while copying into `/tmp/pytest-of-rich/...`. `/tmp` is a 12 GB tmpfs
(RAM on this box) and stood at 100%, 8 KB free. `python3 -m background.disk_headroom --reap --dry-run` reported
"would free 0 MB from 0 expired scratch dir(s)". The space was held by about 3,800 top-level entries older than 72
hours (`b13probe` 766 MB, `b13` 551 MB, `p4c_probe` 426 MB, `regid`, `inv`, `wcr_arms`, several `published-site-*`
copies, `occ_ledger_*.json`), none of them matching a `SCRATCH_PATTERNS` entry. The reaper's identification is
positive only, by design, so a probe written under an ad-hoc name is never reaped.

**What was done.** A scan of `/proc/*/cwd`, `/proc/*/fd` and command lines found no live process holding any of
them. Every top-level `/tmp` entry owned by this user and older than 72 hours, except `claude-1000`,
`capland2.log` and `pytest-of-rich`, was removed: 3,834 entries, 8,096 MB. `/tmp` went to 33%. The list of names is at
`~/.cache/.tmp_scratch_cleared_2026-11-02.txt`. The contents cannot be recovered; they were scratch on a RAM disk that a
reboot would also have cleared. After the cleanup the named file passed (13 passed).

**Scoped gate at HEAD after the cleanup.** Run without `-x` in a clean detached checkout of 08f267b666 (`_scoped_gate_argv`, 337 test files): 0 failures and 0 errors at 14% when this was filed; the log is `/var/tmp/gatechk.log`. That is not a green. The publisher's next attempt is the gate of record, and the wedge stays open until it passes.

**What this does not fix.** The class (its second instance; the first is `WORKER_FINDING_THE_REFUSAL_NAMED_THE_WALL_CROSSING_REGISTER_AND_THE_CAUSE_WAS_A_FULL_TMPFS_2026-09-05.md`): the lanes write probes to `/tmp` under free names and nothing ages them out.
Two candidate remedies, not chosen here: probes write under one declared prefix that the reaper owns, or the reaper
also ages out unpatterned entries that no live process holds, past a long TTL. The second weakens the positive-only
property the module was built on, so it is a design choice for whoever holds `background/disk_headroom.py`. That file
also carries an uncommitted edit in the shared tree (the `pytest-of-*/pytest-[0-9]*` grain and the `*-current`
guard, dated 2026-09-06 in its own comments) that has never landed. That edit is not this worker's, and it was left as found.
