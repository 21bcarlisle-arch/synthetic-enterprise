**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0

# The BARE count has no floor now — 13 of 33 became 6 of 26, and the widening that could have shipped fail-open reads the operator, not the characters

Successor to `WORKER_RESULT_TWENTY_THREE_REGISTERS_NAME_THEIR_REFUSAL_AND_THE_THIRTEEN_LEFT_CANNOT_REFUSE_AT_ALL_2026-09-21.md`,
which named the defect and deliberately did not ride the fix in on `d933508ff`, because widening
moves `raw_loads`, which feeds `pairs()`, and therefore every NARROWER/PAIRED/UNSETTLED verdict.
This is that change, measured on its own.

## The work was built and never landed

`tools/conditional_registration_survey.py` and its test file were already modified in the shared
working tree, mtime `2026-09-21 22:56`, by a prior invocation holding this same claim — and in no
commit, at HEAD or at origin. Not stranded, not a rival: the same item's previous turn ended before
it landed. `ps` showed the only live `surgical_land` belonged to the settlement-ceiling item in a
different worktree. This turn measured it, proved it, and landed it.

## Measured on ONE variable, in a clean `HEAD` worktree

The working-tree JSON could not be the measurement. Its diff carried line shifts in
`simulation/net_new_acquisition.py` (1198→1294), `run_phase2b.py` (1966→1872) and
`tools/run_value_cycle_ab.py` — **other lanes' uncommitted edits to unrelated files**, which the
survey walks because it reads the whole tree. A generated artefact regenerated in a dirty shared
tree measures every writer at once. So both runs below were done in a detached `HEAD` worktree under
`~/.cache`, the only difference between them being the one tool file.

| | register classes | call sites | NARROWER | PAIRED | UNSETTLED | UNBOUND | BARE | proven |
|---|---|---|---|---|---|---|---|---|
| `HEAD` tool | 25 | 21 | 0 | 2 | 19 | 11341 | **13 of 33** | True |
| widened | 19 | 17 | 0 | 2 | 15 | 11339 | **6 of 26** | True |

**NAMED is 20 in both.** The seven that left are exactly the seven the brief named — `COTBook.void_days`,
`CustomerCommPreferenceRegister.can_contact`, `PaymentBehaviourAnalytics.get_score` and `.get_metrics`,
`PSRBook.update_needs`, `TriadNotificationBook.issue_alert`, `HedgingSchedule.add_contract` — and no
NAMED accessor moved. The widening took nothing out of the catalogue that could refuse.

**NARROWER is 0 before and after, and that is not the instrument going blind:** `--prove` still
separates the pre-repair `run_phase2b` tree from the repaired one, exit 0, on both runs. A survey
that reported zero because it could no longer see the defect we know existed would be void, not
zero, and the proof is what distinguishes those.

`UNSETTLED` fell 19→15 and `call_sites` 21→17 because six register classes left the catalogue
entirely: their only raw read was the guarded one. Those four sites were never defects — UNSETTLED
is a question list, and four questions were answered by looking at the guard.

## What the seven actually look like, and why counting them was worse than wrong

```python
def issue_alert(self, alert: TriadAlert) -> TriadAlert:
    if alert.account_id not in self._profiles:
        raise KeyError(f"Account {alert.account_id} not enrolled")
    ...self._profiles[alert.account_id]...          # <- was reported BARE
```

`issue_alert` and `add_contract` **already raise a `KeyError` naming the key and the book** — the
exact thing the refusal audit asks for. The survey was pointing the reader at two accessors that
were already right, because they name it one statement earlier than the walk looked. `update_needs`
returns `False`; the other four return `None`. None of the seven can be reached with an absent key.

## The fail-open this widening could have shipped

`if k in self._items: return` followed by `self._items[k]` contains the textual needle
`in self._items` exactly as the real guard does — and it leaves the read reachable on **precisely
the paths where it raises**. A widening matched on characters would have moved that accessor out of
the catalogue while making it the worst instance in it. `_tests_absence_from` therefore reads the
AST operator — `NotIn`, or `Not` over `In` — never the unparsed text. `or` is admitted because
absence on either side still reaches the leave; `and` is not, because absence alone does not trigger
it. And the guard body must actually leave (`return`/`raise`/`continue`/`break`): logging the miss
and carrying on is the shape that looks like a guard and is not.

## The control is mutation-proven — four mutations, each caught by its own leg

Run in-process by monkeypatch, so no mutation ever entered the shared tree.

| mutation | leg that reds | fired |
|---|---|---|
| `_membership_guarded` → `return True` | the bare read is no longer reported at all | yes |
| `_tests_absence_from` → textual `f"in self.{book}" in unparse(test)` | the presence-test-that-leaves is called guarded | yes |
| `_always_leaves` conjunct dropped | the fall-through body is called a guard | yes |
| admit `ast.And` beside `ast.Or` | absence-under-`and` is called a guard | yes |

The second is the one that matters, and it was checked for the flattering reading: under that
mutation the **real** absence guard is still correctly unreported, so the leg fired on polarity and
not on some other mechanism catching it by accident.

The partition control is one assertion pair over the same book read twice — once behind the guard,
once bare — per CLAUDE.md's rule that a guard refusing *everything* passes every leg written to ask
whether it refuses correctly.

## What is now true that was not

**BARE has no floor.** It read 13 when 6 was the true figure — inflated ~54% by unreachable code
nobody could write. A control can now key to `BARE == 0` and mean it, so the instrument can be used
to prove the class is closed. The six left are real and drivable:

`AcquisitionJourney.current_stage`, `CarbonLedger.events`, `CompetitivePressureLedger._closed_window`,
`ConsumerDutyBoardRegister.outcome_trend`, `LedgerBook.verify_against_invoicing`,
`_DoorRowWalker.handle_data`.

The refusal-catalogue leg is keyed to the **property** — an accessor that cannot be reached with an
absent key has no refusal to name, so it does not belong in the catalogue — and not to today's count
of 6, which moves with every accessor anyone writes. It also asserts the catalogue is non-empty: an
instrument reporting nothing has stopped looking, not proved the class closed.

R12: diagnostic. None of these counts is a target. Driving BARE to zero by widening the detector
again, rather than by naming refusals, would make the number better and the world worse.
