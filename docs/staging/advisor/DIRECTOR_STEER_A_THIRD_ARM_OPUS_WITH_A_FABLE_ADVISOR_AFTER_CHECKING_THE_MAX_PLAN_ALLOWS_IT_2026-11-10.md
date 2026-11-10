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

## Step 1 done: it is available on the plan, and the installed CLI gives the wrong Fable (worker tick, 10 Nov 2026 ~19:20 GMT)

Four probes, each an Opus 5.5 `-p` session asked to consult its advisor once on a one-line question. A fifth, a one-word task, accepted the flag and never consulted the advisor. The served
models are read from the result's `modelUsage`, never from the flag. Probes are in `/var/tmp/fable-advisor-probe/`.

| CLI | `--advisor` | Outcome | Advisor model that served |
|---|---|---|---|
| 2.1.319 (installed) | `fable` | accepted, advisor called | **`claude-fable-5-1`** (10,578 input tokens, uncached) |
| 2.1.319 | `claude-fable-5-2` | **refused**: "cannot be used as an advisor" | none |
| 2.1.322 (released today, isolated prefix `/var/tmp/cc-2-1-322`) | `claude-fable-5-2` | accepted | `claude-fable-5-2` (10,656 input, uncached) |
| 2.1.322 | `fable` | accepted | `claude-fable-5-2` |

- **No usage-credits consent was asked for in any probe, and none was accepted.** The API's own rate-limit event
  reads `overageStatus: rejected`, `overageDisabledReason: org_level_disabled`, `isUsingOverage: false`. So advisor
  calls cannot bill to credits on this account. They draw the plan's windows: the five-hour and seven-day windows
  are both `allowed`. That is inferred from the event, because no per-call draw is reported. At 18:55 GMT the event
  read 0.25 of the seven-day window and 0.40 of the five-hour window used.
- No flag-disabling variable is set: only `DISABLE_AUTOUPDATER`. `advisorModel` is unset in `~/.claude/settings.json`
  before and after every probe. Only the per-session flag was used.
- **The finding:** on the installed 2.1.319, "a Fable advisor" silently means Fable 5.1. An arm run there would test
  the wrong model, and nothing in the flag would show it. The arm runs on 2.1.322 from the isolated prefix, and the
  served advisor model is checked on every run, as the Fable readings were. The installed CLI is not changed.

**Step 2, not yet run.** The task is one long, already-closed diagnosis with a known answer, run twice at equal
effort: Opus 5.5 alone, then Opus 5.5 with a `claude-fable-5-2` advisor. The candidate is the naive organ's loop
diagnosis. The next tick picks it, files a pre-registration before either run, and runs both. The blind-read test
graded today (`docs/staging/records/SEAT_PREREG_FABLE_5_2_..._2026-11-10.md`) found Fable at about 2.4× Opus's
tokens for equal catches on short reads. So this arm's prediction is that the advisor's cost is visible and its
benefit, if any, shows only on the long task.
