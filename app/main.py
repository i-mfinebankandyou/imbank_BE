from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.scan import router as scan_router

app = FastAPI(title="PII Guardian API", version="0.1.0")

# (선택) 프론트 로컬 테스트용 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서버가 작동중인지 확인
@app.get("/health")
def health():
    return {"status": "ok"}


# 여기서 엔드포인트 묶음 등록
app.include_router(scan_router, prefix="/api")