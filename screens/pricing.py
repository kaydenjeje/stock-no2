import streamlit as st

from lib import storage


def render(state):
    st.subheader("요금제")

    st.markdown(
        """
| | Free | Pro |
|---|---|---|
| 스코어보드 | TOP 5 | TOP 20 |
| 관심종목 | 1개 | 무제한 |
| 지표 변화 확인 | O | O |
| 학습 센터 | 일부 | 전체 |
| 매매 저널 | X | O |
| 광고 | 있음 | 없음 |
"""
    )

    st.markdown("### 월 9,900원")
    st.caption("커피 3잔 값으로, 매일의 확인 습관을 만들어요.")

    st.warning(
        "이 화면의 결제 버튼은 실제 PG(결제) 연동 없이 상태만 바꾸는 테스트용입니다. "
        "실제 결제는 §8-6(전자상거래법 정기결제 고지 등) 확인 후 별도 연동이 필요해요."
    )

    if state.get("plan") == "pro":
        st.success("현재 Pro 플랜을 이용 중이에요. (테스트 모드)")
        if st.button("Free로 되돌리기 (테스트용)"):
            state["plan"] = "free"
            storage.save_state(state)
            st.rerun()
    else:
        if st.button("7일 무료체험 시작 (테스트용 Pro 전환)", type="primary"):
            state["plan"] = "pro"
            storage.save_state(state)
            st.rerun()
