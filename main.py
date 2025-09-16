M = 1 << 31   # основание
N = 100       # число разрядов


def normalize(a):
    return a[:N]

def from_int(x: int):
    neg = x < 0
    if neg:
        x = -x
    digits = []
    for _ in range(N):
        digits.append(x % M)
        x //= M
    if x > 0:
        print("Overflow!")
    if neg:
        digits = to_twos_complement(digits)
    return digits


def to_int(a):
    if is_negative(a):
        a = from_twos_complement(a)
        return -_to_int_abs(a)
    else:
        return _to_int_abs(a)


def _to_int_abs(a):
    val = 0
    for i in reversed(range(N)):
        val = val * M + a[i]
    return val


def is_negative(a):
    return a[-1] >= (M >> 1)


def to_twos_complement(a):
    res = [(M - 1 - d) for d in a]
    carry = 1
    for i in range(N):
        tmp = res[i] + carry
        res[i] = tmp % M
        carry = tmp // M
    return res


def from_twos_complement(a):
    res = [(M - 1 - d) for d in a]
    carry = 1
    for i in range(N):
        tmp = res[i] + carry
        res[i] = tmp % M
        carry = tmp // M
    return res


def add(a, b):
    carry = 0
    res = []
    for i in range(N):
        s = a[i] + b[i] + carry
        res.append(s % M)
        carry = s // M
    if carry:
        print("Overflow!")
    return normalize(res)


def sub(a, b):
    return add(a, to_twos_complement(b))


def compare_abs(a, b):
    for i in reversed(range(N)):
        if a[i] != b[i]:
            return 1 if a[i] > b[i] else -1
    return 0


def mul(a, b):
    """Полное умножение массивов"""
    sign = is_negative(a) ^ is_negative(b)

    if is_negative(a):
        a = from_twos_complement(a)
    if is_negative(b):
        b = from_twos_complement(b)

    res = [0] * (2 * N)
    for i in range(N):
        carry = 0
        for j in range(N):
            if i + j >= 2 * N:
                break
            tmp = res[i + j] + a[i] * b[j] + carry
            res[i + j] = tmp % M
            carry = tmp // M
        if i + N < 2 * N:
            res[i + N] += carry

    if any(res[N:]):
        print("Overflow!")

    res = res[:N]
    if sign:
        res = to_twos_complement(res)
    return res


def shift_left(a, k):
    """Сдвиг влево на k разрядов"""
    if k >= N:
        return [0] * N
    return [0]*k + a[:-k]


def mul_digit(a, d):
    """Умножение на одну цифру d < M"""
    res = [0] * N
    carry = 0
    for i in range(N):
        tmp = a[i] * d + carry
        res[i] = tmp % M
        carry = tmp // M
    if carry:
        print("Overflow!")
    return res


def div(a, b):
    """деление (a // b)"""
    A_sign = is_negative(a)
    B_sign = is_negative(b)
    sign = A_sign ^ B_sign

    if A_sign:
        a = from_twos_complement(a)
    if B_sign:
        b = from_twos_complement(b)

    if all(x == 0 for x in b):
        print("Division by zero!")
        return [0] * N

    q = [0] * N
    r = [0] * N  # остаток

    for i in reversed(range(N)):
        # сдвигаем остаток и добавляем текущую цифру
        r = shift_left(r, 1)
        r[0] = a[i]

        # подбираем максимально возможную цифру q_digit (бинпоиск)
        q_digit = 0
        lo, hi = 0, M - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            candidate = mul_digit(b, mid)
            if compare_abs(candidate, r) <= 0:
                q_digit = mid
                lo = mid + 1
            else:
                hi = mid - 1

        q[i] = q_digit
        # r = r - b * q_digit
        r = sub(r, mul_digit(b, q_digit))

    q = normalize(q)
    if sign:
        q = to_twos_complement(q)
    return q


if __name__ == "__main__":
    x = from_int(12345678901234567890)
    y = from_int(-987654321)

    print("x =", to_int(x))
    print("y =", to_int(y))

    print("x + y =", to_int(add(x, y)))
    print("x - y =", to_int(sub(x, y)))
    print("x * y =", to_int(mul(x, y)))
    print("x // y =", to_int(div(x, y)))
