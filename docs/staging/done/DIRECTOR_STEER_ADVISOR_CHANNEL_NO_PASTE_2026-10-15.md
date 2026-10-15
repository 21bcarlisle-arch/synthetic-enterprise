**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] I can't paste: my advisor's staged steers carry my word (2026-10-15)

**The director's words, to his advisor, 15 Oct:**
- 09:49 BST: "Is there a way to create a separate staging channel for comments and instructions. So I don't have to paste? So you can do it. Give now and next instructions and guidance directly?"
- 14:00 BST: "I can't paste, that's the whole issue!"

His console link dropped at about 09:45 and he cannot reach the pane. Severity is BLOCKING because the director's steering path is down.

**Evidence the path is broken:** `DIRECTOR_STEER_STRETCH_LOG_AND_DECK_2026-10-15.md`, staged at 09:50, was still undrawn in the staging root at 14:00, while worker turns spent the day on world texture work.

## WORK THIS CREATES (canonical, in-document)

1. **Now, ahead of everything, finishing only the piece in hand:** act on `DIRECTOR_STEER_STRETCH_LOG_AND_DECK_2026-10-15.md`. Then send an NTFY naming both files, so he knows the channel works.

2. **The advisor channel.** Build it as the smallest mechanism. It is a canon G8 amendment, in his words above.
   - The folder is `docs/staging/advisor/`. A file there with the staging header, attributed "on the director's standing delegation of 15 Oct" or quoting his chat words with the time, is treated as his paste.
   - It is drawn at rung zero by the next turn of any lane: worker tick, executor or seat. That lane finishes the piece in hand first and never stops mid-landing.
   - On reading, the machine sends an NTFY acknowledgement naming the file. When the file is actioned, it moves to done with what was done.
   - The staging watcher's arrival NTFY for that folder is what wakes the lanes.
   - Test that an advisor file is drawn first, and that one without a valid attribution is refused with its reason.
   - **What the delegation covers:** pacing and his usage readings, sequencing and focus, clear-down steering, factual corrections, chasing owed items, and relaying answers he has given in chat.
   - **What it does not cover:** the mission, canon intent, curriculum values, reserved actions, or a decision that is his. For those, the file must quote his explicit words; otherwise treat it as a proposal and raise it to him.
   - Record the amendment in `DIRECTOR_CANON.md` G8, marked as his words.

3. **The interactive seat.** If the console session has exited, its handoff and any work it held are the executor's to land. Say on NTFY whether the console session is up, so he knows whether to sign in again.

4. **The rest of the week.** The 09:50 steer's list stands: the machine-class known issues, the 145 banners, staging fates, then C34 and EP17 minted for Monday under his 06:50 words. World texture work (W1_29, L2.4, storage charging) is not clear-down. Land what is in hand, then park the rest as atoms for next week. The last usage reading was 71% at 06:45. Keep the 6-point reserve.

Keep going between pieces.

## Progress (worker tick, 2026-10-15 ~15:40 BST)

- **Item 2, the channel: built.** `background/advisor_channel.py` reads `docs/staging/advisor/` (top
  level only; `done/` is the archive). A file is drawn when it has the staging header and quotes his
  chat words with a time, or says it acts "on the director's standing delegation of 15 Oct". Any
  other file is refused with its reason and never drawn. The rung-zero text goes first in all three
  lanes' prompts: `worker_tick.compose_prompt`, `seat_executor.build_prompt`, and
  `delivery_seat._prompt`. It carries the delegation's limits and the move-to-`done/` rule. The
  acknowledgement is one NTFY per file, keyed on the file. The staging watcher sends it on arrival
  (its scan reads only the root, so the folder is checked separately), and a lane's draw sends it
  if the watcher has not. Tests: `tests/background/test_advisor_channel.py`. It covers drawn
  first in each lane, refused with its reason, both verdicts reachable in one folder, and one ack
  per file. A mutation that drops the executor's prefix reds it. The G8 amendment is in
  `DIRECTOR_CANON.md` in his words.
- **Still open:** item 1's NTFY naming both files, item 3 (whether the console session is up), and
  item 4 (the rest of the week). The mothball steer follows this one.

## Done (2026-10-15, console seat)

1. **The 09:50 steer** was actioned (`ec1e50480`, in done/). The NTFY naming both files went at 15:21 UTC.
2. **The channel** is `4a581cd72`, plus provenance in `7bc3e3d3a`: a file is drawn only if origin holds its exact bytes in a commit signed by the advisor's key. A second build of the channel by the console seat, made without a claim, was not landed and is on tag `wip/advisor-channel-2026-10-15`.
3. **The interactive seat** is up: tmux `claude`, since 09:53 BST. The same 15:21 NTFY said so. The dropped console's held work landed: the parked-atom fix as `47e544e24`. Its land-twice control is superseded in part by `ed7e89d12`, and the remainder is handed off.
4. **The rest of the week:**
   - Done: the banners (`3a692ad58`), staging fates (`2f17ba79f`), C34 and EP17 minted on his 05:52Z words, and the parked-atom fix.
   - Now running live: the hold re-ask and tombstone fixes, since the shared checkout fast-forwarded past its 56 blockers.
   - Still open: the draw ledger crediting by path, carried in DIRECTION's `wrong` list.
   - Parked for next week by another lane: W1_29.
   - The mothball steer that followed is done too (`565bd6303`).
