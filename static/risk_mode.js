const priceTiers = [
    { min: 0.01, max: 1, spread: 0.01 },
    { min: 1, max: 5, spread: 0.03 },
    { min: 5, max: 20, spread: 0.05 },
    { min: 20, max: 50, spread: 0.08 },
    { min: 50, max: 200, spread: 0.10 },
    { min: 200, max: 400, spread: 0.50 },
    { min: 400, max: 1000, spread: 1.00 },
    { min: 1000, max: 5000, spread: 5.00 }
];
const shareSizes = [20, 50, 100, 200, 300, 400, 500, 600, 800, 1000];

let questions = [];
let current = 0;
let correct = 0;
let startTime = 0;
let times = [];

const spreadDisplay = document.getElementById("spread-display");
const riskInput = document.getElementById("risk-input");
const feedback = document.getElementById("risk-feedback");
const countDisplay = document.getElementById("current-count");
const resultDiv = document.getElementById("risk-results");

function generateQuestion() {
    const tier = priceTiers[Math.floor(Math.random() * priceTiers.length)];
    const price = (Math.floor(Math.random() * (tier.max * 100 - tier.min * 100)) + tier.min * 100) / 100;
    const cents = tier.spread;
    const bid = price.toFixed(2);
    const ask = (price + cents).toFixed(2);
    const size = shareSizes[Math.floor(Math.random() * shareSizes.length)];
    const risk = (cents * size).toFixed(2);

    return {
        bid,
        ask,
        size,
        risk: parseFloat(risk)
    };
}

function showQuestion() {
    const q = questions[current];
    spreadDisplay.textContent = `${q.bid} x ${q.ask} | ${q.size} shares`;
    countDisplay.textContent = current + 1;
    riskInput.value = "";
    feedback.textContent = "";
    riskInput.focus();
    startTime = Date.now();
}

function finishGame() {
    document.getElementById("risk-container").style.display = "none";
    resultDiv.style.display = "block";

    const max = Math.max(...times).toFixed(2);
    const avg = (times.reduce((a, b) => a + b, 0) / times.length).toFixed(2);
    const sorted = [...times].sort((a, b) => a - b);
    const median = (sorted.length % 2 === 0)
        ? ((sorted[sorted.length / 2] + sorted[sorted.length / 2 - 1]) / 2).toFixed(2)
        : sorted[Math.floor(sorted.length / 2)].toFixed(2);
    const freq = {};
    sorted.forEach(t => {
        const key = t.toFixed(1);
        freq[key] = (freq[key] || 0) + 1;
    });
    const mode = Object.entries(freq).reduce((a, b) => b[1] > a[1] ? b : a)[0];

    document.getElementById("accuracy").textContent = ((correct / 10) * 100).toFixed(0);
    document.getElementById("max-time").textContent = max;
    document.getElementById("average-time").textContent = avg;
    document.getElementById("median-time").textContent = median;
    document.getElementById("mode-time").textContent = mode;
    document.getElementById("stddev-time").textContent = stdDev(times).toFixed(2);
}

function stdDev(arr) {
    const mean = arr.reduce((a, b) => a + b) / arr.length;
    return Math.sqrt(arr.map(x => (x - mean) ** 2).reduce((a, b) => a + b) / arr.length);
}

riskInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        const userRisk = parseFloat(riskInput.value);
        const q = questions[current];
        const timeTaken = (Date.now() - startTime) / 1000;
        times.push(timeTaken);

        if (Math.abs(userRisk - q.risk) < 0.01) {
            feedback.textContent = "Correct!";
            feedback.style.color = "green";
            correct++;
        } else {
            feedback.textContent = `Wrong. Correct: $${q.risk.toFixed(2)}`;
            feedback.style.color = "red";
        }

        current++;
        if (current < 10) {
            setTimeout(showQuestion, 1000);
        } else {
            setTimeout(finishGame, 1000);
        }
    }
});

for (let i = 0; i < 10; i++) {
    questions.push(generateQuestion());
}
showQuestion();
