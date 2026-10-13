"""
EXPRESSION TREE GENERATOR AND EVALUATOR  (single file, Python 3.6+)
Paste into any online Python compiler and press RUN - no input or install needed.

Pipeline (4 modules):
   1. tokenize()    : text            -> tokens
   2. to_postfix()  : tokens          -> postfix (shunting-yard algorithm)
   3. build_tree()  : postfix         -> binary expression tree
   4. evaluate()    : tree            -> numeric result   (+ traversals / tree print)

Supports: + - * / ^  brackets ( )  decimals  and unary minus  e.g. -(2+3)*4
"""

OPS = {"+": 1, "-": 1, "*": 2, "/": 2, "u-": 3, "^": 4}   # operator precedence
RIGHT = {"^"}            # right-associative operators
UNARY = {"u-"}           # unary minus (internal name)
SHOW = {"u-": "neg"}     # how internal names are displayed


class Node:
    def __init__(self, value, left=None, right=None):
        self.value, self.left, self.right = value, left, right


# ---------------------------------------------------------------------
# MODULE 1 : TOKENIZER
# ---------------------------------------------------------------------
def tokenize(expr):
    tokens, num = [], ""
    for ch in expr + " ":                      # extra space flushes the last number
        if ch.isdigit() or ch == ".":
            num += ch
            continue
        if num:
            if num.count(".") > 1 or num == ".":
                raise ValueError("Bad number '%s'" % num)
            tokens.append(num)
            num = ""
        if ch == " ":
            continue
        if ch in "+-*/^()":
            prev = tokens[-1] if tokens else None
            if ch == "-" and (prev is None or prev == "(" or prev in OPS):
                tokens.append("u-")            # minus at start / after operator = unary
            else:
                tokens.append(ch)
        else:
            raise ValueError("Invalid character '%s'" % ch)
    return tokens


# ---------------------------------------------------------------------
# MODULE 2 : INFIX -> POSTFIX  (shunting-yard)
# ---------------------------------------------------------------------
def to_postfix(tokens):
    out, stack = [], []
    for t in tokens:
        if t == "(":
            stack.append(t)
        elif t == ")":
            while stack and stack[-1] != "(":
                out.append(stack.pop())
            if not stack:
                raise ValueError("Mismatched ')'")
            stack.pop()
        elif t in UNARY:
            stack.append(t)
        elif t in OPS:
            while (stack and stack[-1] != "(" and
                   (OPS[stack[-1]] > OPS[t] or
                    (OPS[stack[-1]] == OPS[t] and t not in RIGHT))):
                out.append(stack.pop())
            stack.append(t)
        else:
            out.append(t)                      # number
    while stack:
        if stack[-1] == "(":
            raise ValueError("Mismatched '('")
        out.append(stack.pop())
    return out


# ---------------------------------------------------------------------
# MODULE 3 : EXPRESSION TREE BUILDER
# ---------------------------------------------------------------------
def build_tree(postfix):
    stack = []
    for t in postfix:
        if t in UNARY:
            if not stack:
                raise ValueError("Missing operand for unary minus")
            stack.append(Node(t, stack.pop()))
        elif t in OPS:
            if len(stack) < 2:
                raise ValueError("Missing operand for '%s'" % t)
            right, left = stack.pop(), stack.pop()
            stack.append(Node(t, left, right))
        else:
            float(t)                           # validates the number
            stack.append(Node(t))
    if len(stack) != 1:
        raise ValueError("Invalid expression")
    return stack[0]


# ---------------------------------------------------------------------
# MODULE 4 : EVALUATOR + TRAVERSALS + TREE PRINTER
# ---------------------------------------------------------------------
def evaluate(n):
    if n.value in UNARY:
        return -evaluate(n.left)
    if n.value not in OPS:
        return float(n.value)                  # leaf = number
    a, b = evaluate(n.left), evaluate(n.right)
    if n.value == "+": return a + b
    if n.value == "-": return a - b
    if n.value == "*": return a * b
    if n.value == "/":
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        return a / b
    if a < 0 and b != int(b):
        raise ValueError("Negative number to a fractional power")
    return a ** b


def preorder(n):
    return [] if n is None else [n.value] + preorder(n.left) + preorder(n.right)


def postorder(n):
    return [] if n is None else postorder(n.left) + postorder(n.right) + [n.value]


def inorder(n):                                # fully bracketed infix
    if n.value in UNARY:
        return "(-" + inorder(n.left) + ")"
    if n.value not in OPS:
        return n.value
    return "(" + inorder(n.left) + " " + n.value + " " + inorder(n.right) + ")"


def height(n):
    return 0 if n is None else 1 + max(height(n.left), height(n.right))


def show_tree(n, level=0):
    """Tree turned 90 degrees: root at the left, right child above, left child below."""
    if n is None:
        return
    show_tree(n.right, level + 1)
    print("      " + "      " * level + SHOW.get(n.value, n.value))
    show_tree(n.left, level + 1)


def fmt(tokens):
    return " ".join(SHOW.get(t, t) for t in tokens)


def number(x):
    return "%.10g" % x


# ---------------------------------------------------------------------
# DRIVER
# ---------------------------------------------------------------------
def process(expr):
    print("Expression :", expr)
    try:
        tokens = tokenize(expr)
        postfix = to_postfix(tokens)
        root = build_tree(postfix)
        print("Tokens     :", fmt(tokens))
        print("Postfix    :", fmt(postfix))
        print("Prefix     :", fmt(preorder(root)))
        print("Infix      :", inorder(root))
        print("Tree height:", height(root))
        print("Tree (turned 90 degrees):")
        show_tree(root)
        print("RESULT     :", number(evaluate(root)))
    except (ValueError, ZeroDivisionError, OverflowError) as e:
        print("ERROR      :", e)
    print("-" * 56)


def self_test():
    """Checks the evaluator against Python's own arithmetic."""
    cases = ["(3 + 4) * 5 - 6 / 2", "2 + 3 * 4", "2 ^ 3 ^ 2", "-(2 + 3) * 4",
             "100 / 10 / 5", "10 - 4 - 3", "3.5 * 2 + 1", "2 * -3", "-2 ^ 2", "((7))"]
    for c in cases:
        got = evaluate(build_tree(to_postfix(tokenize(c))))
        want = eval(c.replace("^", "**"))
        assert abs(got - want) < 1e-9, (c, got, want)
    print("Self-test passed: %d expressions match Python's own result." % len(cases))


if __name__ == "__main__":
    for e in ["(3 + 4) * 5 - 6 / 2",
              "2 + 3 * 4",
              "2 ^ 3 ^ 2",
              "-(2 + 3) * 4",
              "3.5 * 2 + 1",
              "10 / (5 - 5)",        # error demo
              "(2 + 3",              # error demo
              "7 & 2"]:              # error demo
        process(e)
    self_test()

    # ---- optional: type your own expressions (needs a compiler that supports input) ----
    INTERACTIVE = False              # change to True to try your own expressions
    while INTERACTIVE:
        try:
            text = input("Enter expression (blank to quit): ")
        except EOFError:
            break
        if not text.strip():
            break
        process(text)
