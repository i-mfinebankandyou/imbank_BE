import io
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

# ✅ httpx 0.28+ 스타일: lifespan 인자 제거
transport = ASGITransport(app=app)

@pytest.mark.asyncio
async def test_scan_txt_ok():
    sample = "이메일 test@example.com 과 010-1234-5678"
    f = io.BytesIO(sample.encode("utf-8"))
    files = {"file": ("sample.txt", f, "text/plain")}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/scan?context_window=1", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["filename"] == "sample.txt"
    assert "detected_counts" in body
    assert body["detected_counts"]["email"] >= 1

@pytest.mark.asyncio
async def test_reject_large_file():
    big = b"x" * (26 * 1024 * 1024)  # 26MB (>25MB)
    f = io.BytesIO(big)
    files = {"file": ("big.txt", f, "text/plain")}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/scan", files=files)
    assert r.status_code == 413

@pytest.mark.asyncio
async def test_reject_extension():
    f = io.BytesIO(b"hello")
    files = {"file": ("evil.exe", f, "application/octet-stream")}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/scan", files=files)
    assert r.status_code == 415

@pytest.mark.asyncio
async def test_txt_without_extension_but_text_content_type_is_ok():
    f = io.BytesIO(b"phone 010-1234-5678")
    files = {"file": ("noext", f, "text/plain")}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/scan", files=files)
    assert r.status_code == 200
    assert "detected_counts" in r.json()

@pytest.mark.asyncio
async def test_context_window_bounds():
    f = io.BytesIO(b"email a@b.co\nline2\nline3")
    files = {"file": ("a.txt", f, "text/plain")}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/scan?context_window=10", files=files)
    assert r.status_code == 200  # 라우터에서 le=10 제한 있음