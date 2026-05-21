# CodeSight · AI Code Review Agent 🔍

> An autonomous AI agent that clones a GitHub repository, parses source files using AST, and generates structured, confidence-rated code review comments — all through a sleek Streamlit dashboard.

---

# Project Overview

CodeSight is a fully agentic AI pipeline for automated code review. Paste any public GitHub URL and the agent:

1. **Clones** the repository locally using GitPython
2. **Parses** every Python file using Python's `ast` module — extracting functions, async functions, and classes as semantic chunks
3. **Reviews** all chunks in parallel via the Groq LLM API (`llama-3.3-70b-versatile`)
4. **Generates** structured JSON review comments with:
   - severity ratings
   - confidence scores
   - actionable suggestions
5. **Creates** a repository-level health summary:
   - health score (0–100)
   - issue breakdown
   - recurring patterns
   - critical findings
   - recommended next steps
6. **Displays** everything in an interactive Streamlit dashboard with filters and JSON export

Every issue includes a **confidence score (0–100%)**.

Low-confidence findings are automatically separated under a **“Verify This”** label — demonstrating responsible AI behavior instead of presenting all findings with equal certainty.

---

# Live Demo

https://codesight-ai-code-review-agent.streamlit.app

---

# Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python |
| Repository Cloning | GitPython |
| Parsing Engine | Python AST |
| LLM Provider | Groq |
| Model | llama-3.3-70b-versatile |
| Concurrency | ThreadPoolExecutor |
| Environment Variables | python-dotenv |
| Deployment | Streamlit Cloud |

---

# Setup Instructions

## Prerequisites

- Python 3.10+
- Git installed
- Groq API key

Get your API key here:

https://console.groq.com

---

## 1. Clone the Repository

```bash
git clone https://github.com/adityajhinjha/ai-code-review-agent.git
cd ai-code-review-agent
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## 5. Run the Application

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

Paste a GitHub repository URL and click:

```text
Analyze →
```

---

# Architecture Diagram

```text
┌──────────────────────────────────────────────────────────────┐
│                    app.py (Streamlit UI)                    │
│   URL Input → Analyze Button → Filters → JSON Export       │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│               pipeline.py (Orchestrator)                    │
│     Coordinates ingestion → parsing → review pipeline       │
└──────────────┬───────────────────────┬───────────────────────┘
               │                       │
               ▼                       ▼

┌──────────────────────┐    ┌───────────────────────────────┐
│     ingestion.py     │    │          parser.py           │
│──────────────────────│    │───────────────────────────────│
│ • Validate URL       │    │ • ast.parse()                │
│ • Clone repository   │    │ • Extract semantic chunks    │
│ • Find Python files  │    │ • Syntax-error fallback      │
└──────────────────────┘    └───────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────┐
│                reviewer.py (LLM Interface)                  │
│──────────────────────────────────────────────────────────────│
│ • Prompt Engineering                                        │
│ • Parallel AI Reviews                                       │
│ • Confidence Scoring                                        │
│ • Repository Summary Generation                             │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                      │
│──────────────────────────────────────────────────────────────│
│ • Issue Cards                                               │
│ • Severity Filters                                          │
│ • Confidence Filters                                        │
│ • Health Score                                              │
│ • JSON Export                                               │
└──────────────────────────────────────────────────────────────┘
```

---

# File Structure

```text
ai-code-review-agent/
│
├── app.py
│
├── agent/
│   ├── __init__.py
│   ├── ingestion.py
│   ├── parser.py
│   ├── pipeline.py
│   └── reviewer.py
│
├── prompts/
│   ├── review_prompt.txt
│   └── summary_prompt.txt
│
├── requirements.txt
├── README.md
└── .env
```

---

# End-to-End Pipeline

```text
GitHub URL
    │
    ▼
Clone Repository
    │
    ▼
Find Python Files
    │
    ▼
AST Parsing
    │
    ▼
Semantic Chunk Extraction
    │
    ▼
Parallel LLM Reviews
    │
    ▼
Structured JSON Results
    │
    ▼
Repository Health Summary
    │
    ▼
Interactive Dashboard
```

---

# Key Features

## AST-Based Semantic Parsing
Uses Python’s built-in `ast` module to extract:
- functions
- async functions
- classes

instead of sending entire files to the LLM.

---

## Parallel AI Reviews

Uses:

```python
ThreadPoolExecutor
```

to review multiple chunks simultaneously, reducing latency significantly.

---

## Confidence-Rated Reviews

Every issue includes:
- severity
- confidence score
- actionable suggestion

Low-confidence findings are isolated under:
```text
Verify This
```

---

## Syntax Error Recovery

Even if AST parsing fails, the system:
- creates fallback chunks,
- preserves exact syntax error locations,
- still allows the AI to analyze broken files.

---

## Repository Health Summary

The agent generates:
- overall health score,
- issue breakdown,
- recurring patterns,
- critical issues,
- recommended next steps.

---

# Configuration Constants

| Constant | File | Default |
|---|---|---|
| MAX_CHUNKS | pipeline.py | 5 |
| MAX_WORKERS | pipeline.py | 5 |
| MIN_LINES | parser.py | 5 |
| MODEL_NAME | reviewer.py | llama-3.3-70b-versatile |

---

# Known Limitations

1. Duplicate chunk reviews — ast.walk() extracts both a class and its methods as separate chunks, so method code gets reviewed twice, wasting API calls and producing conflicting findings.
2. Limited chunk review count (`MAX_CHUNKS = 5`)
3. No persistent database
4. Small functions silently skipped — Any function under MIN_LINES = 5 is never reviewed with no warning. A one-liner like def get_password(): return "hardcoded123" would be completely missed
5. No retry/backoff system
6. No clone timeout — Repo.clone_from() has no timeout. A large repository will block the UI indefinitely with no way to cancel.
7. No GitHub PR commenting yet

---

# Future Improvements

## Multi-Language Support
Add support for:
- JavaScript
- TypeScript
- Go
- Rust

using `tree-sitter`.

---

## GitHub Pull Request Integration
Post inline comments directly onto pull requests.

---

## Incremental Reviews
Review only changed files/chunks using hashing and caching.

---

## Distributed Architecture
Add:
- Celery
- Redis
- background job queues

for multi-user scalability.

---

## Analytics Dashboard
Track:
- issue trends,
- repository health over time,
- recurring problematic files.

---

# Health Score Reference

| Score | Label | Meaning |
|---|---|---|
| 90–100 | Excellent | Minor or no issues |
| 70–89 | Good | Few medium issues |
| 50–69 | Fair | Multiple medium issues |
| 30–49 | Poor | Several high-severity issues |
| 0–29 | Critical | Fundamental problems |

---

# Dependencies

| Package | Purpose |
|---|---|
| streamlit | Frontend UI |
| openai | Groq OpenAI-compatible client |
| python-dotenv | Environment variable loading |
| gitpython | GitHub repository cloning |

---

# License

This project is open-source and available under the MIT License.

---

# Author

**Aditya Jhinjha**

GitHub:
https://github.com/adityajhinjha