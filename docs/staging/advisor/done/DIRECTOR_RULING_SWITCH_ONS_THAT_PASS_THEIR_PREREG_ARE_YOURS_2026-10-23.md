**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

**Knowledge:** none -- a governance ruling on who switches defaults on; it states no domain understanding a Knowledge page would carry

# [DIRECTOR-RULING] The annualised advance goes on by default, and a switch-on that passes its own pre-registered rule is the machine's call (2026-10-23)

**Type:** RULING, through the advisor channel. It answers the `for_the_director` row raised by `7e31d8f7`, the annualised-advance default-on. It also sets a standing rule. The advisor put this to the director:

> One item is waiting for you: switching that better bill estimate on by default. My recommendation is yes, since it passed the rule it set before testing. It's also arguably not your call at all, because it's an ordinary billing setting that doesn't change a ruling. If you agree, I'll tell the machine to approve it and to switch things like this on itself in future when they pass their pre-set rule.

The director's words, from chat on Fri 23 Oct:

- 07:03 BST: "Great. All good. Do these."

## What it means

1. **The annualised advance goes on by default now.** The bill estimate reads it (`30674a4bd`), on the grade at `7e31d8f7`:
   - the decision rule fixed before the arms ran was met;
   - estimate error was lower in 9 of 9 years;
   - catch-ups fell 22%;
   - catch-ups of £500 or more fell from 30 to 24.

   Close the row with this ruling. Carry the corrected section-1 projection with the switch.
2. **Standing rule: a switch whose pre-registered rule is met is yours to turn on.** This covers a default-off switch on supplier policy or world behaviour, where the rule was fixed before the arms ran and the grade meets it. You switch it on yourself, and you do not raise it for the director, provided that:
   - it changes no ruling, curriculum value or reserved action (G5, G9, P11, C14);
   - it does not change the world after supplier results were seen, unless new evidence requires it (W7 principle 2);
   - the grade, the rule and the switch-on are on one record, with a control that reds if the default reverts.

   Report each switch-on in the stretch log. Anything outside these conditions still comes to him, with a recommendation (G9, as amended 19 Oct).
3. **The reverse holds too.** A switch whose rule is refuted stays off, on the same record, with the reason. A rule may not be rewritten after its arms are read. A new rule is a new pre-registration.
4. **Where this lands.** Add one line to canon G9 recording the rule, quoting his words. Point the `director_concerns` raise path at it: a raise for a switch that meets these conditions is refused, with the reason.

— Director ruling, 23 Oct 2026, his words above; the drafting is the advisor's.

## Done

*Worker tick, 2026-10-23 06:20Z. Moved here unactioned. It was REFUSED by the advisor-channel draw.*

The draw reports that the commit which last staged this file (`ebf866ecc`, author `t`) is not signed
by the advisor's pinned key. The draw therefore gives this file no authority, and nothing in it has
been acted on:

- the annualised advance has not been switched on;
- canon G9 has not been edited;
- the `director_concerns` raise path has not been changed.

The original staging commit `d9faa7916` (author `Claude`) cannot be verified here either, because
`gpg.ssh.allowedSignersFile` is not configured in this tree.

**If the ruling is genuine, the advisor must re-stage it through a signed commit.** The content quotes
07:03 BST, "Great. All good. Do these." Until it is re-staged, the `for_the_director` row raised by
`7e31d8f7` stays open.

**Why it was refused: the cause, found by the seat executor on 23 Oct.** `ebf866ecc` is a seat
landing, not the advisor's. It added the `**Knowledge:**` header line, because
`tools/knowledge_layer_gate.py` refused every merge that brought in a `DIRECTOR_RULING_` file without
one. That edit made the file's last commit a non-advisor commit, and from then on
`advisor_channel.provenance` could never grant it authority. `git diff d9faa7916 ebf866ecc` shows the
header line as the only change; no word of the ruling changed. The class is fixed in the commit that
adds this note. The knowledge gate no longer watches files the advisor stages directly in
`docs/staging/advisor/`, and `done/` stays watched
(`test_an_ADVISOR_STAGED_ruling_is_not_asked_to_be_edited_because_the_edit_voids_its_authority`,
which fails both when the exemption is removed and when it is widened). So a re-staged ruling will
now arrive without any lane needing to edit it.
