import time
import requests
import pandas as pd

PAGE_SIZE = 50000
WHERE_2023_2024 = (
    "crash_date >= '2023-01-01T00:00:00' AND crash_date < '2025-01-01T00:00:00'"
)


def fetch_all(url, where, order_col, page_size=PAGE_SIZE):
    frames = []
    offset = 0
    while True:
        params = {
            "$limit": page_size,
            "$offset": offset,
            "$where": where,
            "$order": order_col,
        }
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        frames.append(pd.DataFrame(batch))
        print(f"  fetched {offset + len(batch)} rows...")
        offset += page_size
        if len(batch) < page_size:
            break
        time.sleep(0.2)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


if __name__ == "__main__":
    print("Fetching Traffic Crashes - Crashes (full 2023-2024 window)...")
    crashes = fetch_all(
        "https://data.cityofchicago.org/resource/85ca-t3if.json",
        WHERE_2023_2024,
        "crash_record_id",
    )
    crashes.to_parquet("data/raw/crashes.parquet", index=False)
    print(f"  saved {crashes.shape}")

    print("Fetching Traffic Crashes - People (full 2023-2024 window)...")
    people = fetch_all(
        "https://data.cityofchicago.org/resource/u6pd-qa9d.json",
        WHERE_2023_2024,
        "person_id",
    )
    people.to_parquet("data/raw/people.parquet", index=False)
    print(f"  saved {people.shape}")

    print("Done.")
