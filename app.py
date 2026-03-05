# -*- coding: utf-8 -*-
"""
재활의학과 의국 주소록 관리 시스템
메인 엔트리 — st.navigation 라우터

실행:
    streamlit run app.py
"""

import streamlit as st

from modules.db import init_db

# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="의국 주소록",
    page_icon="📋",
    layout="centered",
)

# ── DB 초기화 (앱 시작 시 1회) ────────────────────────────────────────────────
init_db()

# ── 페이지 라우팅 ─────────────────────────────────────────────────────────────
survey_page = st.Page("pages/survey.py", title="설문 입력", icon="📝", default=True)
admin_page = st.Page("pages/admin.py", title="관리자", icon="🔒")
print_page = st.Page("pages/print_preview.py", title="인쇄 미리보기", icon="🖨️")

pg = st.navigation([survey_page, admin_page, print_page])
pg.run()
