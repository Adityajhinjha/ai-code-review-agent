import os
import json
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables
load_dotenv()


# Groq client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL_NAME = "llama-3.3-70b-versatile"


def load_prompt(filename: str) -> str:
    """Load a system prompt from the prompts directory."""
    path = os.path.join("prompts", filename)
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


SYSTEM_PROMPT  = load_prompt("review_prompt.txt")
SUMMARY_PROMPT = load_prompt("summary_prompt.txt")


def build_syntax_error_notice(error_info: dict) -> str:
    """
    Build an explicit, pinpointed syntax-error block to inject into the prompt.
    All fields come directly from Python's SyntaxError exception — no guessing.
    """
    line    = error_info.get("line", "unknown")
    message = error_info.get("message", "SyntaxError")
    text    = error_info.get("text", "").rstrip()
    offset  = error_info.get("offset") or 0

    # Build a caret pointer so the LLM can see exactly where on the line Python choked
    pointer = (" " * (offset - 1) + "^") if offset else ""

    notice = f"""
⚠️  PYTHON SYNTAX ERROR DETECTED — THIS FILE COULD NOT BE PARSED
════════════════════════════════════════════════════════════════
  Error type : {message}
  Line number: {line}
  Source line: {text}
               {pointer}
════════════════════════════════════════════════════════════════
Your FIRST issue MUST report this syntax error with:
  - title      : "Syntax Error"
  - severity   : "high"
  - confidence : 100
  - description: Reference the EXACT line number ({line}) and explain what is wrong.
  - suggestion : Give the precise fix for line {line}.
After reporting the syntax error, continue reviewing the rest of the code normally.
"""
    return notice


def build_user_message(chunk: dict) -> str:
    """Build the user prompt, injecting a pinpointed notice for syntax-error files."""
    notice = ""
    if chunk.get("syntax_error") and chunk.get("syntax_error_info"):
        notice = build_syntax_error_notice(chunk["syntax_error_info"])

    return f"""Review this code:{notice}

File: {chunk['file']}
Type: {chunk['type']}
Name: {chunk['name']}

Code:
{chunk['code']}
"""


def review_code_chunk(chunk: dict) -> dict:
    """Send a semantic code chunk to the LLM for review."""
    try:
        print(f"Sending API request for: {chunk['name']}")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": build_user_message(chunk)},
            ]
        )

        result = response.choices[0].message.content
        return json.loads(result)

    except Exception as e:
        print(f"Review failed for {chunk['name']}: {e}")
        return {"issues": []}


def summarize_reviews(all_reviews: list) -> dict:
    """
    Send all chunk reviews to the LLM to produce a repo-level health summary.

    Args:
        all_reviews: The full list of review dicts returned by run_review_pipeline.

    Returns:
        A dict matching the summary_prompt.txt schema, or a fallback on failure.
    """
    if not all_reviews:
        return {
            "health_score": 100,
            "health_label": "Excellent",
            "issue_breakdown": {"high": 0, "medium": 0, "low": 0, "total": 0},
            "most_problematic": [],
            "top_critical_issues": [],
            "recurring_patterns": [],
            "positive_observations": ["No issues found across all reviewed chunks."],
            "recommended_next_steps": ["Increase MAX_CHUNKS to review more of the codebase."],
        }

    user_message = f"""Here are the code review results for all chunks in the repository.
Produce a high-level repository health summary based on these reviews.

Reviews:
{json.dumps(all_reviews, indent=2)}
"""

    try:
        print("\nGenerating repository summary...")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SUMMARY_PROMPT},
                {"role": "user",   "content": user_message},
            ]
        )

        result = response.choices[0].message.content
        summary = json.loads(result)
        print("Summary generated successfully.\n")
        return summary

    except Exception as e:
        print(f"Summary generation failed: {e}")
        return {
            "health_score": 0,
            "health_label": "Unknown",
            "issue_breakdown": {"high": 0, "medium": 0, "low": 0, "total": 0},
            "most_problematic": [],
            "top_critical_issues": [],
            "recurring_patterns": [],
            "positive_observations": [],
            "recommended_next_steps": ["Summary generation failed. Check logs for details."],
        }