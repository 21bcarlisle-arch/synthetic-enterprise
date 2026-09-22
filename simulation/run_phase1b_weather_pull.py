"""Phase 1b's per-property weather pull — THE REFUSED DESIGN, and it now says so.

WHAT THIS WAS. Real daily weather (2016-01-01 to 2025-06-07) for the four supply-book
locations, one CSV per location in `sim/weather_data/`, per the Master Backlog's Phase 1b
deliverable 3 ("store it, do not correlate yet"). It did that, and the four archives it
wrote are still the world's real per-property record.

WHY IT REFUSES NOW. The director refused per-property pulls: a household's sky is resolved
from the per-cell store (`sim/weather_world.py`, built by `tools/build_weather_world.py
--build`), which serves eighteen times more premises than four filenames ever could. Every
settlement leg was migrated onto it — the fabric leg, then the demand-shape and forward-price
legs (2026-09-21), then the gas/HDD leg, which had been a third resolver handing ten of
eighteen premises a 1991-2020 climate normal. Nothing this script writes is read by anything
the book settles, bills or hedges on.

WHY IT IS A REFUSAL AND NOT A DELETION. `docs/staging/` has carried "still the refused design,
still executable" forward four times (2026-09-16, -20, and twice on -21), each note declining
to delete it because "deleting a runner is a judgement for the lane that owns the migration".
The judgement was stuck because retiring the per-property design was treated as one unit, and
it is not: `weather_inputs._weather_source_customer_id` and `weather_cell_siting.cell_matched_site`
still serve `load_weather_means`'s remaining readers and the W1_14 siting controls, so they stay.
This runner serves NO reader and was the only piece of it holding a route to the network. So the
hazard goes and the record stays.

THE HAZARD THAT MAKES IT WORTH A REFUSAL RATHER THAN A COMMENT. On 2026-09-06 this script,
pointed at a live Open-Meteo daily rate limit, wrote 125-byte header-only CSVs over real
archives and exited 0 — see
`docs/staging/done/SEAT_FINDING_A_RATE_LIMITED_WEATHER_PULL_WROTE_HEADER_ONLY_CSVS_OVER_TEN_YEARS_OF_REAL_ARCHIVE_AND_EXITED_ZERO_2026-09-06.md`.
`sim/weather_ingestor.write_weather_csv` grew two refusals in that commit and that specific
data-loss path is closed at the ingestor. But it iterates the LIVE supply book, so its blast
radius is still every archive the book names, and a comment saying "superseded" stops nobody
who runs the file. A refusal that names its reason is how we find out if the refusal was wrong.
"""


class RefusedDesign(RuntimeError):
    """This runner's design was refused; the reason and the successor are in the message.

    A DISTINCT type, the `sim/weather_ingestor.WeatherArchiveRefusal` idiom, so a control can
    assert THIS refusal fired rather than assert on some generic error that an unrelated
    breakage — a missing supply book, an import failure — would also produce.
    """


PULL_START = "2016-01-01"
PULL_END = "2025-06-07"
OUTPUT_DIR = "sim/weather_data"

SUCCESSOR = "tools/build_weather_world.py --build"


def main():
    """Refuse, naming the reason and the successor. Never pulls, never writes.

    The refusal is raised BEFORE anything is resolved or opened, and this module imports
    neither `sim.weather_ingestor` nor the supply book any more, so there is no inner
    function left to call round it.
    """
    raise RefusedDesign(
        "REFUSED: the per-property weather pull is the design the director refused. "
        f"A household's sky comes from the per-cell store — build it with `{SUCCESSOR}`, "
        "which covers every premise instead of the four that happen to match a filename. "
        f"This script looped the LIVE supply book writing {OUTPUT_DIR}/<customer_id>.csv, and "
        "on 2026-09-06 it wrote header-only CSVs over ten years of real archive and exited 0. "
        "If you need one cell's history, that is a store build, not a per-property archive. "
        "If you believe this refusal is wrong, the reason is named here so you can say which "
        "part of it is false."
    )


if __name__ == "__main__":
    main()
