# CodeSight · AI Code Review Agent 🔍

An AI-powered code review tool that analyzes Python GitHub repositories and surfaces bugs, security vulnerabilities, performance issues, and bad coding practices — all through a sleek Streamlit interface.

---

## ✨ Features

- **Automated Repository Ingestion** — Paste any public GitHub URL and the agent clones it instantly
- **AST-Based Parsing** — Extracts semantic chunks (functions, async functions, classes) using Python's `ast` module; syntax-error files are handled gracefully with fallback chunks
- **Parallel AI Review** — Sends all code chunks to the LLM in parallel via a `ThreadPoolExecutor` for fast turnaround
- **Categorized Issue Detection** — Bugs, security vulnerabilities, performance issues, readability problems, and bad coding practices
- **Confidence Scoring** — Every issue carries a 0–100 confidence score; low-confidence findings are flagged separately as *Verify This*
- **Repository Health Summary** — Repo-level health score (0–100), issue breakdown, recurring patterns, positive observations, and recommended next steps
- **Interactive Filters** — Filter results by severity, confidence tier, and chunk type (function / class / file)
- **JSON Export** — Download the full review report as a structured JSON file

---

## 🗂️ Project Structure

```
ai-code-review-agent/
│
├── app.py                  # Streamlit UI — entry point
│
├── agent/
│   ├── __init__.py
│   ├── ingestion.py        # GitHub URL validation, repo cloning, Python file discovery
│   ├── parser.py           # AST parsing, chunk extraction, fallback chunk creation
│   ├── pipeline.py         # Orchestrates the full review pipeline end-to-end
│   └── reviewer.py         # LLM API calls (Groq), prompt building, summary generation
│
├── prompts/
│   ├── review_prompt.txt   # System prompt for per-chunk code review
│   └── summary_prompt.txt  # System prompt for repo-level health summary
│
├── requirements.txt
└── .env                    # API keys (not committed)
```

---

## 🧠 How It Works

```
GitHub URL
    │
    ▼
[ingestion.py]  →  Clone repo, find all .py files
    │
    ▼
[parser.py]     →  Parse files with AST, extract functions/classes as chunks
                   (syntax-error files become whole-file fallback chunks)
    │
    ▼
[pipeline.py]   →  Parallel LLM review of all chunks (ThreadPoolExecutor)
    │
    ▼
[reviewer.py]   →  Groq API calls with structured JSON output
    │
    ▼
[app.py]        →  Render results in Streamlit with filters + export
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/adityajhinjha/ai-code-review-agent.git
cd ai-code-review-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your free API key at [console.groq.com](https://console.groq.com).

### 5. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser, paste a GitHub repository URL, and click **Run Review**.

---

## ⚙️ Configuration

| Constant | File | Default | Description |
|---|---|---|---|
| `MAX_CHUNKS` | `pipeline.py` | `5` | Max code chunks reviewed per run |
| `MAX_WORKERS` | `pipeline.py` | `5` | Parallel LLM API calls |
| `MIN_LINES` | `parser.py` | `5` | Minimum lines for a chunk to be reviewed |
| `MODEL_NAME` | `reviewer.py` | `llama-3.3-70b-versatile` | Groq model used |
| `CLONE_DIR` | `ingestion.py` | `tmp/cloned_repo` | Local path for cloned repos |

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web UI |
| `openai` | OpenAI-compatible client (used with Groq's API) |
| `python-dotenv` | Load environment variables from `.env` |
| `gitpython` | Clone GitHub repositories programmatically |

---

## 🔍 Review Categories

The agent evaluates code across five dimensions:

- **Bugs** — Logic errors, unhandled exceptions, wrong return values, mutable default arguments
- **Security** — Hardcoded secrets, injection risks, unsafe use of `eval`/`exec`/`pickle`, missing input validation
- **Performance** — Redundant computations, inefficient data structures, blocking I/O in async contexts
- **Readability** — Unclear naming, functions with too many responsibilities, missing docstrings, deep nesting
- **Bad Practices** — Bare `except` blocks, dead code, magic numbers, PEP 8 / PEP 20 violations

---

## 📊 Health Score Reference

| Score | Label | Meaning |
|---|---|---|
| 90 – 100 | ✅ Excellent | Minor or no issues |
| 70 – 89 | 🟢 Good | A few medium issues, nothing critical |
| 50 – 69 | 🟡 Fair | Multiple medium issues or one high-severity issue |
| 30 – 49 | 🟠 Poor | Several high-severity issues requiring attention |
| 0 – 29 | 🔴 Critical | Fundamental problems needing immediate fixing |

---

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Aditya Jhinjha**  
[GitHub](https://github.com/adityajhinjha) 