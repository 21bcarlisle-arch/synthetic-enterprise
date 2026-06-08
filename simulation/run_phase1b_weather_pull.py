"""Phase 1b weather pull: real daily historical weather (2016-01-01 to
2025-06-07) for the four customer locations, stored as one CSV per
location in sim/weather_data/ — per the Master Backlog's Phase 1b
deliverable 3 ("store it, do not correlate yet").
"""

import os


from saas.customers import CUSTOMERS
from sim.weather_ingestor import get_daily_weather, write_weather_csv

PULL_START = "2016-01-01"
PULL_END = "2025-06-07"
OUTPUT_DIR = "sim/weather_data"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    total_records_written = 0
    customer_record_counts = {}
    
    for customer in CUSTOMERS:
        customer_id = customer["customer_id"]
        latitude = customer["location"]["lat"]
        longitude = customer["location"]["lon"]
        region = customer["location"]["region"]
        
        print(f"Fetching weather for {customer_id} ({region}, {latitude}, {longitude})...")
        records = get_daily_weather(customer_id, latitude, longitude, PULL_START, PULL_END)
        print(f"  -> {len(records)} records retrieved")
        
        output_path = f"{OUTPUT_DIR}/{customer_id}.csv"
        write_weather_csv(records, output_path)
        print(f"  -> Weather data written to {output_path}")
        
        total_records_written += len(records)
        customer_record_counts[customer_id] = len(records)
    
    print(f"Total customers processed: {len(CUSTOMERS)}")
    print(f"Total records written across all customers: {total_records_written}")
    
    return customer_record_counts

if __name__ == "__main__":
    main()
