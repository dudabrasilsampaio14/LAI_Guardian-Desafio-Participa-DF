from lai_guardian.core.validators import validate_cpf_mod11

def test_cpf_valid():
    assert validate_cpf_mod11("529.982.247-25") is True

def test_cpf_invalid():
    assert validate_cpf_mod11("111.111.111-11") is False
