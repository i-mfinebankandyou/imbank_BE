from typing import Dict, Any, List
from .patterns import PATTERNS
from .validators import luhn_ok, rrn_checksum_ok
from .utils import make_context
import re

def _post_filter(kind: str, raw: str) -> bool:
    if kind == "credit_card":
        return luhn_ok(raw)
    if kind == "rrn":
        return rrn_checksum_ok(raw)
    return True

def scan_text(text: str, context_window:int = 0) -> Dict[str, Any]:
    """
    텍스트 전체를 스캔하여 findings와 counts를 반환.
    context_window: 주변 라인 포함 범위 (기본 0)
    """
    lines = text.splitlines()
    findings: List[Dict[str, Any]] = []
    counts = {k: 0 for k in PATTERNS.keys()}

    for tname, pattern in PATTERNS.items():
        for m in pattern.finditer(text):
            start = m.start()
            before = text[:start]
            line_idx = before.count("\n")
            col_idx = start - (before.rfind("\n") + 1 if "\n" in before else 0)
            raw = m.group(0)

            # 후처리(체크섬 등) 실패시 스킵
            if not _post_filter(tname, raw):
                continue

            ctx_first, ctx_last, ctx = make_context(lines, line_idx, context_window)
            findings.append({
                "type": tname,
                "value": raw,
                "line": line_idx + 1,
                "col": col_idx + 1,
                "context_lines": [ctx_first + 1, ctx_last + 1],
                "context": ctx if context_window > 0 else None,
            })
            counts[tname] += 1

    return {"findings": findings, "counts": counts}