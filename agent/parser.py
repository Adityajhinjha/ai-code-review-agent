import ast
from typing import List, Dict, Tuple, Optional


# Ignore tiny functions/classes
MIN_LINES = 5


def read_file(file_path: str) -> str:
    """Safely read a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""


def parse_python_file(
    file_path: str,
) -> Tuple[Optional[ast.AST], Optional[str], Optional[dict]]:
    """
    Parse Python file into AST tree.

    Returns:
        tree              - AST tree, or None on failure
        source_code       - raw source text
        syntax_error_info - dict with exact error details if SyntaxError, else None
    """
    source_code = read_file(file_path)

    if not source_code:
        return None, None, None

    try:
        tree = ast.parse(source_code)
        return tree, source_code, None

    except SyntaxError as e:
        error_info = {
            "message": e.msg,
            "line":    e.lineno,
            "offset":  e.offset,
            "text":    (e.text or "").rstrip(),
        }
        print(f"Syntax error in {file_path}: {e.msg} (line {e.lineno})")
        return None, source_code, error_info


def extract_chunks(
    tree: ast.AST,
    source_code: str,
    file_path: str,
) -> List[Dict]:
    """Extract semantic chunks (functions, async functions, classes) from AST."""
    chunks = []

    for node in ast.walk(tree):

        if not isinstance(node, (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
            ast.ClassDef,
        )):
            continue

        line_count = node.end_lineno - node.lineno
        if line_count < MIN_LINES:
            continue

        chunk_type = "class" if isinstance(node, ast.ClassDef) else "function"

        chunks.append({
            "type":              chunk_type,
            "name":              node.name,
            "file":              file_path,
            "start_line":        node.lineno,
            "end_line":          node.end_lineno,
            "line_count":        line_count,
            "code":              ast.get_source_segment(source_code, node),
            "syntax_error":      False,
            "syntax_error_info": {},
        })

    return chunks


def make_fallback_chunk(
    file_path: str,
    source_code: str,
    error_info: Optional[dict] = None,
) -> Dict:
    """
    When a file fails AST parsing, wrap the entire source as one chunk so the
    LLM can still review it. Stores the exact SyntaxError details so the
    reviewer prompt can quote the precise line number and message.
    """
    line_count = source_code.count("\n") + 1
    return {
        "type":              "file",
        "name":              file_path.replace("\\", "/").split("/")[-1],
        "file":              file_path,
        "start_line":        1,
        "end_line":          line_count,
        "line_count":        line_count,
        "code":              source_code,
        "syntax_error":      True,
        "syntax_error_info": error_info or {},
    }


def parse_repository_files(python_files: List[str]) -> List[Dict]:
    """
    Parse all Python files and extract semantic chunks.
    Files with syntax errors become a single whole-file fallback chunk so the
    AI reviewer can still report the exact problem with its line number.
    """
    all_chunks = []

    for file_path in python_files:

        tree, source_code, error_info = parse_python_file(file_path)

        if tree is None:
            if source_code:
                fallback = make_fallback_chunk(file_path, source_code, error_info)
                all_chunks.append(fallback)
                print(f"  → Fallback chunk created for: {file_path}")
            continue

        chunks = extract_chunks(
            tree=tree,
            source_code=source_code,
            file_path=file_path,
        )
        all_chunks.extend(chunks)

    return all_chunks