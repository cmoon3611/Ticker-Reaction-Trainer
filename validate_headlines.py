import json

HEADLINES_FILE = "headlines.json"

def validate_headlines():
    with open(HEADLINES_FILE, "r") as f:
        headlines = json.load(f)

    errors = []
    for i, entry in enumerate(headlines):
        tickers = entry.get("tickers", [])
        for j, ticker in enumerate(tickers):
            # Check if ticker is a dict
            if not isinstance(ticker, dict):
                errors.append(f"Headline {i}, ticker {j}: Not a dict: {ticker}")
                continue
            # Check for ticker or symbol
            symbol = ticker.get("ticker") or ticker.get("symbol")
            if not symbol or not isinstance(symbol, str):
                errors.append(f"Headline {i}, ticker {j}: Missing or invalid 'ticker'/'symbol'")
            # Check category exists and is valid
            category = ticker.get("category")
            if not category or category not in ("A", "B", "C", "D"):
                errors.append(f"Headline {i}, ticker {j}: Missing or invalid 'category'")

    if errors:
        print("Found issues in ticker data:")
        for err in errors:
            print(" -", err)
    else:
        print("All ticker entries look good!")

if __name__ == "__main__":
    validate_headlines()
