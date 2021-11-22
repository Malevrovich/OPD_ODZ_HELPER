from odz_helper import rev_convert, convert, get_logic_masks, find_odz
from random import randint
from Parser import parse
from Printer import print_case, print_root
import copy

def test_convert():
    for x in range(-2**15, 2**15):
        if(rev_convert(convert(x)) != x):
            print("ERROR AT ", x)
            print("CONVERT: ", convert(x))
            print("REV_CONVERT: ", rev_convert(convert(x)))
            return

def test_mask(expected, ans):
    if sorted(expected) != sorted(ans):
        print("ERROR TEST GET MASKS")
        print(ans, ", but expected ", expected, sep='')
        exit(-1)

def test_get_masks():
    class first_test:
        expected = ['1111111111101222', '1111111111100112', '1111111111100101', '1111111111110022', '1111111111110102']
        test_mask(expected, get_logic_masks(-27, -11))
    
    class second_test:
        expected = ['1111111111102222', '1111111111110222']
        test_mask(expected, get_logic_masks(-32, -9))

    class third_test:
        expected = ['1111111111110111']
        test_mask(expected, get_logic_masks(-9, -9))
    
    class fourth_test:
        expected = ['1111111111111222']
        test_mask(expected, get_logic_masks(-8, -1))
    
    class fifth_test:
        expected = ['1111111111111222', '0000000000000222', '0000000000001022', '0000000000001102']
        test_mask(expected, get_logic_masks(-8, 13))

    class sixth_test:
        expected = ['1000000000000022', '1000000000000102']
        test_mask(expected, get_logic_masks(-2**15, -32763))

    class seventh_test:
        expected = ['0111111111011122', '0111111111011012', '0111111111122222']
        test_mask(expected, get_logic_masks(32730, 2**15 - 1))

    class eight_test:
        expected = ['1012222222222222', '1001222222222222', '1000122222222222', '1000012222222222', '1000001222222222', '1000000122222222', '1000000012222222', '1000000001222222', '1000000000122222', '1000000000012222', '1000000000001222', '1000000000000122', '1000000000000012', '1000000000000001', '1122222222222222', '0000000000000000']
        test_mask(expected, get_logic_masks(-32767, 0))

    # while True:
    #     mn, mx = map(int, input().split(" "))
    #     print(get_logic_masks(mn, mx))

def calc(expr, args, deep=0):
    ans = None

    sign = 1
    if expr.lhs is not None and expr.lhs.with_minus:
        sign = -1

    if expr.op == '+':
        ans = sign*args[deep] + calc(expr.rhs, args, deep+1)
    elif expr.op == '-':
        ans = sign*args[deep] - calc(expr.rhs, args, deep+1)
    elif expr.op == '&':
        ans = sign*args[deep] & calc(expr.rhs, args, deep+1)
    elif expr.op == '|':
        ans = sign*args[deep] | calc(expr.rhs, args, deep+1)
    else:
        ans = args[deep]
    
    if expr.with_minus:
        ans *= -1

    if ans < -2**15 or ans > 2**15:
        print("OVERFLOW AT CALC")
        print("EXPR: ", end='')
        print_root(expr)
        print()
        print(f"WHERE LHS RANGE: [{expr.lhs.min}:{expr.lhs.max}]")
        print_case(expr)
        print(f"RANGE: [{expr.min}:{expr.max}]")
        print("RES: ", ans)
        exit(-1)
    
    return ans

def test_calc():
    while True:
        print(calc(parse(input()), list(map(int, input().split(' ')))))

def test_case(root, case, args=None):
    if args is None:
        args = []

    args.append(0)
    
    mn = None
    mx = None
    if case.op is None:
        mn = case.min
        mx = case.max
    else:
        mn = case.lhs.min
        mx = case.lhs.max

    for i in (mn, randint(mn, mx), mx):
        args[-1] = i
        if case.rhs is not None:
            test_case(root, case.rhs, copy.deepcopy(args))
        else:
            calc(root, args)
            # print(f"args: {args}\tres={calc(root, args)}")

def test_odz(expr=None, cases=None):
    expr = parse(input()) if expr is None else expr
    cases = find_odz(expr) if cases is None else cases
    for case in cases:
        test_case(case, case)

def test_find_odz():
    class add_test:
        test_odz(parse("A + B"))
    class sub_test:
        test_odz(parse("A - B"))
    class and_test:
        test_odz(parse("A & B"))
    class or_test:
        test_odz(parse("A | B"))
    class neg_test:
        test_odz(parse("-A + B"))
        test_odz(parse("A - -B"))
        test_odz(parse("-A + -B"))
        test_odz(parse("-A - -B"))
    class my_func_test:
        test_odz(parse("A & (B + C)"))
        test_odz(parse("A + (B | C)"))
        test_odz(parse("A | (-B - C)"))
        test_odz(parse("-A - (B & C)"))
        test_odz(parse("A & (-B - C)"))
        test_odz(parse("-A - (B & C)"))
    class big_test:
        test_odz(parse("A + (B + C)"))
        test_odz(parse("A + (B - C)"))
        test_odz(parse("A - (B + C)"))
        test_odz(parse("A - (B - C)"))
        test_odz(parse("A + (B & C)"))
        test_odz(parse("A | (B + C)"))
