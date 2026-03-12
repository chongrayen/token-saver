const shortenBtn = document.getElementById("shortenBtn");
const copyBtn = document.getElementById("copyBtn");
const outputEl = document.getElementById("output");
const shorthandEl = document.getElementById("shorthandBlock");
const statsEl = document.getElementById("stats");
const ratioSlider = document.getElementById("ratio");
const ratioValue = document.getElementById("ratioValue");
const shorthandToggle = document.getElementById("shorthand");

ratioSlider.addEventListener("input", () => {
  ratioValue.textContent = ratioSlider.value;
});

copyBtn.addEventListener("click", async () => {
  const text = outputEl.textContent.trim();
  if (!text || copyBtn.disabled) return;
  await navigator.clipboard.writeText(text);
  copyBtn.textContent = "Copied!";
  setTimeout(() => (copyBtn.textContent = "Copy summary"), 1500);
});

shortenBtn.addEventListener("click", async () => {
  const text = document.getElementById("inputText").value;
  if (!text.trim()) {
    alert("Paste a prompt first.");
    return;
  }

  const payload = {
    text,
    ratio: parseInt(ratioSlider.value, 10) / 100,
    maxSentences: document.getElementById("maxSentences").value || null,
    maxChars: document.getElementById("maxChars").value || null,
    shorthand: shorthandToggle.checked,
  };

  shortenBtn.disabled = true;
  shortenBtn.textContent = "Crunching…";
  copyBtn.disabled = true;
  shorthandEl.classList.add("hidden");
  statsEl.classList.add("hidden");

  try {
    const res = await fetch("/api/shorten", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || "Request failed");
    }

    outputEl.textContent = data.summary;
    copyBtn.disabled = false;

    if (data.shorthand) {
      shorthandEl.textContent = data.shorthand;
      shorthandEl.classList.remove("hidden");
    } else {
      shorthandEl.classList.add("hidden");
    }

    statsEl.innerHTML = `Original tokens: <strong>${data.stats.originalTokens}</strong> · Summary tokens: <strong>${data.stats.summaryTokens}</strong> · Reduction: <strong>${data.stats.reductionPercent}%</strong>`;
    statsEl.classList.remove("hidden");
  } catch (err) {
    outputEl.textContent = `Error: ${err.message}`;
  } finally {
    shortenBtn.disabled = false;
    shortenBtn.textContent = "Shorten prompt";
  }
});
