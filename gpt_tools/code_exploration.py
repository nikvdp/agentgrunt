import os
import re
from typing import List, Tuple


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


def tree(directory: str, depth: int = 3) -> str:
    """Print a directory tree"""

    def _tree(dir_path: str, prefix: str, depth_remaining: int) -> str:
        if depth_remaining < 0:
            return ""
        if not os.path.isdir(dir_path):
            return ""
        contents = os.listdir(dir_path)
        entries = []
        for i, entry in enumerate(sorted(contents)):
            is_last = i == len(contents) - 1
            new_prefix = prefix + ("â””â”€â”€ " if is_last else "â”œâ”€â”€ ")
            child_path = os.path.join(dir_path, entry)
            if os.path.isdir(child_path):
                entries.append(new_prefix + entry)
                entries.append(
                    _tree(
                        child_path,
                        prefix + ("    " if is_last else "â”‚   "),
                        depth_remaining - 1,
                    )
                )
        return "\n".join(entries)

    return _tree(directory, "", depth)


def find_function_signatures(file_path: str, language: str) -> List[Tuple[int, str]]:
    """Find function signatures in a file"""
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
        "ruby": [r"def [a-zA-Z_][\w$]*"],
        "python": [r"def [a-zA-Z_][\w$]*\("],
    }

    matches = []
    with open(file_path, "r") as f:
        for line_no, line in enumerate(f, start=1):
            for pattern in patterns.get(language, []):
                match = re.search(pattern, line)
                if match:
                    matches.append((line_no, match.group()))

    return matches
