import random

import streamlit as st

from lib import content


def render(state):
    st.subheader("학습 센터")

    term, desc = content.today_term()
    st.markdown(f"**오늘 배울 지표: {term}**")
    st.info(desc)

    st.markdown("#### 용어사전")
    for t, d in content.LEARN_TERMS.items():
        with st.expander(t):
            st.write(d)

    st.markdown("#### 퀴즈")
    if "quiz_idx" not in st.session_state:
        st.session_state.quiz_idx = random.randrange(len(content.QUIZ_BANK))

    q = content.QUIZ_BANK[st.session_state.quiz_idx]
    choice = st.radio(q["q"], q["options"], index=None, key=f"quiz_{st.session_state.quiz_idx}")

    if choice is not None:
        if q["options"].index(choice) == q["answer"]:
            st.success("맞았어요!")
        else:
            st.error(f"아쉬워요. 정답은 '{q['options'][q['answer']]}' 입니다.")
        if st.button("다음 퀴즈"):
            st.session_state.quiz_idx = random.randrange(len(content.QUIZ_BANK))
            st.rerun()
