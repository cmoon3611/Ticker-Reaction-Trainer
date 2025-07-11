from flask import Flask, render_template, jsonify, request, session
import random
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Needed for session management

HEADLINES_FILE = "headlines.json"

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

@app.route("/get_headline")
def get_headline():
    if not HEADLINES:
        return jsonify({"headline": "No headlines yet!", "tickers": [], "category": ""})

    last_headline = session.get("last_headline")
    # Filter headlines excluding the last one sent
    choices = [h for h in HEADLINES if h != last_headline]
    if not choices:
        # If only one headline exists or all headlines are same, return it
        headline = HEADLINES[0]
    else:
        headline = random.choice(choices)

    session["last_headline"] = headline
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

if __name__ == "__main__":
    app.run(debug=True)
