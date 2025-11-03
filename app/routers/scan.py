# app/routers/scan.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.modules.scanner.scan import scan_text  # ✅ 스캐너 로직 연결

router = APIRouter(tags=["scan"])

MAX_MB = 25
ALLOWED_EXT = {".txt", ".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}

def _ext(name: str) -> str:
    name = (name or "").lower()
    dot = name.rfind(".")
    return name[dot:] if dot != -1 else ""

@router.post("/scan")
async def scan(
    file: UploadFile = File(...),
    context_window: int = Query(0, ge=0, le=10, description="문맥으로 포함할 위/아래 라인 수"),
):
    # 1) 파일 읽기
    data = await file.read()

    # 2) 크기 제한
    if len(data) > MAX_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large (>{MAX_MB}MB)")

    # 3) 확장자 화이트리스트(느슨한 기본 검사)
    ext = _ext(file.filename)
    if ext and ext not in ALLOWED_EXT:
        raise HTTPException(status_code=415, detail=f"File extension not allowed: {ext}")

    # 4) 타입별 처리 (.txt만 분석, 나머지는 아직 미구현)
    if ext == ".txt" or (not ext and (file.content_type or "").startswith("text/")):
        # 4-1) 텍스트 디코딩 (UTF-8 우선, 실패 시 무시)
        text = data.decode("utf-8", errors="ignore")

        # 4-2) 정규식 기반 PII 스캔
        result = scan_text(text, context_window=context_window)

        # 4-3) 응답
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size_kb": round(len(data) / 1024, 2),
            "detected_counts": result["counts"],
            "findings": result["findings"],  # 각 항목: type/value/line/col/context_lines/context
            "message": "Text scanned successfully.",
        }

    # 5) 미지원 타입(차후 OCR/PDF 파이프라인 연결 예정)
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_kb": round(len(data) / 1024, 2),
        "accepted_ext": sorted(list(ALLOWED_EXT)),
        "message": f"File received but scanning for {ext or file.content_type} not implemented yet.",
    }