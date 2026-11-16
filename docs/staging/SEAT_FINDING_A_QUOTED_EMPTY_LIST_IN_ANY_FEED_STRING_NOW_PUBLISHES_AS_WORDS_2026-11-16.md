**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A quoted empty list in any delivery-feed string now publishes as words, not only in problem text (2026-11-16)

*Delivery seat executor, drawn on `the-direction-record-and-every-site-commit-survive-a-quoted-empty-bracket`.*

## Premise, re-measured at draw

- **Direction record by its own tick:** already happened. 0cf9406744 ("delivery seat: direction for
  the next stretch") landed on origin at 06:57Z 16 Nov.
- **The 15 Nov steer to advisor/done:** already happened. a28a5fc572 moved it at 06:56Z.
- **Why the 06:57 record got past the sweep:** 8503daa89's subject quotes `"reads []"` and says
  "a bare [] is now". The Harness page draws only the newest 12 of the feed's 40 commits
  (`site/harness/index.html`, `.slice(0, 12)`). By 06:57 that subject had dropped past the 12th
  (it is now 26th), so nothing changed. The instance cleared itself as newer commits pushed it down.

## The cause, fixed

`reader_text` ran only on `what_it_got_wrong.problems[].what`. Commit subjects, and every other
string the seat's record puts on the feed, reached the page raw. So the next subject that mentions
`[]` would have refused every site commit again until 12 more commits had landed.
`tools/generate_delivery_page.build` now passes the whole feed through `reader_feed`, which calls
`reader_text` on every string. It walks the feed rather than naming fields, so a new prose field is
covered from its first day. `( )` and `[ ]` are still left alone, because those are what a real
hole leaves.

**Control:** `tests/tools/test_the_seats_prose_reaches_the_harness_page_without_an_empty_field.py::test_every_string_the_feed_publishes_reaches_the_reader_without_an_empty_field`
puts 8503's real subject and two real holes into every section, goes through `build`, and checks
both legs: the quoted `[]` shows no empty field, and both holes still fire the sweep's own shapes.
Three mutations were run, and each one turned the tests red:
- removing `reader_feed` from `build`: 1 failed.
- rewriting `( )` and `[ ]` too: 2 failed.
- not walking into lists: 2 failed.

## Not done: the alarm document, deliberately

`WORKER_FINDING_REPEATING_ALARM_DELIVERY_SEAT_THE_DIRECTION_RECORD_DID_NOT_REACH_ORIGIN_SO_2026-11-08.md`
has been answered: a seat tick landed its own record (0cf9406744). But the shared tree carries 12+/6-
lines of uncommitted annotation on that file (checked 16 Nov). Moving it on origin would make git
refuse the shared tree's fast-forward, which is exactly what 759fac9831 had to undo. Whoever owns
those annotations (the alarm re-asker) should commit them or let them go first. Then the move is
one `git mv` to `done/`, and its resolution is 0cf9406744.

delivery.json is not regenerated here. The seat's next tick does that from the shared tree's code
once this commit is there.
