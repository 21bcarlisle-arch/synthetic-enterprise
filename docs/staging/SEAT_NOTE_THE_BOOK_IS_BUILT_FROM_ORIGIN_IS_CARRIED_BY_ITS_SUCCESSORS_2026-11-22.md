**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

# The book-from-origin item is carried by its successors (22 Nov 2026)

Drawn tick, 22 Nov ~06:00Z, item `the-book-is-built-from-origin-and-a-waiting-book-keeps-its-place`.
Read at draw time, nothing left to build here:

- (1) The C32 hunks were landed in 8aa5aa350a. Both files are identical to origin.
- (2) sim-runner builds from its own origin worktree, landed in b1c7d76b16 with mutation-proven
  controls. Starved-book finding §2 is recorded there.
- (3) The book is in flight: pid 670302, `run_annual_report --save-json
  docs/reports/run_output_b1c7d76b16_20261122T055247Z.json`. Re-running it would launch a second copy
  over the same seeds. Checking its four records is owned by the continuation
  `confirm-the-b1c7d76b16-book-carries-its-four-records`. The stranded key-register control is owned by
  `land-the-key-register-control-stranded-on-salvage-6f87ccb38`.
- The "descends from 6f87ccb38" clause cannot be met (12fb8d29f7 has the correction).

Released through `delivery_lane --release`.

The same tick also drew the BLOCKING won-switch finding. Its only open part is reg 6C. That part is
held by the live claim `end-an-erroneous-gains-supply-under-reg-6c` (seat-executor,
/var/tmp/se-seat-executor, its test was running at draw time), so this tick did not build it.
