# -*- coding: utf-8 -*-
"""인쇄용 HTML/CSS 레이아웃 생성기 — 4가지 디자인 × 2가지 규격 (흑백) v6
핵심 변경: mm → px 단위, CSS Grid → HTML table, max-width:0 트릭, 5pt 폰트
"""

from modules.seed_data import FOOTER_DONG_UI, FOOTER_KOSIN

# ── 상수 ─────────────────────────────────────────────────────────────────────
# 90mm ≈ 340px, 50mm ≈ 189px at 96dpi
CARD_W = 340
CARD_H = 189
DOUBLE_H = CARD_H * 2  # 378px = 100mm


def _t(text: str | None, max_len: int) -> str:
    """텍스트를 max_len 글자로 잘라서 반환. 넘치면 '…' 붙임."""
    if not text:
        return ""
    s = str(text)
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


# ── 공통 CSS ──────────────────────────────────────────────────────────────────

_COMMON_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
    color: #000;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}}

.no-print {{ display: block; text-align: center; padding: 10px; }}
.print-btn {{
    background: #333; color: #fff; border: none; padding: 10px 30px;
    border-radius: 6px; font-size: 14px; cursor: pointer; margin: 5px;
}}
.print-btn:hover {{ background: #555; }}

@media print {{
    .no-print {{ display: none !important; }}
}}

/* 셀 클리핑 */
.cell {{
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 0;
}}
</style>
"""


def _header_html(title: str = "재활의학과 주소록") -> str:
    return f"""
<div class="no-print">
    <h3>{title}</h3>
    <button class="print-btn" onclick="window.print()">인쇄하기</button>
    <p style="font-size:12px; color:#888; margin-top:5px;">
        인쇄 설정: 여백 '없음', 배경 그래픽 '켜기'
    </p>
</div>
"""


def _split_members(members: list[dict]) -> tuple[list[dict], list[dict]]:
    """2그룹: 앞면(2기~19기), 뒷면(Staff+21기~31기)."""
    side_a = [m for m in members if m["cohort_order"] > 0 and m["cohort_order"] <= 19]
    side_b = [m for m in members if m["cohort_order"] == 0 or m["cohort_order"] >= 21]
    return side_a, side_b


def _split_members_4(members: list[dict]) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """4그룹: 더블카드 접이식 용 (각 면 50mm)."""
    side_a, side_b = _split_members(members)
    mid_a = len(side_a) // 2
    mid_b = len(side_b) // 2
    return side_a[:mid_a], side_a[mid_a:], side_b[:mid_b], side_b[mid_b:]


def _footer_html(show: bool) -> str:
    if not show:
        return ""
    return f"""
    <div style="position:absolute; bottom:3px; left:8px; right:8px; font-size:4pt; color:#555; line-height:1.4; border-top:1px solid #999; padding-top:2px">
        {FOOTER_DONG_UI}<br>{FOOTER_KOSIN}
    </div>"""


def _fold_line() -> str:
    """접는 선 (점선)"""
    return f'<div style="width:{CARD_W}px; border-top:1px dashed #aaa; margin:0; height:0"></div>'


# ══════════════════════════════════════════════════════════════════════════════
# Layout A: 표 형식 — HTML table + table-layout:fixed + max-width:0
# ══════════════════════════════════════════════════════════════════════════════

def _layout_a_css(size: str) -> str:
    page_size = "90mm 50mm" if size == "card" else "90mm 100mm"
    pba = "page-break-after: always;" if size == "card" else ""
    double = "" if size == "card" else f".double-page {{ width:{CARD_W}px; height:{DOUBLE_H}px; page-break-after:always; }}"
    return f"""
<style>
@page {{ size: {page_size}; margin: 0; }}
.card-a {{ width:{CARD_W}px; height:{CARD_H}px; padding:6px 8px; overflow:hidden; position:relative; {pba} }}
{double}

.tbl-a {{
    table-layout: fixed;
    width: 100%;
    border-collapse: collapse;
    font-size: 5pt;
    line-height: 1.3;
}}
.tbl-a th {{
    background: #000; color: #fff; font-weight: 600;
    padding: 1px 2px; font-size: 5pt; text-align: left;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.tbl-a td {{
    padding: 1px 2px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 0;
}}
.tbl-a tr:nth-child(even) {{ background: #f0f0f0; }}
</style>"""


def _layout_a_panel(members: list[dict], show_title: bool = True, show_footer: bool = False) -> str:
    hdr = """<thead><tr>
        <th>기수</th><th>성명</th><th>현근무지</th>
        <th>이메일</th><th>면허</th><th>전화번호</th>
    </tr></thead>"""

    rows = ""
    for m in members:
        name = _t(m["name"], 8)
        if m.get("is_tbd"):
            name = f'<span style="color:#999">{name}</span>'
        wp = _t(m.get("workplace", ""), 18)
        em = _t(m.get("email", ""), 20)
        ln = _t(m.get("license_no", ""), 8)
        ph = _t(m.get("phone", ""), 14)
        rows += f"<tr><td style='font-weight:500'>{m['cohort']}</td>"
        rows += f"<td style='font-weight:600'>{name}</td>"
        rows += f"<td>{wp}</td><td>{em}</td><td>{ln}</td><td>{ph}</td></tr>\n"

    title = '<div style="text-align:center; font-size:6pt; font-weight:700; margin-bottom:3px">재활의학과 주소록</div>' if show_title else ""
    return f"""
<div class="card-a">
    {title}
    <table class="tbl-a">
        <colgroup>
            <col style="width:9%">
            <col style="width:11%">
            <col style="width:28%">
            <col style="width:23%">
            <col style="width:10%">
            <col style="width:19%">
        </colgroup>
        {hdr}
        <tbody>{rows}</tbody>
    </table>
    {_footer_html(show_footer)}
</div>"""


def generate_layout_a(members: list[dict], size: str) -> str:
    css = _COMMON_CSS + _layout_a_css(size)
    html = css + _header_html("Layout A: 표 형식")

    if size == "card":
        side_a, side_b = _split_members(members)
        html += _layout_a_panel(side_a, show_title=True, show_footer=False)
        html += _layout_a_panel(side_b, show_title=False, show_footer=True)
    else:
        p1, p2, p3, p4 = _split_members_4(members)
        html += f'<div class="double-page">'
        html += _layout_a_panel(p1, show_title=True, show_footer=False)
        html += _fold_line()
        html += _layout_a_panel(p2, show_title=False, show_footer=False)
        html += '</div>'
        html += f'<div class="double-page">'
        html += _layout_a_panel(p3, show_title=False, show_footer=False)
        html += _fold_line()
        html += _layout_a_panel(p4, show_title=False, show_footer=True)
        html += '</div>'

    return f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{html}</body></html>"


# ══════════════════════════════════════════════════════════════════════════════
# Layout B: 모던 클린 — 기수 + 이름 + 전화번호
# ══════════════════════════════════════════════════════════════════════════════

def _layout_b_css(size: str) -> str:
    page_size = "90mm 50mm" if size == "card" else "90mm 100mm"
    pba = "page-break-after: always;" if size == "card" else ""
    double = "" if size == "card" else f".double-page {{ width:{CARD_W}px; height:{DOUBLE_H}px; page-break-after:always; }}"
    return f"""
<style>
@page {{ size: {page_size}; margin: 0; }}
.card-b {{ width:{CARD_W}px; height:{CARD_H}px; padding:6px 10px; overflow:hidden; position:relative; {pba} }}
{double}

.tbl-b {{
    table-layout: fixed;
    width: 100%;
    border-collapse: collapse;
    font-size: 5pt;
    line-height: 1.3;
}}
.tbl-b td {{
    padding: 1px 2px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 0;
    border-bottom: 1px solid #eee;
}}
</style>"""


def _layout_b_panel(members: list[dict], show_title: bool = True, show_footer: bool = False) -> str:
    rows = ""
    prev_cohort = ""
    for m in members:
        cohort_td = ""
        if m["cohort"] != prev_cohort:
            cohort_td = f'<td style="font-weight:600; background:#e0e0e0; text-align:center">{m["cohort"]}</td>'
            prev_cohort = m["cohort"]
        else:
            cohort_td = '<td></td>'

        name_style = "font-weight:600"
        if m.get("is_tbd"):
            name_style += "; color:#999"

        nm = _t(m['name'], 8)
        ph = _t(m.get('phone', ''), 14)
        rows += f'<tr>{cohort_td}<td style="{name_style}">{nm}</td><td style="color:#444">{ph}</td></tr>\n'

    title = '<div style="font-size:6pt; font-weight:700; margin-bottom:4px; border-bottom:2px solid #000; padding-bottom:2px">재활의학과 주소록</div>' if show_title else ""
    return f"""
<div class="card-b">
    {title}
    <table class="tbl-b">
        <colgroup>
            <col style="width:20%">
            <col style="width:30%">
            <col style="width:50%">
        </colgroup>
        <tbody>{rows}</tbody>
    </table>
    {_footer_html(show_footer)}
</div>"""


def generate_layout_b(members: list[dict], size: str) -> str:
    css = _COMMON_CSS + _layout_b_css(size)
    html = css + _header_html("Layout B: 모던 클린")

    if size == "card":
        side_a, side_b = _split_members(members)
        html += _layout_b_panel(side_a, show_title=True, show_footer=False)
        html += _layout_b_panel(side_b, show_title=False, show_footer=True)
    else:
        p1, p2, p3, p4 = _split_members_4(members)
        html += f'<div class="double-page">'
        html += _layout_b_panel(p1, show_title=True, show_footer=False)
        html += _fold_line()
        html += _layout_b_panel(p2, show_title=False, show_footer=False)
        html += '</div>'
        html += f'<div class="double-page">'
        html += _layout_b_panel(p3, show_title=False, show_footer=False)
        html += _fold_line()
        html += _layout_b_panel(p4, show_title=False, show_footer=True)
        html += '</div>'

    return f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{html}</body></html>"


# ══════════════════════════════════════════════════════════════════════════════
# Layout C: 카드 그리드 — 인당 1카드
# ══════════════════════════════════════════════════════════════════════════════

def _layout_c_css(size: str) -> str:
    page_size = "90mm 50mm" if size == "card" else "90mm 100mm"
    pba = "page-break-after: always;" if size == "card" else ""
    double = "" if size == "card" else f".double-page {{ width:{CARD_W}px; height:{DOUBLE_H}px; page-break-after:always; }}"
    return f"""
<style>
@page {{ size: {page_size}; margin: 0; }}
.card-c {{ width:{CARD_W}px; height:{CARD_H}px; padding:6px; overflow:hidden; position:relative; {pba} }}
{double}

.tbl-c {{
    table-layout: fixed;
    width: 100%;
    border-collapse: collapse;
    font-size: 5pt;
}}
.tbl-c td {{
    border: 1px solid #ccc;
    padding: 2px 3px;
    vertical-align: top;
    overflow: hidden;
    max-width: 0;
}}
.tbl-c td div {{
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}
</style>"""


def _layout_c_panel(members: list[dict], show_title: bool = True, show_footer: bool = False) -> str:
    # 3열 테이블로 배치
    cells = []
    for m in members:
        name_style = "font-weight:700; font-size:5pt"
        if m.get("is_tbd"):
            name_style += "; color:#999"
        nm = _t(m['name'], 8)
        ph = _t(m.get('phone', ''), 14)
        em = _t(m.get('email', ''), 16)
        cell = f"""<div style="font-size:4pt; color:#666">{m['cohort']}</div>
            <div style="{name_style}">{nm}</div>
            <div>{ph}</div>
            <div style="color:#555">{em}</div>"""
        cells.append(cell)

    # 3열씩 행 구성
    rows = ""
    for i in range(0, len(cells), 3):
        row_cells = cells[i:i+3]
        while len(row_cells) < 3:
            row_cells.append("")
        rows += "<tr>" + "".join(f"<td>{c}</td>" for c in row_cells) + "</tr>\n"

    title = f'<div style="text-align:center; font-size:6pt; font-weight:700; margin-bottom:3px">재활의학과 주소록</div>' if show_title else ""
    return f"""
<div class="card-c">
    {title}
    <table class="tbl-c">
        <colgroup><col style="width:33.33%"><col style="width:33.33%"><col style="width:33.34%"></colgroup>
        <tbody>{rows}</tbody>
    </table>
    {_footer_html(show_footer)}
</div>"""


def generate_layout_c(members: list[dict], size: str) -> str:
    css = _COMMON_CSS + _layout_c_css(size)
    html = css + _header_html("Layout C: 카드 그리드")

    if size == "card":
        side_a, side_b = _split_members(members)
        html += _layout_c_panel(side_a, show_title=True, show_footer=False)
        html += _layout_c_panel(side_b, show_title=False, show_footer=True)
    else:
        p1, p2, p3, p4 = _split_members_4(members)
        html += f'<div class="double-page">'
        html += _layout_c_panel(p1, show_title=True, show_footer=False)
        html += _fold_line()
        html += _layout_c_panel(p2, show_title=False, show_footer=False)
        html += '</div>'
        html += f'<div class="double-page">'
        html += _layout_c_panel(p3, show_title=False, show_footer=False)
        html += _fold_line()
        html += _layout_c_panel(p4, show_title=False, show_footer=True)
        html += '</div>'

    return f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{html}</body></html>"


# ══════════════════════════════════════════════════════════════════════════════
# Layout D: 컴팩트 2단 — 이름+전화번호 2열 배치
# ══════════════════════════════════════════════════════════════════════════════

def _layout_d_css(size: str) -> str:
    page_size = "90mm 50mm" if size == "card" else "90mm 100mm"
    pba = "page-break-after: always;" if size == "card" else ""
    double = "" if size == "card" else f".double-page {{ width:{CARD_W}px; height:{DOUBLE_H}px; page-break-after:always; }}"
    return f"""
<style>
@page {{ size: {page_size}; margin: 0; }}
.card-d {{ width:{CARD_W}px; height:{CARD_H}px; padding:6px 10px; overflow:hidden; position:relative; {pba} }}
{double}

.tbl-d {{
    table-layout: fixed;
    width: 100%;
    border-collapse: collapse;
    font-size: 5pt;
    line-height: 1.3;
}}
.tbl-d td {{
    padding: 1px 2px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 0;
}}
</style>"""


def _layout_d_panel(members: list[dict], show_title: bool = True, show_footer: bool = False) -> str:
    # 2단 배치: 멤버를 반으로 나눠 좌/우 2열 테이블
    mid = (len(members) + 1) // 2
    left = members[:mid]
    right = members[mid:]

    def _render_col(mlist: list[dict]) -> str:
        items = ""
        prev_cohort = ""
        for m in mlist:
            if m["cohort"] != prev_cohort:
                items += f'<tr><td colspan="2" style="font-weight:700; border-bottom:1px solid #000; padding-top:2px">{m["cohort"]}</td></tr>\n'
                prev_cohort = m["cohort"]
            name_style = "font-weight:600"
            if m.get("is_tbd"):
                name_style += "; color:#999"
            nm = _t(m['name'], 8)
            ph = _t(m.get("phone", ""), 14)
            items += f'<tr><td style="{name_style}">{nm}</td><td style="color:#333; text-align:right">{ph}</td></tr>\n'
        return items

    title = '<div style="text-align:center; font-size:6pt; font-weight:700; margin-bottom:3px; border-bottom:2px solid #000; padding-bottom:2px">재활의학과 주소록</div>' if show_title else ""

    return f"""
<div class="card-d">
    {title}
    <table style="width:100%; border-collapse:collapse">
        <colgroup><col style="width:50%"><col style="width:50%"></colgroup>
        <tr>
            <td style="vertical-align:top; padding-right:4px; border-right:1px solid #ddd">
                <table class="tbl-d"><colgroup><col style="width:40%"><col style="width:60%"></colgroup><tbody>{_render_col(left)}</tbody></table>
            </td>
            <td style="vertical-align:top; padding-left:4px">
                <table class="tbl-d"><colgroup><col style="width:40%"><col style="width:60%"></colgroup><tbody>{_render_col(right)}</tbody></table>
            </td>
        </tr>
    </table>
    {_footer_html(show_footer)}
</div>"""


def generate_layout_d(members: list[dict], size: str) -> str:
    css = _COMMON_CSS + _layout_d_css(size)
    html = css + _header_html("Layout D: 컴팩트 2단")

    if size == "card":
        side_a, side_b = _split_members(members)
        html += _layout_d_panel(side_a, show_title=True, show_footer=False)
        html += _layout_d_panel(side_b, show_title=False, show_footer=True)
    else:
        p1, p2, p3, p4 = _split_members_4(members)
        html += f'<div class="double-page">'
        html += _layout_d_panel(p1, show_title=True, show_footer=False)
        html += _fold_line()
        html += _layout_d_panel(p2, show_title=False, show_footer=False)
        html += '</div>'
        html += f'<div class="double-page">'
        html += _layout_d_panel(p3, show_title=False, show_footer=False)
        html += _fold_line()
        html += _layout_d_panel(p4, show_title=False, show_footer=True)
        html += '</div>'

    return f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{html}</body></html>"


# ── 통합 ──────────────────────────────────────────────────────────────────────

LAYOUTS = {
    "A: 표 형식": generate_layout_a,
    "B: 모던 클린": generate_layout_b,
    "C: 카드 그리드": generate_layout_c,
    "D: 컴팩트 2단": generate_layout_d,
}

SIZES = {
    "명함 (90×50mm 양면)": "card",
    "세로 더블카드 (90×100mm 4면 접이)": "double",
}
