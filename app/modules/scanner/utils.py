import os # API 키를 안전하게 불러오기 위해 import
import requests

from typing import List, Tuple

UPSTAGE_OCR_URL = "https://api.upstage.ai/v1/document-ai/ocr"

# 주변 문맥 제공
def make_context(lines: List[str], line_idx: int, window: int) -> Tuple[int,int,str]:
    """
    라인 주변 컨텍스트를 window 범위만큼 묶어서 반환
    """
    start = max(0, line_idx - window)
    end = min(len(lines), line_idx + window + 1)
    ctx = "\n".join(lines[start:end])
    return start, end-1, ctx

# OCR 텍스트 추출
def extract_text_with_ocr(file_bytes: bytes) -> str:
    """
    Upstage Document AI (OCR) API를 호출하여 파일(bytes)에서 텍스트를 추출합니다.
    """
    
    # 1. API 키 불러오기 (보안!)
    # 절대 코드에 키를 직접 쓰면 안 됩니다. .env 파일이나 환경변수 사용.
    api_key = os.environ.get("UPSTAGE_API_KEY")
    
    if not api_key:
        print("에러: UPSTAGE_API_KEY 환경변수가 설정되지 않았습니다.")
        return "OCR API 키 오류" # 또는 예외(raise) 처리
        
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # 2. API로 전송할 파일 준비
    files = {
        'document': file_bytes
    }
    
    # 3. API 호출
    try:
        response = requests.post(UPSTAGE_OCR_URL, headers=headers, files=files)
        
        # 4. 결과 파싱 (성공 시)
        if response.status_code == 200:
            result_json = response.json()
            # Upstage API가 반환하는 JSON 구조에 맞춰 'text' 필드를 가져와야 합니다.
            # 예: return result_json['data']['text'] (API 문서를 꼭 확인하세요!)
            return result_json.get("text", "텍스트를 찾을 수 없음")
        else:
            # 5. 결과 파싱 (실패 시)
            print(f"OCR API 오류: {response.status_code}")
            print(response.text)
            return f"OCR API 호출 실패: {response.status_code}"
            
    except Exception as e:
        print(f"OCR 요청 중 예외 발생: {e}")
        return f"OCR 요청 중 오류: {str(e)}"