**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

# Being reachable is not being chosen: the selector fix stops exclusion, not ranking

**Found:** 2026-09-05, director console, correcting this seat's own claim about the fix it had just
landed. **Filed and not acted on**, per the same console turn: *"Machinery this session only if a
reader's page is broken or you cannot land. Everything else files and waits."*

---

## The correction

I reported the selector fix (`b0b5cece4`) as making R1 able to win against machinery work. The
director's reading is narrower and correct:

> *"I think the selector fix is narrower than the problem: it stops blocking findings excluding
> product atoms from candidacy, but once both are candidates, machinery still wins on the ordinary
> ranking. Being reachable isn't the same as being chosen."*

`_drop_lane_blocked` restores product atoms to the CANDIDATE SET. What happens next is the ordinary
dial-weighted draw, plus every rung above it. The evidence that this matters is in the same day's
record: the fix landed, and the autonomous side went on drawing machinery, because it was drawing
from a queue still made mostly of findings this seat filed itself.

## Why it is filed rather than fixed

Nothing is broken by it and nothing cannot land. The gap costs draw ORDER, which is exactly the
class the canon says should wait — and a machinery item that fixes how machinery is chosen is the
most self-referential possible reason to displace R1 on the day R1 finally moved.

## What the fix would have to do, when it is drawn

Not a bigger dial. The dial is the thing that already failed: it orders atoms within the final draw,
and the rungs above that draw never consult it. A real repair has to make product work outrank
machinery ITEMS, which means the ranking has to compare across the two kinds — and
`tools/product_machinery_split.classify_path` is now the one place that knows which is which.

The floor already built (`_product_starvation_stretch`, keyed to a product atom being NAMED in a
commit) is the natural trigger: it fired at 213 commits, drained to 0 the moment PB4 landed, and is
the only signal in the machine that currently distinguishes the two kinds at decision time.

## What would close this

A drawn item, and a measurement afterwards: the product share over a 100-commit window, which is
the number `tools/product_machinery_split` exists to publish. It stood at 0% for the whole stretch
this finding describes and moved to 1% on PB4.
