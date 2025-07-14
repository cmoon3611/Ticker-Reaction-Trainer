import json

# Load your existing headlines JSON (replace with your actual filename)
with open("headlines_old.json", "r") as f:
    old_headlines = json.load(f)

new_headlines = []

for entry in old_headlines:
    headline = entry["headline"]
    category = entry.get("category", "A").upper()  # fallback to "A" if missing
    tickers_list = entry.get("tickers", [])

    # Create new ticker dict list with each ticker having the original category
    new_tickers = [{"ticker": t, "category": category} for t in tickers_list]

    new_entry = {
        "headline": headline,
        "tickers": new_tickers
    }
    new_headlines.append(new_entry)

# Save to a new file (or overwrite)
with open("headlines.json", "w") as f:
    json.dump(new_headlines, f, indent=2)

print("Transformation complete! Saved to headlines.json")
