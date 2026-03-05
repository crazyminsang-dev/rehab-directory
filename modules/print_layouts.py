# -*- coding: utf-8 -*-
"""인쇄용 HTML/CSS 레이아웃 생성기 — 4가지 디자인 × 2가지 규격 (흑백) v5"""

from modules.seed_data import FOOTER_DONG_UI, FOOTER_KOSIN


def _t(text: str | None, max_len: int) -> str:
    """텍스트를 max_len 글자로 잘라서 반환. 넘치면 '…' 붙임."""
    if not text:
        return ""
    s = str(text)
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"

# ── 공통 CSS ──────────────────────────────────────────────────────────────────

_COMMON_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
    color: #000;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}

.no-print { display: block; text-align: center; padding: 10px; }
.print-btn {
    background: #333; color: #fff; border: none; padding: 10px 30px;
    border-radius: 6px; font-size: 14px; cursor: pointer; margin: 5px;
}
.print-btn:hover { background: #555; }

@media print {
    .no-print { display: none !important; }
}

.clip {
    display: block;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}
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
    <div style="position:absolute; bottom:1mm; left:2.5mm; right:2.5mm; font-size:5pt; color:#555; line-height:1.4; border-top:0.3mm solid #999; padding-top:0.5mm">
        {FOOTER_DONG_UI}<br>{FOOTER_KOSIN}
    </div>"""


def _fold_line() -> str:
    """접는 선 (점선)"""
    return '<div style="width:90mm; border-top:0.3mm dashed #aaa; margin:0; height:0"></div>'


# ══════════════════════════════════════════════════════════════════════════════
# Layout A: 개선된 표 형식 — CSS Grid 기반
# ══════════════════════════════════════════════════════════════════════════════

def _layout_a_css(size: str) -> str:
    if size == "card":
        return """
<style>
@page { size: 90mm 50mm; margin: 0; }
.card-a { width: 90mm; height: 50mm; padding: 2mm 2.5mm; page-break-after: always; overflow: hidden; position: relative; }
</style>"""
    else:
        return """
<style>
@page { size: 90mm 100mm; margin: 0; }
.card-a { width: 90mm; height: 50mm; padding: 2mm 2.5mm; overflow: hidden; position: relative; }
.double-page { width: 90mm; height: 100mm; page-break-after: always; }
</style>"""


_GRID_TABLE_CSS = """
<style>
.grid-table {
    display: grid;
    grid-template-columns: 8mm 10mm minmax(0, 1fr) 18mm 8mm 14mm;
    font-size: 6pt; line-height: 1.3; gap: 0;
    width: 85mm;
}
.grid-table > div {
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    padding: 0.3mm 0.5mm; border-bottom: 0.1mm solid #ddd;
    min-width: 0;
}
.grid-hdr {
    background: #000; color: #fff; font-weight: 600;
    padding: 0.4mm 0.5mm !important; border-bottom: none !important;
}
</style>
"""


def _layout_a_panel(members: list[dict], show_title: bool = True, show_footer: bool = False) -> str:
    hdr = ''.join(f'<div class="grid-hdr">{c}</div>' for c in ["기수","성명","현근무지","이메일","면허","전화번호"])
    rows = ""
    for i, m in enumerate(members):
        bg = "background:#f0f0f0;" if i % 2 == 0 else ""
        name = _t(m["name"], 6)
        if m.get("is_tbd"):
            name = f'<span style="color:#999">{name}</span>'
        wp = _t(m.get("workplace", ""), 12)
        em = _t(m.get("email", ""), 16)
        ln = _t(m.get("license_no", ""), 7)
        ph = _t(m.get("phone", ""), 13)
        rows += f'<div style="{bg} font-weight:500">{m["cohort"]}</div>'
        rows += f'<div style="{bg} font-weight:600">{name}</div>'
        rows += f'<div style="{bg}">{wp}</div>'
        rows += f'<div style="{bg}">{em}</div>'
        rows += f'<div style="{bg}">{ln}</div>'
        rows += f'<div style="{bg}">{ph}</div>'

    title = '<div style="text-align:center; font-size:7pt; font-weight:700; margin-bottom:1mm">재활의학과 주소록</div>' if show_title else ""
    return f"""
<div class="card-a">
    {title}
    <div class="grid-table">{hdr}{rows}</div>
    {_footer_html(show_footer)}
</div>"""


def generate_layout_a(members: list[dict], size: str) -> str:
    css = _COMMON_CSS + _layout_a_css(size) + _GRID_TABLE_CSS
    html = css + _header_html("Layout A: 개선된 표 형식")

    if size == "card":
        side_a, side_b = _split_members(members)
        html += _layout_a_panel(side_a, show_title=True, show_footer=False)
        html += _layout_a_panel(side_b, show_title=False, show_footer=True)
    else:
        p1, p2, p3, p4 = _split_members_4(members)
        html += '<div class="double-page">'
        html += _layout_a_panel(p1, show_title=True, show_footer=False)
        html += _fold_line()
        html += _layout_a_panel(p2, show_title=False, show_footer=False)
        html += '</div>'
        html += '<div class="double-page">'
        html += _layout_a_panel(p3, show_title=False, show_footer=False)
        html += _fold_line()
        html += _layout_a_panel(p4, show_title=False, show_footer=True)
        html += '</div>'

    return f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{html}</body></html>"


# ══════════════════════════════════════════════════════════════════════════════
# Layout B: 모던 클린 — 기수 + 이름 + 전화번호
# ══════════════════════════════════════════════════════════════════════════════

def _layout_b_css(size: str) -> str:
    if size == "card":
        return """
<style>
@page { size: 90mm 50mm; margin: 0; }
.card-b { width: 90mm; height: 50mm; padding: 2mm 3mm; overflow: hidden; position: relative; page-break-after: always; }
</style>"""
    else:
        return """
<style>
@page { size: 90mm 100mm; margin: 0; }
.card-b { width: 90mm; height: 50mm; padding: 2mm 3mm; overflow: hidden; position: relative; }
.double-page { width: 90mm; height: 100mm; page-break-after: always; }
</style>"""


def _layout_b_panel(members: list[dict], show_title: bool = True, show_footer: bool = False) -> str:
    items = ""
    prev_cohort = ""
    for m in members:
        if m["cohort"] != prev_cohort:
            cohort_label = f'<span style="display:inline-block; background:#e0e0e0; font-size:6pt; font-weight:600; padding:0.2mm 1.5mm; min-width:7mm; text-align:center">{m["cohort"]}</span>'
            prev_cohort = m["cohort"]
        else:
            cohort_label = '<span style="display:inline-block; min-width:7mm; padding:0.2mm 1.5mm"></span>'

        name_style = "font-weight:600; font-size:6pt"
        if m.get("is_tbd"):
            name_style += "; color:#999"

        nm = _t(m['name'], 6)
        ph = _t(m.get('phone', ''), 13)
        items += f"""
        <div style="display:flex; align-items:baseline; padding:0.2mm 0; border-bottom:0.15mm solid #ddd; font-size:6pt; overflow:hidden; height:3mm">
            {cohort_label}
            <span style="{name_style}; min-width:10mm; margin:0 1mm">{nm}</span>
            <span style="color:#444; flex:1; white-space:nowrap">{ph}</span>
        </div>"""

    title = '<div style="font-size:7pt; font-weight:700; margin-bottom:1.5mm; border-bottom:0.4mm solid #000; padding-bottom:0.5mm">재활의학과 주소록</div>' if show_title else ""
    return f"""
<div class="card-b">
    {title}
    {items}
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
        html += '<div class="double-page">'
        html += _layout_b_panel(p1, show_title=True, show_footer=False)
        html += _fold_line()
        html += _layout_b_panel(p2, show_title=False, show_footer=False)
        html += '</div>'
        html += '<div class="double-page">'
        html += _layout_b_panel(p3, show_title=False, show_footer=False)
        html += _fold_line()
        html += _layout_b_panel(p4, show_title=False, show_footer=True)
        html += '</div>'

    return f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{html}</body></html>"


# ══════════════════════════════════════════════════════════════════════════════
# Layout C: 카드 그리드 — 인당 1카드
# ══════════════════════════════════════════════════════════════════════════════

def _layout_c_css(size: str) -> str:
    if size == "card":
        return """
<style>
@page { size: 90mm 50mm; margin: 0; }
.card-c { width: 90mm; height: 50mm; padding: 2mm; overflow: hidden; position: relative; page-break-after: always; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8mm; }
.person-card { border: 0.2mm solid #aaa; padding: 0.8mm; font-size: 6pt; line-height: 1.25; overflow: hidden; max-height: 10mm; }
</style>"""
    else:
        return """
<style>
@page { size: 90mm 100mm; margin: 0; }
.card-c { width: 90mm; height: 50mm; padding: 2mm; overflow: hidden; position: relative; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8mm; }
.person-card { border: 0.2mm solid #aaa; padding: 0.8mm; font-size: 6pt; line-height: 1.25; overflow: hidden; max-height: 10mm; }
.double-page { width: 90mm; height: 100mm; page-break-after: always; }
</style>"""


def _layout_c_panel(members: list[dict], show_title: bool = True, show_footer: bool = False) -> str:
    cards = ""
    for m in members:
        name_style = "font-weight:700; font-size:6pt"
        if m.get("is_tbd"):
            name_style += "; color:#999"
        nm = _t(m['name'], 6)
        ph = _t(m.get('phone', ''), 13)
        em = _t(m.get('email', ''), 14)
        cards += f"""
        <div class="person-card">
            <div style="font-size:5pt; color:#666">{m['cohort']}</div>
            <div style="{name_style}">{nm}</div>
            <div>{ph}</div>
            <div style="color:#555">{em}</div>
        </div>"""

    title = '<div style="text-align:center; font-size:7pt; font-weight:700; margin-bottom:1mm">재활의학과 주소록</div>' if show_title else ""
    return f"""
<div class="card-c">
    {title}
    <div class="grid">{cards}</div>
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
        html += '<div class="double-page">'
        html += _layout_c_panel(p1, show_title=True, show_footer=False)
        html += _fold_line()
        html += _layout_c_panel(p2, show_title=False, show_footer=False)
        html += '</div>'
        html += '<div class="double-page">'
        html += _layout_c_panel(p3, show_title=False, show_footer=False)
        html += _fold_line()
        html += _layout_c_panel(p4, show_title=False, show_footer=True)
        html += '</div>'

    return f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{html}</body></html>"


# ══════════════════════════════════════════════════════════════════════════════
# Layout D: 컴팩트 2단 — 이름+전화번호 2열 배치
# ══════════════════════════════════════════════════════════════════════════════

def _layout_d_css(size: str) -> str:
    if size == "card":
        return """
<style>
@page { size: 90mm 50mm; margin: 0; }
.card-d { width: 90mm; height: 50mm; padding: 2mm 3mm; overflow: hidden; position: relative; page-break-after: always; }
.two-col { column-count: 2; column-gap: 3mm; font-size: 6pt; line-height: 1.4; }
</style>"""
    else:
        return """
<style>
@page { size: 90mm 100mm; margin: 0; }
.card-d { width: 90mm; height: 50mm; padding: 2mm 3mm; overflow: hidden; position: relative; }
.two-col { column-count: 2; column-gap: 3mm; font-size: 6pt; line-height: 1.4; }
.double-page { width: 90mm; height: 100mm; page-break-after: always; }
</style>"""


def _layout_d_panel(members: list[dict], show_title: bool = True, show_footer: bool = False) -> str:
    items = ""
    prev_cohort = ""
    for m in members:
        if m["cohort"] != prev_cohort:
            if prev_cohort:
                items += '<div style="height:0.5mm"></div>'
            items += f'<div style="font-weight:700; font-size:6pt; border-bottom:0.2mm solid #000; margin-bottom:0.3mm">{m["cohort"]}</div>'
            prev_cohort = m["cohort"]

        name_style = "font-weight:600"
        if m.get("is_tbd"):
            name_style += "; color:#999"

        nm = _t(m['name'], 6)
        ph = _t(m.get("phone", ""), 13)
        items += f"""
        <div style="display:flex; justify-content:space-between; padding:0.2mm 0; font-size:6pt; overflow:hidden; height:2.8mm">
            <span style="{name_style}">{nm}</span>
            <span style="color:#333; white-space:nowrap; margin-left:1mm; flex-shrink:0">{ph}</span>
        </div>"""

    title = '<div style="text-align:center; font-size:7pt; font-weight:700; margin-bottom:1mm; border-bottom:0.4mm solid #000; padding-bottom:0.5mm">재활의학과 주소록</div>' if show_title else ""
    return f"""
<div class="card-d">
    {title}
    <div class="two-col">{items}</div>
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
        html += '<div class="double-page">'
        html += _layout_d_panel(p1, show_title=True, show_footer=False)
        html += _fold_line()
        html += _layout_d_panel(p2, show_title=False, show_footer=False)
        html += '</div>'
        html += '<div class="double-page">'
        html += _layout_d_panel(p3, show_title=False, show_footer=False)
        html += _fold_line()
        html += _layout_d_panel(p4, show_title=False, show_footer=True)
        html += '</div>'

    return f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{html}</body></html>"


# ── 통합 ──────────────────────────────────────────────────────────────────────

LAYOUTS = {
    "A: 개선된 표 형식": generate_layout_a,
    "B: 모던 클린": generate_layout_b,
    "C: 카드 그리드": generate_layout_c,
    "D: 컴팩트 2단": generate_layout_d,
}

SIZES = {
    "명함 (90×50mm 양면)": "card",
    "세로 더블카드 (90×100mm 4면 접이)": "double",
}
