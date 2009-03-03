from functools import partial
from string import digits as digit_chars

from picoparse import compose
from picoparse import one_of, many1, choice, tri, commit, optional
from picoparse.text import run_text_parser, lexeme, build_string, whitespace

# syntax tree classes
operators = ['-','+','*','/']
operator_functions = {
    '-': lambda l, r: l - r,
    '+': lambda l, r: l + r,
    '*': lambda l, r: l * r,
    '/': lambda l, r: l / r,
}
    
class ValueNode(object):
    def __init__(self, value):
        self.left = value
        self.precedence = 1000

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.left)
        
    def evaluate(self):
        return self.left


class ParentheticalNode(object):
    def __init__(self, child):
        self.child = child
        self.precedence = 1000
    
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.child)
    
    def evaluate(self):
        return self.child.evaluate()
        
        
class BinaryNode(object):
    def __init__(self, left, op):
        self.left = left
        self.op = op
        self.right = None
        self.precedence = operators.index(op)
    
    def merge(self, right):
        if self.precedence > right.precedence:
            self.right = right.left
            right.left = self
            return right
        else:
            self.right = right
            return self

    def __repr__(self):
        return "%s(%r, %r, %r)" % (self.__class__.__name__, self.left, self.op, self.right)
        
    def evaluate(self):
        return operator_functions[self.op](self.left.evaluate(), self.right.evaluate())


# parser
digits = partial(lexeme, compose(build_string, partial(many1, partial(one_of, digit_chars))))
operator = partial(lexeme, partial(one_of, operators))
    
@tri
def bin_op():
    left = term()
    op = operator()
    commit()
    right = expression()
    whitespace()
    
    n = BinaryNode(left, op)
    return n.merge(right) 
    
@tri
def parenthetical():
    whitespace()
    one_of('(')
    commit()
    whitespace()
    v = expression()
    whitespace()
    one_of(')')
    whitespace()
    return ParentheticalNode(v)

def int_value():
    return int(digits())

@tri
def float_value():
    whole_part = digits()
    one_of('.')
    commit()
    decimal_part = digits()
    return float('%s.%s' % (whole_part, decimal_part))

def value():
    is_negative = optional(partial(one_of, '-'), False)
    val = choice(float_value, int_value) * (-1 if is_negative else 1)
    return ValueNode(val)

term = partial(choice, parenthetical, partial(lexeme, value))
    
expression = partial(choice, bin_op, term)
    
run_calculator = partial(run_text_parser, expression)


print "calculator results"
def calc(exp):
    tree, _ = run_calculator(exp)
    print exp, '=', tree.evaluate()
    print tree
    print

calc('4')
calc('4 + 5')
calc('(4 + 5)')
print

calc('5 + 20 / 5')
calc('(5 + 20) / 5')
print
calc('5 + (4 * 5) / 5')

calc('0.5 * -2')
calc('0.25 * (-20 + -1 * 20)')