import re

def only_digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")

def validate_cpf_mod11(cpf: str) -> bool:
    nums = [int(d) for d in only_digits(cpf)]
    if len(nums) != 11:
        return False
    if len(set(nums)) == 1:
        return False

    def calc(slice_, start_weight):
        s = sum(v * (start_weight - i) for i, v in enumerate(slice_))
        d = (s * 10) % 11
        return 0 if d == 10 else d

    d1 = calc(nums[:9], 10)
    if d1 != nums[9]:
        return False
    d2 = calc(nums[:10], 11)
    return d2 == nums[10]
