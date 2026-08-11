import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from lib import ai, data, storage


def _build_chart(df):
    d = df.copy()
    d["MA5"] = d["Close"].rolling(5).mean()
    d["MA20"] = d["Close"].rolling(20).mean()
    d["MA60"] = d["Close"].rolling(60).mean()
    plot_df = d.tail(120)

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_heights=[0.72, 0.28]
    )
    fig.add_trace(
        go.Scatter(x=plot_df.index, y=plot_df["Close"], name="종가", line=dict(width=2)),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=plot_df.index, y=plot_df["MA5"], name="5일선", line=dict(width=1)),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=plot_df.index, y=plot_df["MA20"], name="20일선", line=dict(width=1)),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=plot_df.index, y=plot_df["MA60"], name="60일선", line=dict(width=1)),
        row=1, col=1,
    )
    fig.add_trace(
        go.Bar(x=plot_df.index, y=plot_df["Volume"], name="거래량", opacity=0.6),
        row=2, col=1,
    )
    fig.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    return fig


def render(state):
    st.subheader("종목 상세")

    listing = data.get_kr_listing()
    if listing.empty:
        st.warning("종목 목록을 불러오지 못했습니다.")
        return

    labels = (listing["Name"] + " (" + listing["Code"] + ")").tolist()
    codes = listing["Code"].tolist()

    default_code = st.session_state.get("selected_code", "005930")
    default_idx = codes.index(default_code) if default_code in codes else 0

    choice = st.selectbox("종목 검색", labels, index=default_idx)
    idx = labels.index(choice)
    code = codes[idx]
    name = listing.iloc[idx]["Name"]
    st.session_state.selected_code = code

    info = data.get_stock_score(code)
    if not info:
        st.warning("가격 데이터가 부족하거나 불러오지 못했습니다.")
        return

    c1, c2 = st.columns([2, 1])
    c1.metric(f"{name} ({code})", f"{info['latest_price']:,.0f}원", f"{info['change_pct']:+.2f}%")

    watchlist = state.setdefault("watchlist", [])
    in_watchlist = code in watchlist
    with c2:
        st.write("")
        if st.button(
            "🔖 관심종목 해제" if in_watchlist else "➕ 관심종목 추가",
            use_container_width=True,
        ):
            if in_watchlist:
                watchlist.remove(code)
            else:
                watchlist.append(code)
            storage.save_state(state)
            st.rerun()

    df = data.get_price_history(code)
    if not df.empty:
        st.plotly_chart(_build_chart(df), use_container_width=True, config={"displayModeBar": False})

    st.markdown("#### 감지된 지표")
    if info["badges"]:
        st.write(" ".join(f"`{b}`" for b in info["badges"]))
    else:
        st.caption("현재 특별히 감지된 지표가 없습니다.")

    st.markdown("#### AI 지표 해설")
    st.caption("투자의견 · 매수가 · 목표가는 제공하지 않습니다. 지표의 의미만 사실대로 설명해요.")

    if st.button("지표 해설 생성", type="primary"):
        with st.spinner("지표를 해설하는 중..."):
            text, used_ai = ai.explain_indicators(name, info)
        st.session_state["detail_explain"] = text
        st.session_state["detail_explain_ai"] = used_ai
        st.session_state["detail_explain_code"] = code

    if st.session_state.get("detail_explain") and st.session_state.get("detail_explain_code") == code:
        st.info(st.session_state["detail_explain"])
        if not st.session_state.get("detail_explain_ai"):
            st.caption("※ DEEPSEEK_API_KEY가 설정되지 않아 규칙 기반 해설을 보여주고 있어요.")
