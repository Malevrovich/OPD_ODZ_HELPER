import string
import sys

FREE_NAME_CNT = 0
def clear_free_name():
    global FREE_NAME_CNT
    FREE_NAME_CNT = 0

def get_free_name():
    global FREE_NAME_CNT
    FREE_NAME_CNT += 1
    return string.ascii_uppercase[FREE_NAME_CNT - 1]

def print_root(node, file=sys.stdout) -> None:
    if node.lhs is None:
        if node.with_minus:
            print('-', end='', file=file)
        print(get_free_name(), end = '', file=file)
        return

    if node.lhs is not None:
        print_root(node.lhs, file=file)

    if node.op is not None:
        print(' ', end='', file=file)
        print(node.op, end=' ', file=file)

    if node.rhs is not None:
        if node.rhs.lhs is not None:
            print('(', end='', file=file)
        print_root(node.rhs, file=file)
    if node.rhs.lhs is not None:
            print(')', end='',file=file)

def print_case(node, file=sys.stdout) -> None:
    if node.op is not None:
        print_case(node.lhs, file=file)
        print_case(node.rhs, file=file)
        return
    
    print(f"{get_free_name()}: [{node.min};{node.max}]", file=file)
    