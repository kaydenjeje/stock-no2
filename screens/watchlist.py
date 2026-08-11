import streamlit as st

from lib import data, storage


def render(state):
    st.subheader("관심종목 · 알림")

    watchlist = state.get("watchlist", [])
    if not watchlist:
        st.info("아직 등록한 관심종목이 없어요. 종목상세 화면에서 추가해보세요.")
        return

    is_pro = state.get("plan") == "pro"
    limit = None if is_pro else 1
    shown = watchlist if limit is None else watchlist[:limit]
    if limit and len(watchlist) > limit:
        st.caption(f"Free 플랜은 관심종목 {limit}개까지 확인할 수 있어요. 나머지는 Pro에서 볼 수 있어요.")

    st.markdown("#### 오늘 감지된 변화")
    st.caption("지표 변화를 사실 그대로 알려드려요. 매수·매도를 권하지 않습니다.")

    any_alert = False
    for code in shown:
        info = data.get_stock_score(code)
        if not info:
            continue
        for badge in info["badges"]:
            st.write(f"`{info['name']}` {badge}")
            any_alert = True
    if not any_alert:
        st.caption("오늘은 등록한 종목에 특별한 변화가 감지되지 않았어요.")

    st.markdown("#### 알림 종류")
    st.caption("설정만 가능한 목업입니다. 실제 푸시/이메일 발송은 추후 연동 예정이에요 (docs/product-plan-v1.md §8-3 D).")

    settings = state.setdefault(
        "alert_settings", {"ma_cross": True, "volume": True, "flow": False}
    )
    ma_cross = st.checkbox("이평선 교차", value=settings.get("ma_cross", True))
    volume = st.checkbox("거래량 급증", value=settings.get("volume", True))
    flow = st.checkbox("수급 변화", value=settings.get("flow", False))

    new_settings = {"ma_cross": ma_cross, "volume": volume, "flow": flow}
    if new_settings != settings:
        state["alert_settings"] = new_settings
        storage.save_state(state)
