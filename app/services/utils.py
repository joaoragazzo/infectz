from app.exceptions.emptyCartException import EmptyCartException
from app.exceptions.invalidCPF import InvalidCPF
from app.exceptions.invalidFederalUnitException import InvalidFederalUnitException
from app.exceptions.invalidZipCode import InvalidZipCode

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


def is_valid_data(cart_items: list, cpf: str, federal_unit: str, zip_code: str) -> bool:
    if cart_items is None or len(cart_items) == 0:
        raise EmptyCartException("O seu carrinho está vazio. Impossível prosseguir.")

    if cpf is None or not is_valid_cpf(cpf):
        raise InvalidCPF("O CPF fornecido é inválido. Impossível de prosseguir.")
    
    if federal_unit not in ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR",
                     "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]:
        raise InvalidFederalUnitException("O estado fornecido é inválido. Impossível de prosseguir.")
    
    if zip_code is None or len(zip_code) == 0 or not zip_code.isdigit():
        raise InvalidZipCode('O CEP fornecido é inválido. Impossível de prosseguir.')
