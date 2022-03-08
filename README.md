# xpress - Build expressions, serialize them as JSON, and evaluate them in Python

xpress is inspired by JsonLogic but aims to terser at the cost of reduced features. It ONLY supports logical operators.

## Virtues

xpress follows similar principles as JsonLogic

1. Terse(er).
2. Readable. As close to infix expressions as possible
3. Consistent. 3-tuple expressions `["operand", "operator", "operand"]` joined by `AND` and/or `OR` 
4. Secure. We never `eval()`
5. Flexible. Easy to add new operators, easy to build complex structures

## Limitations

1. Only logical operators are supported.
2. Unary operators are not supported.

## Examples

### Simple

```python
xpress.evaluate([1, "==", 1])
# True
```

This is a simple rule, equivalent to 1 == 1. A few things about the format:

1. The operator is always at the 2nd position(index: 1) in the expression 3-tuple. There is only one operator per expression.
2. The operands are either a literal, a variable or an array of literals and/or variables.
3. Each value can be a string, number, boolean, array (non-associative), or null

### Compound

Here we’re beginning to nest rules.

```python
xpress.evaluate([[3, ">", 1], "and", [1, "<", 3]])
# True
```

In an infix language (like Python) this could be written as:

```python
( (3 > 1) and (1 < 3) )
```

### Data-Driven

Obviously these rules aren’t very interesting if they can only take static literal data. Typically xpress will be called with a rule object and a data object. You can use the var operator to get attributes of the data object. Here’s a complex rule that mixes literals and data. The pie isn’t ready to eat unless it’s cooler than 110 degrees, and filled with apples.

```python
rules = [["var:temp", "<", 110], "and", ["var:pie.filling", "==", "apple"]]
data = { "temp" : 100, "pie" : { "filling" : "apple" } };
xpress.evaluate(rules, data);
# True
```

### Always and Never

Sometimes the rule you want to process is “Always” or “Never.” If the first parameter passed to jsonLogic is a non-object, non-associative-array, it is returned immediately.

```python
# Always
xpress.evaluate(True, data_will_be_ignored)
# True
```

```python
# Never
xpress.evaluate(False, i_wasnt_even_supposed_to_be_here)
# False
```

## Supported Operations

### Accessing Data

- `var`

### Logical and Boolean Operators

- `==`
- `===`
- `!=`
- `!==`
- `or`
- `and`

### Numeric Operators

- `>`, `>=`, `<` and `<=`

### Array Operators
- `in`

### String Operators
- `in`

