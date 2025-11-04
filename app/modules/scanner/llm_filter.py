# app/modules/scanner/llm_filter.py
import os
import requests

UPSTAGE_LLM_URL = "https://api.upstage.ai/v1/chat/completions"
MODEL = "solar-1-mini-chat"

SYSTEM_PROMPT = (
    "당신은 OCR 텍스트 오류를 교정하는 전문가입니다. "
    "문장 의미를 바꾸지 말고, 다음 오인식을 교정하세요: "
    "숫자↔영문(O↔0, l↔1, S↔5 등), 잘못된 공백/하이픈/특수문자, "
    "이메일/전화번호/주민등록번호/신용카드번호 형식. "
    "결과는 오직 교정된 텍스트만 출력하세요."
)

class LLMCorrectionError(Exception):
    pass

def correct_text_with_llm(text: str, *, timeout: int = 30, max_chars: int = 8000) -> str:
    """
    OCR로 얻은 텍스트를 LLM으로 보정한다.
    - 긴 문서는 잘라 보냄(최대 max_chars)
    - 실패하면 원문 반환
    """
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        # 운영 중이면 원문 반환이 안정적. 개발 중엔 예외가 더 눈에 잘 띔.
        # raise LLMCorrectionError("UPSTAGE_API_KEY not set")
        return text

    # 너무 긴 텍스트는 잘라서 보냄(해커톤/실무 안전장치)
    payload_text = text[:max_chars]

    try:
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": payload_text},
            ],
            # 필요하면 temperature, top_p 등 조절 가능
        }
        headers = {"Authorization": f"Bearer {api_key}"}

        res = requests.post(UPSTAGE_LLM_URL, headers=headers, json=payload, timeout=timeout)
        res.raise_for_status()
        data = res.json()

        # Upstage 응답 형태 기준
        corrected = data["choices"][0]["message"]["content"]
        corrected = (corrected or "").strip()
        return corrected if corrected else text

    except Exception:
        # 어떤 이유로든 실패하면 원문을 그대로 돌려보내 정규식 탐지까지는 흘러가게 함
        return text
