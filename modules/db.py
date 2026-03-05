# -*- coding: utf-8 -*-
"""SQLite 데이터베이스 — 스키마 초기화, 시딩, CRUD 함수"""

import io
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.seed_data import MEMBERS

DB_PATH = Path(__file__).parent.parent / "directory.db"


@st.cache_resource
def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """스키마 생성 + 시드 데이터 삽입 (테이블이 비어있을 때만)."""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            cohort       TEXT    NOT NULL,
            cohort_order INTEGER NOT NULL,
            name         TEXT    NOT NULL,
            workplace    TEXT    DEFAULT '',
            email        TEXT    DEFAULT '',
            license_no   TEXT    DEFAULT '',
            phone        TEXT    DEFAULT '',
            is_submitted INTEGER NOT NULL DEFAULT 0,
            is_tbd       INTEGER NOT NULL DEFAULT 0,
            submitted_at TEXT,
            updated_at   TEXT,
            updated_by   TEXT
        )
    """)
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM members").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO members (cohort, cohort_order, name, is_tbd) VALUES (?, ?, ?, ?)",
            MEMBERS,
        )
        conn.commit()


# ── 조회 ──────────────────────────────────────────────────────────────────────

def get_all_members(exclude_tbd: bool = False) -> list[dict]:
    conn = get_db()
    sql = "SELECT * FROM members"
    if exclude_tbd:
        sql += " WHERE is_tbd = 0"
    sql += " ORDER BY cohort_order ASC, id ASC"
    rows = conn.execute(sql).fetchall()
    return [dict(r) for r in rows]


def get_member_by_id(member_id: int) -> dict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
    return dict(row) if row else None


def get_submission_stats() -> dict:
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM members WHERE is_tbd = 0").fetchone()[0]
    submitted = conn.execute(
        "SELECT COUNT(*) FROM members WHERE is_tbd = 0 AND is_submitted = 1"
    ).fetchone()[0]
    return {"total": total, "submitted": submitted, "pending": total - submitted}


def get_members_by_status(submitted: bool) -> list[dict]:
    conn = get_db()
    val = 1 if submitted else 0
    rows = conn.execute(
        "SELECT * FROM members WHERE is_tbd = 0 AND is_submitted = ? ORDER BY cohort_order ASC, id ASC",
        (val,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_all_members_for_print() -> list[dict]:
    """인쇄용 전체 데이터 (TBD 포함, 정렬)."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM members ORDER BY cohort_order ASC, id ASC"
    ).fetchall()
    return [dict(r) for r in rows]


# ── 수정 ──────────────────────────────────────────────────────────────────────

def update_member(
    member_id: int,
    workplace: str,
    email: str,
    license_no: str,
    phone: str,
    updated_by: str = "self",
):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        """UPDATE members
           SET workplace = ?, email = ?, license_no = ?, phone = ?,
               is_submitted = 1, submitted_at = COALESCE(submitted_at, ?),
               updated_at = ?, updated_by = ?
           WHERE id = ?""",
        (workplace, email, license_no, phone, now, now, updated_by, member_id),
    )
    conn.commit()


def update_member_name(member_id: int, name: str):
    """TBD 회원의 이름을 확정할 때 사용."""
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "UPDATE members SET name = ?, is_tbd = 0, updated_at = ? WHERE id = ?",
        (name, now, member_id),
    )
    conn.commit()


def bulk_update_from_csv(df: pd.DataFrame) -> int:
    """CSV DataFrame으로부터 DB를 upsert. 반환: 업데이트 건수."""
    conn = get_db()
    updated = 0
    for _, row in df.iterrows():
        member_id = int(row.get("id", 0))
        if member_id <= 0:
            continue
        existing = get_member_by_id(member_id)
        if not existing:
            continue
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            """UPDATE members
               SET workplace = ?, email = ?, license_no = ?, phone = ?,
                   is_submitted = 1, submitted_at = COALESCE(submitted_at, ?),
                   updated_at = ?, updated_by = 'admin'
               WHERE id = ?""",
            (
                str(row.get("workplace", "")),
                str(row.get("email", "")),
                str(row.get("license_no", "")),
                str(row.get("phone", "")),
                now,
                now,
                member_id,
            ),
        )
        updated += 1
    conn.commit()
    return updated


# ── 내보내기 ──────────────────────────────────────────────────────────────────

def export_to_csv() -> bytes:
    members = get_all_members()
    df = pd.DataFrame(members)
    cols = ["id", "cohort", "name", "workplace", "email", "license_no", "phone",
            "is_submitted", "submitted_at", "updated_at"]
    df = df[[c for c in cols if c in df.columns]]
    buf = io.BytesIO()
    df.to_csv(buf, index=False, encoding="utf-8-sig")
    return buf.getvalue()
