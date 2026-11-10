**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] A third arm, Opus with a Fable advisor, after checking the Max plan allows it (2026-11-10)

**Type:** STEER, through the advisor channel. It adds to `DIRECTOR_STEER_TEST_FABLE_5_2_AGAINST_OPUS_5_5_ON_OUR_OWN_WORK_2026-11-10.md` and its pre-registration. The director's words, from chat on Tue 10 Nov:

- 15:15 GMT: "What is fable advisor? Is it a more efficient way to use fable?"
- 15:26 GMT, on the advisor's recommendation to test it as a third arm: "Add it, but start by checking it's available on my max plan?"

**When:** after the current Fable readings are graded.

## What the advisor found (check it)

- **Claude Code's advisor tool is experimental.** The main model consults a stronger advisor at decision points: before committing to an approach, when an error recurs, and before declaring done. The advisor reads the full conversation and returns guidance. "Opus 5 or Opus 5.5 main → Fable or Opus 5+ advisor" is an accepted pairing. Set it with `--advisor fable` for one session, or `/advisor fable`. Headless `/advisor` needs CLI v2.1.260 or later, and Skynet has 2.1.319. It stays off if a variable that disables feature-flag fetching is set, such as `DISABLE_TELEMETRY`. ([docs](https://code.claude.com/docs/en/advisor))
- **Each advisor call re-reads the whole transcript, uncached.** The docs say it pays off on long multi-step tasks where most turns are routine and plan quality decides the outcome, and adds little on short tasks.
- **Billing:** on some plans, Fable, including Fable as advisor, bills to **usage credits** after a one-time consent. A secondary source dated 9 Nov says Max includes Fable models within the weekly limit, up to half of it, with Pro on credits after a launch offer that ends 16 Nov. This morning's Fable readings hit the 5-hour limit, which fits with Max counting Fable against plan limits. None of this is confirmed for his account.

## 1. First: confirm it is available on his Max plan, and how it bills

Before any advisor run, establish on Skynet:
- whether `--advisor fable` on an Opus 5.5 session is accepted, refused, or asks for the usage-credits consent;
- that no flag-disabling variable keeps it off;
- from `/usage` or the session totals, whether Fable advisor tokens count against the plan's limits.

**Never accept the usage-credits consent.** That is real money on his account and is his alone (G5). If the plan needs it, stop and raise it in `for_the_director` with what it would cost, and run no advisor arm.

## 2. Then the third arm, on a task it can actually help

The current readings are short single reads, where the advisor adds least. Use **one long, real, already-closed task** with a known answer: for example, the naive organ's loop diagnosis, or another closed diagnosis or design read whose defects were confirmed. Run it twice, at equal effort:
- Opus 5.5 alone;
- Opus 5.5 with a Fable advisor.

Report apart and never blended:
- quality against the known answer;
- main-model tokens and advisor tokens;
- allowance drawn;
- time;
- how many advisor calls, and whether the guidance changed the outcome.

One task decides little. Say so, and say what it would take to decide more.

## Note

The advisor is not a blind reviewer: it sees the main model's own reasoning. At best it complements the two blind readers. It does not replace them.

## Risk

Touches: one or two test sessions' settings, and the plan's usage.
Blast radius: test spend only. Pace against the director's latest reading (21% at 07:42 today).
Probable failure modes:
- Accepting the usage-credits consent by default, or a prompt timing out into acceptance. Refuse it explicitly.
- A saved `advisorModel` left set after the test, quietly applying to every seat. Use the per-session flag, and verify `advisorModel` is unset afterwards.

Proportionality: reversible and narrow — just do it, apart from the consent, which is his.

— Director steer, 10 Nov 2026, his words above; the reading and drafting are the advisor's.
