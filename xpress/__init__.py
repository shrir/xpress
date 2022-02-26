# This the implementation for evaluation of xpress expressions. It contains:
# - Operators(Courtesy: JSONLogic Python(https://github.com/nadirizr/json-logic-py))
# - Parsing of the expression tree.
from functools import reduce, partial
from typing import List, Dict, Any


def soft_equals(a: Any, b: Any) -> bool:
    """Implements the '==' operator, which does type JS-style coertion."""
    if isinstance(a, str) or isinstance(b, str):
        return str(a) == str(b)
    if isinstance(a, bool) or isinstance(b, bool):
        return bool(a) is bool(b)
    return a == b


def hard_equals(a: Any, b: Any) -> bool:
    """Implements the '===' operator."""
    if type(a) != type(b):
        return False
    return a == b


def less(a: Any, b: Any) -> bool:
    """Implements the '<' operator with JS-style type coertion."""
    types = set([type(a), type(b)])
    if float in types or int in types:
        try:
            a, b = float(a), float(b)
        except TypeError:
            # NaN
            return False
    return a < b


def less_or_equal(a: Any, b: Any) -> bool:
    """Implements the '<=' operator with JS-style type coertion."""
    return (
        less(a, b) or soft_equals(a, b)
    )


operators = {
    "==": soft_equals,
    "===": hard_equals,
    "!=": lambda a, b: not soft_equals(a, b),
    "!==": lambda a, b: not hard_equals(a, b),
    ">": lambda a, b: less(b, a),
    ">=": lambda a, b: less(b, a) or soft_equals(a, b),
    "<": less,
    "<=": less_or_equal,
    "in": lambda a, b: a in b if "__contains__" in dir(b) else False,
}

logical_operators = {
    "and": lambda a, b: a and b,
    "or": lambda a, b: a or b
}


def separate_logical_operator_and_operands(expression) -> str:

    op = set()
    operands = []
    for item in expression:
        if isinstance(item, str) and item in logical_operators:
            op.add(item)
        else:
            operands.append(item)

    logical_operators_in_expression = [
        item for item in expression if isinstance(
            item, str) and item in logical_operators]

    if not op:
        raise Exception(f"Invalid expression: {expression}")
    elif len(op) > 1:
        raise Exception(
            f"Ambigious expression '{expression}': "
            "Multiple operators at the same level"
        )

    return op.pop(), operands


def resolve(item: Any, data: Dict=None) -> Any:
    if not isinstance(item, str) or not item.startswith("var:"):
        return item

    var_name = item[len("var:"):]
    try:
        return reduce(dict.__getitem__, var_name.split("."), data)
    except KeyError as e:
        raise Exception(f"Undefined variable: {e}")


def evaluate(expression: List, data: Dict=None) -> bool:
    """
    Evaluates the expression with the given data.
    """
    result = False
    data = data or {}

    if not expression:
        return False

    if not isinstance(expression, (list, tuple)):
        return expression

    #  Single item in a list. e.g. [value] or [["operand", "operator", "value"]]
    if len(expression) == 1:
        if isinstance(expression[0], (list, tuple)):
            return evaluate(expression[0], data)
        return expression[0]

    # 3-tuple expression. e.g. ["operand", "operator", "value"]
    if len(expression) == 3 and not [
            item for item in expression if isinstance(
                item, str) and item in logical_operators]:
        try:
            lhs, op, rhs = expression
            return operators[op](resolve(lhs, data), resolve(rhs, data))
        except KeyError as e:
            raise Exception(f"Unknown operator {e} in expression {expression}")
        except ValueError as e:
            raise
            raise Exception(f"Invalid expression: {expression}")

    # Nested expression with logical operators
    # We're recursing but the expressions won't be long to cause RecrusionError
    # TODO: Implement short circuit
    logical_op, operands = separate_logical_operator_and_operands(expression)
    return reduce(
        logical_operators[logical_op],
        map(partial(evaluate, data=data), operands)
    )

    return result
