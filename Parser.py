from Printer import print_root

class Node:
    def __init__(self):
        self.lhs = None # Node expected
        self.rhs = None # Node expected

        self.min = -2**15
        self.max = 2**15 - 1

        self.with_minus = False

        self.op = None


def parse(s) -> Node:
    node = Node()
    s = s.lstrip()

    if s[0] == '(':
        s = s[1:]


    lhs = Node()
    node.lhs = lhs
    
    if s[0] == '-':
        lhs.with_minus = True
        s = s[1:]

    if s[0].isalpha():
        s = s[1:]

    s = s.lstrip()

    if s[0] in ('+', '-', '&', '|'):
        node.op = s[0]
        s = s[1:]

    s = s.lstrip()

    if s[0] == '(':
        node.rhs = parse(s)
    else:
        node.rhs = Node()

    if s[0] == '-':
        node.rhs.with_minus = True

    if node.op == '-':
        node.op = '+'
        node.rhs.with_minus = not(node.rhs.with_minus)

    return node   

def test_parse(s = None) -> None:
    global FREE_NAME_CNT
    FREE_NAME_CNT = 0
    
    if s is None:
        s = input()
    
    print_root(parse(s))
    print() 
