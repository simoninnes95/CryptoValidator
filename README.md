# CryptoValidator

A tool for validating USDT (Tether) wallet balances on the TRON network by comparing locally held balance records against live on-chain data from the Tokenview API.

## Objective

Given a CSV of wallet addresses with expected balances, the tool:

1. Queries the [Tokenview API](https://services.tokenview.io) asynchronously to fetch current USDT balances for each address.
2. Compares API-reported balances against the locally stored values.
3. Outputs categorised results:
   - **validated.csv** — balances match
   - **flagged.csv** — balances differ
   - **nulls.csv** — balance could not be retrieved

## Prerequisites

- Python 3.10+
- A Tokenview API key

## Setup

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd CryptoValidator
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirement.txt
   ```

3. **Configure environment variables**

   Create a `.env` file in the project root:

   ```
   API_KEY=your_tokenview_api_key
   ```

4. **Add wallet data**

   Place your wallet addresses in `data/wallets.csv` with the following columns:

   ```
   address,account_id,asset,balance
   ```

## Usage

Run the validator from the project root:

```bash
python -m src.main
```

Results are written to the `results/` directory.

## Project Structure

```
data/wallets.csv          Input wallet addresses and expected balances
results/                  Output CSVs (validated, flagged, nulls, raw API results)
src/
  main.py                 Entry point
  common/addresses.py     Loads addresses from CSV
  common/rate_limiter.py  Token-bucket rate limiter for API requests
  routes/balance_check.py Async balance fetching and CSV output
  tests/test_balances.py  Validates result counts and categorises outputs
```
