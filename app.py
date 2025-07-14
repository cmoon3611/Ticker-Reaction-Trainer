from flask import Flask, render_template, jsonify, request, session
import random
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Needed for session management

HEADLINES_FILE = "headlines_old.json"

def load_headlines():
    if os.path.exists(HEADLINES_FILE):
        with open(HEADLINES_FILE, "r") as f:
            return json.load(f)
    return []

def save_headlines(headlines):
    with open(HEADLINES_FILE, "w") as f:
        json.dump(headlines, f, indent=2)

HEADLINES = load_headlines()

@app.route("/")
def intro():
    return render_template("intro.html")

@app.route("/trainer")
def trainer():
    return render_template("index.html")

@app.route("/burst_mode")
def burst_mode():
    return render_template("burst_mode.html")

@app.route("/get_headline")
def get_headline():
    if not HEADLINES:
        return jsonify({"headline": "No headlines yet!", "tickers": [], "category": ""})

    mode = request.args.get("mode", "").lower()

    if mode == "burst":
        # For burst mode, pick any random headline (no exclusion)
        headline = random.choice(HEADLINES)
    else:
        # Normal mode: exclude last headline shown (to avoid repetition)
        last_headline_text = session.get("last_headline_text")
        choices = [h for h in HEADLINES if h["headline"] != last_headline_text]
        if not choices:
            headline = HEADLINES[0]
        else:
            headline = random.choice(choices)
        session["last_headline_text"] = headline["headline"]

    return jsonify(headline)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    print(f"Submission: {data}")  # For logging or storage purposes
    return jsonify({"status": "ok"})

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
    category = data.get("category", "").strip().upper()

    if not headline or not tickers or category not in ("A", "B", "C", "D"):
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    if any(not isinstance(t, str) or not t.isalpha() or not t.isupper() for t in tickers):
        return jsonify({"status": "error", "message": "Invalid tickers format"}), 400

    new_entry = {
        "headline": headline,
        "tickers": tickers,
        "category": category
    }

    HEADLINES.append(new_entry)
    save_headlines(HEADLINES)

    return jsonify({"status": "success"})

# NEW: Endpoint to get all headlines
@app.route("/headlines", methods=["GET"])
def get_all_headlines():
    return jsonify(HEADLINES)

# NEW: Endpoint to remove a headline by exact headline text
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

if __name__ == "__main__":
    app.run(debug=True)
