from datetime import date

import streamlit as st

from lib import data, storage


def render(state):
    st.subheader("매매 저널")
    st.caption("스스로 기록하고, 그날의 지표를 자동으로 붙여서 나중에 복기할 수 있어요.")

    listing = data.get_kr_listing()
    labels = (listing["Name"] + " (" + listing["Code"] + ")").tolist() if not listing.empty else []
    codes = listing["Code"].tolist() if not listing.empty else []

    with st.form("journal_form", clear_on_submit=True):
        sel = st.selectbox("종목", labels) if labels else None
        action = st.radio("구분", ["매수", "매도"], horizontal=True)
        memo = st.text_area("메모", placeholder="그날의 생각을 남겨보세요")
        submitted = st.form_submit_button("기록 추가", type="primary")

        if submitted and sel:
            code = codes[labels.index(sel)]
            info = data.get_stock_score(code)
            entry = {
                "date": date.today().isoformat(),
                "code": code,
                "name": info["name"] if info else code,
                "action": action,
                "memo": memo,
                "score": info["score"] if info else None,
                "rsi": round(info["rsi"], 1) if info else None,
            }
            state.setdefault("journal", []).insert(0, entry)
            storage.save_state(state)
            st.success("기록했어요.")

    st.markdown("#### 지난 기록")
    journal = state.get("journal", [])
    if not journal:
        st.caption("아직 기록이 없어요.")
    for e in journal:
        with st.container(border=True):
            st.write(f"**{e['date']} · {e['name']} · {e['action']}**")
            if e.get("memo"):
                st.write(e["memo"])
            if e.get("score") is not None:
                st.caption(f"그날 스코어 {e['score']}점 · RSI {e['rsi']}")
