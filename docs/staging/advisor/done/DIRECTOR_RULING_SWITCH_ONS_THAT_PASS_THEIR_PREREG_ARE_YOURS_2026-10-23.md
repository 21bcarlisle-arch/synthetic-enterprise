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

*Autonomous worker, 23 Oct 2026. Actioned. This replaces a 06:20Z note that moved the file here
unactioned; that note's refusal was wrong. It is corrected below.*

**Why the first refusal was wrong.** The draw judged authority from the LAST commit to touch this
file. That was `ebf866ecc` (author `t`), a lane's two-line edit adding the `**Knowledge:**` header so
a merge would pass the knowledge gate. The edit was unsigned, so the draw refused the whole file as
unsigned. But the advisor's own staging commit, `d9faa7916`, verifies GOOD against the pinned key:
`git -c gpg.ssh.allowedSignersFile=tools/advisor_allowed_signers verify-commit d9faa7916`. The
note's other claim, that `d9faa7916` "cannot be verified here" because no allowed-signers file was
configured, was also wrong: `tools/advisor_allowed_signers` is in the tree and is what the channel
uses. His ruling was genuine from 07:03 BST; the machine's own edit made it read as forged.
`background/advisor_channel.py` now names that case in its refusal: the signed original, the later
unsigned edit(s), and the diff to read. It still refuses, because authority is the signed bytes.

**What was done, the ruling's four points:**
1. **The annualised advance is on by default.** `DecisionPolicy.bill_estimate_reads_the_annualised_advance`
   defaults True on every standing policy. A revert control in
   `tests/company/billing/test_the_estimate_reads_the_annualised_advance_when_switched_on.py`
   reds if the default goes back to off; the mutation was run and it fired. The grade, the rule
   and the switch-on are on one record:
   `docs/staging/records/WORKER_PREREG_THE_BILL_ESTIMATE_READS_THE_ANNUALISED_ADVANCE_2026-10-22.md`
   §5, with the corrected section-1 projection marked beside its claim. `tools/read_instruction_arms.py`
   now stamps the estimate an arm ran, not its flag, so a flag-less arm cannot read as the
   three-read control. The `for_the_director` row `the-estimated-bill-can-read-the-customer` is
   answered with his words.
2. **The standing rule** is one line in canon G9, quoting "Great. All good. Do these.".
3. **The raise path refuses** a switch-on proposal under the ruling, and names it as the reason
   (`director_concerns.switch_on_refusal`). It lets through a `reserved` concern, and one whose text
   says `outside the 23 Oct ruling: <why>`.
4. **Reported** in the stretch log.

**Left as its own prereg:** the gas nine-month floor
(`WORKER_PREREG_THE_GAS_ESTIMATE_FLOORS_THE_ADVANCE_AT_NINE_MONTHS_2026-10-22.md`). Its build sits
unlanded in the shared working tree and was not touched.
