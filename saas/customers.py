"""Customer cohort — identities, geography, and home characteristics.

Defines the four resi customer profiles as plain data: a single source of
truth for later phases (pricing, hedging, weather correlation) to read from,
rather than each owning its own copy of who these customers are.

The module includes:
- A constant `CUSTOMERS` which is a list of four customer dictionaries.
- Accessor functions to retrieve customer data by ID or segment.
- A function to transform customer data into the format required by the settlement pipeline.

Each customer dictionary has the following keys:
- "customer_id": A unique identifier for the customer.
- "acquisition_date": The date the customer was acquired.
- "location": A nested dictionary containing latitude, longitude, and region.
- "home_type": A string describing the type of home.
- "bedrooms": The number of bedrooms in the home.
- "epc_rating": The Energy Performance Certificate rating.
- "eac_kwh": Estimated annual consumption in kilowatt-hours. This field may be `None` for future smart-meter customers.
- "commodity": The type of energy commodity (e.g., electricity). This is included to support potential expansion to gas in the future.
- "contract_type": The type of contract the customer has.
- "segment": The market segment the customer belongs to.

The module adheres to the "pure, seam-safe" pattern, ensuring that it contains only data and accessor functions without any imports from other simulation modules, I/O operations, or network calls. This separation helps maintain clear boundaries between different parts of the system.
"""

CUSTOMERS = [
    {
        "customer_id": "C1",
        "acquisition_date": "2016-01-01",
        "location": {"lat": 51.5074, "lon": -0.1278, "region": "London"},
        "home_type": "urban_flat",
        "bedrooms": 2,
        "epc_rating": "D",
        "eac_kwh": 2800,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    {
        "customer_id": "C2",
        "acquisition_date": "2016-04-01",
        "location": {"lat": 53.4808, "lon": -2.2426, "region": "Manchester"},
        "home_type": "suburban_semi",
        "bedrooms": 3,
        "epc_rating": "D",
        "eac_kwh": 3500,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    {
        "customer_id": "C3",
        "acquisition_date": "2016-07-01",
        "location": {"lat": 55.8642, "lon": -4.2518, "region": "Glasgow"},
        "home_type": "tenement_flat",
        "bedrooms": 2,
        "epc_rating": "E",
        "eac_kwh": 3200,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    {
        "customer_id": "C4",
        "acquisition_date": "2016-10-01",
        "location": {"lat": 51.8330, "lon": -1.8433, "region": "Cotswolds"},
        "home_type": "rural_detached",
        "bedrooms": 4,
        "epc_rating": "E",
        "eac_kwh": 5500,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "resi",
    },
    {
        "customer_id": "C5",
        "acquisition_date": "2016-01-01",
        "location": {"lat": 51.5074, "lon": -0.1278, "region": "London"},
        "home_type": "small_office",
        "bedrooms": None,
        "epc_rating": "C",
        "eac_kwh": 25000,
        "profile_class": 3,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "SME",
    },
    {
        "customer_id": "C6",
        "acquisition_date": "2016-04-01",
        "location": {"lat": 53.4808, "lon": -2.2426, "region": "Manchester"},
        "home_type": "warehouse_unit",
        "bedrooms": None,
        "epc_rating": "D",
        "eac_kwh": 45000,
        "profile_class": 3,
        "commodity": "electricity",
        "contract_type": "fixed_1yr",
        "segment": "SME",
    },
]


def get_customer(customer_id: str) -> dict | None:
    """
    Retrieve a customer record by customer ID.

    :param customer_id: The unique identifier for the customer.
    :return: The customer dictionary if found, otherwise None.
    """
    return next((customer for customer in CUSTOMERS if customer["customer_id"] == customer_id), None)


def get_customers_for_segment(segment: str) -> list[dict]:
    """
    Retrieve all customer records that match a given segment.

    :param segment: The market segment to filter by.
    :return: A list of customer dictionaries matching the segment, in the order they appear in CUSTOMERS.
    """
    return [customer for customer in CUSTOMERS if customer["segment"] == segment]


def customer_to_settlement_input(customer: dict) -> dict:
    """
    Transform a customer record into the minimal format required by the settlement pipeline.

    :param customer: The customer dictionary to transform.
    :return: A dictionary containing only "customer_id" and "acquisition_date".
    """
    return {
        "customer_id": customer["customer_id"],
        "acquisition_date": customer["acquisition_date"]
    }
