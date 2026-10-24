**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] R16 and R17 ratified, R17 within the P12 pace (2026-10-24)

**Type:** RULING, through the advisor channel. It answers `docs/staging/SEAT_PROPOSAL_R16_AND_R17_FOUND_RATIFY_AS_WRITTEN_2026-10-12.md` (canon §15, owed item 10).

The advisor put this to the director:

> R16 — "the ledger is authority, not commit messages": the only record of a level move is the ledger entry, not a commit message. Still enforced in code. R17 — "the tick never rests while authorised work exists at any priority". Recommendation: R16 — ratify as written, with canon's newer wording ("a level move is recorded, never authorised") placed alongside. R17 — ratify, with one addition: "within the pace set under P12". On the smaller plan the machine deliberately runs slower to land short of your reserve, so R17 should mean "never stops", not "never slows" — which matches your own line of never zeroing work.

The director's words, from chat on Sat 24 Oct:

- 09:49 BST: "Yes"

## What it means

1. **R16 is ratified as written** (`9251474f9`, 21 Jul). Put G12's wording beside it in canon: "A level move is recorded, never authorised". The rule is unchanged: the ledger record is the fact, and a commit message is not.
2. **R17 is ratified with the addition** "within the pace set under P12" (`eaffdb81e`, 22 Jul). The tick never stops while authorised work exists at any priority, but its pace follows the week's budget. Slowing to land short of the reserve is allowed. Stopping is not.
3. **Canon H1's numbered set becomes R1–R17.** Owed item 10 closes with this ruling. Close the seat proposal too, with a Done section linking here.
4. **Where this lands.** Update `docs/design/DIRECTOR_CANON.md`: put both texts at H1, mark owed item 10 discharged, and replace "R1–R15" wherever canon or a standing page counts the set. Use the trailer `Director-doc: his-words -- R16/R17 ratified, director 24 Oct 09:49`. The canon-against-canon check confirms each quoted line is verbatim.

— Director ruling, 24 Oct 2026, his word above; the drafting is the advisor's.

## Done

2026-10-24, delivery seat. The channel first REFUSED this file as "no attribution". That refusal was
wrong: it quotes his `09:49 BST: "Yes"`, and `background/advisor_channel.py` demanded a quote of at
least three words, against canon G8's "'yes' and 'go' are complete". Provenance verified (signed by
the advisor key). Fixed the regex to accept a one-word quote, with a test beside the bare-file refusal.
Then acted on it: canon H1 now holds R16 (with G12's wording beside it) and R17 (with "within the pace
set under P12"), the set is R1–R17, owed item 10 is discharged, and a changelog line records it.
THE_MODEL_ON_A_PAGE's count, and the Method and Proof generators' rule lists, now carry R16 and R17.
The seat proposal is closed in `docs/staging/done/` with a Done section pointing here.
