from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from summarizer import summarize_payload

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="/static")


@app.post("/api/shorten")
def shorten_text():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Text is required."}), 400

    ratio = float(data.get("ratio", 0.35))
    max_sentences = data.get("maxSentences")
    max_chars = data.get("maxChars")
    shorthand = bool(data.get("shorthand", False))

    ratio = max(0.05, min(ratio, 1.0))
    if isinstance(max_sentences, str) and max_sentences.strip() == "":
        max_sentences = None
    if isinstance(max_chars, str) and max_chars.strip() == "":
        max_chars = None

    try:
        max_sentences = int(max_sentences) if max_sentences is not None else None
    except (TypeError, ValueError):
        max_sentences = None

    try:
        max_chars = int(max_chars) if max_chars is not None else None
    except (TypeError, ValueError):
        max_chars = None

    payload = summarize_payload(
        text=text,
        ratio=ratio,
        max_sentences=max_sentences,
        max_chars=max_chars,
        shorthand=shorthand,
    )
    payload["ratioUsed"] = ratio
    return jsonify(payload)


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/<path:path>")
def static_proxy(path: str):
    target = FRONTEND_DIR / path
    if target.is_file():
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5050)
