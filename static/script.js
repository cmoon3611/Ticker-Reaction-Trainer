let headline = "";
let expectedTickers = [];
let expectedCategory = "";
let startTime = 0;

async function loadHeadline() {
  try {
    const res = await fetch("/get_headline");
    const data = await res.json();
    headline = data.headline;
    expectedTickers = data.tickers.map(t => t.toUpperCase());
    expectedCategory = data.category.toUpperCase();
    document.getElementById("headline").innerText = headline;
    document.getElementById("response").value = "";
    document.getElementById("response").focus();
    document.getElementById("result").innerText = "";
    startTime = Date.now();
  } catch (err) {
    document.getElementById("headline").innerText = "⚠️ Failed to load headline.";
    console.error("Headline load error:", err);
  }
}

function checkAnswer(userInput) {
  const expectedT = expectedTickers;
  const expectedC = expectedCategory;

  const input = userInput.toUpperCase().trim();

  if (!input) return { correct: false, message: "Please enter your answer." };

  const parts = input.split(/[\s,]+/);

  const categoryInput = parts[parts.length - 1];
  if (!["A", "B", "C"].includes(categoryInput)) {
    return { correct: false, message: "Category must be A, B, or C." };
  }

  const tickersInput = parts.slice(0, parts.length - 1);

  if (tickersInput.length === 0) {
    return { correct: false, message: "Please enter at least one ticker." };
  }

  for (const t of tickersInput) {
    if (!/^[A-Z]+$/.test(t)) {
      return { correct: false, message: `Ticker "${t}" is invalid.` };
    }
  }

  const expectedSet = new Set(expectedT);
  const inputSet = new Set(tickersInput);

  for (const t of expectedSet) {
    if (!inputSet.has(t)) {
      return { correct: false, message: `Missing ticker: ${t}` };
    }
  }

  for (const t of inputSet) {
    if (!expectedSet.has(t)) {
      return { correct: false, message: `Unexpected ticker: ${t}` };
    }
  }

  if (categoryInput !== expectedC) {
    return { correct: false, message: `Category incorrect. Expected: ${expectedC}` };
  }

  return { correct: true, message: "Correct!" };
}

async function submitResponse() {
  const responseInput = document.getElementById("response");
  const userAnswer = responseInput.value.trim();

  if (!userAnswer) return;

  const elapsedSeconds = ((Date.now() - startTime) / 1000).toFixed(2);

  const resultElem = document.getElementById("result");

  const check = checkAnswer(userAnswer);

  if (check.correct) {
    resultElem.style.color = "#00f260";
    resultElem.innerText = `✅ Correct! Reaction time: ${elapsedSeconds} seconds`;
  } else {
    resultElem.style.color = "#ff0033";
    resultElem.innerText = `❌ ${check.message}`;
    return;
  }

  try {
    await fetch("/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        headline,
        userAnswer,
        time: elapsedSeconds
      }),
    });
  } catch (err) {
    console.warn("Failed to send submission:", err);
  }

  setTimeout(loadHeadline, 1800);
}

window.onload = () => {
  loadHeadline();

  const responseInput = document.getElementById("response");

  // Force input value uppercase on user typing
  responseInput.addEventListener("input", () => {
    responseInput.value = responseInput.value.toUpperCase();
  });

  responseInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      submitResponse();
    }
  });
};
