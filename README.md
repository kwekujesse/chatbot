# 🧭 CareerCompass

> **Navigate your future.** — An AI-powered career services chatbot for college students.

CareerCompass is a rule-based chatbot that answers career-related questions on topics like resumes, interviews, internships, job searching, LinkedIn, salary negotiation, networking, and more. When a question falls outside its knowledge base, it seamlessly escalates to GPT-4o mini for an intelligent, in-character response.

Built as a 3-week group project for an AI/ML/DL Chatbot course.

---

## Live Demo

> Deployed on Vercel — *(add your URL here once deployed)*

---

## Screenshots

> *(add screenshots here)*

---

## Features

- **12 intents** covering the full career services domain
- **180+ training questions** in the dataset (exceeds 150 minimum)
- **Rule-based engine** with NLTK stemming — handles ~90% of questions instantly
- **GPT-4o mini fallback** — intelligently handles edge cases outside the ruleset
- **Premium minimal UI** — compact floating card, white space, smooth animations
- **SVG icons**, typing indicator, quick-start chips, message slide-in animations
- **Fully deployable** on Vercel

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| NLP | NLTK (Porter Stemmer, stopwords, tokenizer) |
| AI Fallback | OpenAI GPT-4o mini |
| Frontend | HTML, CSS, Vanilla JS |
| Deployment | Vercel |

---

## Project Structure

```
chatbot/
├── app.py                  # Flask server — 2 routes (GET / and POST /chat)
├── chatbot.py              # Rule-based engine + OpenAI fallback
├── vercel.json             # Vercel deployment config
├── requirements.txt
├── templates/
│   └── index.html          # Chat UI with animations
├── static/
│   └── style.css           # Premium minimal styling
└── data/
    ├── intents.json        # 12 intents — keywords + responses
    └── dataset.csv         # 180 questions (15 per intent)
```

---

## How It Works

```
User Input
    │
    ▼
Preprocess (lowercase → strip punctuation → tokenize → stem)
    │
    ▼
Score each intent by keyword stem overlap
    │
    ├─ Score ≥ 1 → Rule-based response (instant, from intents.json)
    │
    └─ Score = 0 → GPT-4o mini fallback (career-scoped system prompt)
```

The rule engine uses **Porter stemming** so variations like "interviewing", "interviews", and "interview" all match the same intent keywords. Each matched intent returns a randomly selected response from its pool, adding natural variety.

---

## Intents

| Intent | Topic |
|---|---|
| `resume_writing` | Resume format, length, action verbs, ATS |
| `cover_letter` | Cover letter structure, tone, templates |
| `interview_prep` | STAR method, behavioral questions, dress code |
| `internship_search` | Finding internships, timelines, applications |
| `job_search` | Job boards, entry-level roles, tracking applications |
| `linkedin_profile` | Profile optimization, headline, networking |
| `career_fair` | Preparation, elevator pitch, follow-up |
| `salary_negotiation` | How to negotiate, market rates, counter offers |
| `networking` | Informational interviews, cold outreach, alumni |
| `graduate_school` | Applications, GRE, statement of purpose |
| `on_campus_recruiting` | OCI timelines, info sessions, superdays |
| `career_assessment` | Career quizzes, strengths, Holland Code |

---

## Getting Started (Local)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/careercompass.git
cd careercompass
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API key
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_key_here
```

### 4. Run
```bash
python app.py
```

Open `http://localhost:5000` in your browser.

---

## Deployment (Vercel)

1. Push this repo to GitHub (public or private)
2. Go to [vercel.com](https://vercel.com) → **Add New Project** → import your repo
3. Framework preset: **Other**
4. Click **Deploy**
5. Go to **Project Settings → Environment Variables** and add:
   - `OPENAI_API_KEY` → your OpenAI key
6. Redeploy — done.

> The `.env` file is in `.gitignore` and is **never pushed to GitHub**. Your API key is safe.

---

## Dataset

The dataset lives in `data/dataset.csv` with two columns:

```
question,intent
How do I write a good resume?,resume_writing
What should I include in my resume?,resume_writing
...
```

**180 rows total** — 15 questions per intent across 12 intents.

---

## Team

> Add your team members here

---

## Course

> Add your course name and due date here

---

## License

This project was built for educational purposes as part of a university course assignment.
