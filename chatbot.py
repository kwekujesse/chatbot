import json
import random
import re
import os
from pathlib import Path

# Load .env file if present (no external dependency needed)
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# On Vercel (and other read-only filesystems), /tmp is the only writable location
nltk.data.path.insert(0, "/tmp/nltk_data")

# Download required NLTK data on first run
for pkg in ("punkt", "punkt_tab", "stopwords"):
    try:
        nltk.data.find(f"tokenizers/{pkg}" if "punkt" in pkg else f"corpora/{pkg}")
    except LookupError:
        nltk.download(pkg, download_dir="/tmp/nltk_data", quiet=True)

_stemmer = PorterStemmer()
_stop_words = set(stopwords.words("english"))

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_intents(path: str = None) -> list[dict]:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "data", "intents.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Pre-stem all keywords so we only do it once at load time
    for intent in data["intents"]:
        intent["stemmed_keywords"] = set(
            _stemmer.stem(kw.lower()) for kw in intent["keywords"]
        )
    return data["intents"]


_INTENTS = None  # lazy-loaded singleton


def _get_intents() -> list[dict]:
    global _INTENTS
    if _INTENTS is None:
        _INTENTS = load_intents()
    return _INTENTS


# ---------------------------------------------------------------------------
# Text preprocessing
# ---------------------------------------------------------------------------

def preprocess(text: str) -> list[str]:
    """Lowercase, strip punctuation, tokenize, remove stopwords, stem."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = word_tokenize(text)
    stems = [
        _stemmer.stem(t)
        for t in tokens
        if t not in _stop_words and len(t) > 1
    ]
    return stems


# ---------------------------------------------------------------------------
# Intent detection
# ---------------------------------------------------------------------------

def get_intent(user_input: str) -> tuple[str | None, int]:
    """Return (intent_name, score). Score is number of keyword stem matches."""
    stems = set(preprocess(user_input))
    best_intent = None
    best_score = 0

    for intent in _get_intents():
        score = len(stems & intent["stemmed_keywords"])
        if score > best_score:
            best_score = score
            best_intent = intent["name"]

    return best_intent, best_score


# ---------------------------------------------------------------------------
# Response selection
# ---------------------------------------------------------------------------

def get_response(intent_name: str) -> str:
    """Return a random response from the matched intent's pool."""
    for intent in _get_intents():
        if intent["name"] == intent_name:
            return random.choice(intent["responses"])
    return _fallback_static()


# ---------------------------------------------------------------------------
# Fallback responses
# ---------------------------------------------------------------------------

_STATIC_FALLBACKS = [
    "I'm not quite sure I caught that. Could you rephrase? I'm best at topics like resumes, interviews, internships, networking, LinkedIn, career fairs, salary, grad school, and career exploration.",
    "Hmm, that one's outside my wheelhouse! Try asking about resumes, cover letters, job searching, interviewing, or career planning — those are my specialties.",
    "I didn't quite understand that. I'm CareerCompass, your career services assistant! Ask me about job searching, resumes, interviews, networking, internships, or salary negotiation.",
]


def _fallback_static() -> str:
    return random.choice(_STATIC_FALLBACKS)


def _fallback_openai(user_input: str) -> str:
    """Call OpenAI API as an intelligent fallback, scoped to career topics."""
    try:
        from openai import OpenAI

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return _fallback_static()

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=300,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are CareerCompass, a friendly and knowledgeable career services assistant "
                        "for college students. Only answer career-related questions (resumes, cover letters, "
                        "job searching, interviews, internships, networking, LinkedIn, salary negotiation, "
                        "graduate school, career planning). If the question is completely unrelated to careers, "
                        "politely redirect the user back to career topics. Keep answers concise and encouraging."
                    ),
                },
                {"role": "user", "content": user_input},
            ],
        )
        return response.choices[0].message.content
    except Exception:
        return _fallback_static()


# ---------------------------------------------------------------------------
# Main chat entry point
# ---------------------------------------------------------------------------

CONFIDENCE_THRESHOLD = 1  # minimum keyword matches to trust the rule-based result


def analyze(user_input: str) -> dict:
    """Return full pipeline breakdown for the visualizer."""
    text_lower = user_input.lower()
    text_clean = re.sub(r"[^a-z0-9\s]", " ", text_lower)
    all_tokens = word_tokenize(text_clean)

    token_info = []
    for t in all_tokens:
        if len(t) <= 1:
            token_info.append({"word": t, "status": "short"})
        elif t in _stop_words:
            token_info.append({"word": t, "status": "stopword"})
        else:
            token_info.append({"word": t, "status": "kept", "stem": _stemmer.stem(t)})

    stem_pairs = [
        {"word": t["word"], "stem": t["stem"]}
        for t in token_info if t["status"] == "kept"
    ]
    stems_set = {p["stem"] for p in stem_pairs}

    intents = _get_intents()
    scores = sorted(
        [{"name": i["name"], "score": len(stems_set & i["stemmed_keywords"])} for i in intents],
        key=lambda x: x["score"],
        reverse=True,
    )

    winner = scores[0] if scores and scores[0]["score"] >= CONFIDENCE_THRESHOLD else None
    response_pool = []
    chosen_response = None
    if winner:
        for intent in intents:
            if intent["name"] == winner["name"]:
                response_pool = intent["responses"]
                chosen_response = random.choice(response_pool)
                break
    else:
        chosen_response = _fallback_static()

    return {
        "raw": user_input,
        "token_info": token_info,
        "stem_pairs": stem_pairs,
        "scores": scores,
        "winner": winner,
        "response_pool": response_pool,
        "chosen_response": chosen_response,
        "used_fallback": winner is None,
    }


def chat(user_input: str) -> str:
    """
    Primary chat function.
    1. Run rule-based keyword matching.
    2. If confident → return rule-based response.
    3. If not confident → call Claude API fallback (or static fallback if API unavailable).
    """
    if not user_input or not user_input.strip():
        return "Please type a question and I'll do my best to help!"

    intent_name, score = get_intent(user_input)

    if score >= CONFIDENCE_THRESHOLD and intent_name:
        return get_response(intent_name)

    # Not confident — use OpenAI as smart fallback
    return _fallback_openai(user_input)
