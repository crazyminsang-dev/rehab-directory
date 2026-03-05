# -*- coding: utf-8 -*-
"""설문 입력 페이지 — 회원용 (모바일 최적화)"""

import re

import streamlit as st

from modules.db import get_all_members, get_member_by_id, update_member

st.title("재활의학과 의국 주소록")
st.caption("아래 정보를 입력해주세요. 입력하신 정보는 의국 주소록 제작에만 사용됩니다.")

# ── 회원 식별 ─────────────────────────────────────────────────────────────────
params = st.query_params
param_id = params.get("id")

member = None

if param_id:
    # 개인 링크 모드: ?id=N
    member = get_member_by_id(int(param_id))
    if not member:
        st.error("잘못된 링크입니다. 관리자에게 문의하세요.")
        st.stop()
    if member["is_tbd"]:
        st.error("아직 확정되지 않은 자리입니다.")
        st.stop()
    st.info(f"**{member['cohort']}  {member['name']}** 님의 정보를 입력해주세요.")
else:
    # 마스터 URL 모드: 드롭다운 선택
    members = get_all_members(exclude_tbd=True)
    options = {f"{m['cohort']}  {m['name']}": m for m in members}
    selected_label = st.selectbox(
        "이름을 선택하세요",
        options=[""] + list(options.keys()),
        index=0,
        placeholder="기수 — 이름을 선택하세요",
    )
    if not selected_label:
        st.info("위 목록에서 본인의 이름을 선택해주세요.")
        st.stop()
    member = options[selected_label]

# ── 이미 제출된 경우 안내 ─────────────────────────────────────────────────────
if member["is_submitted"]:
    st.warning(
        f"이미 {member['submitted_at']}에 제출하셨습니다. "
        "다시 제출하면 기존 정보가 덮어씌워집니다."
    )

# ── 입력 폼 ──────────────────────────────────────────────────────────────────
with st.form("survey_form", clear_on_submit=False):
    workplace = st.text_input(
        "현 근무지 (병원/의원명 + 주소)",
        value=member.get("workplace", ""),
        placeholder="예: OO병원 재활의학과, 부산 서구 암남동 34번지",
    )
    email = st.text_input(
        "이메일",
        value=member.get("email", ""),
        placeholder="example@email.com",
    )
    license_no = st.text_input(
        "면허번호",
        value=member.get("license_no", ""),
        placeholder="의사면허번호 (숫자)",
    )
    phone = st.text_input(
        "전화번호",
        value=member.get("phone", ""),
        placeholder="010-0000-0000",
    )

    submitted = st.form_submit_button("제출하기", type="primary", use_container_width=True)

    if submitted:
        # 유효성 검사
        errors = []
        if not workplace.strip():
            errors.append("현 근무지를 입력해주세요.")
        if email.strip() and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()):
            errors.append("이메일 형식이 올바르지 않습니다.")
        if phone.strip() and not re.match(r"^[\d\-\(\)\s\+]+$", phone.strip()):
            errors.append("전화번호 형식이 올바르지 않습니다.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            update_member(
                member["id"],
                workplace.strip(),
                email.strip(),
                license_no.strip(),
                phone.strip(),
                updated_by="self",
            )
            st.success("제출이 완료되었습니다! 감사합니다.")
            st.balloons()
