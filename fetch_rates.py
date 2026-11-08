"""
Fetch ECB reference rates against USD (via Frankfurter) into rates.json.

Shape: {"EUR": {"YYYY-MM-DD": rate, ...}, "GBP": {...}, ...}, one series per
currency the ECB publishes. Rate = units of that currency per 1 USD.
ECB business days only. Stdlib only.
"""

import json
import sys
import urllib.request
from datetime import date

START = "2024-12-01"
URL = f"https://api.frankfurter.dev/v1/{START}..?base=USD"

# Loose sanity bounds per 1 USD for a few widely used currencies: a value
# outside these is a bad response, not a market move.
BOUNDS = {"EUR": (0.5, 1.5), "GBP": (0.4, 1.3), "HUF": (150.0, 700.0),
          "JPY": (50.0, 300.0), "CHF": (0.4, 1.5)}


def main() -> int:
    req = urllib.request.Request(URL, headers={"User-Agent": "fx-rates-action"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())

    by_currency = {}
    for day, rates in data["rates"].items():
        for cur, rate in rates.items():
            lo, hi = BOUNDS.get(cur, (0.0, float("inf")))
            if not isinstance(rate, (int, float)) or rate <= 0 or not lo <= rate <= hi:
                print(f"bad rate {cur} {day}: {rate}", file=sys.stderr)
                return 1
            by_currency.setdefault(cur, {})[day] = rate

    missing = [c for c in BOUNDS if c not in by_currency]
    days = sorted(by_currency.get("EUR", {}))
    # Too few days or a stale end means the source returned sampled or
    # truncated data; keep the previous file.
    if missing or len(days) < 200 or (date.today() - date.fromisoformat(days[-1])).days > 7:
        print(f"suspicious response: missing {missing}, {len(days)} days", file=sys.stderr)
        return 1

    with open("rates.json", "w", encoding="utf-8") as f:
        json.dump(by_currency, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"rates.json: {len(by_currency)} currencies, {len(days)} days, {days[0]}..{days[-1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
