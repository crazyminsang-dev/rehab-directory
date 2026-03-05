# -*- coding: utf-8 -*-
"""관리자 비밀번호 인증"""

import streamlit as st


def check_password() -> bool:
    """비밀번호 확인. 세션에 인증 상태 저장."""
    if st.session_state.get("authenticated"):
        return True

    st.subheader("관리자 로그인")
    password = st.text_input("비밀번호를 입력하세요", type="password", key="admin_pw")
    if password:
        if password == st.secrets.get("admin_password", "rehab2026"):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다.")
    return False
