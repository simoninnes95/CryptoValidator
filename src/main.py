import asyncio

from src.common.addresses import get_addresses
from src.routes.balance_check import run, write_csv
from src.tests.test_balances import test_balances

ADDRESSES = get_addresses("data/wallets.csv")

if __name__ == "__main__":
    results = asyncio.run(run(ADDRESSES))
    write_csv(results)
    test_balances()
    print(f"Done")