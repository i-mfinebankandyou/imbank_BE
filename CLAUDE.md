# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

PII Guardian API - 업로드된 파일에서 개인식별정보(PII)를 탐지하는 FastAPI 기반 백엔드 서비스입니다. 정규식 패턴 매칭과 검증 알고리즘을 사용합니다.

## 개발 명령어

### 환경 설정
```bash
# 가상환경 활성화
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 서버 실행
```bash
# 개발 서버 (자동 리로드)
uvicorn app.main:app --reload

# 프로덕션 방식 서버
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 테스트
```bash
# 전체 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_scan_engine.py
pytest tests/test_scan_endpoint.py

# 상세 출력과 함께 실행
pytest -v

# 특정 테스트 함수 실행
pytest tests/test_scan_engine.py::test_engine_basic_counts
```

## 아키텍처

### 핵심 구조
```
app/
├── main.py              # FastAPI 앱 초기화, CORS 설정, health 엔드포인트
├── routers/
│   └── scan.py         # /api/scan 엔드포인트 (파일 검증)
└── modules/
    └── scanner/
        ├── scan.py      # 핵심 scan_text() 오케스트레이터
        ├── patterns.py  # PII 유형별 정규식 패턴
        ├── validators.py # 후처리 검증기 (Luhn, 주민등록번호 체크섬)
        └── utils.py     # 문맥 윈도우 추출
```

### 요청 흐름
1. **라우터** (`app/routers/scan.py`): 파일 업로드 처리, 크기(최대 25MB) 및 확장자 화이트리스트 검증
2. **스캐너** (`app/modules/scanner/scan.py`): `patterns.py`의 정규식 패턴을 텍스트에 적용
3. **검증기**: `luhn_ok()`로 신용카드 검증, `rrn_checksum_ok()`로 주민등록번호 검증하여 후처리 필터링
4. **응답**: 라인/컬럼 위치와 선택적 문맥 윈도우를 포함한 탐지 결과 반환

### PII 탐지 유형
- `email`: 이메일 주소
- `phone_kr`: 한국 전화번호 (+82, 010- 형식 지원)
- `ipv4`: IPv4 주소
- `url`: HTTP/HTTPS URL
- `rrn`: 주민등록번호 (체크섬 검증 포함)
- `credit_card`: 13-19자리 카드 번호 (Luhn 알고리즘 검증)

### 검증 로직
패턴 매칭 후 후처리 필터링을 거칩니다:
- **신용카드**: Luhn 체크섬 통과 필수 (`validators.luhn_ok()`)
- **주민등록번호**: 가중치 체크섬 검증 통과 필수 (`validators.rrn_checksum_ok()`)
- **기타 유형**: 후처리 필터링 없음, 패턴 매칭으로 충분

### 문맥 윈도우 기능
`context_window` 쿼리 파라미터(0-10)로 탐지 결과에 포함할 주변 라인 수를 제어합니다:
- `0`: 문맥 없음 (기본값)
- `N`: 매칭된 라인 위/아래로 N개 라인 포함
- `utils.make_context()`에서 구현, (시작_라인, 끝_라인, 문맥_텍스트) 반환

## 주요 제약사항

- 최대 파일 크기: 25MB (`scan.py:24`에서 강제)
- 허용 확장자: `.txt`, `.pdf`, `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.bmp`, `.webp`
- 현재 `.txt` 파일만 스캔 기능이 완전히 구현됨
- CORS는 `localhost:3000`으로 설정 (프론트엔드 개발용)
- 문맥 윈도우 범위: 0-10 라인 (FastAPI Query 검증기로 강제)

## 테스트 참고사항

- `pytest` 사용, `asyncio_mode = auto` 설정 (`pytest.ini`에 구성)
- 엔드포인트 테스트는 `httpx.AsyncClient`와 `ASGITransport` 사용 (httpx 0.28+ 호환)
- 테스트 파일은 엔진 로직(`test_scan_engine.py`)과 API 동작(`test_scan_endpoint.py`) 모두 검증
- 성능 테스트는 약 10만 라인 문서 처리 확인
