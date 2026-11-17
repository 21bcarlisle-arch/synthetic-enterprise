# The seven kinds of decision put to the director, and where each one ends (2026-11-17)

*Why this page exists.* Two coders sorted the director's 76 answers into seven kinds and agreed on the
kind only 57 times in 76 (75%). The line between measurement and harness caused 5 of the 19
disagreements
(`docs/staging/done/SEAT_FINDING_HOW_OFTEN_THE_DIRECTOR_ACCEPTS_THE_RECOMMENDATION_BY_KIND_2026-11-17.md`).
A kind can move to the machine only when his answers on it are near-certain, and that can only be
counted once the kind's edge is fixed. This page fixes the edges. `background/direction.py`
`DECISION_KINDS` holds the names, and `director_concerns --raise --decision-kind` records one on
every new `for_the_director` row when it is raised. It is recorded beside the routing `kind` (where
the row was sent) and, later, the `answer_code` (how he answered).

**The unit.** The kind belongs to what the recommendation asks him to approve, not to the subject it
mentions. A harness change justified by a fidelity finding is a harness decision.

## The line that splits most often: measurement against harness

Ask **what is left running once the recommendation has been carried out**.

- **measurement**: the result is an *answer*, such as a number, a grade or a verdict, and the
  machine works exactly as before until some later decision uses that answer. A trial counts as
  measurement when its arms run for a bounded time and **its default at the end is to stop**
  unless the graded result earns a further decision.
- **harness**: the result is a *standing change* to how the machine works, and it runs again
  without anyone deciding again. That holds **even when the thing left running is itself a
  measurement**: a recurring estimate, a reader on every qualifying commit, a gate, a template
  every future steer must fill. A trial whose **default at the end is to keep running** unless a
  kill rule fires is harness, because the decision being asked for is to adopt it.

The five decisions the two coders split, placed by this rule. *I wrote this rule after seeing the
splits. It is a ruling for codings from now on, not a blind re-coding.*

| decision | seat coder | worker coder | this rule | why |
|---|---|---|---|---|
| two-reader review of risky commits (28 Oct) | measurement | harness | **harness** | Readers run on every qualifying commit, and it keeps running unless fewer than half of the findings are confirmed |
| calibrate the readers on our history (5 Nov) | measurement | harness | **measurement** | A one-off fit against our own rework, plus one review of what each gate caught. Nothing changes until it is used |
| estimate the cost of work to come (24 Oct) | measurement | harness | **harness** | A forecast that keeps running and learns from its misses |
| a steer with more than two outcomes gets a decision map (13 Nov) | outside source | harness | **harness** | A template every future steer of that shape must fill. The "no install" outcome rejects Wayfinder only as a side effect |
| abstraction is one research family (7 Nov) | outside source | measurement | **outside source** | Puts a family of outside methods (AST, ontologies, knowledge graphs) into the reading rota. The census beside it is incidental, and kind 5 comes before kind 6 |

## All seven kinds, in precedence order: when two apply, the first one wins

1. **`g5`**: the recommended *action itself* falls in a `RESERVED_CATEGORIES` class
   (`background/one_way_door.py`): real money, real people, real-world legal, contractual or
   regulatory commitments, public claims that cannot be retracted, live credentials and security
   posture, or destroying evidence. **Edge:** a harness or fidelity change that only *mentions*
   one of these classes is not g5. Registering for licensed microdata is g5, because it is a real
   commitment. A daemon that may page his phone is not g5 unless it widens what reaches real
   people. Recorded only on a `reserved` row, and every `reserved` row records it.
2. **`strategy`**: what the company is for, what it values or offers, the canon's intent, the
   mission's wording. **Edge against fidelity:** ask whether a published source could settle it,
   even in principle. If one could, it is fidelity. If the answer is a choice about what we want,
   it is strategy.
3. **`curriculum`**: which world the company lives through. That means a world switch, forward
   years, founder count, seed families, book depth or run size. **Edge against strategy:** it
   changes the *run* the company faces, not the company's aim. **Edge against fidelity:** it picks
   among worlds that are already faithful, and does not make one more faithful.
4. **`fidelity`**: making the world, or the supplier's model of the world, more like the real
   thing, where evidence could decide it. That covers physics, data, behaviour, definitions of a
   real quantity, and regulatory practice. **Edge against outside source:** if the decision is
   *whether to use* a particular dataset or tool, it is kind 5. If it is *what the world should do*
   given the evidence, it is kind 4.
5. **`outside_source`**: adopt, reject or read a named outside source, tool, model, plugin,
   framework or family of methods. This includes adding one to the reading rota.
6. **`measurement`**: see the line above. It produces an answer and leaves nothing running.
7. **`harness`**: see the line above. It is a standing change to the machine's own process:
   gates, queues, seats, readers, efficiency, publishing, the site's upkeep.

## Where the kind is recorded: two channels, one code

- **A `for_the_director` row** records `decision_kind` when it is raised and `answer_code` when he
  answers (`director_concerns --raise --decision-kind`, `--answer --answer-code`).
- **An advisor-channel steer or ruling** never becomes a row, and 41 of the 85 decisions in the 17 Nov
  count came this way, including 16 of the 19 measurement ones. The lane that actions a
  `DIRECTOR_STEER_` or `DIRECTOR_RULING_` file codes it once, when it moves the file to
  `docs/staging/advisor/done/`. It writes exactly one line in the file's `## Done` section:
  `Decision: <decision_kind> <answer_code>`, for example `Decision: measurement yes`. When his words
  answer no recommendation, because the steer is his own initiative, it writes
  `Decision: none -- <reason>`. The kind is what the advisor's recommendation asked him to approve,
  placed by the edges above. The code is how he answered it: `yes`, `changed`, `no` or `returned`.
- `director_concerns --acceptance` counts both channels together. The kind, not the channel, is what
  may move to the machine. It also names any coded-after-the-gate file that it could not read.
  `tests/background/test_director_concerns.py` refuses a steer or ruling that reaches advisor/done
  from 18 Nov without the line. Files that arrived earlier are not re-coded.

## What this page does not settle

- **The other 14 splits** (strategy against fidelity or curriculum; g5 against harness, outside
  source or fidelity) are placed by the edges above, but nobody has re-coded them under these rules.
  The next count has to code each new row once, when it is raised, by these rules. It must not
  re-code history.
- **Rows raised before 17 Nov carry no `decision_kind`.** `--acceptance` counts them as
  `unkinded (<routing kind>)` and never guesses a kind for them, the same way it treats an uncoded
  answer.
