M = 1 << 31   # основание
N = 100       # число разрядов


def normalize(a):
    return a[:N]

def from_int(x: int):
    """Перевод числа x из int в массив длины N в M-ричной системе счисления"""
    neg = x < 0
    if neg:
        x = -x
    digits = []
    for _ in range(N):
        digits.append(x % M)
        x //= M
    if neg:
        digits = to_twos_complement(digits)

    # Проверяем переполнение по знакам:
    # если знак int числа и приведенного отличаются -> переполнение
    digits_sign = (digits[-1] >> 30) & 1  # старший бит в последнем разряде (M=2^31)
    x_sign = neg

    if digits_sign != x_sign:
        print("Переполнение при инициализации!")

    return digits


def to_int(a):
    """Перевод числа из записи для большой арифметики в int"""
    if is_negative(a):
        a = from_twos_complement(a)
        return -_to_int_abs(a)
    else:
        return _to_int_abs(a)


def _to_int_abs(a):
    """Перевод модуля числа из записи для большой арифметики в int"""
    val = 0
    for i in reversed(range(N)):
        val = val * M + a[i]
    return val


def is_negative(a):
    return a[-1] >= (M >> 1)


def to_twos_complement(a):
    """Преобразование в дополнительный код для отрицательных чисел (для перевода из int в массив)"""
    res = [(M - 1 - d) for d in a]
    carry = 1
    for i in range(N):
        tmp = res[i] + carry
        res[i] = tmp % M
        carry = tmp // M
    return res


def from_twos_complement(a):
    """Преобразование из дополнительный кода для отрицательных чисел (для перевода из массива в int)"""
    res = [(M - 1 - d) for d in a]
    carry = 1
    for i in range(N):
        tmp = res[i] + carry
        res[i] = tmp % M
        carry = tmp // M
    return res


def add(a, b):
    """Сложение больших чисел"""
    carry = 0
    res = []
    for i in range(N):
        s = a[i] + b[i] + carry
        res.append(s % M)
        carry = s // M

    res = normalize(res)

    # Проверяем переполнение по знакам:
    # если a и b одного знака, а результат другого → переполнение
    a_sign = (a[-1] >> 30) & 1   # старший бит в последнем разряде (M=2^31)
    b_sign = (b[-1] >> 30) & 1
    r_sign = (res[-1] >> 30) & 1

    if a_sign == b_sign and r_sign != a_sign:
        print("Переполнение при сложении!")

    return res


def sub(a, b):
    """Разность для больших чисел"""
    return add(a, to_twos_complement(b))


def compare_abs(a, b):
    """Сравнение модулей больших чисел"""
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
        print("Переполнение при умножении!")
    else:
        # Проверяем переполнение по знакам:
        # если a и b одного знака, а результат другого → переполнение
        a_sign = (a[-1] >> 30) & 1   # старший бит в последнем разряде (M=2^31)
        b_sign = (b[-1] >> 30) & 1
        r_sign = (res[N-1] >> 30) & 1

        if a_sign == b_sign and r_sign != a_sign:
            print("Переполнение при умножении!")

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
        print("Overflow4!")
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
    x = from_int(2**355)
    y = from_int(-2**126)
    print("x =", to_int(x))
    print("y =", to_int(y))

    print("x + y =", to_int(add(x, y)))
    print("x - y =", to_int(sub(x, y)))
    print("x * y =", to_int(mul(x, y)))
    print("x // y =", to_int(div(x, y)))
    print("y * (x // y) =", to_int(mul(y, div(x, y))))


