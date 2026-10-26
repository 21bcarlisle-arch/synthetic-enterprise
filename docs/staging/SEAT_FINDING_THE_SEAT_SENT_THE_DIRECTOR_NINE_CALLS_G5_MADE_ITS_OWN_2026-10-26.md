**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The seat sent the director nine calls that canon G5 made its own, because nothing made a raise say which reserved action it was

Found from the director's 26 Oct question (13:40, advisor channel: "Is it valid to even be asking
me these questions?") and the advisor's steer of the same day. On the morning of 26 Oct,
`DIRECTION.yaml` held 13 open `for_the_director` rows and How it's built said 13 questions waited on
him. Four were G5 actions: the analytics on poesys.net (real people's data), the plan tier (real
money), the Hugging Face token (a credential), and the GitHub link (his private-repository plan).
The other nine were the seat's own calls: pricing, modelling and process choices that G5 says to
act on, record how to reverse, and report.

## Why it happened

Every one of the 13 was raised as kind `strategy` or `canon_intent`, including the four reserved
ones. `raise_concern` accepted a `reserved` kind but never asked which of the G5 classes it was, so
the list had no way to separate "his to rule" from "his to read". The page then counted every open
row as waiting on him.

## What changed (landed with this finding)

- The nine are withdrawn on the seat's own recommendation, each with how to reverse it. The four
  are answered with his 13:47 words.
- `raise_concern(kind="reserved")` refuses without a G5 class from `RESERVED_CATEGORIES`, and
  refuses a G5 class on any other kind. `direction.validate` flags an open reserved row that names
  none. Mutation-proven by `test_a_reserved_concern_names_its_G5_class_or_is_not_raised`.
- How it's built lists only reserved rows under "Waiting on the director (reserved actions only)",
  each with its class. It counts other open concerns in one line, as raised for him to read and
  not waiting.

## What is not changed, and why

The steer's literal wording ("a `for_the_director` row must name its G5 class, or it is not
raised") would also end the operating model's escalation of strategy, vision and canon-intent
concerns. That would change canon intent, so it is raised as a proposal
(`the-26-oct-advisor-steer-asks-that`) and not enacted.

## End-to-end check

- The world wrong: not applicable; this is the harness.
- The maths wrong: the count was correct. It counted the wrong population.
- Him wrong: no. G5 says plainly that these were the seat's calls.
- Not that simple: a G5 class on the row stops a mislabelled raise. It does not stop a reserved
  action from being raised as `strategy`. That second leg is judgement, and a word-matching guard
  would fire falsely, as `one_way_door`'s publish carve-out shows.
