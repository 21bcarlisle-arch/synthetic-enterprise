"""The one lossy step in the published weather-cells map, named by the defect it catches.

`tools/generate_weather_cells_data.py` says of `downsample_modal` that "it is tested for exactly
that confusion". Until this file it was not: the claim was in the module docstring and nothing
anywhere imported the function. That is the shape this project keeps paying for -- a control
asserted in prose beside the code it describes -- so the claim is made true rather than deleted.

THE CONFUSION. Every NUMBER on the page comes from the full-resolution derivation; only the
PICTURE is coarsened, 1 km to 5 km. A band id is a label, so the only summary that may coarsen it
is one that returns a label some cell in the block actually holds. A mean or a median returns a
band that belongs to no cell in the block and will sit on the map looking like a place -- and it
will look entirely plausible, because it is a real band elsewhere in Britain.
"""
from __future__ import annotations

import numpy as np

from tools.generate_weather_cells_data import downsample_modal

#: Chosen so the three summaries DISAGREE and each wrong one is a band no cell in the block holds.
#: labels [1, 1, 1, 5, 9, 9]: mode 1, median 3, mean 4.33. Neither 3 nor 4 is present in the block,
#: which is the whole point -- a mean-based downsample invents a band and cannot be caught by any
#: assertion about the map's range.
BLOCK_LABELS = [1, 1, 1, 5, 9, 9]
BLOCK_ROWS = [0, 0, 0, 1, 1, 1]
BLOCK_COLS = [0, 1, 2, 0, 1, 2]


def _grid():
    """One 10x10 km grid at 1 km, downsampled by 5. Land in block (0,0) and a single cell at (1,1).

    Both legs of the block partition are populated on purpose: a block WITH land and a block
    WITHOUT. A downsampler that returned the empty-fill for everything would satisfy every
    assertion about empty blocks on its own.
    """
    labels = BLOCK_LABELS + [7]
    rows = BLOCK_ROWS + [5]
    cols = BLOCK_COLS + [5]
    return downsample_modal(np.array(labels), np.array(rows), np.array(cols), (10, 10), block=5)


def test_a_coarsened_block_takes_the_modal_band_and_not_the_mean_or_the_median():
    """DEFECT: summarising labels with a QUANTITY, which invents a band no cell in the block holds.

    Pinned to 1 -- the mode -- and the two plausible wrong answers are named so a future reader
    can see the assertion is not merely "some number came out". A mean would give 4, a median 3,
    and both are real bands somewhere in Britain, so nothing about the map's range would catch it.
    """
    grid, _, _ = _grid()
    assert grid[0][0] == 1, "the modal band of {} is 1".format(BLOCK_LABELS)
    assert grid[0][0] != 3, "3 is the MEDIAN and no cell in this block holds it"
    assert grid[0][0] != 4, "4 is the rounded MEAN and no cell in this block holds it"


def test_the_summary_only_ever_returns_a_band_some_cell_in_the_block_actually_holds():
    """DEFECT: the property behind the test above, keyed to the property rather than to today's 1.

    A pinned answer goes red when the fixture changes and stays green when the summary rots into
    something that happens to agree on this one block. This is the same claim over the whole
    populated partition: every published band is one of its own block's inputs.
    """
    grid, _, _ = _grid()
    populated = {(0, 0): set(BLOCK_LABELS), (1, 1): {7}}
    for (br, bc), holdable in populated.items():
        assert int(grid[br][bc]) in holdable, (
            "block ({}, {}) published band {}, which no cell in it holds".format(
                br, bc, grid[br][bc]))


def test_a_block_holding_no_land_is_marked_empty_rather_than_defaulting_to_band_zero():
    """DEFECT: a not-found block falling back to a VALID band, which paints sea as a climate.

    -1 is outside the band vocabulary and the page draws it as nothing. Zero would be band zero.
    """
    grid, height, width = _grid()
    assert (height, width) == (2, 2), "10 km at 5 km blocks is 2x2, got {}x{}".format(height, width)
    assert grid[0][1] == -1 and grid[1][0] == -1, "blocks with no land must read empty, not band 0"


def test_a_grid_that_does_not_divide_by_the_block_keeps_the_partial_block():
    """DEFECT: floor division, which silently drops Britain's last few kilometres off the map.

    12 km at 5 km blocks is three blocks, the third holding 2 km. Truncating gives two and the
    loss is invisible: the picture is still a picture and still looks like Britain.
    """
    grid, height, width = downsample_modal(
        np.array([4]), np.array([11]), np.array([11]), (12, 12), block=5)
    assert (height, width) == (3, 3), "12 km at 5 km blocks is 3x3, got {}x{}".format(height, width)
    assert grid[2][2] == 4, "the cell in the partial block must survive the coarsening"
