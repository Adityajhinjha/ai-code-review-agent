from concurrent.futures import ThreadPoolExecutor, as_completed

from agent.ingestion import (
    clone_repository,
    get_python_files,
)

from agent.parser import (
    parse_repository_files,
)

from agent.reviewer import (
    review_code_chunk,
    summarize_reviews,
)


MAX_CHUNKS  = 5
MAX_WORKERS = 5   # parallel Groq API calls — safe for free-tier rate limits


def _review_single(index: int, total: int, chunk: dict) -> dict:
    """Review one chunk and return the formatted result. Called from threads."""
    print(f"[{index}/{total}] Reviewing: {chunk['name']}")
    review_result = review_code_chunk(chunk)
    return {
        "file":     chunk["file"],
        "function": chunk["name"],
        "type":     chunk["type"],
        "issues":   review_result["issues"],
        "_order":   index,   # preserve original chunk order in output
    }


def run_review_pipeline(repo_url: str) -> tuple[list, dict]:
    """
    Run the complete AI code review pipeline.

    Chunk reviews run in parallel (ThreadPoolExecutor) so all Groq API
    calls are in-flight at once instead of waiting serially.

    Returns:
        all_reviews - list of per-chunk review results (original order)
        summary     - repo-level health summary dict
    """

    print("\nStarting AI Code Review Pipeline...\n")

    # Step 1: Clone repository
    repo_path = clone_repository(repo_url)

    # Step 2: Find Python files
    python_files = get_python_files(repo_path)
    print(f"Found {len(python_files)} Python files.\n")

    # Step 3: Parse repository into semantic chunks
    chunks = parse_repository_files(python_files)
    print(f"Extracted {len(chunks)} semantic chunks.\n")

    # Step 4: Limit chunks
    chunks = chunks[:MAX_CHUNKS]
    total  = len(chunks)
    print(f"Reviewing {total} chunks in parallel (workers={MAX_WORKERS})...\n")

    # Step 5: Review all chunks in parallel
    raw_results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = {
            executor.submit(_review_single, idx, total, chunk): idx
            for idx, chunk in enumerate(chunks, start=1)
        }

        for future in as_completed(futures):
            try:
                raw_results.append(future.result())
            except Exception as e:
                idx = futures[future]
                print(f"  ✗ Chunk {idx} failed: {e}")

    # Restore original chunk order
    all_reviews = sorted(raw_results, key=lambda r: r.pop("_order"))

    print("\nReview pipeline completed.\n")

    # Step 6: Generate repo-level summary
    summary = summarize_reviews(all_reviews)

    return all_reviews, summary


if __name__ == "__main__":

    repo_url = "https://github.com/pallets/flask"

    results, summary = run_review_pipeline(repo_url)

    # ── Per-chunk results ────────────────────────────────────────────────────
    print("\nPER-CHUNK RESULTS:\n")

    for result in results[:3]:

        print("=" * 80)
        print(f"Function : {result['function']}")
        print(f"File     : {result['file']}")
        print(f"Type     : {result['type']}")
        print("\nIssues:\n")

        for issue in result["issues"]:
            print(f"  - Title      : {issue['title']}")
            print(f"    Severity   : {issue['severity']}")
            print(f"    Confidence : {issue['confidence']}")
            print(f"    Description: {issue['description']}")
            print(f"    Suggestion : {issue['suggestion']}")
            print()

    # ── Repository summary ───────────────────────────────────────────────────
    print("=" * 80)
    print("REPOSITORY HEALTH SUMMARY")
    print("=" * 80)

    print(f"\nHealth Score : {summary.get('health_score')} / 100  ({summary.get('health_label')})")

    breakdown = summary.get("issue_breakdown", {})
    print(f"Issues Found : {breakdown.get('total', 0)} total  "
          f"(High: {breakdown.get('high', 0)}, "
          f"Medium: {breakdown.get('medium', 0)}, "
          f"Low: {breakdown.get('low', 0)})")

    print("\nTop Critical Issues:")
    for issue in summary.get("top_critical_issues", []):
        print(f"  [{issue['severity'].upper()}] {issue['title']}")
        print(f"    → {issue['file']} :: {issue['function']}")
        print(f"    {issue['description']}")

    print("\nRecurring Patterns:")
    for pattern in summary.get("recurring_patterns", []):
        print(f"  • {pattern}")

    print("\nPositive Observations:")
    for obs in summary.get("positive_observations", []):
        print(f"  ✓ {obs}")

    print("\nRecommended Next Steps:")
    for i, step in enumerate(summary.get("recommended_next_steps", []), start=1):
        print(f"  {i}. {step}")

    print()