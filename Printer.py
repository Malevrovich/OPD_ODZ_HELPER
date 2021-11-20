import string
from typing import FrozenSet

FREE_NAME_CNT = 0
def clear_free_name():
    global FREE_NAME_CNT
    FREE_NAME_CNT = 0

def get_free_name():
    global FREE_NAME_CNT
    FREE_NAME_CNT += 1
    return string.ascii_uppercase[FREE_NAME_CNT - 1]

def print_root(node) -> None:
    if node.lhs is None:
        if node.with_minus:
            print('-', end='')
        print(get_free_name(), end = '')
        return

    if node.lhs is not None:
        print_root(node.lhs)

    if node.op is not None:
        print(' ', end='')
        print(node.op, end=' ')

    if node.rhs is not None:
        if node.rhs.lhs is not None:
            print('(', end='')
        print_root(node.rhs)
    if node.rhs.lhs is not None:
            print(')', end='')

def print_case(node) -> None:
    if node.op is not None:
        print_case(node.lhs)
        print_case(node.rhs)
        return
    
    print(f"{get_free_name()}: [{node.min};{node.max}]")
    