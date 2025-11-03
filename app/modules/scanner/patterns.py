# scanner/patterns.py
import re

PATTERNS = {
    "email": re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b"),
    # 대한민국 휴대폰/전화 (간단 버전)
    "phone_kr": re.compile(r"(?:\+82[-\s]?)?(?:0)?(?:1[0-9]|2|[3-6][1-5])[-\s]?\d{3,4}[-\s]?\d{4}\b"),
    "ipv4": re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"),
    "url": re.compile(r"\bhttps?://[^\s,<>\"']+\b"),
    # 주민등록번호(형식) — 체크섬은 validators.py에서
    "rrn": re.compile(r"\b(\d{6})[- ]?(\d{7})\b"),
    # 신용카드 숫자 (13~19 자리, 구분자 포함 가능) — Luhn 체크는 validators.py
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
}