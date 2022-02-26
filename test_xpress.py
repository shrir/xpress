import pytest
from xpress import (soft_equals, hard_equals, less, less_or_equal, evaluate)


@pytest.mark.parametrize(
    "a, b, result",
    [
        pytest.param(1, 1, True, id="int soft equal"),
        pytest.param(1, 2, False, id="int not soft equal"),
        pytest.param(1, "1", True, id="int as str soft equal"),
        pytest.param(0, False, True, id="int as bool soft equal"),
    ]
)
def test_soft_equals(a, b, result):
    assert soft_equals(a, b) == result


@pytest.mark.parametrize(
    "a, b, result",
    [
        pytest.param(1, 1, True, id="int hard equal"),
        pytest.param(1, "1", False, id="int as str not hard equal"),
        pytest.param(0, False, False, id="int as bool not hard equal"),
    ]
)
def test_hard_equals(a, b, result):
    assert hard_equals(a, b) == result


@pytest.mark.parametrize(
    "a, b, result",
    [
        pytest.param(1, 1, False, id="int not less"),
        pytest.param(0, 1, True, id="int less"),
        pytest.param(0, False, False, id="int as bool not less"),
    ]
)
def test_less(a, b, result):
    assert less(a, b) == result


@pytest.mark.parametrize(
    "a, b, result",
    [
        pytest.param(1, 1, True, id="int equal"),
        pytest.param(0, 1, True, id="int less or equal"),
        pytest.param(0, False, True, id="int as bool equal"),
    ]
)
def test_less_or_equal(a, b, result):
    assert less_or_equal(a, b) == result


@pytest.mark.parametrize(
    "expr, data, result",
    [
        pytest.param([1, "==", 1], {}, True, id="int soft equal"),
        pytest.param([1, "==", "1"], {}, True, id="int as str soft equal"),
        pytest.param([0, "==", False], {}, True, id="int as bool soft equal"),
        pytest.param([1, "===", 1], {}, True, id="int hard equal"),
        pytest.param(
            [1, "===", "1"],
            {},
            False,
            id="int as str not hard equal"),
        pytest.param(
            [0, "===", False],
            {},
            False,
            id="int as bool not hard equal"),
        pytest.param([1, "!=", 2], {}, True, id="int soft not equal"),
        pytest.param([1, "!=", "2"], {}, True, id="int as str soft not equal"),
        pytest.param(
            [1, "!=", False],
            {},
            True,
            id="int as bool soft not equal"),
        pytest.param([1, "!==", 2], {}, True, id="int hard not equal"),
        pytest.param([1, "!==", "1"], {}, True, id="int as str hard not equal"),
        pytest.param(
            [1, "!==", False],
            {},
            True,
            id="int as bool hard not equal"),
        pytest.param([1, "<", 2], {}, True, id="less than"),
        pytest.param([1, "<=", 2], {}, True, id="less than or equals"),
        pytest.param([2, ">", 1], {}, True, id="greater than"),
        pytest.param([2, ">=", 1], {}, True, id="greater than or equals"),
        pytest.param(
            [2, "in", [1, 2, 3, 4, 5]],
            {},
            True,
            id="int in list"
        ),
        pytest.param([True, "or", False], {}, True, id="true or false"),
        pytest.param([False, "or", "apple"], {}, "apple", id="false or str"),
        pytest.param(
            [False, "or", None, "or", "apple"],
            {},
            "apple",
            id="false or null or str"
        ),
        pytest.param([True, "and", True], {}, True, id="true and true"),
        pytest.param(
            [True, "and", True, "and", True, "and", False],
            {},
            False,
            id="true and true and true and false"),
        pytest.param(
            [True, "and", "apple", "and", False],
            {},
            False,
            id="true and str and false"
        ),
        pytest.param(
            [True, "and", "apple", "and", 3.14],
            {},
            3.14,
            id="true and str and int"
        ),
        pytest.param(
            ["var:a", ">", 1],
            {"a": 5},
            True,
            id="Variable greater than int"
        ),
        pytest.param(
            [10, ">", "var:a"],
            {"a": 5},
            True,
            id="int greater than variable"
        ),
        pytest.param(
            ["var:a.b.c", "==", 1],
            {"a": {"b": {"c": 1}}},
            True,
            id="Variable from nested dict equals int"
        ),
        pytest.param(
            [[False, "and", False], "or", True],
            {},
            True,
            id="Nested expression 1"
        ),
        pytest.param(
            [
                ["var:a", ">", "10"],
                "and",
                [
                    [10, "in", "var:c"],
                    "or",
                    ["var:b", "==", "string1"]
                ]
            ],
            {"a": 5, "b": "string1", "c": [1, 2, 3, 4]},
            False,
            id="Nested expression 2"
        ),
    ]
)
def test_evaluate(expr, data, result):
    assert evaluate(expr, data) == result


def test_invalid_expression():
    expr = [["var:a", ">", 1], ["var:b", ">", 5]]
    data = {"a": 1, "b": 2}
    with pytest.raises(Exception) as exc_info:
        evaluate(expr, data)
    assert exc_info.value.args[0] == f"Invalid expression: {expr}"


def test_ambigious_expression():
    expr = [["var:a", ">", 1], "and", ["var:b", ">", 5], "or", True]
    data = {"a": 1, "b": 2}
    with pytest.raises(Exception) as exc_info:
        evaluate(expr, data)
    assert exc_info.value.args[0] == (
        f"Ambigious expression '{expr}': "
        "Multiple operators at the same level"
    )


def test_undefined_variable():
    expr = [["var:a", ">", 1], "and", ["var:b", ">", 5]]
    data = {"a": 1}
    with pytest.raises(Exception) as exc_info:
        evaluate(expr, data)
    assert exc_info.value.args[0] == f"Undefined variable: 'b'"


def test_unknown_operator():
    expr = [["var:a", "*", 1], "and", ["var:b", ">", 5]]
    data = {"a": 1}
    with pytest.raises(Exception) as exc_info:
        evaluate(expr, data)
    assert exc_info.value.args[0] == (
        f"Unknown operator '*' in expression ['var:a', '*', 1]")
