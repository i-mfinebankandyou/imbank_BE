import pytest
from app.modules.scanner.scan import scan_text

SAMPLE = """안녕하세요
메일은 test@example.com 입니다.
전화는 010-1234-5678 로 주세요
의심카드 4111 1111 1111 1111 도 적어둘게요
주민등록 950101-1234567 은 예시입니다
끝
"""

def test_engine_basic_counts():
    res = scan_text(SAMPLE, context_window=0)
    counts = res["counts"]
    # 최소 기대값: 이메일 1, 휴대폰 1
    assert counts["email"] >= 1
    assert counts["phone_kr"] >= 1
    # 카드/주민번호는 luhn/체크섬 통과 여부에 따라 0 또는 1
    assert isinstance(counts["credit_card"], int)
    assert isinstance(counts["rrn"], int)

def test_engine_findings_structure():
    res = scan_text(SAMPLE, context_window=1)
    f0 = res["findings"][0]
    # 키 유효성
    for key in ("type","value","line","col","context_lines","context"):
        assert key in f0
    # 1-based line/col
    assert f0["line"] >= 1
    assert f0["col"] >= 1
    # context_window>0 이면 context 포함
    assert f0["context"] is not None

def test_engine_context_window_zero():
    res = scan_text(SAMPLE, context_window=0)
    for f in res["findings"]:
        assert f["context"] is None

def test_engine_large_text_performance():
    # 성능 연기: 대략 1e5 글자에서 예외 없이 동작만 확인
    big = ("a\n"*50000) + "email me a@b.co\n" + ("z\n"*50000)
    res = scan_text(big, context_window=0)
    assert res["counts"]["email"] >= 1