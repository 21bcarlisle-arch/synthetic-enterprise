import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_customer():
    return {
        "customer_id": "C1",
        "eac_kwh": 3500,
        "acquisition_date": "2016-01-01",
        "commodity": "electricity",
        "segment": "resi",
        "hedge_fraction": 0.5,
        "contract_type": "fixed_1yr",
    }


@pytest.fixture
def sample_ssp_series():
    rng = np.random.default_rng(42)
    ssp_values = rng.uniform(30, 80, 48)
    index = range(1, 49)
    return pd.Series(ssp_values, index=index)


@pytest.fixture
def sample_date_range():
    return ("2016-01-01", "2016-03-31")
