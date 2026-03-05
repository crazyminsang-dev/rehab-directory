# -*- coding: utf-8 -*-
"""인쇄 미리보기 페이지 — 레이아웃 선택 + 규격 선택 + 미리보기/다운로드"""

import streamlit as st
import streamlit.components.v1 as components

from modules.db import get_all_members_for_print
from modules.print_layouts import LAYOUTS, SIZES

st.title("주소록 인쇄 미리보기")

# ── 옵션 선택 ────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    layout_name = st.radio("레이아웃", list(LAYOUTS.keys()))
with col2:
    size_name = st.radio("인쇄 규격", list(SIZES.keys()))

# ── HTML 생성 ────────────────────────────────────────────────────────────────
members = get_all_members_for_print()
generate_fn = LAYOUTS[layout_name]
size_key = SIZES[size_name]
html_content = generate_fn(members, size_key)

# ── 미리보기 ─────────────────────────────────────────────────────────────────
st.divider()
st.subheader("미리보기")
st.caption("아래는 축소 미리보기입니다. 정확한 크기는 HTML을 다운로드하여 Chrome에서 인쇄하세요.")

preview_height = 500 if size_key == "card" else 800
components.html(html_content, height=preview_height, scrolling=True)

# ── 다운로드 ─────────────────────────────────────────────────────────────────
st.divider()
st.download_button(
    "HTML 파일 다운로드",
    data=html_content,
    file_name=f"의국주소록_{layout_name[0]}.html",
    mime="text/html",
    type="primary",
    use_container_width=True,
)
st.caption(
    "다운로드한 HTML 파일을 Chrome에서 열고 Ctrl+P로 인쇄하세요. "
    "설정: 여백 '없음', 배경 그래픽 '켜기', 용지 크기는 사용자 지정으로 mm 입력."
)
