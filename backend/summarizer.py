from __future__ import annotations

import math
import re
from typing import Dict, List, Sequence

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for",
    "if", "in", "into", "is", "it", "of", "on", "or", "such", "that",
    "the", "their", "then", "there", "these", "they", "this", "to",
    "was", "will", "with", "your", "you", "from", "have", "has", "had",
    "were", "can", "could", "would", "should", "do", "does", "did", "not",
    "no", "yes", "about", "up", "down", "over", "under", "so", "just",
}

ABBREVIATIONS = {
    "people": "ppl",
    "message": "msg",
    "messages": "msgs",
    "because": "b/c",
    "before": "b4",
    "between": "btwn",
    "without": "w/o",
    "with": "w/",
    "information": "info",
    "priority": "prio",
    "update": "upd",
    "request": "req",
    "requests": "reqs",
    "regarding": "re:",
    "please": "pls",
    "thanks": "tx",
    "tomorrow": "tmrw",
    "tonight": "2nite",
    "department": "dept",
    "management": "mgmt",
    "approximately": "~",
    "number": "#",
    "increase": "+",
    "decrease": "-",
}

WORD_RE = re.compile(r"[\w']+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
MULTISPACE_RE = re.compile(r"\s+")


def split_sentences(text: str) -> List[str]:
    raw = SENTENCE_SPLIT_RE.split(text.strip())
    sentences = [s.strip() for s in raw if s.strip()]
    return sentences or [text.strip()]


def tokenize(sentence: str) -> List[str]:
    return WORD_RE.findall(sentence.lower())


def score_sentences(sentences: Sequence[str]) -> List[float]:
    freq: Dict[str, int] = {}
    for sent in sentences:
        for word in tokenize(sent):
            if word in STOPWORDS:
                continue
            freq[word] = freq.get(word, 0) + 1
    if not freq:
        return [0.0] * len(sentences)
    max_freq = max(freq.values())
    scores = []
    for sent in sentences:
        score = 0.0
        for word in tokenize(sent):
            if word in STOPWORDS:
                continue
            score += freq[word] / max_freq
        scores.append(score)
    return scores


def summarize(
    text: str,
    ratio: float = 0.35,
    max_sentences: int | None = None,
    max_chars: int | None = None,
) -> str:
    sentences = split_sentences(text)
    if len(sentences) == 1:
        summary = sentences[0]
    else:
        scores = score_sentences(sentences)
        target = max(1, math.ceil(len(sentences) * ratio))
        if max_sentences is not None:
            target = min(target, max_sentences)
        ranked_indices = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)
        chosen = sorted(ranked_indices[:target])
        summary = " ".join(sentences[i] for i in chosen)

    summary = MULTISPACE_RE.sub(" ", summary).strip()
    if max_chars is not None and len(summary) > max_chars:
        summary = summary[: max_chars - 1].rstrip() + "…"
    return summary


def apply_shorthand(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        word = match.group(0)
        lower = word.lower()
        if lower in ABBREVIATIONS:
            repl_word = ABBREVIATIONS[lower]
            if word[0].isupper() and len(word) > 1:
                return repl_word.capitalize()
            return repl_word
        return word

    return WORD_RE.sub(repl, text)


def summarize_payload(
    text: str,
    ratio: float = 0.35,
    max_sentences: int | None = None,
    max_chars: int | None = None,
    shorthand: bool = False,
) -> dict:
    summary = summarize(text, ratio=ratio, max_sentences=max_sentences, max_chars=max_chars)
    original_tokens = len(text.split())
    summary_tokens = len(summary.split())
    reduction = 0.0
    if original_tokens:
        reduction = 100 * (1 - summary_tokens / original_tokens)

    payload = {
        "summary": summary,
        "stats": {
            "originalTokens": original_tokens,
            "summaryTokens": summary_tokens,
            "reductionPercent": round(reduction, 1),
        },
    }
    if shorthand:
        payload["shorthand"] = apply_shorthand(summary)
    return payload
