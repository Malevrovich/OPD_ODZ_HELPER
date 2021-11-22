# Takes A + (B - (D | (E & (...))))
import copy
from Parser import parse
from Printer import print_root, print_case, clear_free_name
import Tests

# FUNCS FOR LOGIC OPERATIONS 
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

def to_mask(s):
    while len(s) < 16:
        s += '2'
    return s

def get_logic_masks(range_min, range_max) -> list:
    range_max = min(range_max, 2**15 - 1)
    range_min = max(range_min, -2**15)
    res = []

    if range_min == -2**15 and range_max == 2**15 - 1:
        return ['2' * 16]

    if range_min * range_max < 0:
        res = get_logic_masks(range_min, -1)
        res.extend(get_logic_masks(0, range_max))
        return res

    if range_min != 0 and range_max == 0:
        res = get_logic_masks(range_min, -1)
        res.extend(get_logic_masks(0, 0))
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
    if (not lower.startswith(common) or range_min == -2**15) and (not upper.startswith(common) or range_max == 2**15 - 1):
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

def to_args(mask, op, cur_lhs='', cur_rhs='') -> list:
    res = []
    if len(cur_lhs) == 16:
        return [(cur_lhs, cur_rhs)]

    if mask[len(cur_lhs)] == '1':
        if op == '&':
            res.extend(to_args(mask, op, cur_lhs + '1', cur_rhs + '1'))
        
        if op == '|':
            # Uncomment for more accurate result (It will slow program)
            # res.extend(to_args(mask, op, cur_lhs + '0', cur_rhs + '1'))
            # res.extend(to_args(mask, op, cur_lhs + '1', cur_rhs + '0'))
            res.extend(to_args(mask, op, cur_lhs + '1', cur_rhs + '1'))
    
    if mask[len(cur_lhs)] == '0':
        if op == '&':
            # Uncomment for more accurate result (It will slow program)
            # res.extend(to_args(mask, op, cur_lhs + '1', cur_rhs + '0'))
            # res.extend(to_args(mask, op, cur_lhs + '0', cur_rhs + '1'))
            res.extend(to_args(mask, op, cur_lhs + '0', cur_rhs + '0'))
        
        if op == '|':
            res.extend(to_args(mask, op, cur_lhs + '0', cur_rhs + '0'))

    if mask[len(cur_lhs)] == '2':
        res.extend(to_args(mask, op, cur_lhs + '2', cur_rhs + '2'))

    return res

def to_range(arg):
    if arg[0] == '2':
        return -2**15, 2**15 - 1

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


# FUNCS TO FIND ODZ:
def apply_case(res, root, a_range_min, a_range_max, b_range_min, b_range_max, accurance) -> None:
    case = copy.deepcopy(root)

    find_odz(case.lhs, a_range_min, a_range_max, accurance)
    
    vars = find_odz(case.rhs, b_range_min, b_range_max, accurance)
    for v in vars:
        tmp = copy.deepcopy(case)
        tmp.rhs = v
        res.append(tmp)

def find_odz(root, range_min=-2**15, range_max=2**15-1, accurance=2):
    res = []
    
    if root.with_minus:
        range_min, range_max = -range_max, -range_min

    if root.op is None:
        root.min = range_min
        root.max = range_max
        return [root]
    
    if root.op == '+':
        # Case 1
        apply_case(res, root, range_min // 2, range_max // 2, range_min // 2, range_max // 2, accurance)
        # Case 2
        apply_case(res, root, range_min, (range_min + range_max) // 2, 0, (range_max - range_min) // 2, accurance)
        # Case 3
        apply_case(res, root, 0, (range_max - range_min) // 2, range_min, (range_min + range_max) // 2, accurance)

    
    if root.op in ('&', '|'):
        # get possible results masks
        masks = get_logic_masks(range_min, range_max)

        # Convert mask to possible args masks
        arg_masks = []
        for mask in masks:
            if mask.endswith('2' * accurance):
                arg_masks.extend(to_args(mask, root.op))
        
        for args in arg_masks:
            l_range = to_range(args[0])
            r_range = to_range(args[1])

            apply_case(res, root, l_range[0], l_range[1], r_range[0], r_range[1], accurance)

    return res

def main():
    out = open("odz.txt", 'w+')

    expr = parse(input())
    
    cases = find_odz(expr,accurance=8)
    for c in cases:
        clear_free_name()
        print_root(c, file=out)
        print('', file=out)


        clear_free_name()
        print_case(c, file=out)
        print('', file=out)
    print("testing cur odz...")
    Tests.test_odz(expr, cases)
    print("odz is correct")

if __name__ == '__main__':
    # MY FUNC: H & (L + (D | (-G - (B & (F + (C & (-A - (E & K)...)
    Tests.test_get_masks()
    print("Get mask tests success")
    Tests.test_convert()
    print("Convert tests success")
    # test_calc()
    # Tests.test_find_odz()
    print("Find odz tests success")
    main()