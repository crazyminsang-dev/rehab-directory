# -*- coding: utf-8 -*-
"""관리자 페이지 — 비밀번호 보호, 진행현황, 편집, CSV, 링크생성"""

import pandas as pd
import streamlit as st

from modules.auth import check_password
from modules.db import (
    bulk_update_from_csv,
    export_to_csv,
    get_all_members,
    get_member_by_id,
    get_members_by_status,
    get_submission_stats,
    update_member,
    update_member_name,
)

if not check_password():
    st.stop()

st.title("관리자 페이지")

# ── CSV 백업 버튼 (항상 최상단) ───────────────────────────────────────────────
csv_data = export_to_csv()
st.download_button(
    "CSV 백업 다운로드",
    data=csv_data,
    file_name="의국주소록_백업.csv",
    mime="text/csv",
    type="secondary",
    use_container_width=True,
)
st.divider()

# ── 탭 구성 ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["진행 현황", "데이터 편집", "가져오기/내보내기", "링크 생성"])

# ━━ 탭 1: 진행 현황 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    stats = get_submission_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("전체 인원", stats["total"])
    c2.metric("제출 완료", stats["submitted"])
    c3.metric("미제출", stats["pending"])

    progress = stats["submitted"] / max(stats["total"], 1)
    st.progress(progress, text=f"진행률 {progress:.0%}")

    st.subheader("미제출 명단")
    pending = get_members_by_status(submitted=False)
    if pending:
        for m in pending:
            st.write(f"- **{m['cohort']}** {m['name']}")
    else:
        st.success("모든 회원이 제출 완료했습니다!")

    st.subheader("제출 완료 명단")
    done = get_members_by_status(submitted=True)
    if done:
        for m in done:
            st.write(f"- **{m['cohort']}** {m['name']}  ({m['submitted_at']})")

# ━━ 탭 2: 데이터 편집 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    st.subheader("전체 데이터 테이블 (직접 편집 가능)")
    st.caption("현근무지, 이메일, 면허번호, 전화번호 칸을 클릭하여 직접 수정할 수 있습니다. 수정 후 아래 '변경사항 저장' 버튼을 눌러주세요.")
    all_members = get_all_members()
    df = pd.DataFrame(all_members)
    display_cols = ["id", "cohort", "name", "workplace", "email", "license_no", "phone"]
    df_edit = df[[c for c in display_cols if c in df.columns]].copy()
    df_edit.columns = ["ID", "기수", "이름", "현근무지", "이메일", "면허번호", "전화번호"]

    edited_df = st.data_editor(
        df_edit,
        use_container_width=True,
        hide_index=True,
        disabled=["ID", "기수", "이름"],
        column_config={
            "ID": st.column_config.NumberColumn(width="small"),
            "기수": st.column_config.TextColumn(width="small"),
            "이름": st.column_config.TextColumn(width="small"),
            "현근무지": st.column_config.TextColumn(width="large"),
            "이메일": st.column_config.TextColumn(width="medium"),
            "면허번호": st.column_config.TextColumn(width="small"),
            "전화번호": st.column_config.TextColumn(width="medium"),
        },
        key="member_editor",
    )

    if st.button("변경사항 저장", type="primary", key="save_table_edits"):
        save_count = 0
        for idx, row in edited_df.iterrows():
            member_id = int(row["ID"])
            orig = df_edit.iloc[idx]
            if (row["현근무지"] != orig["현근무지"] or row["이메일"] != orig["이메일"]
                    or row["면허번호"] != orig["면허번호"] or row["전화번호"] != orig["전화번호"]):
                update_member(
                    member_id,
                    str(row["현근무지"]),
                    str(row["이메일"]),
                    str(row["면허번호"]),
                    str(row["전화번호"]),
                    updated_by="admin",
                )
                save_count += 1
        if save_count:
            st.success(f"{save_count}건 저장 완료")
            st.rerun()
        else:
            st.info("변경된 내용이 없습니다.")

    st.divider()
    st.subheader("개별 수동 입력")
    st.caption("문자/카카오톡으로 받은 정보를 대리 입력합니다.")

    members_for_edit = get_all_members()
    options_edit = {f"[{m['id']}] {m['cohort']} {m['name']}": m for m in members_for_edit}
    selected_edit = st.selectbox(
        "회원 선택",
        options=[""] + list(options_edit.keys()),
        index=0,
        key="edit_select",
    )

    if selected_edit:
        m = options_edit[selected_edit]

        # TBD 회원인 경우 이름 변경 가능
        if m["is_tbd"]:
            new_name = st.text_input("새 이름 (Staff 자리 확정)", value="", key="tbd_name")
            if st.button("이름 확정", key="confirm_name"):
                if new_name.strip():
                    update_member_name(m["id"], new_name.strip())
                    st.success(f"이름이 '{new_name.strip()}'으로 확정되었습니다.")
                    st.rerun()

        with st.form("admin_edit_form"):
            workplace = st.text_input("현 근무지", value=m.get("workplace", ""), key="ae_wp")
            email = st.text_input("이메일", value=m.get("email", ""), key="ae_em")
            license_no = st.text_input("면허번호", value=m.get("license_no", ""), key="ae_ln")
            phone = st.text_input("전화번호", value=m.get("phone", ""), key="ae_ph")

            if st.form_submit_button("저장", type="primary"):
                update_member(
                    m["id"],
                    workplace.strip(),
                    email.strip(),
                    license_no.strip(),
                    phone.strip(),
                    updated_by="admin",
                )
                st.success(f"{m['cohort']} {m['name']} 정보가 저장되었습니다.")
                st.rerun()

# ━━ 탭 3: 가져오기/내보내기 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:
    st.subheader("CSV 내보내기")
    csv_bytes = export_to_csv()
    st.download_button(
        "CSV 다운로드",
        data=csv_bytes,
        file_name="의국주소록.csv",
        mime="text/csv",
    )

    st.divider()
    st.subheader("CSV 가져오기 (복원)")
    st.caption(
        "백업 CSV 파일을 업로드하면 기존 데이터를 덮어씁니다. "
        "CSV에는 id, workplace, email, license_no, phone 컬럼이 필요합니다."
    )
    uploaded = st.file_uploader("CSV 파일 업로드", type=["csv"], key="csv_upload")
    if uploaded:
        try:
            df_up = pd.read_csv(uploaded, encoding="utf-8-sig")
            st.dataframe(df_up.head(10))
            if st.button("가져오기 실행", type="primary"):
                count = bulk_update_from_csv(df_up)
                st.success(f"{count}건의 데이터가 업데이트되었습니다.")
                st.rerun()
        except Exception as e:
            st.error(f"CSV 읽기 오류: {e}")

# ━━ 탭 4: 링크 생성 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:
    st.subheader("개인 설문 링크")
    st.caption("아래 링크를 복사하여 카카오톡으로 전송하세요.")

    # 앱 URL 설정
    app_url = st.text_input(
        "앱 URL (배포 후 수정)",
        value="https://rehab-directory.streamlit.app",
        key="app_url",
    )

    members_link = get_all_members(exclude_tbd=True)

    # 필터: 미제출만 보기
    show_only_pending = st.checkbox("미제출자만 표시", value=True)
    if show_only_pending:
        members_link = [m for m in members_link if not m["is_submitted"]]

    for m in members_link:
        link = f"{app_url}/?id={m['id']}"
        status = "제출완료" if m["is_submitted"] else "미제출"
        col1, col2 = st.columns([3, 5])
        with col1:
            st.write(f"**{m['cohort']}** {m['name']} ({status})")
        with col2:
            st.code(link, language=None)

    st.divider()
    st.subheader("카카오톡 안내 메시지 템플릿")
    template = f"""[의국 주소록 정보 입력 요청]

안녕하세요, 선생님.
의국 주소록 업데이트를 위해 아래 링크에서 정보를 입력해주세요.

{app_url}/

(현근무지, 이메일, 면허번호, 전화번호)
감사합니다."""

    st.text_area("복사해서 사용하세요", value=template, height=200, key="msg_template")
