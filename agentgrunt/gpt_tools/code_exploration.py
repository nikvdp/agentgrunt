import os
import re
from typing import List, Tuple, Optional


def bfs_find(base: str, pattern: str) -> List[str]:
    """Breadth-first search for filenames matching a pattern"""
    queue = [base]
    matched_files = []
    while queue:
        current_path = queue.pop(0)
        if os.path.isdir(current_path):
            for entry in os.listdir(current_path):
                full_path = os.path.join(current_path, entry)
                if os.path.isdir(full_path):
                    queue.append(full_path)
                elif re.search(pattern, entry):
                    matched_files.append(full_path)
    return matched_files


def grep(
    file_path: str, pattern: str, recursive: bool = False
) -> List[Tuple[str, int, str]]:
    """Search for a pattern in a file or a directory (recursively)"""
    matches = []
    if os.path.isdir(file_path) and recursive:
        for root, _, files in os.walk(file_path):
            for file in files:
                matches.extend(grep(os.path.join(root, file), pattern))
    elif os.path.isfile(file_path):
        with open(file_path, "r") as f:
            for line_no, line in enumerate(f, start=1):
                if re.search(pattern, line):
                    matches.append((file_path, line_no, line.strip()))
    return matches


def tree(directory: str, prefix: str = "", depth_remaining: int = 3) -> str:
    """Print a directory tree"""
    if depth_remaining < 0 or not os.path.isdir(directory):
        return ""
    contents = os.listdir(directory)
    entries = []
    for i, entry in enumerate(sorted(contents)):
        is_last = i == len(contents) - 1
        new_prefix = prefix + ("└── " if is_last else "├── ")
        child_path = os.path.join(directory, entry)
        if os.path.isdir(child_path):
            entries.append(new_prefix + entry)
            entries.extend(
                tree(
                    child_path,
                    prefix + ("    " if is_last else "│   "),
                    depth_remaining - 1,
                ).split("\n")
            )
        else:
            entries.append(new_prefix + entry)
    return "\n".join(entries)


def find_function_signatures(file_path: str, language: str) -> List[Tuple[int, str]]:
    """
    Find function signatures in a file.
    Returns a list of tuples, where each tuple contains a line number (int) and the matching line (str).
    """
    if not file_path or not os.path.exists(file_path):
        return []

    patterns = {
        "javascript": [  # js is always fun
            r"function\s*[a-zA-Z_][\w$]*\s*\(",  # Named function
            r"\bfunction\s*\(",  # Anonymous function
            r"[a-zA-Z_][\w$]*\s*=\s*function\s*\(",  # Function assigned to a variable
            r"[a-zA-Z_][\w$]*\s*=\s*\([^)]*\)\s*=>",  # Arrow function assigned to a variable
            r"[a-zA-Z_][\w$]*\s*:\s*function\s*\(",  # Method in an object literal (named function)
            r"[a-zA-Z_][\w$]*\s*:\s*\([^)]*\)\s*=>",  # Method in an object literal (arrow function)
            r"export\s+function\s+[a-zA-Z_][\w$]*\(",  # Named exported function
            r"export\s+default\s+function\s*[a-zA-Z_][\w$]*\s*\(",  # Default exported function (named)
            r"export\s+default\s+function\s*\(",  # Default exported function (anonymous)
            r"export\s+default\s+[a-zA-Z_][\w$]*",  # Default exported function assigned to a variable
        ],
        "c": [r"\b[a-zA-Z_][\w$]*\s*\([^)]*\)\s*{"],  # Function definitions
        "cpp": [r"\b[a-zA-Z_][\w$]*\s*\([^)]*\)\s*{"],
        "ruby": [r"def [a-zA-Z_][\w$]*"],
        "python": [r"def [a-zA-Z_][\w$]*\("],
        "go": [r"func [a-zA-Z_][\w$]*\("],
        "rust": [r"fn [a-zA-Z_][\w$]*\("],
    }

    matches = []
    with open(file_path, "r") as f:
        for line_no, line in enumerate(f, start=1):
            for pattern in patterns.get(language, []):
                match = re.search(pattern, line)
                if match:
                    matches.append((line_no, match.group()))

    return matches


def extract_function_content(
    language: str, signature: str, content: List[str]
) -> Optional[List[str]]:
    """
    Extracts the content of a function given its signature and the content of the file.

    Args:
        signature (str): The function signature.
        content (List[str]): The content of the file.
        language (str): The programming language.

    Returns:
        List[str]: The lines of code that make up the function.
    """
    if language == "python":
        return extract_python_function(signature, content)
    else:  # Default to handling curly brace languages like JavaScript
        return extract_curly_brace_function(signature, content)


def extract_python_function(signature: str, content: List[str]) -> Optional[List[str]]:
    start_line = None
    end_line = None
    for idx, line in enumerate(content):
        if signature in line:
            start_line = idx
            break

    if start_line is None:
        return None

    signature_end_line = start_line
    # If the signature ends on the same line, use the start_line as the signature_end_line
    if "):" in content[start_line]:
        signature_end_line = start_line
    else:
        for idx, line in enumerate(content[start_line + 1 :]):
            if "):" in line:
                signature_end_line = start_line + idx + 1
                break

    initial_indent = len(content[signature_end_line + 1]) - len(
        content[signature_end_line + 1].lstrip()
    )
    indent_stack = [initial_indent]
    for idx, line in enumerate(content[signature_end_line + 1 :]):
        current_indent = len(line) - len(line.lstrip())
        if current_indent > indent_stack[-1] and line.strip():
            indent_stack.append(current_indent)
        elif current_indent <= indent_stack[-1] and line.strip():
            while indent_stack and current_indent < indent_stack[-1]:
                indent_stack.pop()
            if not indent_stack:
                end_line = signature_end_line + idx + 1
                break

    return content[start_line : (end_line or signature_end_line + 1) + 1]


def extract_curly_brace_function(
    signature: str, content: List[str]
) -> Optional[List[str]]:
    start_line = None
    brace_count = 0
    for idx, line in enumerate(content):
        if signature in line:
            start_line = idx
            break

    if start_line is None:
        return None

    end_line = start_line

    for idx, line in enumerate(content[start_line:]):
        brace_count += line.count("{") - line.count("}")
        if brace_count == 0:
            end_line = start_line + idx
            break

    return content[start_line : end_line + 1]
