import html
import io
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt  # Wajib ada untuk fungsi mewarna jadual (background_gradient)
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import plotly.colors
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dashboard Analisis Denggi", layout="wide")

MS_PER_DAY = 24 * 60 * 60 * 1000

# --- CSS KHUSUS UNTUK CETAKAN PDF, JADUAL STATUS WABAK & TOOLTIP METRIK ---
st.markdown(
    """
    <style>
    @media print {
        header {visibility: hidden;}
        section[data-testid="stSidebar"] {display: none;}
        .stButton > button {display: none;}
        footer {visibility: hidden;}
        .stAlert {page-break-inside: avoid;}
        .metric-tooltip-bubble {display: none !important;}
        .metric-hover-card {padding: 0 !important; box-shadow: none !important; background: transparent !important;}
        .no-print {display: none !important;}
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        padding: 8px;
        text-align: center;
        border: 1px solid #ddd;
    }
    .stApp {
        transition: background-color 0.5s ease;
    }
    /* Jadual STATUS WABAK (DENGGI) - Sama seperti paparan WhatsApp */
    .sw-wrapper {
        width: 100%;
        overflow-x: auto;
        background: #ffffff;
        padding: 6px;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    .sw-title-banner {
        background-color: #eadbe2;
        color: #111111;
        font-weight: 800;
        font-size: 1.25rem;
        text-align: center;
        padding: 8px 12px;
        border: 1px solid #333333;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .sw-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, Helvetica, sans-serif;
        font-size: 0.84rem;
        color: #000000;
        margin-bottom: 14px;
    }
    .sw-table:last-child {
        margin-bottom: 0;
    }
    .sw-table th, .sw-table td {
        border: 1px solid #333333;
        padding: 5px 8px;
        color: #000000;
        vertical-align: middle;
    }
    .sw-sec-tamat {
        background-color: #980000 !important;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 0.92rem;
        text-align: center;
        padding: 6px 8px !important;
    }
    .sw-sec-aktif {
        background-color: #733f0d !important;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 0.92rem;
        text-align: center;
        padding: 6px 8px !important;
    }
    .sw-col-hdr {
        background-color: #f9ca9c !important;
        color: #000000 !important;
        font-weight: 700;
        text-align: center !important;
        line-height: 1.25;
    }
    .sw-tiada {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: 700;
        text-align: center !important;
        padding: 7px !important;
    }
    .sw-lok-link {
        cursor: pointer;
        text-align: left !important;
        background-color: #ffffff !important;
        transition: background-color 0.15s ease, color 0.15s ease;
    }
    .sw-lok-link:hover {
        background-color: #eff6ff !important;
        color: #1d4ed8 !important;
        text-decoration: underline;
    }
    /* Sembunyikan butang pencetus navigasi SW_JUMP_* sepenuhnya */
    [class*="st-key-sw_jump_trigger_"] {
        position: fixed !important;
        left: -9999px !important;
        top: -9999px !important;
        width: 1px !important;
        height: 1px !important;
        overflow: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Kad metrik interaktif dengan kesan tonasi & gelembung info */
    .metric-hover-card {
        position: relative;
        padding: 4px 10px 8px 10px;
        border-radius: 10px;
        transition: background-color 0.25s ease, box-shadow 0.25s ease;
        cursor: help;
    }
    .metric-hover-card:hover {
        background-color: rgba(255, 75, 75, 0.08);
        box-shadow: 0 0 0 1px rgba(255, 75, 75, 0.35);
    }
    .metric-hover-label {
        font-size: 0.875rem;
        line-height: 1.4;
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .metric-hover-badge {
        font-size: 0.72rem;
        opacity: 0.7;
        border: 1px solid currentColor;
        border-radius: 50%;
        width: 15px;
        height: 15px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
    }
    .metric-hover-value {
        font-size: 2.25rem;
        font-weight: 400;
        line-height: 1.2;
    }
    .metric-tooltip-bubble {
        visibility: hidden;
        opacity: 0;
        position: absolute;
        top: calc(100% + 8px);
        right: 0;
        width: 350px;
        max-width: 85vw;
        background-color: #1e2430;
        color: #f8fafc;
        padding: 14px 16px;
        border-radius: 10px;
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.28);
        border: 1px solid rgba(255, 255, 255, 0.14);
        font-size: 0.82rem;
        line-height: 1.5;
        text-align: left;
        z-index: 9999;
        pointer-events: none;
        transform: translateY(-4px);
        transition: opacity 0.2s ease, transform 0.2s ease, visibility 0.2s ease;
    }
    .metric-hover-card:hover .metric-tooltip-bubble {
        visibility: visible;
        opacity: 1;
        transform: translateY(0);
    }
    .tooltip-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #fca5a5;
        margin-bottom: 6px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.12);
        padding-bottom: 4px;
    }
    .tooltip-section {
        margin-bottom: 6px;
    }
    .tooltip-formula {
        background-color: rgba(255, 255, 255, 0.08);
        padding: 5px 8px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 0.8rem;
        color: #fde68a;
        margin: 4px 0 6px 0;
    }
    .tooltip-current {
        background-color: rgba(56, 189, 248, 0.14);
        border-left: 3px solid #38bdf8;
        padding: 6px 8px;
        border-radius: 4px;
        margin-top: 6px;
        color: #e0f2fe;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_today_malaysia():
    """Mengesan tarikh semasa secara automatik mengikut zon waktu Malaysia (Asia/Kuala_Lumpur)."""
    try:
        return pd.Timestamp.now(tz="Asia/Kuala_Lumpur").tz_localize(None).normalize()
    except Exception:
        return pd.Timestamp.today().normalize()


def format_wabak_no(val):
    """Memformat nombor wabak supaya bersih tanpa '.0' di hujung."""
    try:
        f_val = float(val)
        if f_val.is_integer():
            return str(int(f_val))
        return str(f_val)
    except Exception:
        return str(val).strip()


def format_kaw_jagaan(val):
    s = str(val).strip().upper()
    if "DEWAN BANDARAYA" in s or "DBKL" in s:
        return "DBKL"
    if "PKD" in s or "KKM" in s or "KESIHATAN" in s:
        return "KKM"
    return s if s and s != "NAN" else "-"


def format_parlimen(val):
    s = str(val).strip().upper()
    s = s.replace("PARLIMEN ", "").strip()
    if "BANDAR TUN RAZAK" in s or s == "BTR":
        return "BTR"
    return s if s and s != "NAN" else "-"


def fmt_date_short(dt):
    if pd.isna(dt):
        return "-"
    return f"{dt.day}/{dt.month}/{dt.year}"


def get_status_bg(st_str):
    s = str(st_str).upper()
    if "HOTSPOT" in s:
        return "#fe0000"
    if "TAK TERKAWAL" in s:
        return "#3e85c7"
    if "TERKAWAL" in s:
        return "#f4cccc"
    if "TAMAT" in s:
        return "#b6d7a8"
    return "#ffffff"


def get_kaw_bg(k_str):
    k = str(k_str).upper()
    if k == "DBKL":
        return "#a2c4e5"
    if k == "KKM":
        return "#b6d7a8"
    return "#ffffff"


def get_parl_bg(p_str):
    p = str(p_str).upper()
    if p == "BTR":
        return "#b4a7d6"
    if p == "CHERAS":
        return "#ffd966"
    return "#ffffff"


def build_status_wabak_tables(df, report_date):
    """Menjana jadual WABAK TAMAT dan SENARAI WABAK AKTIF mengikut logik harian."""
    report_date = pd.Timestamp(report_date).normalize()
    current_year = report_date.year

    df_w = df[df["Jenis Kes"] == "Wabak"].dropna(subset=["Wabak No"]).copy()
    if df_w.empty:
        return pd.DataFrame(), pd.DataFrame()

    if (
        "Epid Tahun (Tkh Daftar)" in df_w.columns
        and df_w["Epid Tahun (Tkh Daftar)"].notna().any()
    ):
        df_w["_yr"] = pd.to_numeric(
            df_w["Epid Tahun (Tkh Daftar)"], errors="coerce"
        ).fillna(df_w["Tarikh Daftar"].dt.year)
    else:
        fallback_dt = (
            df_w["Tkh Notifikasi"].fillna(df_w["Tarikh Daftar"])
            if "Tkh Notifikasi" in df_w.columns
            else df_w["Tarikh Daftar"]
        )
        df_w["_yr"] = fallback_dt.dt.year

    df_w_yr = df_w[df_w["_yr"] == current_year]
    ep_count_map = (
        df_w_yr.groupby("Lokaliti (Alamat Semasa)")["Wabak No"].nunique().to_dict()
    )

    tamat_rows = []
    aktif_rows = []

    status_rank_map = {
        "WABAK TERKAWAL": 0,
        "WABAK TAK TERKAWAL": 1,
        "HOTSPOT": 2,
    }

    for (w_no, lok), grp in df_w.groupby(["Wabak No", "Lokaliti (Alamat Semasa)"]):
        raw_status = (
            str(grp["Wabak Status"].dropna().iloc[0]).strip()
            if grp["Wabak Status"].notna().any()
            else "Wabak Terkawal"
        )
        status_upper = raw_status.upper()

        if "Tkh Notifikasi" in grp.columns:
            t_series = (
                grp["Tkh Notifikasi"]
                .fillna(grp["Tarikh Daftar"])
                .dropna()
                .sort_values()
                .tolist()
            )
        else:
            t_series = grp["Tarikh Daftar"].dropna().sort_values().tolist()

        if not t_series:
            continue

        t_mula = t_series[1] if len(t_series) >= 2 else t_series[0]
        t_last = max(t_series)
        t_tamat = t_last + pd.Timedelta(days=14)

        kaw_val = (
            format_kaw_jagaan(grp["Pihak Pentadbir Lokaliti"].dropna().iloc[0])
            if "Pihak Pentadbir Lokaliti" in grp.columns
            and grp["Pihak Pentadbir Lokaliti"].notna().any()
            else "-"
        )
        parl_val = (
            format_parlimen(grp["Mukim/Zon (Alamat Semasa)"].dropna().iloc[0])
            if "Mukim/Zon (Alamat Semasa)" in grp.columns
            and grp["Mukim/Zon (Alamat Semasa)"].notna().any()
            else "-"
        )
        jumlah_kes = len(grp)
        bil_episod = int(ep_count_map.get(lok, 1))

        if "TAMAT" in status_upper:
            if t_tamat.normalize() == report_date:
                tempoh = max((t_tamat - t_mula).days, 1)
                tamat_rows.append(
                    {
                        "Wabak No": w_no,
                        "STATUS WABAK": "WABAK TAMAT",
                        "KAW JAGAAN": kaw_val,
                        "PARLIMEN": parl_val,
                        "LOKALITI": str(lok).strip(),
                        "JUMLAH KES": jumlah_kes,
                        "BIL EPISOD": bil_episod,
                        "TEMPOH WABAK": tempoh,
                        "TARIKH MULA": fmt_date_short(t_mula),
                        "TARIKH TAMAT": fmt_date_short(t_tamat),
                        "_rank": 0,
                    }
                )
        else:
            tempoh = max((report_date - t_mula).days, 1)
            aktif_rows.append(
                {
                    "Wabak No": w_no,
                    "STATUS WABAK": status_upper,
                    "KAW JAGAAN": kaw_val,
                    "PARLIMEN": parl_val,
                    "LOKALITI": str(lok).strip(),
                    "JUMLAH KES": jumlah_kes,
                    "BIL EPISOD": bil_episod,
                    "TEMPOH WABAK": tempoh,
                    "TARIKH MULA": fmt_date_short(t_mula),
                    "TARIKH TAMAT": fmt_date_short(t_tamat),
                    "_rank": status_rank_map.get(status_upper, 3),
                }
            )

    df_tamat = pd.DataFrame(tamat_rows)
    if not df_tamat.empty:
        df_tamat = df_tamat.sort_values(
            by=["KAW JAGAAN", "PARLIMEN", "LOKALITI"]
        ).reset_index(drop=True)
        df_tamat["BIL"] = range(1, len(df_tamat) + 1)

    df_aktif = pd.DataFrame(aktif_rows)
    if not df_aktif.empty:
        df_aktif = df_aktif.sort_values(
            by=["_rank", "KAW JAGAAN", "PARLIMEN", "LOKALITI"]
        ).reset_index(drop=True)
        df_aktif["BIL"] = df_aktif.groupby("STATUS WABAK").cumcount() + 1

    return df_tamat, df_aktif


def render_status_wabak_html(df_tamat, df_aktif):
    """Membina paparan jadual HTML STATUS WABAK (DENGGI) dengan lokaliti boleh klik."""
    clickable_rows = []
    row_idx = 0

    header_cells = (
        '<th class="sw-col-hdr" style="width:42px;">BIL</th>'
        '<th class="sw-col-hdr" style="width:165px;">STATUS WABAK</th>'
        '<th class="sw-col-hdr" style="width:95px;">KAW JAGAAN</th>'
        '<th class="sw-col-hdr" style="width:95px;">PARLIMEN</th>'
        '<th class="sw-col-hdr">LOKALITI</th>'
        '<th class="sw-col-hdr" style="width:72px;">JUMLAH<br>KES</th>'
        '<th class="sw-col-hdr" style="width:70px;">BIL<br>EPISOD</th>'
        '<th class="sw-col-hdr" style="width:74px;">TEMPOH<br>WABAK</th>'
        '<th class="sw-col-hdr" style="width:86px;">TARIKH<br>MULA</th>'
        '<th class="sw-col-hdr" style="width:86px;">TARIKH<br>TAMAT</th>'
    )

    def build_rows_html(df_sec):
        nonlocal row_idx
        if df_sec is None or df_sec.empty:
            return '<tr><td colspan="10" class="sw-tiada">TIADA</td></tr>'
        html_parts = []
        for _, r in df_sec.iterrows():
            st_val = str(r["STATUS WABAK"])
            kaw_val = str(r["KAW JAGAAN"])
            parl_val = str(r["PARLIMEN"])
            lok_val = str(r["LOKALITI"])
            s_bg = get_status_bg(st_val)
            k_bg = get_kaw_bg(kaw_val)
            p_bg = get_parl_bg(parl_val)

            clickable_rows.append((lok_val, r["Wabak No"]))
            cur_idx = row_idx
            row_idx += 1

            html_parts.append(
                f"<tr>"
                f'<td style="background-color:{s_bg}; text-align:right;">{int(r["BIL"])}</td>'
                f'<td style="background-color:{s_bg}; text-align:left;">{html.escape(st_val)}</td>'
                f'<td style="background-color:{k_bg}; text-align:center;">{html.escape(kaw_val)}</td>'
                f'<td style="background-color:{p_bg}; text-align:center;">{html.escape(parl_val)}</td>'
                f'<td class="sw-lok-link" data-sw-idx="{cur_idx}" title="Klik untuk melihat analisis terperinci bagi {html.escape(lok_val)}">{html.escape(lok_val)}</td>'
                f'<td style="background-color:#ffffff; text-align:right;">{int(r["JUMLAH KES"])}</td>'
                f'<td style="background-color:#ffffff; text-align:right;">{int(r["BIL EPISOD"])}</td>'
                f'<td style="background-color:#ffffff; text-align:right;">{int(r["TEMPOH WABAK"])}</td>'
                f'<td style="background-color:#ffffff; text-align:right;">{html.escape(str(r["TARIKH MULA"]))}</td>'
                f'<td style="background-color:#ffffff; text-align:right;">{html.escape(str(r["TARIKH TAMAT"]))}</td>'
                f"</tr>"
            )
        return "".join(html_parts)

    tamat_body = build_rows_html(df_tamat)
    aktif_body = build_rows_html(df_aktif)

    table_html = (
        '<div class="sw-wrapper">'
        '<div class="sw-title-banner">STATUS WABAK (DENGGI)</div>'
        '<table class="sw-table">'
        '<thead>'
        '<tr><th colspan="10" class="sw-sec-tamat">WABAK TAMAT</th></tr>'
        f"<tr>{header_cells}</tr>"
        '</thead>'
        f"<tbody>{tamat_body}</tbody>"
        "</table>"
        '<table class="sw-table">'
        '<thead>'
        '<tr><th colspan="10" class="sw-sec-aktif">SENARAI WABAK AKTIF</th></tr>'
        f"<tr>{header_cells}</tr>"
        '</thead>'
        f"<tbody>{aktif_body}</tbody>"
        "</table>"
        "</div>"
    )
    return table_html, clickable_rows


def render_status_wabak_png(df_tamat, df_aktif):
    """Menjana gambar PNG resolusi tinggi jadual STATUS WABAK (DENGGI) untuk perkongsian WhatsApp."""
    font_dir = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
    font_reg_path = os.path.join(font_dir, "DejaVuSans.ttf")
    font_bold_path = os.path.join(font_dir, "DejaVuSans-Bold.ttf")

    scale = 2
    f_title = ImageFont.truetype(font_bold_path, 17 * scale)
    f_sec = ImageFont.truetype(font_bold_path, 12 * scale)
    f_hdr = ImageFont.truetype(font_bold_path, 10 * scale)
    f_cell = ImageFont.truetype(font_reg_path, 10 * scale)
    f_cell_bold = ImageFont.truetype(font_bold_path, 10 * scale)

    col_widths = [w * scale for w in [42, 165, 92, 92, 439, 70, 68, 72, 80, 80]]
    total_w = sum(col_widths)

    headers = [
        ["BIL"],
        ["STATUS WABAK"],
        ["KAW JAGAAN"],
        ["PARLIMEN"],
        ["LOKALITI"],
        ["JUMLAH", "KES"],
        ["BIL", "EPISOD"],
        ["TEMPOH", "WABAK"],
        ["TARIKH", "MULA"],
        ["TARIKH", "TAMAT"],
    ]

    h_title = 34 * scale
    h_gap = 6 * scale
    h_sec = 24 * scale
    h_hdr = 34 * scale
    h_row = 24 * scale
    h_tiada = 26 * scale
    h_section_space = 22 * scale
    pad = 8 * scale

    n_tamat = len(df_tamat) if df_tamat is not None and not df_tamat.empty else 0
    n_aktif = len(df_aktif) if df_aktif is not None and not df_aktif.empty else 0

    tamat_body_h = (n_tamat * h_row) if n_tamat > 0 else h_tiada
    aktif_body_h = (n_aktif * h_row) if n_aktif > 0 else h_tiada

    total_h = (
        pad * 2
        + h_title
        + h_gap
        + h_sec
        + h_hdr
        + tamat_body_h
        + h_section_space
        + h_sec
        + h_hdr
        + aktif_body_h
    )

    img = Image.new("RGB", (total_w + pad * 2, total_h), "#ffffff")
    draw = ImageDraw.Draw(img)
    border_col = "#333333"
    lw = max(1, scale // 2)

    def draw_centered_text(box, lines, font, fill="#000000"):
        x1, y1, x2, y2 = box
        line_heights = []
        for ln in lines:
            bbox = draw.textbbox((0, 0), ln, font=font)
            line_heights.append(bbox[3] - bbox[1])
        spacing = 3 * scale
        tot_th = sum(line_heights) + spacing * (len(lines) - 1)
        cur_y = y1 + ((y2 - y1) - tot_th) / 2
        for idx, ln in enumerate(lines):
            bbox = draw.textbbox((0, 0), ln, font=font)
            tw = bbox[2] - bbox[0]
            tx = x1 + ((x2 - x1) - tw) / 2
            draw.text((tx, cur_y), ln, font=font, fill=fill)
            cur_y += line_heights[idx] + spacing

    def draw_left_text(box, text, font, fill="#000000", left_pad=8):
        x1, y1, x2, y2 = box
        bbox = draw.textbbox((0, 0), text, font=font)
        th = bbox[3] - bbox[1]
        ty = y1 + ((y2 - y1) - th) / 2
        draw.text((x1 + left_pad * scale, ty), text, font=font, fill=fill)

    def draw_right_text(box, text, font, fill="#000000", right_pad=8):
        x1, y1, x2, y2 = box
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = x2 - tw - right_pad * scale
        ty = y1 + ((y2 - y1) - th) / 2
        draw.text((tx, ty), text, font=font, fill=fill)

    y = pad
    x0 = pad
    x_end = pad + total_w

    draw.rectangle(
        [x0, y, x_end, y + h_title], fill="#eadbe2", outline=border_col, width=lw
    )
    draw_centered_text(
        (x0, y, x_end, y + h_title), ["STATUS WABAK (DENGGI)"], f_title, "#111111"
    )
    y += h_title + h_gap

    def draw_section(sec_title, sec_bg, df_sec):
        nonlocal y
        draw.rectangle(
            [x0, y, x_end, y + h_sec], fill=sec_bg, outline=border_col, width=lw
        )
        draw_centered_text((x0, y, x_end, y + h_sec), [sec_title], f_sec, "#ffffff")
        y += h_sec

        cx = x0
        for cw, h_lines in zip(col_widths, headers):
            draw.rectangle(
                [cx, y, cx + cw, y + h_hdr], fill="#f9ca9c", outline=border_col, width=lw
            )
            draw_centered_text((cx, y, cx + cw, y + h_hdr), h_lines, f_hdr, "#000000")
            cx += cw
        y += h_hdr

        if df_sec is None or df_sec.empty:
            draw.rectangle(
                [x0, y, x_end, y + h_tiada], fill="#ffffff", outline=border_col, width=lw
            )
            draw_centered_text(
                (x0, y, x_end, y + h_tiada), ["TIADA"], f_cell_bold, "#000000"
            )
            y += h_tiada
        else:
            for _, r in df_sec.iterrows():
                cx = x0
                st_val = str(r["STATUS WABAK"])
                kaw_val = str(r["KAW JAGAAN"])
                parl_val = str(r["PARLIMEN"])
                s_color = get_status_bg(st_val)

                row_specs = [
                    (str(int(r["BIL"])), s_color, "right", f_cell),
                    (st_val, s_color, "left", f_cell),
                    (kaw_val, get_kaw_bg(kaw_val), "center", f_cell),
                    (parl_val, get_parl_bg(parl_val), "center", f_cell),
                    (str(r["LOKALITI"]), "#ffffff", "left", f_cell),
                    (str(int(r["JUMLAH KES"])), "#ffffff", "right", f_cell),
                    (str(int(r["BIL EPISOD"])), "#ffffff", "right", f_cell),
                    (str(int(r["TEMPOH WABAK"])), "#ffffff", "right", f_cell),
                    (str(r["TARIKH MULA"]), "#ffffff", "right", f_cell),
                    (str(r["TARIKH TAMAT"]), "#ffffff", "right", f_cell),
                ]

                for cw, (txt, bg, align, fnt) in zip(col_widths, row_specs):
                    draw.rectangle(
                        [cx, y, cx + cw, y + h_row],
                        fill=bg,
                        outline=border_col,
                        width=lw,
                    )
                    box = (cx, y, cx + cw, y + h_row)
                    if align == "center":
                        draw_centered_text(box, [txt], fnt, "#000000")
                    elif align == "right":
                        draw_right_text(box, txt, fnt, "#000000")
                    else:
                        draw_left_text(box, txt, fnt, "#000000")
                    cx += cw
                y += h_row

    draw_section("WABAK TAMAT", "#980000", df_tamat)
    y += h_section_space
    draw_section("SENARAI WABAK AKTIF", "#733f0d", df_aktif)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def read_raw_bytes(raw_bytes, file_name):
    """Membaca fail Excel (.xlsx, .xls) dan CSV (Microsoft Excel Comma Separated Values File) secara automatik."""
    file_name = file_name.lower()
    df = None

    def try_read_csv(data_bytes):
        encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
        for enc in encodings:
            try:
                temp_df = pd.read_csv(
                    io.BytesIO(data_bytes), encoding=enc, sep=None, engine="python"
                )
                if temp_df is not None and len(temp_df.columns) > 1:
                    return temp_df
            except Exception:
                continue
        return None

    if file_name.endswith(".csv"):
        df = try_read_csv(raw_bytes)
        if df is None:
            raise ValueError(
                "Fail CSV tidak dapat dibaca. Sila pastikan format lajur adalah sah."
            )
    else:
        try:
            df = pd.read_excel(io.BytesIO(raw_bytes))
        except Exception:
            df = try_read_csv(raw_bytes)
            if df is None:
                html_tables = pd.read_html(io.BytesIO(raw_bytes))
                if html_tables:
                    df = html_tables[0]

    if df is None or df.empty:
        raise ValueError("Fail kosong atau tidak mengandungi data.")

    df.columns = df.columns.astype(str).str.strip()

    if "Tarikh Daftar" not in df.columns and "Lokaliti (Alamat Semasa)" not in df.columns:
        for i in range(min(10, len(df))):
            row_vals = [str(v).strip() for v in df.iloc[i].values]
            if "Tarikh Daftar" in row_vals or "Lokaliti (Alamat Semasa)" in row_vals:
                df.columns = row_vals
                df = df.iloc[i + 1 :].reset_index(drop=True)
                break

    if "Wabak No" in df.columns:
        df["Wabak No"] = pd.to_numeric(df["Wabak No"], errors="coerce")

    for col in ["Jenis Kes", "Wabak Status", "Lokaliti (Alamat Semasa)"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .replace({"nan": pd.NA, "None": pd.NA, "": pd.NA})
            )

    date_cols = [
        "Tarikh Daftar",
        "Tarikh Onset",
        "Tkh Notifikasi",
        "Tkh PTP Aktiviti Pertama",
        "Tkh SRT Aktiviti Pertama",
        "Tkh ULV Aktiviti Pertama",
    ]
    for date_col in date_cols:
        if date_col in df.columns:
            try:
                df[date_col] = pd.to_datetime(
                    df[date_col], format="mixed", dayfirst=True, errors="coerce"
                )
            except Exception:
                df[date_col] = pd.to_datetime(
                    df[date_col], dayfirst=True, errors="coerce"
                )

    return df


def load_data(uploaded_file):
    return read_raw_bytes(uploaded_file.getvalue(), uploaded_file.name)


@st.cache_data(show_spinner="Memuatkan pangkalan data sejarah 5 tahun...")
def load_historical_data():
    """Mencari dan memuatkan fail data sejarah 5 tahun yang disimpan dalam repositori."""
    candidate_files = [
        "data_sejarah.csv",
        "data_sejarah.xlsx",
        "data_sejarah.xls",
        "historical_data.csv",
        "historical_data.xlsx",
    ]
    for fname in candidate_files:
        if os.path.exists(fname):
            with open(fname, "rb") as f:
                df_hist = read_raw_bytes(f.read(), fname)
            return df_hist, fname
    return None, None


def merge_datasets(df_hist, df_current):
    """Menggabungkan data sejarah 5 tahun dengan data tahun semasa tanpa rekod berganda."""
    if df_hist is None and df_current is None:
        return None
    if df_hist is None:
        return df_current.copy()
    if df_current is None:
        return df_hist.copy()

    combined = pd.concat([df_hist, df_current], ignore_index=True)

    if "Notifikasi No" in combined.columns and combined["Notifikasi No"].notna().any():
        combined["Notifikasi No"] = combined["Notifikasi No"].astype(str).str.strip()
        combined = combined.drop_duplicates(subset=["Notifikasi No"], keep="last")
    elif "Kes No" in combined.columns and combined["Kes No"].notna().any():
        combined["Kes No"] = combined["Kes No"].astype(str).str.strip()
        combined = combined.drop_duplicates(subset=["Kes No"], keep="last")
    else:
        dedup_cols = [
            c
            for c in ["Lokaliti (Alamat Semasa)", "Tarikh Daftar", "No Rumah", "Wabak No"]
            if c in combined.columns
        ]
        if dedup_cols:
            combined = combined.drop_duplicates(subset=dedup_cols, keep="last")

    return combined.reset_index(drop=True)


def parse_address(address):
    address = str(address).upper()
    blok, tingkat = "TIDAK PASTI", "TIDAK PASTI"

    match1 = re.search(r"([A-Z0-9]+)\s*-\s*(\d+)\s*-\s*\d+", address)
    if match1:
        blok, tingkat = match1.group(1), match1.group(2)
    else:
        match_blok = re.search(r"(?:BLOK|BLOCK)\s*([A-Z0-9]+)", address)
        if match_blok:
            blok = match_blok.group(1)
        match_tingkat = re.search(r"(?:TINGKAT|LEVEL|TGKT)\s*(\d+)", address)
        if match_tingkat:
            tingkat = match_tingkat.group(1)

    if blok != "TIDAK PASTI":
        blok_clean = re.sub(r"^0+", "", blok)
        blok = blok_clean if blok_clean else "0"

    if tingkat != "TIDAK PASTI":
        tingkat_clean = re.sub(r"^0+", "", tingkat)
        tingkat = tingkat_clean if tingkat_clean else "0"

    return pd.Series([blok, tingkat])


# =========================================================
# ENJIN AI EPIDEMIOLOGI BERASASKAN DATA (ZERO-HALLUCINATION)
# =========================================================
def compute_ai_epidemiological_analytics(df, df_lok, pilihan_lokaliti, today_my):
    """Mengira ramalan 4 minggu (95% CI), matriks risiko eskalasi, korelasi operasi & pelan tindakan terus daripada data."""
    df_calc = df.copy()
    df_calc["_yr"] = pd.to_numeric(
        df_calc.get("Epid Tahun (Tkh Daftar)", pd.Series(dtype=float)), errors="coerce"
    ).fillna(df_calc["Tarikh Daftar"].dt.year)
    df_calc["_me"] = pd.to_numeric(
        df_calc.get("Epid Minggu (Tkh Daftar)", pd.Series(dtype=float)), errors="coerce"
    )

    valid_w = df_calc.dropna(subset=["_yr", "_me"]).copy()
    valid_w["_yr"] = valid_w["_yr"].astype(int)
    valid_w["_me"] = valid_w["_me"].astype(int)

    weekly_df = (
        valid_w.groupby(["_yr", "_me"])
        .size()
        .reset_index(name="Kes")
        .sort_values(["_yr", "_me"])
        .reset_index(drop=True)
    )
    weekly_df["Minggu"] = (
        weekly_df["_yr"].astype(str)
        + "-ME"
        + weekly_df["_me"].astype(str).str.zfill(2)
    )

    # 1. Ramalan Trend 4 Minggu (OLS + Selang Keyakinan 95%)
    forecast_rows = []
    slope_per_week = 0.0
    if len(weekly_df) >= 4:
        recent = weekly_df.tail(min(12, len(weekly_df))).copy()
        x = np.arange(len(recent), dtype=float)
        y = recent["Kes"].values.astype(float)
        slope_per_week, intercept = np.polyfit(x, y, 1)
        y_hat = intercept + slope_per_week * x
        resid = y - y_hat
        dof = max(len(x) - 2, 1)
        s_err = float(np.sqrt(np.sum(resid**2) / dof))
        x_mean = float(np.mean(x))
        sxx = float(np.sum((x - x_mean) ** 2))
        t_crit = 2.228 if dof >= 10 else (2.306 if dof >= 8 else 2.776)

        last_yr = int(recent["_yr"].iloc[-1])
        last_me = int(recent["_me"].iloc[-1])

        for step in range(1, 5):
            xf = float(len(recent) - 1 + step)
            yf = max(0.0, float(intercept + slope_per_week * xf))
            se_pred = s_err * np.sqrt(
                1.0 + 1.0 / len(x) + ((xf - x_mean) ** 2) / max(sxx, 1e-6)
            )
            ci_low = max(0.0, yf - t_crit * se_pred)
            ci_high = yf + t_crit * se_pred

            f_me = last_me + step
            f_yr = last_yr
            if f_me > 52:
                f_me -= 52
                f_yr += 1
            forecast_rows.append(
                {
                    "Minggu": f"{f_yr}-ME{f_me:02d}",
                    "Unjuran Kes": round(yf, 1),
                    "95% CI Bawah": round(ci_low, 1),
                    "95% CI Atas": round(ci_high, 1),
                }
            )
    df_forecast = pd.DataFrame(forecast_rows)

    # 2. Korelasi Operasi & Kelewatan Kawalan Vektor
    lag_specs = [
        ("Onset → Notifikasi", "Tarikh Onset", "Tkh Notifikasi"),
        ("Notifikasi → PTP (Larviciding)", "Tkh Notifikasi", "Tkh PTP Aktiviti Pertama"),
        ("Notifikasi → SRT (Fogging)", "Tkh Notifikasi", "Tkh SRT Aktiviti Pertama"),
        ("Notifikasi → ULV", "Tkh Notifikasi", "Tkh ULV Aktiviti Pertama"),
    ]
    lag_summary = []
    for label, c_start, c_end in lag_specs:
        if c_start in df_calc.columns and c_end in df_calc.columns:
            diff_days = (df_calc[c_end] - df_calc[c_start]).dt.days
            valid_d = diff_days[(diff_days >= 0) & (diff_days <= 60)].dropna()
            if not valid_d.empty:
                lag_summary.append(
                    {
                        "Metrik Kelewatan": label,
                        "Median (Hari)": round(float(valid_d.median()), 1),
                        "Purata (Hari)": round(float(valid_d.mean()), 1),
                        "Sampel Kes (n)": int(len(valid_d)),
                    }
                )
    df_lags = pd.DataFrame(lag_summary)

    # Perbandingan kelengahan mengikut Status Wabak
    status_comp_rows = []
    df_w_all = df_calc[df_calc["Jenis Kes"] == "Wabak"].dropna(subset=["Wabak No"]).copy()
    if not df_w_all.empty:
        if "Tarikh Onset" in df_w_all.columns and "Tkh Notifikasi" in df_w_all.columns:
            df_w_all["_onset_lag"] = (
                df_w_all["Tkh Notifikasi"] - df_w_all["Tarikh Onset"]
            ).dt.days
        else:
            df_w_all["_onset_lag"] = np.nan

        if (
            "Tkh Notifikasi" in df_w_all.columns
            and "Tkh SRT Aktiviti Pertama" in df_w_all.columns
        ):
            df_w_all["_srt_lag"] = (
                df_w_all["Tkh SRT Aktiviti Pertama"] - df_w_all["Tkh Notifikasi"]
            ).dt.days
        else:
            df_w_all["_srt_lag"] = np.nan

        for st_name, grp in df_w_all.groupby("Wabak Status"):
            o_valid = grp["_onset_lag"][
                (grp["_onset_lag"] >= 0) & (grp["_onset_lag"] <= 45)
            ].dropna()
            s_valid = grp["_srt_lag"][
                (grp["_srt_lag"] >= 0) & (grp["_srt_lag"] <= 45)
            ].dropna()
            status_comp_rows.append(
                {
                    "Status Wabak": str(st_name),
                    "Bil. Episod": int(grp["Wabak No"].nunique()),
                    "Purata Kes / Episod": round(
                        len(grp) / max(grp["Wabak No"].nunique(), 1), 1
                    ),
                    "Purata Lengah Onset→Notif (Hari)": round(float(o_valid.mean()), 1)
                    if not o_valid.empty
                    else None,
                    "Purata Lengah Notif→SRT (Hari)": round(float(s_valid.mean()), 1)
                    if not s_valid.empty
                    else None,
                }
            )
    df_status_corr = pd.DataFrame(status_comp_rows)

    # 3. Matriks Risiko Eskalasi Wabak Aktif & Unjuran 14 Hari (95% CI Poisson)
    active_risk_rows = []
    df_act = df_w_all[
        ~df_w_all["Wabak Status"].astype(str).str.contains("Tamat", case=False, na=False)
    ].copy()
    if not df_act.empty:
        for (w_no, lok), grp in df_act.groupby(["Wabak No", "Lokaliti (Alamat Semasa)"]):
            st_w = str(grp["Wabak Status"].iloc[0])
            t_ser = (
                grp["Tkh Notifikasi"].fillna(grp["Tarikh Daftar"])
                if "Tkh Notifikasi" in grp.columns
                else grp["Tarikh Daftar"]
            )
            t_list = t_ser.dropna().sort_values().tolist()
            if not t_list:
                continue
            t_mula = t_list[1] if len(t_list) >= 2 else t_list[0]
            tempoh = max((today_my - t_mula).days, 1)
            kes = len(grp)
            vel = kes / tempoh
            c_7d = int((t_ser >= (today_my - pd.Timedelta(days=7))).sum())
            c_prev7d = int(
                (
                    (t_ser < (today_my - pd.Timedelta(days=7)))
                    & (t_ser >= (today_my - pd.Timedelta(days=14)))
                ).sum()
            )
            rate_daily = max(c_7d / 7.0, vel * 0.5)
            proj_14d = rate_daily * 14.0
            ci_l = max(0.0, proj_14d - 1.96 * np.sqrt(max(proj_14d, 0.5)))
            ci_u = proj_14d + 1.96 * np.sqrt(max(proj_14d, 0.5))

            # Skor Risiko Eskalasi (0 - 100) berasaskan Velocity, Kes 7 Hari Terkini, Tempoh & Status
            risk_score = min(
                100,
                int(
                    round(
                        min(vel * 35, 35)
                        + min(c_7d * 8, 30)
                        + min(tempoh * 0.6, 20)
                        + (
                            15
                            if "HOTSPOT" in st_w.upper()
                            else (10 if "TAK TERKAWAL" in st_w.upper() else 0)
                        )
                    )
                ),
            )
            risk_tier = (
                "KRITIKAL"
                if risk_score >= 70
                else ("TINGGI" if risk_score >= 45 else "SEDERHANA")
            )

            active_risk_rows.append(
                {
                    "No. Wabak": format_wabak_no(w_no),
                    "Lokaliti": str(lok).strip(),
                    "Status Semasa": st_w,
                    "Jumlah Kes": kes,
                    "Tempoh (Hari)": tempoh,
                    "Velocity (Kes/Hari)": round(vel, 2),
                    "Kes 7 Hari Terkini": c_7d,
                    "Kes 7-14 Hari Lalu": c_prev7d,
                    "Unjuran +14 Hari": round(proj_14d, 1),
                    "95% CI (+14 Hari)": f"{ci_l:.1f} – {ci_u:.1f}",
                    "Skor Risiko": risk_score,
                    "Tahap Risiko": risk_tier,
                }
            )
    df_active_risk = pd.DataFrame(active_risk_rows)
    if not df_active_risk.empty:
        df_active_risk = df_active_risk.sort_values(
            by=["Skor Risiko", "Velocity (Kes/Hari)"], ascending=False
        ).reset_index(drop=True)

    # 4. Ringkasan Spesifik Lokaliti Dipilih untuk Pelan Tindakan
    lok_summary = {}
    if df_lok is not None and not df_lok.empty and pilihan_lokaliti:
        df_l = df_lok.copy()
        df_l[["_Blok", "_Tingkat"]] = df_l["No Rumah"].apply(parse_address)
        valid_bt = df_l[(df_l["_Blok"] != "TIDAK PASTI") & (df_l["_Tingkat"] != "TIDAK PASTI")]
        top_cluster = "Tiada kluster bertingkat dikenal pasti"
        if not valid_bt.empty:
            grp_bt = valid_bt.groupby(["_Blok", "_Tingkat"]).size().sort_values(ascending=False)
            top_b, top_t = grp_bt.index[0]
            top_cluster = f"Blok {top_b}, Tingkat {top_t} ({int(grp_bt.iloc[0])} kes)"

        top_occ = (
            str(df_l["Pekerjaan"].dropna().mode().iloc[0])
            if "Pekerjaan" in df_l.columns and not df_l["Pekerjaan"].dropna().empty
            else "Tidak Dinyatakan"
        )
        top_nat = (
            str(df_l["Status Kewarganegaraan"].dropna().mode().iloc[0])
            if "Status Kewarganegaraan" in df_l.columns
            and not df_l["Status Kewarganegaraan"].dropna().empty
            else "Tidak Dinyatakan"
        )
        med_age = (
            round(float(pd.to_numeric(df_l["Umur (Tahun)"], errors="coerce").median()), 1)
            if "Umur (Tahun)" in df_l.columns
            and pd.to_numeric(df_l["Umur (Tahun)"], errors="coerce").notna().any()
            else None
        )
        lok_summary = {
            "lokaliti": pilihan_lokaliti,
            "jumlah_kes_sejarah": int(len(df_l)),
            "bil_episod_wabak": int(
                df_l[df_l["Jenis Kes"] == "Wabak"]["Wabak No"].dropna().nunique()
            ),
            "kluster_utama": top_cluster,
            "pekerjaan_dominan": top_occ,
            "kewarganegaraan_dominan": top_nat,
            "median_umur": med_age,
        }

    return {
        "weekly_df": weekly_df,
        "df_forecast": df_forecast,
        "slope_per_week": slope_per_week,
        "df_lags": df_lags,
        "df_status_corr": df_status_corr,
        "df_active_risk": df_active_risk,
        "lok_summary": lok_summary,
    }


def generate_grounded_ai_response(question, analytics, today_my, provider, api_key):
    """Menjana jawapan berpandukan data sebenar tanpa halusinasi (menggunakan LLM percuma jika tersedia, atau enjin analitik terbina dalam)."""
    q_lower = question.lower().strip()
    df_forecast = analytics["df_forecast"]
    df_lags = analytics["df_lags"]
    df_status_corr = analytics["df_status_corr"]
    df_active_risk = analytics["df_active_risk"]
    lok_sum = analytics["lok_summary"]
    slope = analytics["slope_per_week"]

    # Bina konteks fakta 100% sahih daripada data
    fact_packet = {
        "tarikh_laporan": fmt_date_short(today_my),
        "trend_mingguan_kes_per_minggu": round(slope, 2),
        "ramalan_4_minggu_95CI": df_forecast.to_dict(orient="records")
        if not df_forecast.empty
        else [],
        "kelewatan_operasi": df_lags.to_dict(orient="records")
        if not df_lags.empty
        else [],
        "perbandingan_status_wabak": df_status_corr.to_dict(orient="records")
        if not df_status_corr.empty
        else [],
        "wabak_aktif_risiko_tertinggi": df_active_risk.head(8).to_dict(orient="records")
        if not df_active_risk.empty
        else [],
        "ringkasan_lokaliti_dipilih": lok_sum,
    }

    # Jika pengguna memasukkan kunci API percuma (Personal Gmail Gemini Thinking / Groq / OpenRouter)
    if api_key and api_key.strip():
        system_prompt = (
            "Anda ialah Pakar Epidemiologi Denggi KKM. Jawab soalan pengguna HANYA berdasarkan fakta "
            "dan angka dalam JSON DATA_SAHIH di bawah. JANGAN reka atau anggar sebarang angka yang tiada "
            "dalam JSON. Nyatakan Selang Keyakinan 95% (95% CI) apabila membincangkan ramalan. Jawab dalam "
            "Bahasa Melayu yang jelas, berstruktur dan praktikal untuk tindakan lapangan."
        )
        user_prompt = (
            f"DATA_SAHIH:\n{json.dumps(fact_packet, ensure_ascii=False, indent=2)}\n\n"
            f"SOALAN PENGGUNA: {question}"
        )

        try:
            key_clean = api_key.strip()
            if provider == "Gemini Thinking (Personal Gmail AI Studio)":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key_clean}"
                payload = {
                    "systemInstruction": {"parts": [{"text": system_prompt}]},
                    "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                    "generationConfig": {
                        "temperature": 0.0,
                        "thinkingConfig": {"thinkingBudget": 1024},
                    },
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=25) as resp:
                    res_json = json.loads(resp.read().decode("utf-8"))
                parts = (
                    res_json.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [])
                )
                text_out = "\n".join(
                    p.get("text", "") for p in parts if not p.get("thought", False)
                ).strip()
                if text_out:
                    return text_out, "Gemini 2.5 Flash Thinking (Grounded on Data)"

            elif provider in ("Groq (Free Tier)", "OpenRouter (Free Tier)"):
                if provider == "Groq (Free Tier)":
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    model_name = "llama-3.3-70b-versatile"
                else:
                    url = "https://openrouter.ai/api/v1/chat/completions"
                    model_name = "google/gemini-2.5-flash:free"
                payload = {
                    "model": model_name,
                    "temperature": 0.0,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {key_clean}",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=25) as resp:
                    res_json = json.loads(resp.read().decode("utf-8"))
                text_out = (
                    res_json.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )
                if text_out:
                    return text_out, f"{provider} (Grounded on Data)"
        except urllib.error.HTTPError as he:
            if he.code == 429:
                st.warning(
                    "⚠️ Had kuota percuma API dicapai buat sementara waktu (akan reset secara automatik). Paparan beralih kepada Enjin AI Analitik Terbina Dalam (100% bebas had & sifar halusinasi)."
                )
            else:
                st.warning(
                    f"⚠️ Sambungan API tidak tersedia (Kod {he.code}). Paparan menggunakan Enjin AI Analitik Terbina Dalam."
                )
        except Exception:
            st.warning(
                "⚠️ Menggunakan Enjin AI Analitik Terbina Dalam (100% berasaskan data)."
            )

    # Fallback / Enjin Analitik Terbina Dalam (100% Berasaskan Data, Tanpa API)
    lines = []
    if any(k in q_lower for k in ["ramal", "predict", "forecast", "ci", "trend", "minggu"]):
        arah = "menurun" if slope < -0.2 else ("meningkat" if slope > 0.2 else "mendatar")
        lines.append(
            f"### 📈 Ramalan Epidemiologi 4 Minggu Hadapan (Selang Keyakinan 95%)\n"
            f"- **Kadar Perubahan Mingguan Semasa:** **{slope:+.2f} kes/minggu** (trend keseluruhan sedang **{arah}**)."
        )
        if not df_forecast.empty:
            for _, r in df_forecast.iterrows():
                lines.append(
                    f"- **{r['Minggu']}:** Unjuran **{r['Unjuran Kes']} kes** *(95% CI: {r['95% CI Bawah']} – {r['95% CI Atas']} kes)*"
                )
        if not df_active_risk.empty:
            top_r = df_active_risk.iloc[0]
            lines.append(
                f"\n**Lokaliti Risiko Tertinggi (+14 Hari):** **{top_r['Lokaliti']}** ({top_r['Status Semasa']}) dengan unjuran **{top_r['Unjuran +14 Hari']} kes baharu** *(95% CI: {top_r['95% CI (+14 Hari)']})*."
            )

    elif any(k in q_lower for k in ["korelasi", "correlation", "punca", "lewat", "lag", "sebab"]):
        lines.append("### 🔗 Analisis Korelasi & Kelewatan Operasi Kawalan")
        if not df_lags.empty:
            for _, r in df_lags.iterrows():
                lines.append(
                    f"- **{r['Metrik Kelewatan']}:** Median **{r['Median (Hari)']} hari** (Purata **{r['Purata (Hari)']} hari**, n={r['Sampel Kes (n)']})"
                )
        if not df_status_corr.empty:
            lines.append("\n**Perbandingan Mengikut Status Wabak:**")
            for _, r in df_status_corr.iterrows():
                o_txt = (
                    f"{r['Purata Lengah Onset→Notif (Hari)']} hari"
                    if pd.notna(r["Purata Lengah Onset→Notif (Hari)"])
                    else "N/A"
                )
                s_txt = (
                    f"{r['Purata Lengah Notif→SRT (Hari)']} hari"
                    if pd.notna(r["Purata Lengah Notif→SRT (Hari)"])
                    else "N/A"
                )
                lines.append(
                    f"- **{r['Status Wabak']}** ({r['Bil. Episod']} episod, purata **{r['Purata Kes / Episod']} kes/episod**): Lengah Onset→Notifikasi = **{o_txt}**, Lengah Notifikasi→SRT = **{s_txt}**."
                )

    else:
        # Pelan Tindakan Taktikal & Ringkasan Menyeluruh
        lok_name = lok_sum.get("lokaliti", "Lokaliti Dipilih")
        lines.append(f"### 🎯 Pelan Tindakan Taktikal & Analisis Data: {lok_name}")
        if lok_sum:
            umur_txt = (
                f"{lok_sum['median_umur']} tahun"
                if lok_sum.get("median_umur") is not None
                else "Tidak Dinyatakan"
            )
            lines.append(
                f"- **Profil Lokaliti:** **{lok_sum['jumlah_kes_sejarah']} kes** direkodkan merentasi **{lok_sum['bil_episod_wabak']} episod wabak**. Kluster struktur utama tertumpu di **{lok_sum['kluster_utama']}**."
            )
            lines.append(
                f"- **Demografi Sasaran:** Kumpulan dominan ialah **{lok_sum['kewarganegaraan_dominan']}**, pekerjaan **{lok_sum['pekerjaan_dominan']}** (median umur **{umur_txt}**)."
            )
        if not df_active_risk.empty:
            top3 = df_active_risk.head(3)
            lines.append("\n**Keutamaan Intervensi Lapangan (Top 3 Risiko Eskalasi):**")
            for _, r in top3.iterrows():
                lines.append(
                    f"1. **{r['Lokaliti']}** (*{r['Status Semasa']}* | Skor Risiko **{r['Skor Risiko']}/100**): {r['Jumlah Kes']} kes dalam {r['Tempoh (Hari)']} hari (Velocity **{r['Velocity (Kes/Hari)']} kes/hari**). Unjuran +14 hari: **{r['Unjuran +14 Hari']} kes** *(95% CI: {r['95% CI (+14 Hari)']})*."
                )
        lines.append(
            "\n**Cadangan Tindakan Operasi (Berdasarkan Data):**\n"
            "- **Pemusnahan Tempat Pembiakan (PTP / S&D):** Fokus radius 200m bermula dari blok & tingkat kluster utama dalam tempoh **< 48 jam** selepas notifikasi.\n"
            "- **Semburan Ruang Termal (SRT) & ULV:** Laksanakan kitaran ulangan pada hari ke-7 hingga ke-10 bagi lokaliti dengan kes aktif dalam 7 hari terakhir untuk memutuskan rantaian generasi kedua nyamuk *Aedes*.\n"
            "- **Pengesanan Kes Aktif (ACD) & Promosi Kesihatan:** Sasar kumpulan demografi/pekerjaan dominan bagi mengurangkan tempoh lengah dari mula gejala (`Tarikh Onset`) ke fasiliti kesihatan."
        )

    return "\n".join(lines), "Enjin Analitik Statistik Terbina Dalam (100% Data-Driven, Tanpa API)"


# --- PENGURUSAN STATE (MEMORI APLIKASI) ---
if "selected_lokaliti" not in st.session_state:
    st.session_state.selected_lokaliti = None
if "selected_wabak" not in st.session_state:
    st.session_state.selected_wabak = None
if "episode_filter" not in st.session_state:
    st.session_state.episode_filter = "Semua"
if "scroll_to_analisis" not in st.session_state:
    st.session_state.scroll_to_analisis = False
if "ai_custom_question" not in st.session_state:
    st.session_state.ai_custom_question = "Jana pelan tindakan taktikal dan ramalan risiko wabak semasa."


def set_lokaliti_dan_wabak(lokaliti, wabak_no):
    st.session_state.selected_lokaliti = lokaliti
    st.session_state.selected_wabak = f"Wabak No: {format_wabak_no(wabak_no)}"
    st.session_state.episode_filter = "Semua"


def jump_to_lokaliti_from_table(lokaliti, wabak_no):
    st.session_state.selected_lokaliti = lokaliti
    st.session_state.selected_wabak = f"Wabak No: {format_wabak_no(wabak_no)}"
    st.session_state.episode_filter = "Semua"
    st.session_state.scroll_to_analisis = True


def set_lokaliti_sahaja(lokaliti):
    st.session_state.selected_lokaliti = lokaliti
    st.session_state.selected_wabak = None
    st.session_state.episode_filter = "Semua"


def set_chart_year_range(state_key, start_yr, end_yr):
    st.session_state[state_key] = (start_yr, end_yr)


def set_ai_prompt(prompt_text):
    st.session_state.ai_custom_question = prompt_text


# --- ANTARA MUKA UTAMA ---
st.title("🦟 Dashboard Analisis Kes Denggi (Spesifik Wabak)")

today_my = get_today_malaysia()

# Muatkan data sejarah 5 tahun secara automatik jika wujud dalam sistem
df_hist, hist_filename = load_historical_data()

if df_hist is not None:
    min_yr = (
        int(df_hist["Tarikh Daftar"].dt.year.min())
        if df_hist["Tarikh Daftar"].notna().any()
        else "Sejarah"
    )
    max_yr = (
        int(df_hist["Tarikh Daftar"].dt.year.max())
        if df_hist["Tarikh Daftar"].notna().any()
        else "Terkini"
    )
    st.info(
        f"🗄️ **Pangkalan Data Sejarah Aktif:** `{hist_filename}` ({len(df_hist):,} rekod kes dari tahun **{min_yr} – {max_yr}**) telah dimuatkan secara automatik. Muat naik fail harian **2026** di bawah untuk menggabungkan data terkini."
    )
else:
    st.warning(
        "ℹ️ Fail sejarah 5 tahun (`data_sejarah.csv` / `data_sejarah.xlsx`) belum ditemui dalam repositori. Anda masih boleh memuat naik fail data di bawah seperti biasa."
    )

uploaded_file = st.file_uploader(
    "Muat Naik Fail Harian Tahun Semasa (2026) - Format Excel atau CSV",
    type=["xlsx", "xls", "csv"],
)

if uploaded_file is not None or df_hist is not None:
    try:
        df_current = load_data(uploaded_file) if uploaded_file is not None else None
        df = merge_datasets(df_hist, df_current)

        if uploaded_file is not None and df_hist is not None:
            st.success(
                f"✅ **Data Digabungkan:** Rekod sejarah 5 tahun + fail terkini `{uploaded_file.name}` berjaya disatukan (**{len(df):,} jumlah rekod**)."
            )

        # --- PENGIRAAN KEKERAPAN EPISODE WABAK KESELURUHAN ---
        df_wabak_sahaja = df[df["Jenis Kes"] == "Wabak"].dropna(subset=["Wabak No"])
        kekerapan_wabak = df_wabak_sahaja.groupby("Lokaliti (Alamat Semasa)")[
            "Wabak No"
        ].nunique()
        semua_lokaliti_list = sorted(df["Lokaliti (Alamat Semasa)"].dropna().unique())
        episode_map = {lok: kekerapan_wabak.get(lok, 0) for lok in semua_lokaliti_list}

        # ---------------------------------------------------------
        # PENGURUSAN MENU SIDEBAR
        # ---------------------------------------------------------
        st.sidebar.header("Tetapan Analisis")

        episodes_ada = sorted(list(set(episode_map.values())))
        pilihan_tapis_ep = ["Semua"] + [
            f"{int(e)} Episode" for e in episodes_ada if e > 0
        ]

        try:
            ep_idx = pilihan_tapis_ep.index(st.session_state.episode_filter)
        except ValueError:
            ep_idx = 0

        pilihan_filter_episode = st.sidebar.selectbox(
            "1. Tapis Kekerapan (Episode):", pilihan_tapis_ep, index=ep_idx
        )
        st.session_state.episode_filter = pilihan_filter_episode

        if pilihan_filter_episode == "Semua":
            senarai_lokaliti_tapis = semua_lokaliti_list
        else:
            ep_val = int(pilihan_filter_episode.split()[0])
            senarai_lokaliti_tapis = sorted(
                [lok for lok, count in episode_map.items() if count == ep_val]
            )

        if not senarai_lokaliti_tapis:
            st.sidebar.warning("Tiada lokaliti untuk kategori ini.")
            pilihan_lokaliti = None
            df_lok = pd.DataFrame()
        else:
            index_lokaliti = 0
            if st.session_state.selected_lokaliti in senarai_lokaliti_tapis:
                index_lokaliti = senarai_lokaliti_tapis.index(
                    st.session_state.selected_lokaliti
                )

            pilihan_lokaliti = st.sidebar.selectbox(
                "2. Pilih Lokaliti", senarai_lokaliti_tapis, index=index_lokaliti
            )

            if pilihan_lokaliti != st.session_state.selected_lokaliti:
                st.session_state.selected_lokaliti = pilihan_lokaliti
                st.session_state.selected_wabak = None

            df_lok = df[df["Lokaliti (Alamat Semasa)"] == pilihan_lokaliti].copy()

        pilihan_kategori = None
        if not df_lok.empty:
            pilihan_wabak_list = []
            df_w_only = df_lok[df_lok["Jenis Kes"] == "Wabak"].dropna(subset=["Wabak No"])
            if not df_w_only.empty:
                wabak_ordered = (
                    df_w_only.groupby("Wabak No")["Tarikh Daftar"]
                    .max()
                    .sort_values(ascending=False)
                    .index.tolist()
                )
                for w in wabak_ordered:
                    pilihan_wabak_list.append(f"Wabak No: {format_wabak_no(w)}")

            if "Satu Kes" in df_lok["Jenis Kes"].values:
                pilihan_wabak_list.append("Satu Kes (Kes Terpencil)")

            index_wabak = 0
            if st.session_state.selected_wabak in pilihan_wabak_list:
                index_wabak = pilihan_wabak_list.index(st.session_state.selected_wabak)

            pilihan_kategori = st.sidebar.selectbox(
                "3. Kategori Kes/Wabak:", pilihan_wabak_list, index=index_wabak
            )
            st.session_state.selected_wabak = pilihan_kategori

        # --- FUNGSI MUAT TURUN PDF ---
        st.sidebar.markdown("---")
        if st.sidebar.button("🖨️ Muat Turun / Cetak PDF"):
            components.html(
                """
                <script>
                window.parent.print();
                </script>
                """,
                height=0,
            )
        st.sidebar.markdown(
            "*Tekan butang di atas dan pilih 'Save as PDF' sebagai destinasi cetakan.*"
        )
        st.sidebar.markdown("---")

        # --- TETAPAN AI PERCUMA (PILIHAN - TIADA API DIPERLUKAN) ---
        with st.sidebar.expander("🧠 Tetapan AI Thinking (Pilihan Percuma)"):
            st.caption(
                "Tanpa kunci API, dashboard tetap menjalankan Enjin AI Statistik & Ramalan 95% CI terbina dalam secara percuma. Jika mahu huraian LLM percuma (auto-reset kuota harian), masukkan kunci API dari akaun Gmail peribadi (`aistudio.google.com`), Groq, atau OpenRouter."
            )
            ai_provider = st.selectbox(
                "Penyedia AI Percuma:",
                [
                    "Enjin AI Statistik Terbina Dalam (Tanpa API)",
                    "Gemini Thinking (Personal Gmail AI Studio)",
                    "Groq (Free Tier)",
                    "OpenRouter (Free Tier)",
                ],
                key="ai_provider_choice",
            )
            ai_api_key = ""
            if ai_provider != "Enjin AI Statistik Terbina Dalam (Tanpa API)":
                ai_api_key = st.text_input(
                    "Kunci API Percuma:",
                    type="password",
                    placeholder="Tampal kunci API percuma di sini...",
                    key="ai_free_api_key",
                )

        # ---------------------------------------------------------
        # JADUAL HARIAN: STATUS WABAK (DENGGI) - INTERAKTIF & WHATSAPP EXPORT
        # ---------------------------------------------------------
        st.markdown("---")
        df_sw_tamat, df_sw_aktif = build_status_wabak_tables(df, today_my)
        sw_png_bytes = render_status_wabak_png(df_sw_tamat, df_sw_aktif)
        sw_html, sw_clickable_rows = render_status_wabak_html(df_sw_tamat, df_sw_aktif)

        bar_c1, bar_c2, bar_c3 = st.columns([2.2, 2.2, 2.6])
        with bar_c1:
            st.download_button(
                label="📸 Muat Turun Gambar Table (WhatsApp)",
                data=sw_png_bytes,
                file_name=f"Status_Wabak_Denggi_{today_my.strftime('%d-%m-%Y')}.png",
                mime="image/png",
                use_container_width=True,
            )
        with bar_c2:
            with st.popover(
                "🖼️ Paparan Screenshot Penuh (WhatsApp)", use_container_width=True
            ):
                st.caption(
                    "Klik kanan pada gambar di bawah dan pilih **Copy Image** atau **Save Image As** untuk terus tampal ke WhatsApp."
                )
                st.image(sw_png_bytes, use_container_width=True)
        with bar_c3:
            st.markdown(
                f'<div class="no-print" style="text-align:right; padding-top:8px; font-size:0.88rem; opacity:0.85;">'
                f'📅 <b>Tarikh Laporan (Auto):</b> {fmt_date_short(today_my)}  |  <i>Klik nama lokaliti untuk analisis</i>'
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown(sw_html, unsafe_allow_html=True)

        if sw_clickable_rows:
            for idx_sw, (lok_sw, w_no_sw) in enumerate(sw_clickable_rows):
                st.button(
                    f"SW_JUMP_{idx_sw}",
                    key=f"sw_jump_trigger_{idx_sw}_{format_wabak_no(w_no_sw)}",
                    on_click=jump_to_lokaliti_from_table,
                    args=(lok_sw, w_no_sw),
                )

            components.html(
                """
                <script>
                (function() {
                    const doc = window.parent.document;

                    function hideJumpButtons() {
                        const buttons = doc.querySelectorAll('button');
                        buttons.forEach(btn => {
                            if (btn.innerText && btn.innerText.trim().startsWith('SW_JUMP_')) {
                                const container = btn.closest('[data-testid="stElementContainer"], .element-container') || btn.parentElement;
                                if (container) {
                                    container.style.cssText = 'position:fixed;left:-9999px;top:-9999px;width:1px;height:1px;overflow:hidden;opacity:0;pointer-events:none;margin:0;padding:0;';
                                }
                            }
                        });
                    }

                    function bindTableClicks() {
                        hideJumpButtons();
                        const cells = doc.querySelectorAll('.sw-lok-link[data-sw-idx]');
                        cells.forEach(cell => {
                            if (cell.dataset.swBound === '1') return;
                            cell.dataset.swBound = '1';
                            cell.addEventListener('click', function() {
                                const idx = this.getAttribute('data-sw-idx');
                                const targetLabel = 'SW_JUMP_' + idx;
                                const buttons = doc.querySelectorAll('button');
                                for (const btn of buttons) {
                                    if (btn.innerText && btn.innerText.trim() === targetLabel) {
                                        btn.click();
                                        break;
                                    }
                                }
                            });
                        });
                    }

                    bindTableClicks();
                    const timer = setInterval(bindTableClicks, 250);
                    setTimeout(() => clearInterval(timer), 6000);
                })();
                </script>
                """,
                height=0,
            )

        # ---------------------------------------------------------
        # PUSAT ANALISIS AI & RAMALAN EPIDEMIOLOGI (DATA-DRIVEN, ZERO-HALLUCINATION)
        # ---------------------------------------------------------
        st.markdown("---")
        st.header("🧠 Pusat Analisis AI & Ramalan Epidemiologi (Data-Driven)")
        st.caption(
            "Semua ramalan, selang keyakinan 95% (95% CI), korelasi operasi, dan pelan tindakan dijana terus daripada data sebenar tanpa halusinasi."
        )

        ai_analytics = compute_ai_epidemiological_analytics(
            df, df_lok, pilihan_lokaliti, today_my
        )

        ai_tab1, ai_tab2, ai_tab3 = st.tabs(
            [
                "📈 Ramalan Trend & 95% Confidence Interval",
                "🔗 Korelasi Data & Kelewatan Operasi",
                "🎯 Soal Jawab AI & Pelan Tindakan",
            ]
        )

        with ai_tab1:
            col_ai_f1, col_ai_f2 = st.columns([1.45, 1.0])

            with col_ai_f1:
                weekly_df = ai_analytics["weekly_df"]
                df_forecast = ai_analytics["df_forecast"]
                if not weekly_df.empty and not df_forecast.empty:
                    hist_tail = weekly_df.tail(16)
                    fig_fc = go.Figure()
                    fig_fc.add_trace(
                        go.Scatter(
                            x=hist_tail["Minggu"],
                            y=hist_tail["Kes"],
                            mode="lines+markers",
                            name="Kes Sebenar (Mingguan)",
                            line=dict(color="#2563eb", width=2.5),
                            marker=dict(size=7),
                        )
                    )
                    # Sambungkan titik terakhir sebenar ke ramalan
                    conn_x = [hist_tail["Minggu"].iloc[-1]] + df_forecast[
                        "Minggu"
                    ].tolist()
                    conn_y = [float(hist_tail["Kes"].iloc[-1])] + df_forecast[
                        "Unjuran Kes"
                    ].tolist()
                    conn_hi = [float(hist_tail["Kes"].iloc[-1])] + df_forecast[
                        "95% CI Atas"
                    ].tolist()
                    conn_lo = [float(hist_tail["Kes"].iloc[-1])] + df_forecast[
                        "95% CI Bawah"
                    ].tolist()

                    fig_fc.add_trace(
                        go.Scatter(
                            x=conn_x + conn_x[::-1],
                            y=conn_hi + conn_lo[::-1],
                            fill="toself",
                            fillcolor="rgba(239, 68, 68, 0.16)",
                            line=dict(color="rgba(255,255,255,0)"),
                            hoverinfo="skip",
                            name="Selang Keyakinan 95% (95% CI)",
                        )
                    )
                    fig_fc.add_trace(
                        go.Scatter(
                            x=conn_x,
                            y=conn_y,
                            mode="lines+markers",
                            name="Unjuran AI (4 Minggu)",
                            line=dict(color="#dc2626", width=2.5, dash="dash"),
                            marker=dict(size=8, symbol="diamond"),
                        )
                    )
                    fig_fc.update_layout(
                        title="Unjuran Kes Mingguan (4 Minggu Hadapan dengan 95% CI)",
                        xaxis_title="Minggu Epid",
                        yaxis_title="Jumlah Kes",
                        height=380,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                    )
                    st.plotly_chart(
                        fig_fc, use_container_width=True, key="ai_forecast_chart"
                    )
                    st.dataframe(
                        df_forecast, use_container_width=True, hide_index=True
                    )
                else:
                    st.info(
                        "Data mingguan tidak mencukupi untuk menjana unjuran 4 minggu."
                    )

            with col_ai_f2:
                df_ar = ai_analytics["df_active_risk"]
                if not df_ar.empty:
                    fig_risk = px.scatter(
                        df_ar,
                        x="Tempoh (Hari)",
                        y="Velocity (Kes/Hari)",
                        size="Unjuran +14 Hari",
                        color="Status Semasa",
                        hover_name="Lokaliti",
                        hover_data={
                            "No. Wabak": True,
                            "Jumlah Kes": True,
                            "Unjuran +14 Hari": True,
                            "95% CI (+14 Hari)": True,
                            "Skor Risiko": True,
                        },
                        color_discrete_map={
                            "Wabak Terkawal": "#e06666",
                            "Wabak Tak Terkawal": "#3e85c7",
                            "Hotspot": "#fe0000",
                        },
                        title="Matriks Risiko Eskalasi Wabak Aktif",
                    )
                    fig_risk.update_layout(
                        height=380,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                    )
                    st.plotly_chart(
                        fig_risk, use_container_width=True, key="ai_risk_scatter"
                    )
                    st.dataframe(
                        df_ar[
                            [
                                "Lokaliti",
                                "Tahap Risiko",
                                "Skor Risiko",
                                "Unjuran +14 Hari",
                                "95% CI (+14 Hari)",
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.success("Tiada wabak aktif semasa untuk pemodelan risiko.")

        with ai_tab2:
            c_corr1, c_corr2 = st.columns(2)
            with c_corr1:
                st.markdown("**⏱️ Analisis Kelengahan Operasi Kawalan Vektor**")
                df_lags = ai_analytics["df_lags"]
                if not df_lags.empty:
                    fig_lag = px.bar(
                        df_lags,
                        x="Metrik Kelewatan",
                        y=["Median (Hari)", "Purata (Hari)"],
                        barmode="group",
                        text_auto=True,
                        color_discrete_sequence=["#0ea5e9", "#f59e0b"],
                    )
                    fig_lag.update_layout(
                        height=340,
                        xaxis_title="",
                        yaxis_title="Bilangan Hari",
                        legend_title="",
                    )
                    st.plotly_chart(
                        fig_lag, use_container_width=True, key="ai_lag_chart"
                    )
                    st.dataframe(df_lags, use_container_width=True, hide_index=True)
                else:
                    st.info("Kolum tarikh aktiviti PTP/SRT/ULV tidak lengkap.")

            with c_corr2:
                st.markdown("**📊 Korelasi Status Wabak vs Kelengahan & Saiz Kes**")
                df_sc = ai_analytics["df_status_corr"]
                if not df_sc.empty:
                    st.dataframe(df_sc, use_container_width=True, hide_index=True)
                    st.info(
                        "💡 **Penemuan Data:** Bandingkan *Purata Lengah Onset→Notif (Hari)* antara `Wabak Terkawal` dan `Wabak Tak Terkawal`. Kelewatan pesakit mendapatkan rawatan memanjangkan tempoh nyamuk *Aedes* menggigit pesakit viremia sebelum kawalan vektor dimulakan."
                    )
                else:
                    st.info("Tiada rekod wabak untuk perbandingan status.")

        with ai_tab3:
            q_cols = st.columns(3)
            with q_cols[0]:
                st.button(
                    "📈 Ramalan 4 Minggu & 95% CI",
                    key="btn_ai_q1",
                    on_click=set_ai_prompt,
                    args=(
                        "Berikan ramalan trend kes 4 minggu hadapan berserta Selang Keyakinan 95% (95% CI) dan lokaliti aktif paling berisiko.",
                    ),
                    use_container_width=True,
                )
            with q_cols[1]:
                st.button(
                    "🔗 Korelasi Kelewatan & Eskalasi",
                    key="btn_ai_q2",
                    on_click=set_ai_prompt,
                    args=(
                        "Apakah korelasi antara kelengahan notifikasi/kawalan vektor (PTP, SRT, ULV) dengan status wabak tidak terkawal?",
                    ),
                    use_container_width=True,
                )
            with q_cols[2]:
                st.button(
                    "🎯 Pelan Tindakan Lokaliti Ini",
                    key="btn_ai_q3",
                    on_click=set_ai_prompt,
                    args=(
                        f"Jana pelan tindakan operasi terperinci berdasarkan data bagi lokaliti {pilihan_lokaliti}.",
                    ),
                    use_container_width=True,
                )

            user_ai_q = st.text_input(
                "Tanya AI tentang data, korelasi, ramalan (95% CI) atau pelan tindakan:",
                key="ai_custom_question",
            )
            if user_ai_q:
                ai_answer, ai_engine_label = generate_grounded_ai_response(
                    user_ai_q, ai_analytics, today_my, ai_provider, ai_api_key
                )
                st.caption(f"⚙️ Sumber Analisis: **{ai_engine_label}**")
                st.markdown(ai_answer)

        # ---------------------------------------------------------
        # HIGHLIGHT 1: WABAK AKTIF SEMASA (TOP 5)
        # ---------------------------------------------------------
        df_aktif = df[
            (df["Jenis Kes"] == "Wabak")
            & (df["Wabak Status"].notna())
            & (
                ~df["Wabak Status"]
                .astype(str)
                .str.contains("Tamat", case=False, na=False)
            )
        ].copy()

        st.markdown("---")
        st.header("🚨 Highlight: Wabak Aktif Semasa (Top 5)")

        if not df_aktif.empty:
            data_wabak_aktif = []
            grouped = df_aktif.groupby(["Lokaliti (Alamat Semasa)", "Wabak No"])

            for (lokaliti, wabak_no), group in grouped:
                jumlah_k = len(group)
                tarikh_kes = group["Tarikh Daftar"].dropna().sort_values().tolist()

                if len(tarikh_kes) >= 2:
                    tarikh_mula = tarikh_kes[1]
                elif len(tarikh_kes) == 1:
                    tarikh_mula = tarikh_kes[0]
                else:
                    continue

                tempoh_h = (today_my - tarikh_mula).days
                tempoh_h = max(tempoh_h, 1)

                vel = jumlah_k / tempoh_h
                pct_inc = (vel / jumlah_k) * 100 if jumlah_k > 0 else 0

                data_wabak_aktif.append(
                    {
                        "Lokaliti": lokaliti,
                        "Wabak No": wabak_no,
                        "Jumlah Kes": jumlah_k,
                        "Tempoh (Hari)": tempoh_h,
                        "Kadar Peningkatan (%)": pct_inc,
                    }
                )

            df_highlight = pd.DataFrame(data_wabak_aktif)
            c1, c2, c3 = st.columns(3)

            with c1:
                st.subheader("🚀 Kadar Peningkatan (%)")
                top_kadar = df_highlight.nlargest(5, "Kadar Peningkatan (%)")
                for _, row in top_kadar.iterrows():
                    st.button(
                        f"{row['Kadar Peningkatan (%)']:.1f}% - {row['Lokaliti']}",
                        key=f"kadar_{row['Wabak No']}",
                        on_click=set_lokaliti_dan_wabak,
                        args=(row["Lokaliti"], row["Wabak No"]),
                        use_container_width=True,
                    )

            with c2:
                st.subheader("🔥 Jumlah Kes Tertinggi")
                top_kes = df_highlight.nlargest(5, "Jumlah Kes")
                for _, row in top_kes.iterrows():
                    st.button(
                        f"{row['Jumlah Kes']} Kes - {row['Lokaliti']}",
                        key=f"kes_{row['Wabak No']}",
                        on_click=set_lokaliti_dan_wabak,
                        args=(row["Lokaliti"], row["Wabak No"]),
                        use_container_width=True,
                    )

            with c3:
                st.subheader("⏳ Tempoh Wabak Terlama")
                top_tempoh = df_highlight.nlargest(5, "Tempoh (Hari)")
                for _, row in top_tempoh.iterrows():
                    st.button(
                        f"{row['Tempoh (Hari)']} Hari - {row['Lokaliti']}",
                        key=f"tempoh_{row['Wabak No']}",
                        on_click=set_lokaliti_dan_wabak,
                        args=(row["Lokaliti"], row["Wabak No"]),
                        use_container_width=True,
                    )
        else:
            st.success("Tiada wabak aktif (semasa) direkodkan buat masa ini.")

        # ---------------------------------------------------------
        # HIGHLIGHT 2: EPISODE WABAK TERTINGGI (TOP 10)
        # ---------------------------------------------------------
        st.markdown("---")
        st.header("🔁 Highlight: Kekerapan Episode Wabak Tertinggi (Top 10)")

        top10_kekerapan = kekerapan_wabak.nlargest(10)

        if not top10_kekerapan.empty and top10_kekerapan.max() > 0:
            top10_kekerapan = top10_kekerapan[top10_kekerapan > 0]
            items = list(top10_kekerapan.items())

            cols1 = st.columns(min(len(items), 5))
            for i in range(min(len(items), 5)):
                lokaliti, count = items[i]
                with cols1[i]:
                    st.button(
                        f"**{count} Episode**\n\n{lokaliti}",
                        key=f"kekerapan1_{lokaliti}",
                        on_click=set_lokaliti_sahaja,
                        args=(lokaliti,),
                        use_container_width=True,
                    )

            if len(items) > 5:
                cols2 = st.columns(len(items) - 5)
                for i in range(5, len(items)):
                    lokaliti, count = items[i]
                    with cols2[i - 5]:
                        st.button(
                            f"**{count} Episode**\n\n{lokaliti}",
                            key=f"kekerapan2_{lokaliti}",
                            on_click=set_lokaliti_sahaja,
                            args=(lokaliti,),
                            use_container_width=True,
                        )
        else:
            st.info("Tiada rekod episode wabak dikesan buat masa ini.")

        st.markdown("---")

        # ---------------------------------------------------------
        # ANALISIS LOKALITI & WABAK
        # ---------------------------------------------------------
        st.markdown('<div id="analisis-lokaliti-anchor"></div>', unsafe_allow_html=True)

        if st.session_state.scroll_to_analisis:
            st.session_state.scroll_to_analisis = False
            components.html(
                """
                <script>
                setTimeout(function() {
                    const anchor = window.parent.document.getElementById('analisis-lokaliti-anchor');
                    if (anchor) {
                        anchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }, 150);
                </script>
                """,
                height=0,
            )

        if not df_lok.empty and pilihan_kategori:
            if pilihan_kategori == "Satu Kes (Kes Terpencil)":
                df_filter = df_lok[df_lok["Jenis Kes"] == "Satu Kes"].copy()
                status_wabak_semasa = "Tiada (Satu Kes)"
                tempoh_wabak_hari = 1
                tarikh_mula_str = "N/A"
            else:
                w_no = float(pilihan_kategori.replace("Wabak No: ", ""))
                df_filter = df_lok[df_lok["Wabak No"] == w_no].copy()
                status_wabak_semasa = str(df_filter["Wabak Status"].iloc[0])

                tarikh_kes = df_filter["Tarikh Daftar"].dropna().sort_values().tolist()

                if len(tarikh_kes) >= 2:
                    tarikh_mula = tarikh_kes[1]
                elif len(tarikh_kes) == 1:
                    tarikh_mula = tarikh_kes[0]
                else:
                    tarikh_mula = today_my

                tarikh_mula_str = tarikh_mula.strftime("%d-%m-%Y")

                if "Tamat" in status_wabak_semasa:
                    tarikh_akhir = tarikh_kes[-1]
                else:
                    tarikh_akhir = today_my

                tempoh_wabak_hari = max((tarikh_akhir - tarikh_mula).days, 1)

            jumlah_kes = len(df_filter)
            pentadbir_lokaliti = (
                df_filter["Pihak Pentadbir Lokaliti"].mode()[0]
                if not df_filter["Pihak Pentadbir Lokaliti"].empty
                else "Tidak Dinyatakan"
            )
            rekod_episode_lokaliti = episode_map.get(pilihan_lokaliti, 0)

            st.header(f"📍 Analisis Lokaliti: {pilihan_lokaliti}")
            st.subheader(
                f"Wabak: {pilihan_kategori} | Status: {status_wabak_semasa} | Pentadbir: {pentadbir_lokaliti}"
            )

            st.markdown(
                f"*(**Rekod Sejarah:** Lokaliti ini telah mencatatkan **{rekod_episode_lokaliti} episode penularan wabak** secara keseluruhan)*"
            )

            # --- NOTA SEJARAH EPISODE WABAK & GRAF TREND INTERAKTIF (LEBAR BAR MENGIKUT TEMPOH HARI) ---
            if rekod_episode_lokaliti > 0:
                df_wabak_lok = df_lok[df_lok["Jenis Kes"] == "Wabak"].copy()

                if not df_wabak_lok.empty:
                    wabak_summary = []

                    df_wabak_lok["Wabak_Str"] = df_wabak_lok["Wabak No"].apply(
                        format_wabak_no
                    )
                    unique_wabaks_str = sorted(
                        df_wabak_lok["Wabak_Str"].unique(),
                        key=lambda x: float(x) if x.replace(".", "", 1).isdigit() else 0,
                    )
                    theme_colors = (
                        plotly.colors.qualitative.Plotly
                        + plotly.colors.qualitative.D3
                        + plotly.colors.qualitative.Set2
                    )
                    color_map = {
                        w: theme_colors[i % len(theme_colors)]
                        for i, w in enumerate(unique_wabaks_str)
                    }

                    for w_no, group in df_wabak_lok.groupby("Wabak_Str"):
                        j_kes = len(group)
                        t_kes = group["Tarikh Daftar"].dropna().sort_values().tolist()

                        if len(t_kes) >= 2:
                            t_m = t_kes[1]
                        elif len(t_kes) == 1:
                            t_m = t_kes[0]
                        else:
                            t_m = today_my

                        status_w = str(group["Wabak Status"].iloc[0])
                        t_last = group["Tarikh Daftar"].max()

                        if "Tamat" in status_w:
                            t_a = t_last
                            t_a_str = t_a.strftime("%d-%m-%Y")
                            tempoh = max((t_a - t_m).days, 1)
                            lbl_tarikh = "Tarikh Kes Terakhir"
                            lbl_tempoh = "Tempoh Wabak"
                        else:
                            t_anggaran_tamat = t_last + pd.Timedelta(days=14)
                            t_a_str = t_anggaran_tamat.strftime("%d-%m-%Y")
                            tempoh = max((today_my - t_m).days, 1)
                            lbl_tarikh = "Anggaran Tarikh Tamat"
                            lbl_tempoh = "Tempoh (Sehingga Kini)"

                        width_ms = tempoh * MS_PER_DAY
                        center_dt = t_m + pd.Timedelta(milliseconds=width_ms / 2)
                        end_dt_visual = t_m + pd.Timedelta(days=tempoh)

                        m_val = group["Epid Minggu (Tkh Daftar)"].iloc[0]
                        y_val = (
                            int(group["Epid Tahun (Tkh Daftar)"].iloc[0])
                            if "Epid Tahun (Tkh Daftar)" in group.columns
                            and pd.notnull(group["Epid Tahun (Tkh Daftar)"].iloc[0])
                            else t_m.year
                        )
                        m_label = f"{y_val}-ME{int(m_val):02d}"

                        wabak_summary.append(
                            {
                                "Wabak_Str": w_no,
                                "Tahun": y_val,
                                "Jumlah Kes": j_kes,
                                "Tarikh Mula": t_m,
                                "End_Dt_Visual": end_dt_visual,
                                "Center_Dt": center_dt,
                                "Width_Ms": width_ms,
                                "Tarikh Mula Str": t_m.strftime("%d-%m-%Y"),
                                "Tarikh Akhir Str": t_a_str,
                                "Tempoh (Hari)": tempoh,
                                "Status": status_w,
                                "Minggu_Label": m_label,
                                "Label Tarikh": lbl_tarikh,
                                "Label Tempoh": lbl_tempoh,
                            }
                        )

                    df_plot_all = pd.DataFrame(wabak_summary)

                    if not df_plot_all.empty:
                        global_min_yr = (
                            int(df["Tarikh Daftar"].dt.year.min())
                            if df["Tarikh Daftar"].notna().any()
                            else int(df_plot_all["Tahun"].min())
                        )
                        global_max_yr = (
                            int(df["Tarikh Daftar"].dt.year.max())
                            if df["Tarikh Daftar"].notna().any()
                            else int(df_plot_all["Tahun"].max())
                        )
                        min_yr_plot = min(global_min_yr, int(df_plot_all["Tahun"].min()))
                        max_yr_plot = max(global_max_yr, int(df_plot_all["Tahun"].max()))

                        yr_state_key = f"yr_slider_{pilihan_lokaliti}"
                        if yr_state_key not in st.session_state:
                            st.session_state[yr_state_key] = (min_yr_plot, max_yr_plot)

                        cur_s, cur_e = st.session_state[yr_state_key]
                        if cur_s < min_yr_plot or cur_e > max_yr_plot or cur_s > cur_e:
                            st.session_state[yr_state_key] = (min_yr_plot, max_yr_plot)

                        if min_yr_plot < max_yr_plot:
                            st.markdown("**📅 Kawalan Paparan Tahun Graf:**")
                            avail_yrs = list(range(min_yr_plot, max_yr_plot + 1))
                            btn_cols = st.columns(len(avail_yrs) + 1)
                            with btn_cols[0]:
                                st.button(
                                    f"Semua ({min_yr_plot}–{max_yr_plot})",
                                    key=f"btn_all_yr_{pilihan_lokaliti}",
                                    on_click=set_chart_year_range,
                                    args=(yr_state_key, min_yr_plot, max_yr_plot),
                                    use_container_width=True,
                                )
                            for idx_y, y_opt in enumerate(avail_yrs):
                                with btn_cols[idx_y + 1]:
                                    st.button(
                                        f"{y_opt}",
                                        key=f"btn_yr_{y_opt}_{pilihan_lokaliti}",
                                        on_click=set_chart_year_range,
                                        args=(yr_state_key, y_opt, y_opt),
                                        use_container_width=True,
                                    )

                            yr_start, yr_end = st.slider(
                                "Seret Julat Tahun (2021 hingga 2026):",
                                min_value=min_yr_plot,
                                max_value=max_yr_plot,
                                key=yr_state_key,
                            )
                        else:
                            yr_start, yr_end = min_yr_plot, max_yr_plot

                        df_plot = df_plot_all[
                            (df_plot_all["Tahun"] >= yr_start)
                            & (df_plot_all["Tahun"] <= yr_end)
                        ].copy()

                        start_date_axis = pd.Timestamp(year=yr_start, month=1, day=1)
                        if yr_end == global_max_yr and df["Tarikh Daftar"].notna().any():
                            end_date_axis = max(
                                df["Tarikh Daftar"].max(),
                                df_plot_all["End_Dt_Visual"].max(),
                            ) + pd.Timedelta(days=7)
                        else:
                            end_date_axis = pd.Timestamp(year=yr_end, month=12, day=31)

                        all_periods = pd.period_range(
                            start=start_date_axis, end=end_date_axis, freq="W-SAT"
                        )

                        if not df_plot.empty:
                            df_plot["Period"] = df_plot["Tarikh Mula"].dt.to_period(
                                "W-SAT"
                            )
                            period_to_label = (
                                df_plot.drop_duplicates(subset=["Period"])
                                .set_index("Period")["Minggu_Label"]
                                .to_dict()
                            )
                        else:
                            period_to_label = {}

                        seen_labels = set()
                        period_items = []
                        for p in all_periods:
                            lbl = (
                                str(period_to_label[p])
                                if (p in period_to_label and pd.notnull(period_to_label[p]))
                                else f"{p.end_time.year}-ME{p.week:02d}"
                            )
                            if lbl not in seen_labels:
                                seen_labels.add(lbl)
                                period_items.append(
                                    {
                                        "label": lbl,
                                        "start_ms": int(p.start_time.timestamp() * 1000),
                                        "end_ms": int(
                                            (p.end_time + pd.Timedelta(seconds=1)).timestamp()
                                            * 1000
                                        ),
                                        "start_iso": p.start_time.strftime("%Y-%m-%d"),
                                        "end_iso": (
                                            p.end_time + pd.Timedelta(days=1)
                                        ).strftime("%Y-%m-%d"),
                                    }
                                )

                        x_labels = [item["label"] for item in period_items]

                        tajuk_tempoh = (
                            f"Tahun {yr_start}"
                            if yr_start == yr_end
                            else f"Tahun {yr_start} – {yr_end}"
                        )

                        if not df_plot.empty:
                            zoom_label = "🔍 Zoom / Skrol Garis Masa Minggu Epid (Gerakkan penanda kiri atau kanan):"
                            if len(x_labels) > 10:
                                wk_start, wk_end = st.select_slider(
                                    zoom_label,
                                    options=x_labels,
                                    value=(x_labels[0], x_labels[-1]),
                                    key=f"wk_zoom_{pilihan_lokaliti}_{yr_start}_{yr_end}",
                                )
                                idx_s = x_labels.index(wk_start)
                                idx_e = x_labels.index(wk_end)
                            else:
                                idx_s = 0
                                idx_e = len(x_labels) - 1

                            visible_count = max(idx_e - idx_s + 1, 1)
                            tick_step = max(1, visible_count // 42)
                            tick_vals = [
                                period_items[i]["start_iso"]
                                for i in range(0, len(period_items), tick_step)
                            ]
                            tick_texts = [
                                period_items[i]["label"]
                                for i in range(0, len(period_items), tick_step)
                            ]

                            fig_sejarah = go.Figure()
                            for _, row in df_plot.sort_values(
                                by=["Tarikh Mula", "Wabak_Str"]
                            ).iterrows():
                                w_str = row["Wabak_Str"]
                                fig_sejarah.add_trace(
                                    go.Bar(
                                        x=[row["Center_Dt"]],
                                        y=[row["Jumlah Kes"]],
                                        width=[row["Width_Ms"]],
                                        name=w_str,
                                        marker=dict(
                                            color=color_map[w_str],
                                            line=dict(
                                                width=0.8, color="rgba(0,0,0,0.55)"
                                            ),
                                        ),
                                        opacity=0.9,
                                        selected=dict(marker=dict(opacity=1.0)),
                                        unselected=dict(marker=dict(opacity=0.85)),
                                        customdata=[
                                            [
                                                row["Tarikh Mula Str"],
                                                row["Tarikh Akhir Str"],
                                                row["Tempoh (Hari)"],
                                                w_str,
                                                row["Label Tarikh"],
                                                row["Label Tempoh"],
                                                row["Jumlah Kes"],
                                            ]
                                        ],
                                        hovertemplate="<br>".join(
                                            [
                                                "<b>Wabak No:</b> %{customdata[3]}",
                                                "<b>Jumlah Kes:</b> %{customdata[6]} Kes",
                                                "<b>Tarikh Mula:</b> %{customdata[0]}",
                                                "<b>%{customdata[4]}:</b> %{customdata[1]}",
                                                "<b>%{customdata[5]}:</b> %{customdata[2]} Hari",
                                                "<extra></extra>",
                                            ]
                                        ),
                                    )
                                )

                            fig_sejarah.update_xaxes(
                                type="date",
                                range=[
                                    period_items[idx_s]["start_iso"],
                                    period_items[idx_e]["end_iso"],
                                ],
                                tickmode="array",
                                tickvals=tick_vals,
                                ticktext=tick_texts,
                                tickangle=-90,
                                title="Tahun & Minggu Epid (Lebar Bar = Tempoh Hari Episod)",
                                rangeslider=dict(visible=False),
                            )
                            fig_sejarah.update_yaxes(
                                title="Jumlah Kes Terkumpul",
                                rangemode="tozero",
                            )
                            fig_sejarah.update_layout(
                                title=f"Garis Masa Kekerapan, Saiz & Tempoh Setiap Wabak di {pilihan_lokaliti} ({tajuk_tempoh})",
                                barmode="overlay",
                                height=450,
                                dragmode="pan",
                                legend=dict(
                                    title="No. Wabak (Skrol ▲▼)",
                                    orientation="v",
                                    yanchor="top",
                                    y=1.0,
                                    xanchor="left",
                                    x=1.01,
                                    font=dict(size=11),
                                    tracegroupgap=2,
                                    itemsizing="constant",
                                ),
                            )

                            selected_data = st.plotly_chart(
                                fig_sejarah,
                                on_select="rerun",
                                selection_mode="points",
                                use_container_width=True,
                                key=f"plotly_sejarah_{pilihan_lokaliti}_{yr_start}_{yr_end}",
                            )

                            if len(x_labels) > 10:
                                period_items_json = json.dumps(period_items)
                                components.html(
                                    f"""
                                    <script>
                                    (function() {{
                                        const periodItems = {period_items_json};
                                        const doc = window.parent.document;
                                        const win = window.parent;
                                        let rafId = null;

                                        function findZoomSlider() {{
                                            const sliders = doc.querySelectorAll('[data-testid="stSlider"]');
                                            for (const s of sliders) {{
                                                if (s.textContent && s.textContent.includes('Zoom / Skrol Garis Masa Minggu Epid')) {{
                                                    return s;
                                                }}
                                            }}
                                            return null;
                                        }}

                                        function findHistoryPlot(sliderEl) {{
                                            const charts = doc.querySelectorAll('[data-testid="stPlotlyChart"] .js-plotly-plot');
                                            if (!charts.length) return null;
                                            if (!sliderEl) return charts[0];
                                            const sRect = sliderEl.getBoundingClientRect();
                                            let bestChart = charts[0];
                                            let minDist = Infinity;
                                            for (const c of charts) {{
                                                const cRect = c.getBoundingClientRect();
                                                const dist = Math.abs(cRect.top - sRect.bottom);
                                                if (cRect.top >= sRect.top - 20 && dist < minDist) {{
                                                    minDist = dist;
                                                    bestChart = c;
                                                }}
                                            }}
                                            return bestChart;
                                        }}

                                        function syncZoomLive() {{
                                            const sliderEl = findZoomSlider();
                                            if (!sliderEl || !periodItems.length) return;
                                            const thumbs = sliderEl.querySelectorAll('[role="slider"]');
                                            if (thumbs.length < 2) return;
                                            const v0 = parseInt(thumbs[0].getAttribute('aria-valuenow'), 10);
                                            const v1 = parseInt(thumbs[1].getAttribute('aria-valuenow'), 10);
                                            if (isNaN(v0) || isNaN(v1)) return;
                                            const minIdx = Math.max(0, Math.min(v0, v1));
                                            const maxIdx = Math.min(periodItems.length - 1, Math.max(v0, v1));
                                            const visibleCount = Math.max(maxIdx - minIdx + 1, 1);
                                            const tickStep = Math.max(1, Math.floor(visibleCount / 42));
                                            const tickVals = [];
                                            const tickTexts = [];
                                            for (let i = 0; i < periodItems.length; i += tickStep) {{
                                                tickVals.push(periodItems[i].start_iso);
                                                tickTexts.push(periodItems[i].label);
                                            }}
                                            const plotEl = findHistoryPlot(sliderEl);
                                            if (plotEl && win.Plotly && typeof win.Plotly.relayout === 'function') {{
                                                try {{
                                                    win.Plotly.relayout(plotEl, {{
                                                        'xaxis.range': [periodItems[minIdx].start_iso, periodItems[maxIdx].end_iso],
                                                        'xaxis.tickvals': tickVals,
                                                        'xaxis.ticktext': tickTexts,
                                                        'xaxis.autorange': false
                                                    }});
                                                }} catch (e) {{}}
                                            }}
                                        }}

                                        function bindRealtime() {{
                                            const sliderEl = findZoomSlider();
                                            if (!sliderEl || sliderEl.dataset.rtBound === '1') return;
                                            sliderEl.dataset.rtBound = '1';

                                            const triggerUpdate = () => {{
                                                if (rafId) cancelAnimationFrame(rafId);
                                                rafId = requestAnimationFrame(syncZoomLive);
                                            }};

                                            const observer = new MutationObserver(triggerUpdate);
                                            const thumbs = sliderEl.querySelectorAll('[role="slider"]');
                                            thumbs.forEach(t => {{
                                                observer.observe(t, {{ attributes: true, attributeFilter: ['aria-valuenow'] }});
                                            }});
                                            sliderEl.addEventListener('pointermove', triggerUpdate, {{ passive: true }});
                                            sliderEl.addEventListener('touchmove', triggerUpdate, {{ passive: true }});
                                            syncZoomLive();
                                        }}

                                        bindRealtime();
                                        const retryTimer = setInterval(bindRealtime, 400);
                                        setTimeout(() => clearInterval(retryTimer), 6000);
                                    }})();
                                    </script>
                                    """,
                                    height=0,
                                )

                            if selected_data and selected_data.selection.points:
                                pt = selected_data.selection.points[0]
                                cdata = pt.get("customdata")
                                if cdata and len(cdata) > 3:
                                    clicked_w_no_str = str(cdata[3])
                                elif "curve_number" in pt:
                                    sorted_df_plot = df_plot.sort_values(
                                        by=["Tarikh Mula", "Wabak_Str"]
                                    ).reset_index(drop=True)
                                    clicked_w_no_str = str(
                                        sorted_df_plot.iloc[pt["curve_number"]][
                                            "Wabak_Str"
                                        ]
                                    )
                                else:
                                    clicked_w_no_str = None

                                if clicked_w_no_str:
                                    target_w_str = f"Wabak No: {clicked_w_no_str}"
                                    if st.session_state.selected_wabak != target_w_str:
                                        st.session_state.selected_wabak = target_w_str
                                        st.rerun()
                        else:
                            st.info(
                                f"Tiada episod wabak direkodkan di {pilihan_lokaliti} bagi tempoh **{tajuk_tempoh}**. Pilih tahun lain atau klik **Semua ({min_yr_plot}–{max_yr_plot})** untuk melihat keseluruhan garis masa."
                            )

                        with st.expander(
                            f"📋 Senarai Ringkas Semua Episod Wabak di {pilihan_lokaliti} ({len(df_plot_all)} Episod)"
                        ):
                            df_ep_table = df_plot_all.sort_values(
                                by="Tarikh Mula", ascending=False
                            )[
                                [
                                    "Wabak_Str",
                                    "Minggu_Label",
                                    "Tarikh Mula Str",
                                    "Tarikh Akhir Str",
                                    "Tempoh (Hari)",
                                    "Jumlah Kes",
                                    "Status",
                                ]
                            ].rename(
                                columns={
                                    "Wabak_Str": "No. Wabak",
                                    "Minggu_Label": "Minggu Mula",
                                    "Tarikh Mula Str": "Tarikh Mula",
                                    "Tarikh Akhir Str": "Tarikh Tamat / Anggaran",
                                }
                            )
                            st.dataframe(
                                df_ep_table, use_container_width=True, hide_index=True
                            )

                        if (
                            st.session_state.selected_wabak
                            and "Wabak No:" in st.session_state.selected_wabak
                        ):
                            current_w_str = st.session_state.selected_wabak.replace(
                                "Wabak No: ", ""
                            ).strip()
                            if current_w_str in color_map:
                                bg_hex = color_map[current_w_str]
                                st.markdown(
                                    f"""
                                <style>
                                .stApp {{
                                    background-color: {bg_hex}1A !important;
                                }}
                                </style>
                                """,
                                    unsafe_allow_html=True,
                                )
            # -----------------------------------------------

            kadar_velocity = jumlah_kes / tempoh_wabak_hari
            peratus_increment = (
                (kadar_velocity / jumlah_kes) * 100 if jumlah_kes > 0 else 0
            )

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Jumlah Kes", jumlah_kes)
            col2.metric(
                f"Tempoh (Hari) *Bermula {tarikh_mula_str}*", tempoh_wabak_hari
            )

            safe_lokaliti = html.escape(str(pilihan_lokaliti))
            safe_kategori = html.escape(str(pilihan_kategori))

            velocity_html = (
                f'<div class="metric-hover-card">'
                f'<div class="metric-hover-label">Velocity (Kes/Hari) <span class="metric-hover-badge">?</span></div>'
                f'<div class="metric-hover-value">{kadar_velocity:.2f}</div>'
                f'<div class="metric-tooltip-bubble">'
                f'<div class="tooltip-title">🚀 Velocity (Kes/Hari)</div>'
                f'<div class="tooltip-section"><b>Maksud & Relevansi:</b> Mengukur kelajuan penularan wabak (purata kes baharu sehari). Nilai tinggi (cth. > 1.0 kes/hari) menandakan penularan agresif yang memerlukan kawalan kecemasan segera (ULV & S&D).</div>'
                f'<div class="tooltip-section"><b>Formula & Cara Kira:</b>'
                f'<div class="tooltip-formula">Jumlah Kes ÷ Tempoh Wabak (Hari)</div></div>'
                f'<div class="tooltip-current"><b>Pengiraan Semasa ({safe_lokaliti} — {safe_kategori}):</b><br>'
                f'{jumlah_kes} kes ÷ {tempoh_wabak_hari} hari = <b>{kadar_velocity:.2f} kes/hari</b></div>'
                f'</div></div>'
            )
            col3.markdown(velocity_html, unsafe_allow_html=True)

            increment_html = (
                f'<div class="metric-hover-card">'
                f'<div class="metric-hover-label">Peningkatan (% Harian) <span class="metric-hover-badge">?</span></div>'
                f'<div class="metric-hover-value">{peratus_increment:.1f}%</div>'
                f'<div class="metric-tooltip-bubble">'
                f'<div class="tooltip-title">📈 Peningkatan (% Harian)</div>'
                f'<div class="tooltip-section"><b>Maksud & Relevansi:</b> Mengukur momentum pertumbuhan purata harian berbanding keseluruhan kes terkumpul. Peratusan tinggi menandakan fasa awal wabak yang sedang berkembang pantas; peratusan mengecil menandakan lengkuk epid mulai mendatar.</div>'
                f'<div class="tooltip-section"><b>Formula & Cara Kira:</b>'
                f'<div class="tooltip-formula">(Velocity ÷ Jumlah Kes) × 100</div></div>'
                f'<div class="tooltip-current"><b>Pengiraan Semasa ({safe_lokaliti} — {safe_kategori}):</b><br>'
                f'({kadar_velocity:.2f} ÷ {jumlah_kes} kes) × 100 = <b>{peratus_increment:.1f}% sehari</b></div>'
                f'</div></div>'
            )
            col4.markdown(increment_html, unsafe_allow_html=True)

            st.markdown("---")

            minggu_puncak_txt = "Tiada"
            kes_puncak = 0
            status_arah_txt = "tidak dapat dipastikan"

            max_val_specific = -1
            max_b_specific = "Tidak Dinyatakan"
            max_t_specific = "Tidak Dinyatakan"
            blok_masalah_txt = "Tidak Dinyatakan"
            tingkat_masalah_txt = "Tidak Dinyatakan"

            # ---------------------------------------------------------
            # TABURAN KES MINGGU EPID (Wabak Terpilih Sahaja)
            # ---------------------------------------------------------
            st.subheader(
                f"📈 Taburan Kes Mengikut Minggu Epid ({pilihan_kategori})"
            )
            if (
                "Epid Tahun (Tkh Daftar)" in df_filter.columns
                and df_filter["Epid Tahun (Tkh Daftar)"].nunique() > 1
            ):
                df_filter["_Epid_Sort"] = (
                    df_filter["Epid Tahun (Tkh Daftar)"].astype(int).astype(str)
                    + "-ME"
                    + df_filter["Epid Minggu (Tkh Daftar)"]
                    .astype(int)
                    .astype(str)
                    .str.zfill(2)
                )
                kes_epid = df_filter["_Epid_Sort"].value_counts().sort_index()
            else:
                kes_epid = (
                    df_filter["Epid Minggu (Tkh Daftar)"].value_counts().sort_index()
                )

            if not kes_epid.empty:
                df_epid = kes_epid.reset_index()
                df_epid.columns = ["Minggu Epid", "Jumlah Kes"]
                df_epid["Minggu Epid"] = df_epid["Minggu Epid"].astype(str)

                fig_epid = px.bar(
                    df_epid,
                    x="Minggu Epid",
                    y="Jumlah Kes",
                    color_discrete_sequence=["lightcoral"],
                    text="Jumlah Kes",
                )
                fig_epid.update_traces(textposition="outside")
                fig_epid.update_xaxes(type="category")
                fig_epid.update_layout(
                    xaxis_title="Minggu Epid", yaxis_title="Jumlah Kes", height=350
                )

                st.plotly_chart(
                    fig_epid, use_container_width=True, key="graf_minggu_epid"
                )

                minggu_puncak_txt = str(kes_epid.idxmax())
                kes_puncak = kes_epid.max()
                purata_mingguan = kes_epid.mean()

                ulasan_epid = "**Analisis Terperinci Mingguan:**\n"
                ulasan_epid += f"- Secara purata, terdapat **{purata_mingguan:.1f} kes** didaftarkan setiap minggu.\n"
                ulasan_epid += f"- Minggu puncak bagi penularan ini adalah pada **Minggu Epid {minggu_puncak_txt}** dengan rekod tertinggi **{kes_puncak} kes**.\n"

                if len(kes_epid) >= 2:
                    m_kini = kes_epid.iloc[-1]
                    m_lalu = kes_epid.iloc[-2]
                    perbezaan = m_kini - m_lalu
                    status_arah_txt = (
                        "meningkat"
                        if perbezaan > 0
                        else "menurun"
                        if perbezaan < 0
                        else "mendatar"
                    )
                    ulasan_epid += f"- Perbandingan minggu terkini menunjukkan trend **{status_arah_txt}** ({m_kini} kes vs {m_lalu} kes pada minggu sebelumnya)."
                st.info(ulasan_epid)

            st.markdown("---")

            # ---------------------------------------------------------
            # TABURAN BLOK & TINGKAT + PERINCIAN
            # ---------------------------------------------------------
            st.subheader("🏢 Taburan Kes Mengikut Blok dan Tingkat")
            df_filter[["Blok", "Tingkat"]] = df_filter["No Rumah"].apply(parse_address)

            if (
                len(df_filter["Blok"].unique()) > 1
                or "TIDAK PASTI" not in df_filter["Blok"].values
            ):
                crosstab_bt = pd.crosstab(
                    df_filter["Tingkat"],
                    df_filter["Blok"],
                    margins=True,
                    margins_name="JUMLAH",
                )

                def pad_for_sort(s):
                    return re.sub(r"\d+", lambda m: m.group(0).zfill(5), str(s))

                tingkat_list = list(crosstab_bt.index[:-1])
                blok_list = list(crosstab_bt.columns[:-1])

                tingkat_sorted = sorted(tingkat_list, key=pad_for_sort, reverse=True)
                blok_sorted = sorted(blok_list, key=pad_for_sort)

                crosstab_bt = crosstab_bt.loc[
                    tingkat_sorted + ["JUMLAH"], blok_sorted + ["JUMLAH"]
                ]

                idx_slice = pd.IndexSlice[
                    crosstab_bt.index[:-1], crosstab_bt.columns[:-1]
                ]
                styled_ct = crosstab_bt.style.background_gradient(
                    cmap="Reds", subset=idx_slice
                )
                st.markdown(styled_ct.to_html(), unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                for t in crosstab_bt.index[:-1]:
                    for b in crosstab_bt.columns[:-1]:
                        if crosstab_bt.loc[t, b] > max_val_specific:
                            max_val_specific = crosstab_bt.loc[t, b]
                            max_b_specific = str(b)
                            max_t_specific = str(t)

                blok_totals = crosstab_bt.loc["JUMLAH"][:-1]
                if not blok_totals.empty and blok_totals.max() > 0:
                    blok_masalah_txt = str(blok_totals.idxmax())

                tingkat_totals = crosstab_bt.iloc[:-1]["JUMLAH"]
                if not tingkat_totals.empty and tingkat_totals.max() > 0:
                    tingkat_masalah_txt = str(tingkat_totals.idxmax())

                if max_val_specific > 0:
                    st.warning(
                        f"⚠️ **Sarang Penularan Spesifik:** Takungan vektor berjangkit (hotspot selular) dipercayai tertumpu secara spesifik di kediaman **Blok {max_b_specific}, Tingkat {max_t_specific}** yang menyumbang **{max_val_specific} kes**. Operasi pemusnahan sumber (S&D) dan semburan ruang disarankan untuk difokuskan bermula dari struktur radius ini terlebih dahulu sebelum diperluas ke tempat lain."
                    )

                st.markdown(
                    "##### **Perincian Struktur (Keseluruhan Blok & Tingkat):**"
                )

                blok_group_raw = (
                    df_filter[df_filter["Blok"] != "TIDAK PASTI"]
                    .groupby("Blok")
                    .size()
                )

                if not blok_group_raw.empty:
                    sorted_blok_keys = sorted(blok_group_raw.index, key=pad_for_sort)
                    for blok_name in sorted_blok_keys:
                        b_count = blok_group_raw[blok_name]
                        b_pct = (b_count / jumlah_kes) * 100
                        st.markdown(
                            f"**🔹 Blok {blok_name}: {b_count} kes ({b_pct:.1f}% dari keseluruhan wabak)**"
                        )

                        df_blok_ini = df_filter[
                            (df_filter["Blok"] == blok_name)
                            & (df_filter["Tingkat"] != "TIDAK PASTI")
                        ]
                        if not df_blok_ini.empty:
                            tingkat_group_raw = df_blok_ini.groupby("Tingkat").size()
                            sorted_tingkat_keys = sorted(
                                tingkat_group_raw.index, key=pad_for_sort, reverse=True
                            )

                            for tk_name in sorted_tingkat_keys:
                                t_count = tingkat_group_raw[tk_name]
                                t_pct_overall = (t_count / jumlah_kes) * 100
                                st.write(
                                    f"    🔸 Tingkat {tk_name}: {t_count} kes ({t_pct_overall:.1f}%)"
                                )
                else:
                    st.write("Maklumat blok tidak cukup berstruktur.")
            else:
                st.info(
                    "Tiada struktur blok/tingkat yang jelas ditemui pada 'No Rumah'."
                )

            st.markdown("---")

            # ---------------------------------------------------------
            # 5 KES TERKINI DENGAN LOKASI (BLOK & TINGKAT)
            # ---------------------------------------------------------
            st.subheader("📍 Analisis 5 Kes Terkini")

            top5_daftar = df_filter.sort_values(
                by="Tarikh Daftar", ascending=False
            ).head(5)
            top5_onset = df_filter.sort_values(
                by="Tarikh Onset", ascending=False
            ).head(5)
            common_indices = set(top5_daftar.index).intersection(set(top5_onset.index))

            def highlight_common(row):
                return [
                    "background-color: #ffd700; color: black"
                    if row.name in common_indices
                    else ""
                    for _ in row
                ]

            col_t1, col_t2 = st.columns(2)

            with col_t1:
                st.markdown("**Berdasarkan Tarikh Daftar (Terkini)**")
                st.markdown(
                    top5_daftar[["Tarikh Daftar", "No Rumah", "Blok", "Tingkat"]]
                    .style.apply(highlight_common, axis=1)
                    .to_html(),
                    unsafe_allow_html=True,
                )

            with col_t2:
                st.markdown("**Berdasarkan Tarikh Onset (Terkini)**")
                st.markdown(
                    top5_onset[["Tarikh Onset", "No Rumah", "Blok", "Tingkat"]]
                    .style.apply(highlight_common, axis=1)
                    .to_html(),
                    unsafe_allow_html=True,
                )

            st.markdown(
                "<br>**Ulasan Terperinci Kes Terkini:**", unsafe_allow_html=True
            )

            daftar_locs = top5_daftar.apply(
                lambda x: f"Blok {x['Blok']} Tingkat {x['Tingkat']}", axis=1
            ).tolist()
            onset_locs = top5_onset.apply(
                lambda x: f"Blok {x['Blok']} Tingkat {x['Tingkat']}", axis=1
            ).tolist()

            st.write(
                f"- **Pendaftaran Terkini:** 5 kes terakhir bertumpu di **{', '.join(daftar_locs)}**."
            )
            st.write(
                f"- **Gejala (Onset) Terbaharu:** 5 pesakit terbaharu dikesan menetap di **{', '.join(onset_locs)}**."
            )

            if common_indices:
                st.info(
                    f"💡 Terdapat **{len(common_indices)} kes (diwarnakan kuning)** yang saling bertindih di antara Pendaftaran Terkini dan Onset Terkini, menandakan penularan sangat aktif dan baru (fresh outbreak) sedang berlaku."
                )
            else:
                st.info(
                    "💡 Tiada pertindihan ketara dikesan di antara kes onset terkini dan pendaftaran terkini. Pendaftaran terkini berkemungkinan melibatkan kes tertangguh dari minggu sebelumnya."
                )

            st.markdown("---")

            # ---------------------------------------------------------
            # TABURAN KEMUDAHAN KESIHATAN, WARGA & PEKERJAAN
            # ---------------------------------------------------------
            c_info1, c_info2, c_info3 = st.columns(3)

            fasiliti_utama_txt = "Tidak Dinyatakan"
            top_warga = "Tidak Dinyatakan"
            top_pekerjaan = "Tidak Dinyatakan"

            with c_info1:
                st.subheader("Kemudahan Kesihatan")
                fasiliti_count = df_filter[
                    "Kemudahan Kesihatan(Maklumat Pemberitahu)"
                ].value_counts()
                if not fasiliti_count.empty:
                    fasiliti_utama_txt = fasiliti_count.index[0]
                for f, count in fasiliti_count.items():
                    pct = (count / jumlah_kes) * 100
                    st.write(f"- **{f}**: {count} ({pct:.1f}%)")

            with c_info2:
                st.subheader("Kewarganegaraan")
                warga_count = df_filter["Status Kewarganegaraan"].value_counts()
                if not warga_count.empty:
                    top_warga = warga_count.index[0]
                for w, count in warga_count.items():
                    pct = (count / jumlah_kes) * 100
                    st.write(f"- **{w}**: {count} ({pct:.1f}%)")

            with c_info3:
                st.subheader("Pekerjaan")
                kerja_count = df_filter["Pekerjaan"].value_counts()
                if not kerja_count.empty:
                    top_pekerjaan = kerja_count.index[0]
                for k, count in kerja_count.items():
                    pct = (count / jumlah_kes) * 100
                    st.write(f"- **{k}**: {count} ({pct:.1f}%)")

            st.markdown("---")

            # ---------------------------------------------------------
            # KESIMPULAN & RUMUSAN AI KESELURUHAN
            # ---------------------------------------------------------
            st.header("📝 Kesimpulan & Rumusan Eksekutif Lokaliti")

            zon_bahaya_semasa = list(set(onset_locs))
            zon_str = (
                ", ".join(zon_bahaya_semasa)
                if zon_bahaya_semasa
                else "Tidak Dinyatakan"
            )

            ayat_hotspot = (
                f"Titik jangkitan tertumpu secara kritikal disahkan berada pada Blok {max_b_specific} Tingkat {max_t_specific}."
                if max_b_specific != "Tidak Dinyatakan"
                else ""
            )

            kesimpulan_ai = f"""
            Berdasarkan data harian terkini bagi **{pilihan_lokaliti}** ({pilihan_kategori} - **{status_wabak_semasa}**):
            
            *   **Keterukan Wabak:** Secara teknikal, rantaian penularan ini mula tercetus pada **{tarikh_mula_str}** (pendaftaran kes ke-2), bertahan selama **{tempoh_wabak_hari} hari**, dan telah merekodkan sejumlah **{jumlah_kes} kes**. Kelajuan penularan berada pada tahap **{kadar_velocity:.2f} kes sehari**. Secara kumulatif, lokaliti ini merekodkan sejarah **{rekod_episode_lokaliti} episode wabak**.
            *   **Trend Epidemiologi:** Jumlah kes memuncak pada **Minggu Epid {minggu_puncak_txt}** ({kes_puncak} kes). Analisis menunjukkan trend kes mingguan terkini sedang **{status_arah_txt}**.
            *   **Tumpuan Struktur (Hotspot Dalaman):** Secara kumulatif, **Blok {blok_masalah_txt}** adalah kawasan yang mencatatkan jumlah pesakit teramai manakala takungan penyakit paling banyak dikesan berkumpul di **Tingkat {tingkat_masalah_txt}**. {ayat_hotspot}
            *   **Zon Jangkitan Aktif Terkini:** Mangsa-mangsa dengan episod gejala (onset) paling baharu (newly active vectors) mendiami kawasan **{zon_str}**. 
            *   **Demografi Klinikal:** Kes paling banyak melibatkan kumpulan **{top_warga}** berkerjaya **{top_pekerjaan}**. Fasiliti yang paling banyak menotifikasikan kes dari wabak ini ialah **{fasiliti_utama_txt}**.
            
            **🎯 Rumusan Tindakan:** Fokus S&D dan kawalan semburan nyamuk dewasa wajar dihalakan secara spesifik ke zon jangkitan aktif terkini di **{zon_str}** serta saringan menyeluruh ke atas keseluruhan **Blok {blok_masalah_txt}** sebagai kawasan risiko tertinggi.
            """

            st.success(kesimpulan_ai)

    except Exception as e:
        st.error(f"Ralat sistem: {e}")
