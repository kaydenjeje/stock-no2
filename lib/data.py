"""
주가 데이터 조회 및 스코어링 유니버스 관리.

MVP 범위: 한국 시장(KRX)만 지원, 스크리닝 대상은 아래 CURATED_KR
(시가총액 상위권 위주 약 40종목)로 한정한다. 전종목 스캔은 §6 다음 단계에서
collect_data류 배치로 확장한다. 종목 상세 검색은 전체 KRX 리스트를 사용한다.
"""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

try:
    import FinanceDataReader as fdr
except Exception:  # pragma: no cover
    fdr = None

from lib import scoring

CURATED_KR = [
    ("005930", "삼성전자", "💻 반도체/IT"),
    ("000660", "SK하이닉스", "💻 반도체/IT"),
    ("009150", "삼성전기", "💻 반도체/IT"),
    ("042700", "한미반도체", "💻 반도체/IT"),
    ("000990", "DB하이텍", "💻 반도체/IT"),
    ("035420", "NAVER", "🌐 빅테크/AI플랫폼"),
    ("035720", "카카오", "🌐 빅테크/AI플랫폼"),
    ("259960", "크래프톤", "🌐 빅테크/AI플랫폼"),
    ("018260", "삼성에스디에스", "🌐 빅테크/AI플랫폼"),
    ("373220", "LG에너지솔루션", "🔋 2차전지/소재"),
    ("006400", "삼성SDI", "🔋 2차전지/소재"),
    ("051910", "LG화학", "🔋 2차전지/소재"),
    ("096770", "SK이노베이션", "🔋 2차전지/소재"),
    ("086520", "에코프로", "🔋 2차전지/소재"),
    ("247540", "에코프로비엠", "🔋 2차전지/소재"),
    ("207940", "삼성바이오로직스", "💊 바이오/제약"),
    ("068270", "셀트리온", "💊 바이오/제약"),
    ("196170", "알테오젠", "💊 바이오/제약"),
    ("028300", "HLB", "💊 바이오/제약"),
    ("005380", "현대차", "🚗 자동차/제조"),
    ("000270", "기아", "🚗 자동차/제조"),
    ("012330", "현대모비스", "🚗 자동차/제조"),
    ("329180", "HD현대중공업", "🚗 자동차/제조"),
    ("034020", "두산에너빌리티", "🚗 자동차/제조"),
    ("005490", "POSCO홀딩스", "🏭 주력산업/기타"),
    ("028260", "삼성물산", "🏭 주력산업/기타"),
    ("015760", "한국전력", "🏭 주력산업/기타"),
    ("009830", "한화솔루션", "🏭 주력산업/기타"),
    ("090430", "아모레퍼시픽", "🏭 주력산업/기타"),
    ("051900", "LG생활건강", "🏭 주력산업/기타"),
    ("066570", "LG전자", "🏭 주력산업/기타"),
    ("105560", "KB금융", "🏭 주력산업/기타"),
    ("055550", "신한지주", "🏭 주력산업/기타"),
    ("086790", "하나금융지주", "🏭 주력산업/기타"),
    ("316140", "우리금융지주", "🏭 주력산업/기타"),
    ("000810", "삼성화재", "🏭 주력산업/기타"),
    ("017670", "SK텔레콤", "🏭 주력산업/기타"),
    ("030200", "KT", "🏭 주력산업/기타"),
    ("323410", "카카오뱅크", "🌐 빅테크/AI플랫폼"),
    ("138040", "메리츠금융지주", "🏭 주력산업/기타"),
]

_FALLBACK_LISTING = pd.DataFrame(
    [{"Code": c, "Name": n, "Market": "KRX"} for c, n, _ in CURATED_KR]
)


@st.cache_data(ttl=86400)
def get_kr_listing():
    """검색용 전체 KRX 종목 리스트. 실패 시 CURATED_KR로 대체."""
    if fdr is None:
        return _FALLBACK_LISTING
    try:
        df = fdr.StockListing("KRX-DESC")[["Code", "Name", "Market"]].dropna()
        df["Code"] = df["Code"].astype(str).str.zfill(6)
        return df.reset_index(drop=True)
    except Exception:
        return _FALLBACK_LISTING


def get_name(code):
    listing = get_kr_listing()
    row = listing[listing["Code"] == code]
    if not row.empty:
        return row.iloc[0]["Name"]
    for c, n, _ in CURATED_KR:
        if c == code:
            return n
    return code


@st.cache_data(ttl=1800)
def get_price_history(code, days=300):
    if fdr is None:
        return pd.DataFrame()
    end = date.today()
    start = end - timedelta(days=days)
    try:
        df = fdr.DataReader(code, start, end)
        return df
    except Exception:
        return pd.DataFrame()


def get_stock_score(code):
    df = get_price_history(code)
    if df.empty or len(df) < 60:
        return None
    result = scoring.compute_score_and_badges(df, code=code)
    if result is None:
        return None
    result["code"] = code
    result["name"] = get_name(code)
    return result


@st.cache_data(ttl=3600)
def get_universe_scores():
    results = []
    for code, name, sector in CURATED_KR:
        df = get_price_history(code)
        if df.empty or len(df) < 60:
            continue
        r = scoring.compute_score_and_badges(df, code=code)
        if r:
            r.update({"code": code, "name": name, "sector": sector})
            results.append(r)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def compute_market_temperature(scores):
    if not scores:
        return 50, "보통"
    top = scores[:20] if len(scores) >= 20 else scores
    avg = sum(s["score"] for s in top) / len(top)
    temp = int(round(avg))
    if temp >= 75:
        label = "초고온"
    elif temp >= 60:
        label = "고온"
    elif temp >= 40:
        label = "보통"
    else:
        label = "저온"
    return temp, label
