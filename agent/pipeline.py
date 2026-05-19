from agent.ingestion import (
    clone_repository,
    get_python_files
)

from agent.parser import (
    parse_repository_files
)

from agent.reviewer import (
    review_code_chunk
)

    
MAX_CHUNKS = 5


def run_review_pipeline(repo_url: str) -> list:
    """
    Run the complete AI code review pipeline.
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

    # Step 4: Limit chunks during development
    chunks = chunks[:MAX_CHUNKS]

    print(f"Reviewing {len(chunks)} chunks...\n")

    all_reviews = []

    # Step 5: Review chunks
    for index, chunk in enumerate(chunks, start=1):

        print(f"[{index}/{len(chunks)}] Reviewing: {chunk['name']}")

        review_result = review_code_chunk(chunk)

        all_reviews.append({
        "file": chunk["file"],
        "function": chunk["name"],
        "type": chunk["type"],
        "issues": review_result["issues"]
        })

    print("\nReview pipeline completed.\n")

    return all_reviews


if __name__ == "__main__":

    repo_url = "https://github.com/pallets/flask"

    results = run_review_pipeline(repo_url)

    print("\nFINAL RESULTS:\n")

    for result in results[:3]:

        print("=" * 80)

        print(f"Function : {result['function']}")
        print(f"File     : {result['file']}")
        print(f"Type     : {result['type']}")

        print("\nIssues:\n")

        for issue in result["issues"]:

            print(f"- Title      : {issue['title']}")
            print(f"  Severity   : {issue['severity']}")
            print(f"  Confidence : {issue['confidence']}")
            print(f"  Description: {issue['description']}")
            print(f"  Suggestion : {issue['suggestion']}")
            print()