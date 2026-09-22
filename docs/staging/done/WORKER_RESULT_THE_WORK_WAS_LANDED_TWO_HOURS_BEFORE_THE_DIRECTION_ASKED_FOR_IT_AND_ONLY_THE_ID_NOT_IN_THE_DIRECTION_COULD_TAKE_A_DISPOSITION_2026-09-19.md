**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** delivery-lane-disposition

# The work was landed two hours before the direction asked for it, and only the id NOT in the direction could take a disposition

**Drawn:** `land-the-product-gate-answer-that-is-already-written` (Lane 0, delivery seat).
**Turn:** 2026-09-19, scheduled tick. **Fourth window on one answer.**

---

## The disposition first: a rival landed it, and nothing was redone

The item asked for two paths to be landed, on the premise that they were untracked in the shared
tree:

- `docs/staging/SEAT_RESULT_THE_PRODUCT_GATE_REFUSES_CAP_SEGMENTS_NOT_DECISIONS_AND_EVERY_DECISION_THAT_EXISTED_WAS_DECIDED_2026-09-19.md`
- `tools/svt_refusal_census.py`

**Both are tracked and published.** They are in `209f26be4` (*answer(A_strategy): the product gate
refuses cap segments, not decisions, and every decision that existed was decided*), which is an
ancestor of both `HEAD` and `origin/main`. The content was checked at `origin/main` and not
inferred from the sha — the blobs resolve at 15,538 and 14,456 bytes. `ANCESTOR SHA != landed
CONTENT` is a trap this project has already paid for.

Nothing was redone. The census was not re-run. `UPLIFTABLE_TARIFF_TYPES` was not touched.

**What was recorded instead:**

| id | disposition taken | why that one |
|---|---|---|
| `measure-whether-the-product-gate-is-the-real-ceiling-on-the-methods-reach` | `--premise-spent` (restated), then `--release` | held the live claim and the bound landing |
| `land-the-product-gate-answer-that-is-already-written` | `--release` (focus-row tombstone only) | `--landed-under` refused: no ledger row |

## The direction was not stale when written — it went stale, and it said so

The obvious reading is that the direction repeated a premise that was already false. It did not.
`docs/direction/DIRECTION.yaml` was committed at `8f8cd22f0`, **2026-09-19T02:29:09Z**. The rival's
landing `209f26be4` is stamped **04:19:17Z** — one hour fifty minutes *later*. The paths genuinely
were untracked when the seat wrote the item.

The item also hedged correctly and in advance: *"a rival was working this exact claim at 02:24Z, so
if it is already in a ref, take the DISPOSITION and not the work."* That instruction was followed
exactly, and it is the reason this turn cost minutes rather than a rebuild. **Recorded here as a
control that worked**, because the rest of this document is about one that did not.

## The finding: the id the direction names is the id that cannot be credited

The brief closed with an instruction in capitals — *"IMMEDIATELY AFTER EACH COMMIT, run
`python3 -m background.delivery_lane --landed land-the-product-gate-answer-that-is-already-written`
... it is the ONLY way this lane can see your work moving. Skip it and the claim is swept back into
the pool in 100 minutes."*

That id has **no row in the draw ledger and holds no claim**. Measured, not reasoned:

```
$ python3 -m background.delivery_lane --landed-under land-the-product-gate-... measure-whether-...
credited NOTHING to land-the-product-gate-answer-that-is-already-written:
  land-the-product-gate-answer-that-is-already-written was never drawn --
  the ledger has no row for it, so there is no draw for a landing to reach

$ python3 -m background.delivery_lane --release land-the-product-gate-...
released NO CLAIM ... it is NOT CLAIMED here -- nothing holds it, so nothing was let go
```

Both hand-written dispositions join two rows in the draw ledger. An id with no row can take
neither, **by construction and correctly** — the refusals are well-formed and each names itself.
The defect is not in `delivery_lane`. It is that the brief routes the seat to an id the ledger
cannot see, while the claim actually exposed to the 100-minute sweep sat under a different name:

- **In `DIRECTION.yaml`'s `focus:` list:** `land-the-product-gate-answer-that-is-already-written`
  (the id with no row).
- **Holding the claim, the bound landing and the `premise_spent`:**
  `measure-whether-the-product-gate-is-the-real-ceiling-on-the-methods-reach` — which appears in
  `DIRECTION.yaml` **only in prose**, four times, and is not a `focus:` id at all. Its draw row
  still reads `"source": "focus"`, from an earlier direction file where it was one.

So one piece of work carried two ids, in one message, and the two halves of the lane's bookkeeping
went to opposite ones. Following the brief literally would have printed a refusal and left the
claim to be swept and drawn a fifth time.

## The per-window guard is in force and did its job

The prior turn's repair landed. `_disposition` now compares `premise_spent`'s instant against the
draw, not just the presence of a commit. That guard is why this turn had to **restate** the
premise rather than inherit the 04:37:43Z statement: the window drawn at 04:41:19Z was a new
window, and the old excuse no longer settled it.

The restatement is on the row, and it is the honest sentence for *that* window — the landing at
04:19:17Z predates the 04:41:19Z draw by twenty-two minutes, so there was nothing left to deliver
on when it was handed out. **The guard cost exactly what its docstring said it would cost** ("a
disposition is now per-window ... a sentence nobody was willing to restate was never an explanation
of that window in the first place"), and the sentence was restatable, so it was restated.

## Owed

**A focus id minted for work already tracked under another claim id cannot be credited, and the
brief does not know that.** The narrow remedy is at the point where a Lane 0 focus item names
another id in its `what` text: if the named id holds the claim, the "IMMEDIATELY AFTER" instruction
should name *that* id, not the focus id. The one-leg version is a check that the id a brief tells
the seat to `--landed` is an id with a draw-ledger row — a refusal at compose time costs nothing,
and a wrong one costs a whole window.

**Not written as a new register or a new daemon.** One leg on the compose path, or nothing.
