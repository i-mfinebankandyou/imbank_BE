from typing import List, Tuple

# 주변 문맥 제공
def make_context(lines: List[str], line_idx: int, window: int) -> Tuple[int,int,str]:
    """
    라인 주변 컨텍스트를 window 범위만큼 묶어서 반환
    """
    start = max(0, line_idx - window)
    end = min(len(lines), line_idx + window + 1)
    ctx = "\n".join(lines[start:end])
    return start, end-1, ctx