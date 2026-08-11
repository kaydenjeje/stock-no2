import streamlit as st

from lib import content, data


def render(state):
    st.subheader("오늘의 시장")

    with st.spinner("시장 데이터를 불러오는 중..."):
        scores = data.get_universe_scores()
    temp, temp_label = data.compute_market_temperature(scores)

    c1, c2 = st.columns([1, 2])
    c1.metric("시장 온도", f"{temp}도", temp_label)
    with c2:
        st.info(content.build_market_brief(scores, temp, temp_label))

    st.markdown("#### 스코어 TOP")
    limit = 20 if state.get("plan") == "pro" else 5
    if not scores:
        st.warning("스코어 데이터를 불러오지 못했습니다. 네트워크 상태를 확인해주세요.")
    for i, item in enumerate(scores[:20]):
        locked = i >= limit
        cols = st.columns([0.4, 2.6, 1.2, 3])
        cols[0].write(f"{i + 1}")
        if locked:
            cols[1].write("🔒")
            cols[2].write("Pro 전용")
            cols[3].write("")
        else:
            cols[1].write(f"**{item['name']}** `{item['code']}`")
            cols[2].write(f"{item['score']}점")
            cols[3].write(" · ".join(item["badges"][:2]) if item["badges"] else "—")
    if state.get("plan") != "pro" and len(scores) > limit:
        st.caption(f"{limit + 1}위부터는 Pro 구독에서 볼 수 있어요.")

    st.markdown("#### 나의 관심종목")
    watchlist = state.get("watchlist", [])
    if not watchlist:
        st.caption("아직 등록한 관심종목이 없어요. 종목상세 화면에서 추가해보세요.")
    else:
        for code in watchlist:
            info = data.get_stock_score(code)
            if info:
                badge_str = " · ".join(info["badges"][:2]) if info["badges"] else "특별한 변화 없음"
                st.write(f"**{info['name']}** — {badge_str}")
