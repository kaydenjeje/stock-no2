import streamlit as st

from lib import storage
from screens import detail, home, journal, learn, onboarding, pricing, watchlist

st.set_page_config(
    page_title="초보자 주식 지표 스크리닝",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    .block-container { padding-top: 1.4rem !important; padding-bottom: 3rem !important; }
</style>
""",
    unsafe_allow_html=True,
)

if "app_state" not in st.session_state:
    st.session_state.app_state = storage.load_state()
state = st.session_state.app_state

if "page" not in st.session_state:
    st.session_state.page = "home" if state["onboarded"] else "onboarding"

with st.sidebar:
    st.subheader("🛠️ 개발용 테스트 패널")
    st.caption("실제 로그인/결제 없이 상태를 바꿔가며 테스트하는 용도입니다.")

    plan_choice = st.radio(
        "구독 상태",
        ["free", "pro"],
        index=0 if state.get("plan", "free") == "free" else 1,
        format_func=lambda x: "Free" if x == "free" else "Pro",
    )
    if plan_choice != state.get("plan"):
        state["plan"] = plan_choice
        storage.save_state(state)

    if st.button("온보딩 다시 하기"):
        state["onboarded"] = False
        storage.save_state(state)
        st.session_state.page = "onboarding"
        for k in ("onboard_step", "onboard_answers"):
            st.session_state.pop(k, None)
        st.rerun()

TABS = [
    ("home", "🏠 홈"),
    ("detail", "📈 종목상세"),
    ("watchlist", "🔔 관심종목"),
    ("learn", "📚 학습"),
    ("journal", "📝 저널"),
    ("pricing", "💳 요금제"),
]

if state["onboarded"]:
    cols = st.columns(len(TABS))
    for col, (key, label) in zip(cols, TABS):
        with col:
            btn_type = "primary" if st.session_state.page == key else "secondary"
            if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
                st.session_state.page = key
                st.rerun()
    st.divider()

page = st.session_state.page
if page == "onboarding":
    onboarding.render(state)
elif page == "home":
    home.render(state)
elif page == "detail":
    detail.render(state)
elif page == "watchlist":
    watchlist.render(state)
elif page == "learn":
    learn.render(state)
elif page == "journal":
    journal.render(state)
elif page == "pricing":
    pricing.render(state)
else:
    st.session_state.page = "home"
    st.rerun()

st.markdown("---")
st.caption(
    "⚠️ 본 서비스는 투자자문이 아닌 데이터·학습 목적의 참고 정보만 제공합니다. "
    "투자 판단과 이에 따른 책임은 이용자 본인에게 있습니다."
)
