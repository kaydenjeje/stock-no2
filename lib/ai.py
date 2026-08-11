"""
AI 지표 해설 생성.

§3-2/§8-3 결정에 따라 개인 맞춤 챗봇(Q&A)은 두지 않는다. 이 모듈은
'이미 감지된 지표를 사실대로 설명'하는 단발성 생성만 제공하며, 투자의견 ·
매수가 · 목표가 · 손절가는 절대 출력하지 않도록 프롬프트에 명시한다.

DEEPSEEK_API_KEY가 없으면 규칙 기반 대체 문구를 반환해서, API 키 없이도
앱이 바로 동작하도록 한다.
"""

import os

import streamlit as st

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


def _get_client():
    api_key = None
    try:
        api_key = st.secrets.get("DEEPSEEK_API_KEY")
    except Exception:
        pass
    api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
    if not api_key or OpenAI is None:
        return None
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def _fallback_text(stock_name, info):
    badges = info.get("badges") or []
    lead = ", ".join(badges[:2]) if badges else "특별한 신호가 감지되지 않은"
    return (
        f"{stock_name}는 현재 {lead} 상태예요. "
        f"RSI는 {info['rsi']:.0f}, 거래량은 최근 20일 평균 대비 {info['vol_ratio'] * 100:.0f}%입니다. "
        "이 지표들은 사실을 보여줄 뿐 매수·매도를 권하지 않아요."
    )


def explain_indicators(stock_name, info):
    """반환: (설명 텍스트, AI 사용 여부)"""
    fallback = _fallback_text(stock_name, info)
    client = _get_client()
    if not client:
        return fallback, False

    badges_str = ", ".join(info.get("badges") or []) or "특별한 신호 없음"
    prompt = f"""
너는 주식 초보자에게 지표를 '사실만' 설명하는 도우미야.
절대로 매수/매도 의견, 목표가, 손절가, 투자의견, "~하세요" 같은 행동 권유를 말하지 마.
아래 지표를 2~3문장으로 쉽게 설명해줘.

종목: {stock_name}
현재가: {info['latest_price']:.0f} / 전일대비 {info['change_pct']:+.2f}%
RSI: {info['rsi']:.1f}
거래량 비율(20일 평균 대비): {info['vol_ratio'] * 100:.0f}%
감지된 지표 배지: {badges_str}
"""
    try:
        res = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        text = (res.choices[0].message.content or "").strip()
        return (text or fallback), bool(text)
    except Exception:
        return fallback, False
