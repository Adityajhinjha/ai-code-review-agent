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


def load_prompt() -> str:
    """Load review system prompt from file."""
    with open("prompts/review_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()


SYSTEM_PROMPT = load_prompt()


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