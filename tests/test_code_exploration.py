from ..agentgrunt.gpt_tools.code_exploration import (
    extract_function_content,
    extract_python_function,
    extract_curly_brace_function,
)


def test_extract_python_function():
    # Test case 1: Single-line signature
    content_single_line = [
        "def example_function(param1, param2):",
        "    return param1 + param2",
    ]
    assert (
        extract_python_function("def example_function(", content_single_line)
        == content_single_line
    )

    # Test case 2: Multi-line signature
    content_multi_line = [
        "def process_response(",
        "        self, response, level=0):",
        "    return response",
    ]
    assert (
        extract_python_function("def process_response(", content_multi_line)
        == content_multi_line
    )

    # Test case 3: Signature not found
    assert (
        extract_python_function("def nonexistent_function(", content_single_line)
        == None
    )


def test_extract_curly_brace_function():
    # Test case 1: Normal JavaScript function
    content_js = [
        "function exampleFunction(param1, param2) {",
        "    return param1 + param2;",
        "}",
    ]
    assert (
        extract_curly_brace_function("function exampleFunction(", content_js)
        == content_js
    )

    # Test case 2: Signature not found
    assert (
        extract_curly_brace_function("function nonexistentFunction(", content_js)
        == None
    )


def test_extract_function_content():
    # Test case 1: Python single-line signature
    content_python_single_line = [
        "def example_function(param1, param2):",
        "    return param1 + param2",
    ]
    assert (
        extract_function_content(
            "python", "def example_function(", content_python_single_line
        )
        == content_python_single_line
    )

    # Test case 2: JavaScript function
    content_js = [
        "function exampleFunction(param1, param2) {",
        "    return param1 + param2;",
        "}",
    ]
    assert (
        extract_function_content("javascript", "function exampleFunction(", content_js)
        == content_js
    )
