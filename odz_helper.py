# Takes A + (B - (D | (E & (...))))
import copy
from Parser import parse, test_parse
from Printer import print_root
from Printer import print_case
import Printer


def invert(s):
    res = ''
    for i in s:
        if i == '0':
            res += '1'
        else:
            res += '0'
    return res

def convert(x):
    res = bin(abs(x))[2:]

    while len(res) < 16:
        res = '0' + res

    if x < 0:
        res = invert(res)
        res = bin(int(res, 2) + 1)[2:]
    
    return res

def rev_convert(s):
    res = -2**15 * int(s[0])
    for i in range(1, 16):
        res += 2**(15 - i) * int(s[i])
    return res

def test_convert():
    for x in range(-2**15, 2**15):
        if(rev_convert(convert(x)) != x):
            print("ERROR AT ", x)
            print("CONVERT: ", convert(x))
            print("REV_CONVERT: ", rev_convert(convert(x)))
            return

def apply_case(res, root, a_range_min, a_range_max, b_range_min, b_range_max) -> None:
    case = copy.deepcopy(root)

    find_odz(case.lhs, a_range_min, a_range_max)

    if root.op == '-':
        case.rhs.with_minus = not(case.rhs.with_minus)
    
    vars = find_odz(case.rhs, b_range_min, b_range_max)
    for v in vars:
        tmp = copy.deepcopy(case)
        tmp.rhs = v
        res.append(tmp)

def to_mask(s):
    while len(s) < 16:
        s += '2'
    return s

def get_logic_masks(range_min, range_max) -> list:
    res = []

    if range_min * range_max < 0:
        res = get_logic_masks(range_min, -1)
        res.extend(get_logic_masks(0, range_max))
        return res

    lower = convert(range_min - 1)
    mn = convert(range_min)
    mx = convert(range_max)
    upper = convert(range_max + 1)

    common = ''
    
    i = 0
    while i < 16 and mn[i] == mx[i]:
        common += mn[i]
        i += 1

    # Case 0. Full match
    if not lower.startswith(common) and not upper.startswith(common):
        return [to_mask(common)]


    # Case 1. Getting lower
    lower_mask = common + '0'
    l = 1

    if range_min > -2**15:
        while lower.startswith(lower_mask):
            if l > 1 and lower_mask[l + i - 1] == '0':
                res.append(to_mask(lower_mask[:-1] + '1'))

            lower_mask += mn[l + i]
            l += 1

    res.append(to_mask(lower_mask))
        
    # Case 2. Getting upper
    upper_mask = common + '1'
    u = 1

    if range_max < 2**15 - 1:    
        while upper.startswith(upper_mask):
            if u > 1 and upper_mask[u + i - 1] == '1':
                res.append(to_mask(upper_mask[:-1] + '0'))

            upper_mask += mx[u + i]
            u += 1

    res.append(to_mask(upper_mask))

    return res

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

def to_args(mask, op, cur_lhs='', cur_rhs='') -> list:
    res = []
    if len(cur_lhs) == 16:
        return [(cur_lhs, cur_rhs)]

    if mask[len(cur_lhs)] == '1':
        if op == '&':
            res.extend(to_args(mask, op, cur_lhs + '1', cur_rhs + '1'))
        
        if op == '|':
            res.extend(to_args(mask, op, cur_lhs + '0', cur_rhs + '1'))
            res.extend(to_args(mask, op, cur_lhs + '1', cur_rhs + '0'))
            res.extend(to_args(mask, op, cur_lhs + '1', cur_rhs + '1'))
    
    if mask[len(cur_lhs)] == '0':
        if op == '&':
            res.extend(to_args(mask, op, cur_lhs + '1', cur_rhs + '0'))
            res.extend(to_args(mask, op, cur_lhs + '0', cur_rhs + '1'))
            res.extend(to_args(mask, op, cur_lhs + '0', cur_rhs + '0'))
        
        if op == '|':
            res.extend(to_args(mask, op, cur_lhs + '0', cur_rhs + '0'))

    if mask[len(cur_lhs)] == '2':
        res.extend(to_args(mask, op, cur_lhs + '2', cur_rhs + '2'))

    return res

def test_to_args():
    while True:
        args = to_args(input().replace(' ', ''), input())
        for arg in args:
            print(*arg)

def to_range(arg):
    mn = -2**15 * int(arg[0])
    mx = -2**15 * int(arg[0])
    for i in range(1, 16):
        if arg[i] != '2':
            mn += 2**(15 - i) * int(arg[i])
            mx += 2**(15 - i) * int(arg[i])
        else:
            mn += 0
            mx += 2**(15 - i)
    return mn, mx    

def test_to_range():
    while True:
        print(to_range(input().replace(' ', '')))

def find_odz(root, range_min=-2**15, range_max=2**15-1):
    res = []
    
    if root.with_minus:
        range_min, range_max = -range_max, -range_min

    if root.op is None:
        root.min = range_min
        root.max = range_max
        return [root]
    
    if root.op in ('+', '-'):
        # Case 1
        apply_case(res, root, range_min // 2, range_max // 2, range_min // 2, range_max // 2)
        # Case 2
        apply_case(res, root, range_min, (range_min + range_max) // 2, 0, (range_max - range_min) // 2)
        # Case 3
        apply_case(res, root, 0, (range_max - range_min) // 2, range_min, (range_min + range_max) // 2)

    
    if root.op in ('&', '|'):
        # get possible results masks
        masks = get_logic_masks(range_min, range_max)
        print(f"logic mask for [{range_min};{range_max}] is {masks}")

        # Convert mask to possible args masks
        arg_masks = []
        for mask in masks:
            arg_masks.extend(to_args(mask, root.op))
        
        for args in arg_masks:
            l_range = to_range(args[0])
            r_range = to_range(args[1])

            apply_case(res, root, l_range[0], l_range[1], r_range[0], r_range[1])

    return res

def main():
    expr = parse(input())
    
    cases = find_odz(expr)
    for c in cases:
        Printer.clear_free_name()
        print_root(c)
        print()


        Printer.clear_free_name()
        print_case(c)
        print()


def test_odz():
    expr = parse(input())

    cases = find_odz(expr)


if __name__ == '__main__':
    test_get_masks()
    test_convert()
    main()
