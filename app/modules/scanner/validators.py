def luhn_ok(digits: str) -> bool:
    s = [int(c) for c in digits if c.isdigit()]
    if len(s) < 13:  # 너무 짧으면 카드 아님
        return False
    checksum = 0
    parity = (len(s) - 2) % 2
    for i, n in enumerate(s[:-1]):
        d = n * 2 if i % 2 == parity else n
        if d > 9:
            d -= 9
        checksum += d
    return (checksum + s[-1]) % 10 == 0

def rrn_checksum_ok(rrn: str) -> bool:
    # 형식: YYMMDD-ABCDEFG (13자리). 간단 가중치 검사
    nums = [int(c) for c in rrn if c.isdigit()]
    if len(nums) != 13:
        return False
    weights = [2,3,4,5,6,7,8,9,2,3,4,5]
    total = sum(n*w for n, w in zip(nums[:12], weights))
    check = (11 - (total % 11)) % 10
    return check == nums[12]