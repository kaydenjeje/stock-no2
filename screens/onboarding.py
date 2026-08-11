import streamlit as st

from lib import content, storage


def render(state):
    st.title("몇 가지만 여쭤볼게요")
    st.caption("답변에 따라 학습 콘텐츠 순서를 맞춰드려요. 종목 추천에는 쓰이지 않습니다.")

    questions = content.ONBOARD_QUESTIONS
    total = len(questions)

    if "onboard_step" not in st.session_state:
        st.session_state.onboard_step = 0
    if "onboard_answers" not in st.session_state:
        st.session_state.onboard_answers = []

    step = st.session_state.onboard_step

    if step < total:
        q = questions[step]
        st.progress(step / total)
        st.write(f"**{step + 1}. {q['q']}**")
        choice = st.radio(
            "answer", q["options"], key=f"onboard_q_{step}", label_visibility="collapsed"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("다음", type="primary", use_container_width=True):
                st.session_state.onboard_answers.append(choice)
                st.session_state.onboard_step += 1
                st.rerun()
        with col2:
            if st.button("건너뛰기", use_container_width=True):
                st.session_state.onboard_step = total
                st.rerun()
    else:
        answers = st.session_state.onboard_answers
        beginner_signals = sum(1 for a in answers if a in ("처음 들어요", "6개월 미만"))
        level = "입문" if beginner_signals >= 2 else "초중급"

        state["onboarded"] = True
        state["level"] = level
        storage.save_state(state)

        st.success(f"완료했어요! 추천 학습 레벨: {level}")
        if st.button("홈으로 이동", type="primary", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
