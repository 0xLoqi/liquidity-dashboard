"""Quick script to inspect what's in the cache."""

import sqlite3
import pickle
from pathlib import Path
import pandas as pd

db_path = Path(__file__).parent / "cache.db"

with sqlite3.connect(db_path) as conn:
    cursor = conn.execute("SELECT key, data, timestamp FROM cache")
    rows = cursor.fetchall()

    for key, data_blob, timestamp in rows:
        print(f"\n{'='*60}")
        print(f"Key: {key}")
        print(f"Timestamp: {timestamp}")
        print(f"{'='*60}")

        try:
            data = pickle.loads(data_blob)

            if isinstance(data, dict):
                print(f"Type: dict with keys: {list(data.keys())}")

                # Check for FRED data
                if "fred" in data:
                    fred = data["fred"]
                    print(f"\nFRED data:")
                    for series_name, df in fred.items():
                        if isinstance(df, pd.DataFrame) and len(df) > 0:
                            print(f"  {series_name}: {len(df)} rows, {df['date'].min()} to {df['date'].max()}")
                            # Show latest values
                            latest = df.iloc[-1]
                            print(f"    Latest: {latest['date']} = {latest['value']}")
                        else:
                            print(f"  {series_name}: empty or invalid")

                # Check for BTC data
                if "btc" in data:
                    btc = data["btc"]
                    if isinstance(btc, pd.DataFrame) and len(btc) > 0:
                        print(f"\nBTC data: {len(btc)} rows")
                        print(f"  Range: {btc['date'].min()} to {btc['date'].max()}")
                        print(f"  Latest price: ${btc['price'].iloc[-1]:,.0f}")

                # Check for stablecoin data
                if "stablecoins" in data:
                    stable = data["stablecoins"]
                    if isinstance(stable, pd.DataFrame) and len(stable) > 0:
                        print(f"\nStablecoin data: {len(stable)} rows")
                        print(f"  Range: {stable['date'].min()} to {stable['date'].max()}")
                        print(f"  Latest supply: ${stable['supply'].iloc[-1]/1e9:.1f}B")

            elif isinstance(data, pd.DataFrame):
                print(f"Type: DataFrame with {len(data)} rows")
                print(data.head())
            else:
                print(f"Type: {type(data)}")

        except Exception as e:
            print(f"Error: {e}")
