def is_valid_cpf(cpf: str) -> bool:
    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * len(cpf):
        return False

    sum_first_digit = sum(int(cpf[i]) * (10 - i) for i in range(9))
    first_digit = 11 - (sum_first_digit % 11)
    first_digit = first_digit if first_digit < 10 else 0

    if first_digit != int(cpf[9]):
        return False

    sum_second_digit = sum(int(cpf[i]) * (11 - i) for i in range(10))
    second_digit = 11 - (sum_second_digit % 11)
    second_digit = second_digit if second_digit < 10 else 0

    if second_digit != int(cpf[10]):
        return False

    return True
