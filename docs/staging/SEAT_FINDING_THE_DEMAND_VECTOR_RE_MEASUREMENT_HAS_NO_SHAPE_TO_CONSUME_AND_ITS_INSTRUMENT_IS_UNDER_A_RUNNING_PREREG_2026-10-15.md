**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_29_the_coverage_is_re_measured_against_the_demand_vector`
**Knowledge:** `how-many-synthetic-households` -- the page whose first named limit is that N has not converged

# The demand-vector re-measurement has no shape to consume, and its instrument is under a running prereg

*Delivery seat fork, drawn on W2_29, 2026-10-15. The premise was re-measured before any build, and it
does not hold. Nothing was built. This finding names what is missing.*

## What the exit asks, and what the tree supplies

The exit is the weighted acceptance re-run over the FULL five-component vector
(`tools.reduction_dimension.DEMAND_VECTOR`: annual gas, annual electricity, seasonal gas shape,
half-hourly electricity shape, heating fuel) "once W2_30 lands". W2_30 is at level 2. It does not
supply what the re-run needs, for three reasons.

1. **Neither W2_30 deliverable is in the coverage instrument's reach.** `demand_vector_coverage`
   imports neither `simulation.household_demand_shape` nor `simulation.fabric_demand_path` (checked
   by grep at `9ab9b7959`). Both of those work on SETTLED BOOK PREMISES. `seasonal_gas_split` fits a
   household's own daily fabric gas trace against its HDD (`MIN_DAYS_FOR_FIT = 60`), and
   `fabric_providers_for_book` drives a book premise's half-hourly electricity. The coverage
   population is NEED rows crossed with weather cells, built by `generated_population`. It has an
   annual gas figure from a demand model that stops on 31 March (`demand_case_coverage.DOYS`), and it
   has no daily gas series and no fabric trace. Nothing turns a generated NEED household into the
   series `seasonal_gas_split` consumes.
2. **Both shape components are still declared blind, and correctly.** `REDUCES_OVER.blind_to` is
   `("half_hourly_electricity_shape", "seasonal_gas_shape")`. `peak_window_share` is built by the
   legacy `demand_model.build_demand_shape` over three occupancy patterns. That is the path
   `household_demand_shape`'s own docstring calls collapsed: family1 against single1 sits at 1.6e-4.
   So the axis carries a level and an elderly flag, not a shape.
3. **No defined distance along a shape exists to accept against.** The acceptance is a per-axis KS
   distance at 0.05. A half-hourly shape is a 48-vector and a seasonal shape is a split. Which
   scalar summary (or which multivariate distance) stands for "the distribution of shapes" is a
   design decision the canon does not make and no knowledge page records. That decision has to come
   before the build (K8), and choosing it here would be a picked number.

**What would make the exit buildable**, in order:

- **(a)** A route from a generated household to a fabric trace. Either `generated_population`
  calls the fabric path per household, or the coverage population is drawn from premises that
  already carry one. This is `simulation/` work, outside this atom's `file_scope`.
- **(b)** A written definition of the shape axes. A knowledge page should say what distance two
  households' shapes are apart, and why.
- **(c)** Only then, the re-run.

## Why nothing was built today, even partially

The director parked this row on 2026-10-14 at 18:15: "the N study is research, not clear-down. The
480k rung's five seeds finish ... no further rungs. Next week's step: grade 480k against its
prereg." The instrument under that prereg is `tools/demand_vector_coverage.py` at `b585d3733`, and
HEAD's copy is byte-identical (`git diff b585d3733 HEAD` is empty). Any edit to the module now would
split the instrument from the one the prereg grades.

**State of the 480k run at 03:30 on 2026-10-15** (raw, UNGRADED, so grading stays the parked
next-week step). `/var/tmp/dvn480/s{0,1,3,4}.json` are written, with `n` = 19,529, 25,028, 19,531
and 19,530. Seed 2 started at about 03:25 (pid 1800096, under `leg_a.sh`). At this size a seed took
4.8 to 5.5 hours. Every `.err` read so far is empty.

## Proposed

W2_29 stays at **level 1**. Its `blocked_on` should name (a) and (b) above, not W2_30's level.
W2_30 at level 2 is not what blocks it: what blocks it is the missing bridge from a generated
household to a trace. The map row is not moved here.
