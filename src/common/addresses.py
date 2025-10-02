import polars as pl

def get_addresses(csv_path="./data/wallets.csv"):
    """Load addresses from CSV file and return as a list."""
    df = pl.read_csv(csv_path)
    return df["address"].to_list()

