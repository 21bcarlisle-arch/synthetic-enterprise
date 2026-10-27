# The MPAN core: its structure and check digit

**Type:** REGULATION COMMONS artefact. This file records the TEXT and its citation, readable by
every lane. Each lane's *reading* of it stays its own.

**Why it exists.** `INV_MPAN_CORE_FORMAT` in `docs/design/DOMAIN_INVARIANTS.yaml` (the first cold
read, objection O31) cited the MPAN core's structure from the reader's own knowledge and said "NOT in
the commons: a GAP until a commons page carries it". K8 puts the page before the evaluator.

**Provenance, plainly.** Read on 2026-10-27 in a SECONDARY source only. The primary it cites could
not be fetched from this machine, and two Elexon URLs tried did not carry the text. Everything below
is therefore **[S]** (secondary) until a lane reads the primary.

## Sources

| # | source | status |
|---|---|---|
| S1 | Wikipedia, *Meter Point Administration Number*, read 2026-10-27, sections on the core, distributor IDs and the check digit | read [S] |
| S2 | Energy Retail Association, *Data Item Definition v1 final*, p.23, the check digit (S1's note 28; archived at `web.archive.org/web/20070925074454/http://www.energy-retail.org.uk/pdfs/Data%20Item%20Definition%20v1%20final.pdf`) | **GAP**: not fetched |
| S3 | The MRA / REC data item definitions (now the Retail Energy Code, held for Elexon/RECCo) | **GAP**: not read |

## What S1 says

- **Length.** "The MPAN core is the final 13 digits of the MPAN." It "consists of a two-digit
  Distributor ID, followed by an eight-digit unique identifier", then two more digits and a check
  digit: 2 + 8 + 2 + 1.
- **Distributor ID.** The fourteen DNO licence areas are 10 to 23: 10 Eastern England, 11 East
  Midlands, 12 London, 13 Merseyside and North Wales, 14 West Midlands, 15 North Eastern England,
  16 North Western England, 17 Northern Scotland, 18 Southern Scotland, 19 South Eastern England,
  20 Southern England, 21 Southern Wales, 22 South Western England, 23 Yorkshire.
- **IDNOs.** Independent distribution network operators carry IDs from 24 upward (S1's table runs
  24 to 52 with gaps, tagged "citation needed"). **An IDNO-connected home has a valid core outside
  10-23.** `INV_MPAN_CORE_FORMAT` states 10-23, so on a book that draws IDNO connections it would
  breach on a real MPAN. This book draws none.
- **Check digit.** Multiply the first twelve digits in turn by 3, 5, 7, 13, 17, 19, 23, 29, 31,
  37, 41, 43 (the primes from 3, skipping 11), add the products, and "the check digit is the sum
  modulo 11 modulo 10". S1's code examples apply it to the twelve digits before the check digit.

## Unknown (GAP)

- The primary text of the check digit (S2, S3).
- Whether any IDNO ID above 23 is valid today, and the current list.
