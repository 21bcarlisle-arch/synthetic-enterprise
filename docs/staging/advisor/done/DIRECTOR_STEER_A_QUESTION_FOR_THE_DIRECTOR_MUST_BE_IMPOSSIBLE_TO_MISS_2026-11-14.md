**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] A question for the director must be impossible for the advisor to miss

**Type:** STEER, through the advisor channel. The director's words, from chat, Sat 14 Nov:

- 05:54 GMT: "Are you sure nothing is waiting"
- 05:59 GMT: "Why did you miss this decsion for me? How do we fix that ?"

## What happened

- At 05:53 the advisor told him "Nothing is waiting on you". The `for_the_director` row `the-off-box-dead-man-misses-stops` had been open since the evening of 13 Nov.
- The cause was on the advisor's side. Its last full read of `for_the_director` was Fri 18:51, before the row was raised. At 05:53 it scanned commit titles and did not re-read the rows.
- No commit title said a question had been raised for him. The 22:14 title reads "The off-box dead-man's twice-hourly cron bought no extra delivery...", which is a finding, and nothing in it marks that it asks the director.
- A second cause: the question was one the advisor could answer. The advisor's cloud stall check was not recorded anywhere the machine reads (now fixed by today's ruling).

## The fix: two legs, one on each side

1. **The advisor's side (the advisor owns it).** It does not tell the director what is or is not waiting without reading `DIRECTION.yaml`'s `for_the_director` from origin **in the same turn**. A scan of commits is not a substitute. This is now the advisor's standing practice.
2. **The machine's side.** Make a raised question visible in the commit stream itself:
   - Any commit that adds or reopens a `for_the_director` row carries **`[FOR-THE-DIRECTOR]`** at the start of its title, with the row id.
   - Any commit that closes one says so in its title.
   - Make this mechanical: refuse, in the commit-msg gate, a commit whose diff adds an open row without the marker. A rule kept by memory is the shape the learning loop warns against.

   Keep it to that one leg. No new register and no new alarm.
3. **Before raising a question, check whether the advisor already covers it.** Read the control stack, which now lists the advisor-run cloud check. If an advisor-run control could answer the question, put it to the advisor in a staged note first. A question to the director is for what only he can decide.
4. **Learning loop entry.** File this as a ways-of-working insight: a "nothing is waiting" claim made on a stale read. It is one worked case, and its measure is director questions missed by the advisor, which should be zero.

## Done

14 Nov, worker tick.

- **Leg 1 (the advisor's side)** belongs to the advisor and is recorded in W3, below.
- **Leg 2 (the machine's side)** is one leg in the existing commit-msg gate, `tools/director_document_gate.py`. A commit whose index opens or reopens a `for_the_director` row is refused unless its title starts with `[FOR-THE-DIRECTOR]` and names each id. The rule lives in `background/director_concerns.title_refusal`. The seat's direction commit builds its own marked title (`marked_title` in `delivery_seat.commit_direction`), so the writer that raises most rows is never refused. A close is not gated: this commit's title says it closes its row, as the steer asks. Controls: `tests/tools/test_director_document_gate.py` covers raise, reopen, marker without the id, and close through the gate run as a script. A mutation that never refuses turns both new tests red. No new register and no new alarm.
- **Leg 3:** `docs/operations/MAINTENANCE.md` now lists the advisor's cloud check. W3 makes checking advisor-run controls the step before raising.
- **Leg 4:** the learning-loop entry is W3 in `docs/institutional/ways_of_working.md`. Its measure is director questions missed by the advisor, predicted at zero by 14 Dec.
