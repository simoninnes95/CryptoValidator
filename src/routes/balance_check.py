import asyncio
import aiohttp
import random
import csv
import os

from dotenv import load_dotenv
from src.common.rate_limiter import RateLimiter

load_dotenv()
API_KEY = os.getenv("API_KEY")

BASE_URL = "https://services.tokenview.io/vipapi/usdt/addressdetail"
MAX_CONCURRENCY = 50
RETRY_STATUS = {429, # Too Many Requests
                500, # Internal Server Error
                502, # Bad Gateway
                503, # Service Unavailable
                504} # Gateway Timeout

RATE_LIMIT_PER_MIN = 300 # Based on Tokenview free tier limits
rate_limiter = RateLimiter(capacity=RATE_LIMIT_PER_MIN, refill_per_sec=RATE_LIMIT_PER_MIN / 60.0)


async def fetch_balance(session, addr):
    await rate_limiter.acquire()
    url = f"{BASE_URL}/{addr}?apikey={API_KEY}"
    backoff = 1.0
    for attempt in range(6):
        try:
            async with session.get(url, timeout=20) as r:
                if r.status in RETRY_STATUS:
                    await asyncio.sleep(backoff + random.random() * 0.25)
                    backoff = min(backoff * 2, 16)
                    continue
                data = await r.json(content_type=None)
                if data.get("code") == 1:
                    bal_str = (data.get("data") or {}).get("balance", "0") or "0"
                    try:
                        bal = float(bal_str)
                    except (TypeError, ValueError):
                        bal = None
                    return addr, bal, None
                else:
                    return addr, None, data
        except asyncio.TimeoutError:
            await asyncio.sleep(backoff); backoff = min(backoff * 2, 16)
        except aiohttp.ClientError as e:
            await asyncio.sleep(backoff); backoff = min(backoff * 2, 16)
        except Exception as e:
            return addr, None, {"exception": repr(e)}
    return addr, None, {"error": "exhausted_retries"}

async def run(addresses):
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    async with aiohttp.ClientSession(headers={"Connection": "keep-alive"}) as session:
        async def bounded(addr):
            async with sem:
                return await fetch_balance(session, addr)
        tasks = [asyncio.create_task(bounded(a)) for a in addresses]
        results = []
        for coro in asyncio.as_completed(tasks):
            results.append(await coro)
        return results

def write_csv(results, filename="results/api_results.csv"):
    with open(filename, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Address", "Balance", "Error"])
        for addr, bal, err in results:
            writer.writerow([addr, bal if bal is not None else "", err if err else ""])