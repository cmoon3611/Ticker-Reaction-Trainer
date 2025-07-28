from flask import Flask, render_template, jsonify, request, session
import random
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Needed for session management

HEADLINES_FILE = "headlines.json"
TICKERS_FILE = "tickers.json"

def load_headlines():
    if os.path.exists(HEADLINES_FILE):
        with open(HEADLINES_FILE, "r") as f:
            return json.load(f)
    return []

# Load company/ticker pairs for Ticker Mode
def load_tickers():
    if os.path.exists(TICKERS_FILE):
        with open(TICKERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_headlines(headlines):
    with open(HEADLINES_FILE, "w") as f:
        json.dump(headlines, f, indent=2)

HEADLINES = load_headlines()
TICKERS = load_tickers()

@app.route("/")
def intro():
    return render_template("intro.html")

@app.route("/trainer")
def trainer():
    return render_template("index.html")

@app.route("/burst_mode")
def burst_mode():
    return render_template("burst_mode.html")

@app.route("/instructions")
def instructions():
    return render_template("instructions.html")

@app.route("/risk_mode")
def risk_mode():
    return render_template("risk_mode.html")

@app.route("/add_headline", methods=["GET"])
def add_headline_form():
    return render_template("add_headline.html")

@app.route("/add_headline", methods=["POST"])
def add_headline_submit():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    headline = data.get("headline", "").strip()
    tickers = data.get("tickers", [])

    if not headline or not tickers:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    for t in tickers:
        if not isinstance(t, dict):
            return jsonify({"status": "error", "message": "Each ticker must be an object"}), 400
        symbol = t.get("symbol", "")
        category = t.get("category", "")
        if (
            not isinstance(symbol, str) or not symbol.isalpha() or not symbol.isupper() or
            category not in ("A", "B", "C", "D")
        ):
            return jsonify({"status": "error", "message": "Invalid ticker symbol or category"}), 400

    new_entry = {
        "headline": headline,
        "tickers": tickers
    }

    HEADLINES.append(new_entry)
    save_headlines(HEADLINES)

    return jsonify({"status": "success"})

@app.route("/get_headline")
def get_headline():
    valid_headlines = [h for h in HEADLINES if h.get("tickers") and len(h["tickers"]) > 0]

    if not valid_headlines:
        return jsonify({"headline": "No valid headlines yet!", "tickers": []})

    mode = request.args.get("mode", "").lower()

    if mode == "burst":
        headline = random.choice(valid_headlines)
    else:
        last_headline_text = session.get("last_headline_text")
        choices = [h for h in valid_headlines if h["headline"] != last_headline_text]
        if not choices:
            headline = valid_headlines[0]
        else:
            headline = random.choice(choices)
        session["last_headline_text"] = headline["headline"]

    return jsonify(headline)

@app.route("/get_headlines_batch")
def get_headlines_batch():
    if not HEADLINES:
        return jsonify([])

    batch = random.sample(HEADLINES, min(10, len(HEADLINES)))

    def normalize_entry(entry):
        normalized_tickers = []
        for t in entry.get("tickers", []):
            ticker_symbol = t.get("symbol") or t.get("ticker")
            category = t.get("category", "")
            if ticker_symbol and category:
                normalized_tickers.append({
                    "ticker": ticker_symbol.upper(),
                    "category": category.upper()
                })
        return {
            "headline": entry.get("headline", ""),
            "tickers": normalized_tickers
        }

    batch_normalized = [normalize_entry(h) for h in batch]
    return jsonify(batch_normalized)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    print(f"Submission: {data}")
    return jsonify({"status": "ok"})

@app.route("/headlines", methods=["GET"])
def get_all_headlines():
    return jsonify(HEADLINES)

@app.route("/remove_headline", methods=["POST"])
def remove_headline():
    data = request.get_json()
    headline_to_remove = data.get("headline", "").strip()
    if not headline_to_remove:
        return jsonify({"status": "error", "message": "No headline specified"}), 400

    global HEADLINES
    original_len = len(HEADLINES)
    HEADLINES = [h for h in HEADLINES if h["headline"] != headline_to_remove]

    if len(HEADLINES) == original_len:
        return jsonify({"status": "error", "message": "Headline not found"}), 404

    save_headlines(HEADLINES)
    return jsonify({"status": "success"})

# ✅ NEW ROUTE: Ticker Mode main page
@app.route("/ticker_mode")
def ticker_mode():
    return render_template("ticker_mode.html")

# ✅ NEW ROUTE: Get random company/ticker pair
@app.route("/get_ticker_question")
def get_ticker_question():
    if not TICKERS:
        return jsonify({"name": "No companies loaded!", "ticker": ""})
    entry = random.choice(TICKERS)
    return jsonify(entry)

if __name__ == "__main__":
    app.run(debug=True)
