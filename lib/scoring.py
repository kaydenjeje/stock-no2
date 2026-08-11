"""
종목별 모멘텀 스코어 및 '사실 기반' 지표 배지를 계산한다.

주의(§4 문구 가이드라인): 이 모듈은 매수가/목표가/손절가를 계산하거나
반환하지 않는다. 점수는 객관 지표를 정렬하기 위한 용도일 뿐, 투자의견이
아니다.
"""

from datetime import date, timedelta

import pandas as pd

try:
    from pykrx import stock as pykrx_stock
except Exception:  # pragma: no cover - pykrx가 없거나 초기화에 실패한 경우
    pykrx_stock = None


def fetch_investor_flow(code):
    """최근 5거래일 외국인/기관 순매수 금액(원)을 반환한다. 실패 시 None."""
    if pykrx_stock is None:
        return None
    try:
        end = date.today()
        start = end - timedelta(days=12)
        df = pykrx_stock.get_market_trading_value_by_date(
            start.strftime("%Y%m%d"), end.strftime("%Y%m%d"), code
        )
        if df.empty:
            return None
        return {
            "foreign_5d": float(df["외국인합계"].tail(5).sum()),
            "institution_5d": float(df["기관합계"].tail(5).sum()),
        }
    except Exception:
        return None


def compute_score_and_badges(df, code=None):
    """가격 데이터프레임(OHLCV)에서 스코어와 지표 배지 목록을 계산한다."""
    if df is None or len(df) < 60:
        return None

    close = df["Close"]
    volume = df["Volume"]

    latest_close = float(close.iloc[-1])
    prev_close = float(close.iloc[-2])
    change_pct = ((latest_close - prev_close) / prev_close * 100) if prev_close else 0.0

    ma5 = close.rolling(5).mean()
    ma20 = close.rolling(20).mean()

    vol_mean20 = volume.rolling(20).mean().iloc[-1]
    vol_latest = float(volume.iloc[-1])
    vol_ratio = vol_latest / (float(vol_mean20) + 1e-9) if pd.notna(vol_mean20) else 1.0

    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    rsi_series = 100 - (100 / (1 + rs))
    rsi = float(rsi_series.iloc[-1]) if pd.notna(rsi_series.iloc[-1]) else 50.0

    lookback = close.tail(252) if len(close) >= 252 else close
    max_period = float(lookback.max())
    pct_from_high = (latest_close / max_period - 1) * 100 if max_period else 0.0

    badges = []
    score = 30.0

    if pd.notna(ma5.iloc[-2]) and pd.notna(ma20.iloc[-2]):
        if ma5.iloc[-2] <= ma20.iloc[-2] and ma5.iloc[-1] > ma20.iloc[-1]:
            badges.append("20일선 상향돌파")
            score += 20
        elif ma5.iloc[-1] > ma20.iloc[-1] and latest_close > ma5.iloc[-1]:
            badges.append("20일선 위 안착")
            score += 10

    if vol_ratio >= 1.8:
        badges.append(f"거래량 {vol_ratio * 100:.0f}% (평소 대비)")
        score += 15
    elif vol_ratio >= 1.3:
        badges.append(f"거래량 {vol_ratio * 100:.0f}% (평소 대비)")
        score += 8

    if pct_from_high >= -3:
        badges.append("52주 신고가 근접")
        score += 15

    if 50 <= rsi <= 72:
        badges.append(f"RSI {rsi:.0f} · 상승흐름")
        score += 10
    elif rsi > 78:
        badges.append(f"RSI {rsi:.0f} · 단기 과열")
        score -= 5
    elif rsi < 30:
        badges.append(f"RSI {rsi:.0f} · 단기 침체")

    flow = fetch_investor_flow(code) if code else None
    if flow:
        f5, i5 = flow["foreign_5d"], flow["institution_5d"]
        if f5 > 0 and i5 > 0:
            badges.append("외국인·기관 동반 순매수")
            score += 15
        elif f5 > 0 or i5 > 0:
            badges.append("외국인 또는 기관 순매수")
            score += 8
        elif f5 < 0 and i5 < 0:
            badges.append("외국인·기관 동반 순매도")
            score -= 10

    score = max(0.0, min(100.0, round(score, 1)))

    return {
        "score": score,
        "badges": badges[:4],
        "latest_price": latest_close,
        "change_pct": change_pct,
        "rsi": rsi,
        "vol_ratio": vol_ratio,
    }
