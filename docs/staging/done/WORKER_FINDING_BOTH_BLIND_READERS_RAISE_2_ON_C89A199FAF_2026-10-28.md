**Severity:** MAJOR · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Both blind readers raise 2 finding(s) on c89a199faf (2026-10-28)

*Written by `background/two_reader_review.py`, the automatic lane of the two-reader trial
(director ruling 28 Oct, review 2026-11-11). Nothing here has been checked. Check each pair at
HEAD like any other finding, and record the outcome for the review. Severity is capped at
MAJOR until a check confirms more.*

- **Commit:** `c89a199faf998e228a9403c4ec12d739d38edb50`, committed 2026-10-28T10:57:03Z.
- **Modules it added:** `background/two_reader_review.py`.
- **Verdicts:** A NEEDS_WORK, B NEEDS_WORK (trust ledger,
  `reading-review-live-2026-10-28:c89a199faf:arm{A,B}`).

## Raised by both (pairs from the tool-less matcher; undo any that do not name one defect)

1. **A#1 (MAJOR) `background/two_reader_review.py:432`** A matcher that exits 0 with no parseable json block gives last_json_block -> None -> valid_pairs -> []. Both verdicts are recorded and the outcome is 'read', so the commit leaves the queue for good with nothing filed and no retry. A failed vote can't be told apart from 'no shared finding'. Input: both readers raise a finding and the matcher replies 'They look similar.' with rc 0.
   **B#1 (MAJOR) `background/two_reader_review.py:508`** A matcher that exits 0 with no parseable JSON (prose, or {"pair": ...}) gives last_json_block -> None -> valid_pairs -> [], and the run is logged outcome='read' with both verdicts recorded and nothing filed. The commit then counts as read and is never retried, so a real shared finding is silently dropped. Only rc!=0 is treated as matcher_failed. The test fixture always supplies a valid matcher block, so this edge is never reached.
2. **A#2 (MAJOR) `background/two_reader_review.py:436`** Exceptions from _extract (git archive/tar failure, disk full), from record(), or from filed.write_text skip _append, so no attempt is logged and MAX_ATTEMPTS can never give up on the commit; the timer retries every 30 min indefinitely. If record() raises on arm B after arm A was written, each retry spends two more Opus readers and appends a duplicate arm-A verdict to the trust ledger. If write_text raises after both verdicts are recorded, the finding is lost for good because read_shas already counts the commit as read.
   **B#2 (MAJOR) `background/two_reader_review.py:487`** read_commit only calls _append on its three handled outcomes. An exception from _extract (tar check=True, or the git archive RuntimeError), from record() (TaskClass/Verdict/evaluator whitelist ValueError), or from filed.write_text escapes through try/finally with no attempt logged. So _attempts never reaches MAX_ATTEMPTS, the commit stays waiting[0], and it is retried every 30 min forever. Each retry re-spends both Opus readers when the failure comes after them, and re-records arm A when only arm B's record raises. This contradicts the message's 'given up on after 3 attempts with the reason kept'.

## Raised by one reader only (not filed under the vote)

- A#3 (MAJOR): product-only admits two-reader-review at cadence 0 with no product filter. Every other route filters through item_allowed/item_is_product under that mode ('under a mode the director set to stop machinery, the unknown is the side that waits'). Input: mode product-only and a waiting commit adding background/foo.py -> gate(ROUTE) returns True and two Opus readers start on harness work. The commit message lists only off and fold-only as holding the route and gives no reason for admitting it under product-only.
- A#4 (MINOR): reader_prompt puts the full phase-close-evaluator brief first. That brief requires git log/diff, a reply that starts with a bare PASS/NEEDS_WORK, and a REQUIRED 'python3 -m background.judge_validation record-close' step. A reader limited to Read/Grep/Glob can do none of these, so the instructions conflict and readers may spend turns trying.
- A#5 (MINOR): Every lane test uses a matcher returning valid JSON with rc 0. Nothing reaches the matcher_failed branch, a matcher with broken output, or an exception from _extract/record, so findings 1 and 2 pass every test.
- B#3 (MINOR): An unrecognised severity string (e.g. 'CRITICAL', 'HIGH') is silently mapped to MINOR, which understates _filed_severity and the ledger notes without any flag.
- B#4 (MINOR): Persistent=true only affects OnCalendar= timers. With OnBootSec/OnUnitActiveSec it is a no-op, so the unit suggests a catch-up behaviour it does not have.
- B#5 (MINOR): The claim that a `claude -p --restricted --tools Read Grep Glob` reader is refused paths outside the scratch dir and has no write or shell tool ('measured before this was written') has no evidence artefact in the commit: no transcript, log or test. The lane's safety depends on it, so it is unverified.

## Done

*Autonomous worker, 2026-10-28, the turn that built the lane. This is the lane's first live
reading: the timer fired on arming and read the lane's own landing commit.*

- **Pair 1, CONFIRMED and fixed.** A matcher reply with no `{"pairs": [...]}` block is now
  `matcher_failed`, logged as an attempt and retried. It is no longer read as "no pairs". Held by
  `test_a_matcher_that_answers_in_prose_is_a_failed_match_not_no_pairs`, which goes red when the
  check is mutated away.
- **Pair 2, CONFIRMED and fixed.** `read_commit` now logs any exception as an `error` attempt, so
  `MAX_ATTEMPTS` can give up. Held by `test_an_exception_mid_reading_is_logged_as_an_attempt`, also
  mutation-checked. Residual: if `record()` raises on arm B after arm A was written, a retry
  records arm A again. Both arms go through the same enum and whitelist checks, so only an I/O
  failure can split them.
- **One reader only, actioned anyway:** A#4, because the brief's git and record-close steps
  conflict with read-only tools, so the prompt now says to skip them. B#4, because `Persistent=true`
  was a no-op on this timer, so it is removed. A#5 is spent by the two tests above.
- **One reader only, left open:** A#3. Under `product-only` the route still spawns. The trial is
  the director's ruled work, so I did not hold it under a machinery-stop mode on my own call. It is
  for the seat to decide whether `product-only` should hold it. B#5: the probe evidence is in
  the commit message of the follow-up. A haiku session with these flags read a file inside its
  scratch dir. It was refused `/home/rich/synthetic-enterprise/CLAUDE.md` ("outside the working
  directory") and reported no write tool and no shell tool, and no file was written. B#3 (an
  unknown severity maps to MINOR) is kept as a known understatement.
- **Score for the 11 Nov review:** 2 filed by the vote, 2 confirmed, 0 refuted. The trial total is
  now 7 filed, 6 confirmed, 1 partly spent.
