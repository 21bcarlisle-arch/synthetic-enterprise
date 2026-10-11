# Filing a document to `docs/staging/`

*For advisor sessions and any writer that commits to origin without the lanes' pre-commit gate. Delivery
seat, 2026-10-11.*

Every document under `docs/staging/` must open with one header line in exactly this shape:

    **Severity:** LATENT · **Lane:** <a maturity-map lane, e.g. H_harness> · **Epoch:** unassigned · **Atom:** `unminted`

- **Severity** is one of `BLOCKING` (a control or a published figure is untrustworthy), `LATENT` (a real
  defect that invalidates nothing published) or `RECORDED` (a known, accepted limitation). Pick honestly; the
  seat may reclassify, with its reason beside the header.
- **Lane** is a lane on the maturity map (`docs/design/maturity_map.yaml`).

**Why it matters.** The lanes' commits run `background/finding_severity.py` before they land; a writer that
commits to origin directly does not. A staging document without a valid header then refuses every lane's
merge of origin until someone repairs it by hand -- three advisor documents did this in two days
(`67ab788e5`, `0343cdb6c`, `cfed366da`).

**Check before committing:** `python3 -m background.finding_severity` must report `UNCLASSIFIED 0`.
