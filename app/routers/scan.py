from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(tags=["scan"])

MAX_MB = 25
ALLOWED_EXT = {".txt", ".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}

def _ext(name: str) -> str:
    name = (name or "").lower()
    dot = name.rfind(".")
    return name[dot:] if dot != -1 else ""

@router.post("/scan")
async def scan(file: UploadFile = File(...)):
    # 파일 읽기
    data = await file.read()

    # 크기 제한
    if len(data) > MAX_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large (>{MAX_MB}MB)")

    # 확장자 화이트리스트(느슨한 기본 검사)
    ext = _ext(file.filename)
    if ext and ext not in ALLOWED_EXT:
        raise HTTPException(status_code=415, detail=f"File extension not allowed: {ext}")

    # 아직은 분석 없이 메타 정보만 반환
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_kb": round(len(data) / 1024, 2),
        "accepted_ext": sorted(list(ALLOWED_EXT)),
        "message": "File received. Analysis not implemented yet."
    }