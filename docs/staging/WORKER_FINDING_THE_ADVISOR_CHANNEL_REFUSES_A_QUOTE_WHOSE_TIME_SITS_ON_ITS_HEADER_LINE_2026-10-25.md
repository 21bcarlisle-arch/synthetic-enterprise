**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The advisor channel refuses a file that quotes the director, because the time sits on the header line and not on each quote

**What.** Today's draw refused `docs/staging/advisor/DIRECTOR_STEER_COMFORT_HEALTH_AND_CARBON_ARE_OUTPUTS_AND_BUDGET_FIRST_ADVICE_IS_PARKED_2026-10-25.md`
as "no attribution". It does quote him: "The director's words, from chat on Sun 25 Oct, 06:30 GMT:"
and then four quoted bullets. `background/advisor_channel.py::_QUOTED_CHAT_RE` needs a time and a
quoted span on ONE line (`- 09:49 BST: "..."`), so a time on the header line with the quotes
underneath reads as no quote at all.

**What was done.** Nothing to the file. It was NOT moved to `done/` as the draw asked, because that
would bury his words under a refusal that is wrong. It stays in `docs/staging/advisor/` for a seat to
act on as a quoted steer.

**Proposed fix (not made in this turn: it is a control on his voice and wants its own mutation).**
Accept a time line ending in `:` followed by quoted bullet lines, and add a test with this file's
shape that goes red against today's regex. Provenance (the signed advisor commit) is unchanged and
still guards authenticity.

**Also, the duplicate draw.** `the-map-owed-pages-and-forward-plan` and
`map-steer-knowledge-pages-and-forward-plan` are the same steer. The first id's 07:03 invocation died
on an API error (EAI_AGAIN) and landed nothing; this turn took the work under the second id and
landed the switching page under it. The first id is released.
