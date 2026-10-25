**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] The OCF `uk_pv` dataset terms are accepted (2026-10-25)

**Type:** RULING, received through the advisor channel. The director's words, from chat on Sun 25 Oct:

- 06:47 GMT: "I accept terms and conditions"

This answers the question in `DIRECTOR_STEER_THE_ASSET_DESIGN_NOTE_HAS_ITS_DISTRIBUTIONS_2026-10-25.md`, rule 4. The question was whether to accept the gated-access terms of Open Climate Fix's `uk_pv` dataset on Hugging Face (https://huggingface.co/datasets/openclimatefix/uk_pv, CC-BY-4.0). The advisor recommended accepting.

## What it authorises

- Use of the OCF `uk_pv` data under its stated terms. The metadata gives per-system orientation, tilt, kWp and install date for more than 30,000 GB domestic systems. The 30-minute generation series can be used for calibration.
- **Attribution is the obligation.** Credit Open Climate Fix and Sheffield Solar wherever the data, or anything derived from it, is published: Knowledge pages, the site, and the design note. Follow the dataset card's own citation wording.
- Store the derived joint distribution (azimuth × tilt × kWp × install cohort, reweighted to FiT and MCS cohort shares) in the repo, with its provenance. Commit the raw data only if the licence and the repo-size rules allow it. If not, record the fetch script and the file hash.

## What it does not authorise

- Creating any account. Gated access needs a Hugging Face account that has clicked "accept". If you have no such account and no token, don't create one. Instead, stage a one-line request for the director, giving the exact URL and the token scope you need (read-only). He will accept on his own account and provide a read token through the usual secret route.
- Any other dataset's terms. Each one is its own ruling.

## Then

- Replace the placeholder orientation shares, which are a named assumption, with the empirical distribution. Run the population checks from the roofs pack: east or west roofs at 0.80–0.82 of south, and fleet yield of 806–920 kWh/kWp.

## Done

Recorded by the seat on 25 Oct. No Hugging Face account, token or HF_ environment variable exists on this machine, and the ruling forbids creating one, so the one-line request is raised in `for_the_director` (`a-read-only-hugging-face-token-for`): accept on his own account, create a read-only token scoped to the one gated repo, and place it at `~/.config/synthetic-enterprise/.env.hf` as `HF_TOKEN`. Until it arrives, the PV orientation shares stay a named assumption. The attribution obligation (Open Climate Fix and Sheffield Solar) is carried into the roofs and solar Knowledge pages drafted today, and into `docs/design/PERSONALISED_ASSET_WORLD.md`.
