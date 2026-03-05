# -*- coding: utf-8 -*-
"""인쇄용 HTML/CSS 레이아웃 생성기 — 4가지 디자인 × 2가지 규격"""

from modules.seed_data import FOOTER_DONG_UI, FOOTER_KOSIN

# ── 공통 CSS ──────────────────────────────────────────────────────────────────

_COMMON_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}

.no-print { display: block; text-align: center; padding: 10px; }
.print-btn {
    background: #1E88E5; color: #fff; border: none; padding: 10px 30px;
    border-radius: 6px; font-size: 14px; cursor: pointer; margin: 5px;
}
.print-btn:hover { background: #1565C0; }

@media print {
    .no-print { display: none !important; }
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


def _footer_block() -> str:
    return f"""
<div class="footer-info">
    <div class="footer-line">{FOOTER_DONG_UI}</div>
    <div class="footer-line">{FOOTER_KOSIN}</div>
</div>
"""


def _split_members(members: list[dict]) -> tuple[list[dict], list[dict]]:
    """회원을 두 그룹으로 분리: 앞면(2기~19기), 뒷면(Staff+21기~31기)."""
    side_a = [m for m in members if m["cohort_order"] > 0 and m["cohort_order"] <= 19]
    side_b = [m for m in members if m["cohort_order"] == 0 or m["cohort_order"] >= 21]
    return side_a, side_b


# ══════════════════════════════════════════════════════════════════════════════
# Layout A: 개선된 표 형식
# ══════════════════════════════════════════════════════════════════════════════

def _layout_a_css(size: str) -> str:
    if size == "card":
        return """
<style>
@page { size: 90mm 50mm; margin: 0; }
.card { width: 90mm; height: 50mm; padding: 2mm 3mm; page-break-after: always; overflow: hidden; }
</style>"""
    else:
        return """
<style>
@page { size: 90mm 100mm; margin: 0; }
.card { width: 90mm; height: 100mm; padding: 3mm 4mm; page-break-after: always; overflow: hidden; }
</style>"""


def _layout_a_table(members: list[dict], show_footer: bool = False) -> str:
    rows = ""
    for i, m in enumerate(members):
        bg = "#f8f9fa" if i % 2 == 0 else "#ffffff"
        name_display = m["name"]
        if m.get("is_tbd"):
            name_display = f'<span style="color:#999">{name_display}</span>'
        rows += f"""
        <tr style="background:{bg}">
            <td style="font-weight:500; white-space:nowrap">{m['cohort']}</td>
            <td style="font-weight:600">{name_display}</td>
            <td style="font-size:6pt; max-width:28mm; overflow:hidden; text-overflow:ellipsis">{m.get('workplace','')}</td>
            <td style="font-size:6pt">{m.get('email','')}</td>
            <td style="font-size:6pt">{m.get('license_no','')}</td>
            <td style="font-size:6pt; white-space:nowrap">{m.get('phone','')}</td>
        </tr>"""

    footer = ""
    if show_footer:
        footer = f"""
        <div style="position:absolute; bottom:1mm; left:3mm; right:3mm; font-size:5pt; color:#666; line-height:1.4">
            {FOOTER_DONG_UI}<br>{FOOTER_KOSIN}
        </div>"""

    return f"""
<div class="card" style="position:relative">
    <div style="text-align:center; font-size:8pt; font-weight:700; margin-bottom:1mm; color:#1E88E5">
        재활의학과 주소록
    </div>
    <table style="width:100%; border-collapse:collapse; font-size:6.5pt; line-height:1.3">
        <thead>
            <tr style="background:#1E88E5; color:#fff">
                <th style="padding:0.5mm 1mm; text-align:left">기수</th>
                <th style="padding:0.5mm 1mm; text-align:left">성명</th>
                <th style="padding:0.5mm 1mm; text-align:left">현근무지</th>
                <th style="padding:0.5mm 1mm; text-align:left">이메일</th>
                <th style="padding:0.5mm 1mm; text-align:left">면허</th>
                <th style="padding:0.5mm 1mm; text-align:left">전화번호</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    {footer}
</div>"""


def generate_layout_a(members: list[dict], size: str) -> str:
    side_a, side_b = _split_members(members)
    css = _COMMON_CSS + _layout_a_css(size)
    html = css + _header_html("Layout A: 개선된 표 형식")
    html += _layout_a_table(side_a, show_footer=False)
    html += _layout_a_table(side_b, show_footer=True)
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{html}</body></html>"


# ══════════════════════════════════════════════════════════════════════════════
# Layout B: 모던 클린
# ══════════════════════════════════════════════════════════════════════════════

def _layout_b_css(size: str) -> str:
    if size == "card":
        return """
<style>
@page { size: 90mm 50mm; margin: 0; }
.card-b { width: 90mm; height: 50mm; padding: 2mm 3mm; page-break-after: always; overflow: hidden; }
</style>"""
    else:
        return """
<style>
@page { size: 90mm 100mm; margin: 0; }
.card-b { width: 90mm; height: 100mm; padding: 3mm 4mm; page-break-after: always; overflow: hidden; }
</style>"""


def _layout_b_list(members: list[dict], show_footer: bool = False) -> str:
    items = ""
    prev_cohort = ""
    for m in members:
        cohort_label = ""
        if m["cohort"] != prev_cohort:
            cohort_label = f'<span style="display:inline-block; background:#E3F2FD; color:#1565C0; font-size:5.5pt; font-weight:600; padding:0.3mm 1.5mm; border-radius:1mm; margin-right:1mm">{m["cohort"]}</span>'
            prev_cohort = m["cohort"]
        else:
            cohort_label = '<span style="display:inline-block; width:8mm"></span>'

        name_style = "font-weight:600; font-size:7pt"
        if m.get("is_tbd"):
            name_style += "; color:#999"

        phone_display = m.get("phone", "")
        email_display = m.get("email", "")

        items += f"""
        <div style="display:flex; align-items:baseline; padding:0.3mm 0; border-bottom:0.2mm solid #f0f0f0">
            {cohort_label}
            <span style="{name_style}; min-width:10mm">{m['name']}</span>
            <span style="font-size:5.5pt; color:#666; margin-left:auto; white-space:nowrap">{phone_display}</span>
        </div>"""

    footer = ""
    if show_footer:
        footer = f"""
        <div style="position:absolute; bottom:1mm; left:3mm; right:3mm; font-size:5pt; color:#888; line-height:1.4; border-top:0.3mm solid #e0e0e0; padding-top:0.5mm">
            {FOOTER_DONG_UI}<br>{FOOTER_KOSIN}
        </div>"""

    return f"""
<div class="card-b" style="position:relative">
    <div style="font-size:8pt; font-weight:700; color:#333; margin-bottom:1.5mm; letter-spacing:0.5mm">
        재활의학과 주소록
    </div>
    {items}
    {footer}
</div>"""


def generate_layout_b(members: list[dict], size: str) -> str:
    side_a, side_b = _split_members(members)
    css = _COMMON_CSS + _layout_b_css(size)
    html = css + _header_html("Layout B: 모던 클린")
    html += _layout_b_list(side_a, show_footer=False)
    html += _layout_b_list(side_b, show_footer=True)
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{html}</body></html>"


# ══════════════════════════════════════════════════════════════════════════════
# Layout C: 카드 그리드
# ══════════════════════════════════════════════════════════════════════════════

def _layout_c_css(size: str) -> str:
    if size == "card":
        return """
<style>
@page { size: 90mm 50mm; margin: 0; }
.card-c { width: 90mm; height: 50mm; padding: 2mm; page-break-after: always; overflow: hidden; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1mm; }
.person-card {
    border: 0.2mm solid #e0e0e0; border-radius: 1mm; padding: 1mm;
    font-size: 5.5pt; line-height: 1.3; background: #fafafa;
}
</style>"""
    else:
        return """
<style>
@page { size: 90mm 100mm; margin: 0; }
.card-c { width: 90mm; height: 100mm; padding: 2mm; page-break-after: always; overflow: hidden; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1mm; }
.person-card {
    border: 0.2mm solid #e0e0e0; border-radius: 1mm; padding: 1.2mm;
    font-size: 5.5pt; line-height: 1.3; background: #fafafa;
}
</style>"""


def _layout_c_grid(members: list[dict], show_footer: bool = False) -> str:
    cards = ""
    for m in members:
        name_style = "font-weight:700; font-size:6.5pt; color:#1565C0"
        if m.get("is_tbd"):
            name_style += "; color:#999"
        cards += f"""
        <div class="person-card">
            <div style="font-size:5pt; color:#888">{m['cohort']}</div>
            <div style="{name_style}">{m['name']}</div>
            <div style="color:#555; font-size:5pt; overflow:hidden; text-overflow:ellipsis; white-space:nowrap">{m.get('phone','')}</div>
            <div style="color:#888; font-size:4.5pt; overflow:hidden; text-overflow:ellipsis; white-space:nowrap">{m.get('email','')}</div>
        </div>"""

    footer = ""
    if show_footer:
        footer = f"""
        <div style="position:absolute; bottom:1mm; left:2mm; right:2mm; font-size:4.5pt; color:#888; line-height:1.3">
            {FOOTER_DONG_UI}<br>{FOOTER_KOSIN}
        </div>"""

    return f"""
<div class="card-c" style="position:relative">
    <div style="text-align:center; font-size:7pt; font-weight:700; color:#1E88E5; margin-bottom:1mm">
        재활의학과 주소록
    </div>
    <div class="grid">{cards}</div>
    {footer}
</div>"""


def generate_layout_c(members: list[dict], size: str) -> str:
    side_a, side_b = _split_members(members)
    css = _COMMON_CSS + _layout_c_css(size)
    html = css + _header_html("Layout C: 카드 그리드")
    html += _layout_c_grid(side_a, show_footer=False)
    html += _layout_c_grid(side_b, show_footer=True)
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{html}</body></html>"


# ══════════════════════════════════════════════════════════════════════════════
# Layout D: 컴팩트 2단
# ══════════════════════════════════════════════════════════════════════════════

def _layout_d_css(size: str) -> str:
    if size == "card":
        return """
<style>
@page { size: 90mm 50mm; margin: 0; }
.card-d { width: 90mm; height: 50mm; padding: 2mm 3mm; page-break-after: always; overflow: hidden; }
.two-col { column-count: 2; column-gap: 3mm; font-size: 6pt; line-height: 1.4; }
</style>"""
    else:
        return """
<style>
@page { size: 90mm 100mm; margin: 0; }
.card-d { width: 90mm; height: 100mm; padding: 3mm 4mm; page-break-after: always; overflow: hidden; }
.two-col { column-count: 2; column-gap: 3mm; font-size: 6.5pt; line-height: 1.5; }
</style>"""


def _layout_d_columns(members: list[dict], show_footer: bool = False) -> str:
    items = ""
    prev_cohort = ""
    for m in members:
        if m["cohort"] != prev_cohort:
            if prev_cohort:
                items += '<div style="height:0.5mm"></div>'
            items += f'<div style="font-weight:700; color:#1565C0; font-size:5.5pt; border-bottom:0.2mm solid #1565C0; margin-bottom:0.3mm">{m["cohort"]}</div>'
            prev_cohort = m["cohort"]

        name_style = "font-weight:600"
        if m.get("is_tbd"):
            name_style += "; color:#999"

        phone = m.get("phone", "")
        items += f"""
        <div style="display:flex; justify-content:space-between; padding:0.2mm 0">
            <span style="{name_style}">{m['name']}</span>
            <span style="color:#555; font-size:5.5pt">{phone}</span>
        </div>"""

    footer = ""
    if show_footer:
        footer = f"""
        <div style="position:absolute; bottom:1mm; left:3mm; right:3mm; font-size:5pt; color:#888; line-height:1.3; column-span:all">
            {FOOTER_DONG_UI}<br>{FOOTER_KOSIN}
        </div>"""

    return f"""
<div class="card-d" style="position:relative">
    <div style="text-align:center; font-size:7.5pt; font-weight:700; color:#333; margin-bottom:1mm; border-bottom:0.3mm solid #333; padding-bottom:0.5mm">
        재활의학과 주소록
    </div>
    <div class="two-col">{items}</div>
    {footer}
</div>"""


def generate_layout_d(members: list[dict], size: str) -> str:
    side_a, side_b = _split_members(members)
    css = _COMMON_CSS + _layout_d_css(size)
    html = css + _header_html("Layout D: 컴팩트 2단")
    html += _layout_d_columns(side_a, show_footer=False)
    html += _layout_d_columns(side_b, show_footer=True)
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{html}</body></html>"


# ── 통합 생성 함수 ────────────────────────────────────────────────────────────

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
