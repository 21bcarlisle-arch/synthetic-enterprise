**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — clear the freezers on `H47_the_orientation_header_states_a_figure_it_computes` and `SITE4_ia_register_and_nav`)

# Three of the five freezers are discharged with repairs; the other two are one rule, and I hit a live instance of it by accident while citing a falsifier

**2026-09-17, scheduled tick, worker seat, working the drawn Lane 0 item "clear the six findings
`level_zero_contradicted_by_its_own_controls` prints under FROZEN BY".**

## Correction to the drawn item, first: it is FIVE, not six

The item names six and says to start with `WORKER_FINDING_THE_LIVENESS_REACHABILITY_LEG_...`. The
grader prints **five**, byte-identical for both frozen rows, and the liveness finding is not among
them — another lane discharged it in the stretch between the item being written and drawn. The item
was right about the class and one row stale. Nothing was done about the liveness finding here.

## What is discharged, with the repair in each case

| finding | what was built | falsifiers |
|---|---|---|
| `WORKER_FINDING_THE_LAUNCH_REGISTERS_LOADER_READS_FIVE_PRIORS_...` | `load_register` (the `episode_prior` partition, `item_type=dict`); `record` preserves before it rebuilds and the row says so; `check` raises `RegisterUnreadable` instead of returning the clean board; the deadman PAGES on its own standing-condition key | `test_an_unreadable_launch_register_is_never_an_empty_board.py` — 15 legs, 5 mutations fired |
| `SEAT_FINDING_THE_STALE_COPY_CENSUS_CRASHES_IN_THE_SHARED_TREE_...` | `door_verdicts` degrades on `ImportError` and says so above the rows, carrying this finding's own detached-worktree workaround | 2 legs in `test_stale_copy_refusal.py`, 3 mutations fired |
| `SEAT_FINDING_THE_LIVE_RECORD_RESOLVER_WAS_NOT_EVEN_WIRED_...` | its one UNDECIDED row (`.launch_records.json`) is decided; the both-sides-agree control it lacked is landed | HEAD's six legs + `test_BOTH_sides_of_the_register_route_through_the_resolver_and_agree` |

**The launch-register repair is the one that mattered most and it was not the one the drawn item
called cheapest.** `record` is load → supersede → append → save, and on an unreadable prior the load
half returned `[]`, so the save half wrote a one-element register over whatever was there. A
destroyed `live` record is a claim that can never be contradicted, which is the single thing
`launch_liveness` exists to abolish — arriving through its own writer, for the second time.

## The two that are NOT discharged, and why that changed during the turn

`SEAT_FINDING_THE_HOLDER_WORK_RULE_COUNTS_NAMES_...` and
`SEAT_FINDING_THE_R1_COPYS_MISSING_PARTNER_...` are one defect: the discriminator that routes a
rival working copy is a NAME COUNT, and a name count cannot tell holder work from a renamed draft of
something HEAD already carries.

**I checked the five copies those findings name. All five are gone — same as HEAD, every one. I
concluded the rule had no live instance and was about to say so.** That conclusion was wrong within
the hour, and the refutation arrived sideways: the discharge parser refused my citation of
`tests/background/test_a_live_record_read_from_a_linked_worktree_reads_the_shared_tree.py`, saying
HEAD does not define two of the nodes a `grep` of the working tree had just shown me.

Measured:

| question | answer |
|---|---|
| working copy vs HEAD | 80 added, 185 deleted |
| distinctive lines of `e9ad946cd` the copy contains | **0 of 108** — `predates_landing` |
| disk mtime vs the commit that landed the file | **10:54 vs 12:42** — the copy is OLDER than the landing |
| legs in the working copy / in HEAD | 9 / 10, and they are differently NAMED |
| census verdict | `HOLDER WORK`, routed to `surgical_land --content` |
| `refresh_to_head` verdict | `[refused_supplies_names_head_lacks]` — 4 names |

So both doors refuse in the same direction on the same input, which is the sentence
`SEAT_FINDING_THE_R1_COPYS_MISSING_PARTNER_...` ends on, reproduced verbatim on a file neither
finding ever mentions. Landing this copy whole would delete HEAD's five per-reader legs — named for
what each reader SEES (`..._sees_the_live_failures_not_the_committed_placeholder`) — and re-add four
drafts named for the mechanism (`..._routes_through_the_resolver`). The property version for the
mechanism version, with every gate downstream green.

**What this corrects is not the findings but my reading of them.** The instances rotate; the class
does not. `SEAT_FINDING_THE_R1_COPYS_MISSING_PARTNER_...` predicted exactly this and I read past it:
*"`surgical_land` converts a Kind-B copy into a Kind-A one at the moment it succeeds. Every landing
this class performs leaves a new member of the class behind it. The population is refilled by its
own cure."* An empty instance list is therefore never evidence the rule is safe to leave, and
"are the named copies still there" is the wrong question to ask of this class.

**The one genuinely mixed part, which is why the third door is not optional.** One of the four names
the copy supplies, `test_the_launch_record_reader_routes_through_the_resolver`, controls a wiring
that IS at HEAD and had no landed control at all. The copy is not purely a replacement: it is
holder work and a revert in one indivisible edit, which is `isolate_hunks`' documented limit
(a replacement is one hunk) and not its fault. I did not route around it — the property that row
needed is landed in a file no other lane holds, asserted as AGREEMENT between the two sides rather
than as two routings, with each side mutation-proven to fail alone.

## What is owed, stated as work and not as a shrug

1. **The discriminator, which both findings converge on and neither builds.** Finding 1's clause is
   hunk-level (`symbols_added(H) - HEAD_symbols` non-empty AND `symbols_deleted(H) & HEAD_symbols`
   empty); finding 3's is runnable (a supplied name is dead when executing it raises `AttributeError`
   for a symbol no committed tree defines). They are not rivals — the first grades the EDIT and the
   second grades the NAME, and the live instance above needs the first, because its supplied names
   all resolve fine.
2. **The stale copy is still on the shared tree** and is a silent revert of `e9ad946cd` for anyone
   who names it in a pathspec. Not touched here: it is another lane's file, both doors refuse it,
   and forcing either one is how this class gets worse.
3. Item (3) of the census finding — whether anything else the seven commits added is being counted
   as "does not exist" rather than "has not arrived" — is carried, not counted as discharged.

**The two frozen rows do NOT clear this turn.** Three of five is three of five, and a row that says
"nothing built" while two BLOCKING findings stand is the grader working. The next turn starts from
the clause above rather than from the grading, which is the whole point of writing this down.
