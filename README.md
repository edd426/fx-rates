# fx-rates

Daily ECB reference rates against USD, fetched from
[Frankfurter](https://frankfurter.dev) by a scheduled GitHub Action and
published as one file:

    https://raw.githubusercontent.com/edd426/fx-rates/main/rates.json

Shape: `{"EUR": {"YYYY-MM-DD": rate, ...}, "GBP": {...}, ...}`, one series per
currency the ECB publishes, where rate is units of that currency per 1 USD.
ECB business days only, from December 2024.

The data is the ECB's public reference rates. The code is MIT licensed.
