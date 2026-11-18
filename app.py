import html
import io
import json
import os
import re
import urllib.parse
from datetime import datetime
import matplotlib.pyplot as plt  # Wajib ada untuk fungsi mewarna jadual (background_gradient)
import pandas as pd
import plotly.colors
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dashboard Analisis Denggi", layout="wide")

MS_PER_DAY = 24 * 60 * 60 * 1000

# --- CSS KHUSUS UNTUK CETAKAN PDF, ELEMEN JADUAL & TOOLTIP METRIK ---
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
    /* Jadual Rasmi STATUS WABAK (DENGGI) mengikut format WhatsApp */
    .status-wabak-wrapper {
        width: 100%;
        overflow-x: auto;
        margin-bottom: 10px;
    }
    table.status-wabak-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, Helvetica, sans-serif;
        font-size: 13px;
        color: #000000;
        background-color: #FFFFFF;
    }
    table.status-wabak-table th,
    table.status-wabak-table td {
        border: 1px solid #000000 !important;
        padding: 5px 8px;
        text-align: center;
        vertical-align: middle;
        color: #000000;
        line-height: 1.25;
    }
    table.status-wabak-table .banner-main {
        background-color: #EAD1DC !important;
        color: #000000 !important;
        font-size: 18px;
        font-weight: 700;
        padding: 7px 10px;
        letter-spacing: 0.3px;
    }
    table.status-wabak-table .banner-tamat {
        background-color: #980000 !important;
        color: #FFFFFF !important;
        font-size: 13px;
        font-weight: 700;
        padding: 5px 8px;
    }
    table.status-wabak-table .banner-aktif {
        background-color: #783F04 !important;
        color: #FFFFFF !important;
        font-size: 13px;
        font-weight: 700;
        padding: 5px 8px;
    }
    table.status-wabak-table .col-header {
        background-color: #F9CB9C !important;
        color: #000000 !important;
        font-weight: 700;
        font-size: 12px;
        padding: 6px 6px;
    }
    table.status-wabak-table td.lok-cell {
        text-align: left !important;
        padding-left: 10px;
    }
    table.status-wabak-table td.num-cell {
        text-align: right !important;
        padding-right: 10px;
    }
    table.status-wabak-table td.tiada-cell {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 700;
        padding: 7px 8px;
        text-align: center !important;
    }
    a.status-lok-link {
        color: #000000 !important;
        text-decoration: none;
        display: block;
        width: 100%;
        border-radius: 3px;
        transition: background-color 0.15s ease, color 0.15s ease;
    }
    a.status-lok-link:hover {
        color: #0B5394 !important;
        text-decoration: underline;
        background-color: rgba(11, 83, 148, 0.08);
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


def format_wabak_no(val):
    """Memformat nombor wabak supaya bersih tanpa '.0' di hujung."""
    try:
        f_val = float(val)
        if f_val.is_integer():
            return str(int(f_val))
        return str(f_val)
    except Exception:
        return str(val).strip()


def format_dmy_short(dt):
    """Memformat tarikh kepada format d/m/yyyy (contoh: 10/11/2026)."""
    if pd.isna(dt):
        return "-"
    return f"{dt.day}/{dt.month}/{dt.year}"


def map_kaw_jagaan(val):
    s = str(val).upper().strip()
    if "DBKL" in s or "DEWAN BANDARAYA" in s:
        return "DBKL"
    if "PKD" in s or "KKM" in s:
        return "KKM"
    return s if s and s != "NAN" else "-"


def map_parlimen(val):
    s = str(val).upper().strip()
    if "BANDAR TUN RAZAK" in s:
        return "BTR"
    if "CHERAS" in s:
        return "CHERAS"
    s = s.replace("PARLIMEN ", "").strip()
    return s if s and s != "NAN" else "-"


def get_status_bg_color(status_txt):
    s = str(status_txt).upper().strip()
    if s == "WABAK TERKAWAL":
        return "#F4CCCC"
    if s == "WABAK TAK TERKAWAL":
        return "#3D85C6"
    if s == "HOTSPOT":
        return "#FF0000"
    if "TAMAT" in s:
        return "#B6D7A8"
    return "#FCE5CD"


def get_kaw_bg_color(kaw_txt):
    s = str(kaw_txt).upper().strip()
    if s == "DBKL":
        return "#A4C2F4"
    if s == "KKM":
        return "#B6D7A8"
    return "#FFFFFF"


def get_parlimen_bg_color(parl_txt):
    s = str(parl_txt).upper().strip()
    if s == "BTR":
        return "#B4A7D6"
    if s == "CHERAS":
        return "#FFD966"
    return "#FFFFFF"


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

    # Kesan baris header sebenar jika terdapat tajuk laporan di baris teratas
    if "Tarikh Daftar" not in df.columns and "Lokaliti (Alamat Semasa)" not in df.columns:
        for i in range(min(10, len(df))):
            row_vals = [str(v).strip() for v in df.iloc[i].values]
            if "Tarikh Daftar" in row_vals or "Lokaliti (Alamat Semasa)" in row_vals:
                df.columns = row_vals
                df = df.iloc[i + 1 :].reset_index(drop=True)
                break

    # Penyeragaman jenis data supaya CSV dan Excel seragam
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

    # Penukaran tarikh format Malaysia (DD/MM/YYYY)
    for date_col in ["Tarikh Daftar", "Tarikh Onset", "Tkh Notifikasi"]:
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

    # Buang rekod bertindih menggunakan ID unik (keutamaan kepada fail semasa yang terkini)
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


def build_daily_status_report(df, report_date):
    """Menjana jadual STATUS WABAK (DENGGI) harian mengikut tarikh semasa secara automatik."""
    current_year = report_date.year
    df_w = df[df["Jenis Kes"] == "Wabak"].dropna(subset=["Wabak No"]).copy()
    if df_w.empty:
        return [], []

    df_w["Wabak_Clean"] = df_w["Wabak No"].apply(format_wabak_no)
    df_w["Lok_Norm"] = (
        df_w["Lokaliti (Alamat Semasa)"]
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Bilangan episod bagi tahun semasa sahaja (cth: 2026) mengikut lokaliti
    if "Epid Tahun (Tkh Daftar)" in df_w.columns and df_w["Epid Tahun (Tkh Daftar)"].notna().any():
        df_w_yr = df_w[df_w["Epid Tahun (Tkh Daftar)"] == current_year]
    else:
        df_w_yr = df_w[df_w["Tarikh Daftar"].dt.year == current_year]
    ep_yr_map = df_w_yr.groupby("Lok_Norm")["Wabak_Clean"].nunique().to_dict()

    status_priority = {
        "WABAK TERKAWAL": 1,
        "WABAK TAK TERKAWAL": 2,
        "HOTSPOT": 3,
    }

    active_rows = []
    tamat_rows = []

    for (w_str, lok), grp in df_w.groupby(["Wabak_Clean", "Lokaliti (Alamat Semasa)"]):
        raw_status = str(grp["Wabak Status"].iloc[0]).strip().upper()
        jumlah_kes = len(grp)
        lok_norm = " ".join(str(lok).split())
        bil_episod = int(ep_yr_map.get(lok_norm, 1))

        # Guna Tkh Notifikasi sebagai rujukan utama; fallback ke Tarikh Daftar jika tiada
        notif_dates = (
            grp["Tkh Notifikasi"].dropna().sort_values().tolist()
            if "Tkh Notifikasi" in grp.columns
            else []
        )
        if not notif_dates:
            notif_dates = grp["Tarikh Daftar"].dropna().sort_values().tolist()

        if len(notif_dates) >= 2:
            t_mula = notif_dates[1]
        elif len(notif_dates) == 1:
            t_mula = notif_dates[0]
        else:
            continue

        t_last = notif_dates[-1]
        t_tamat = t_last + pd.Timedelta(days=14)

        kaw = map_kaw_jagaan(
            grp["Pihak Pentadbir Lokaliti"].mode()[0]
            if "Pihak Pentadbir Lokaliti" in grp.columns
            and not grp["Pihak Pentadbir Lokaliti"].dropna().empty
            else ""
        )
        parl = map_parlimen(
            grp["Mukim/Zon (Alamat Semasa)"].mode()[0]
            if "Mukim/Zon (Alamat Semasa)" in grp.columns
            and not grp["Mukim/Zon (Alamat Semasa)"].dropna().empty
            else ""
        )

        row_base = {
            "Wabak_Str": w_str,
            "STATUS WABAK": raw_status,
            "KAW JAGAAN": kaw,
            "PARLIMEN": parl,
            "LOKALITI": str(lok),
            "JUMLAH KES": int(jumlah_kes),
            "BIL EPISOD": bil_episod,
            "TARIKH MULA": format_dmy_short(t_mula),
            "TARIKH TAMAT": format_dmy_short(t_tamat),
            "status_bg": get_status_bg_color(raw_status),
            "kaw_bg": get_kaw_bg_color(kaw),
            "parl_bg": get_parlimen_bg_color(parl),
        }

        if "TAMAT" in raw_status:
            # Papar dalam WABAK TAMAT jika tarikh tamat jatuh pada tarikh hari ini
            if t_tamat.normalize() == report_date:
                row_base["TEMPOH WABAK"] = int(max((t_tamat - t_mula).days, 1))
                tamat_rows.append(row_base)
        else:
            row_base["_prio"] = status_priority.get(raw_status, 4)
            row_base["TEMPOH WABAK"] = int(max((report_date - t_mula).days, 1))
            active_rows.append(row_base)

    if tamat_rows:
        tamat_rows.sort(key=lambda r: (r["KAW JAGAAN"], r["PARLIMEN"], r["LOKALITI"]))
        for idx, r in enumerate(tamat_rows, start=1):
            r["BIL"] = idx

    if active_rows:
        active_rows.sort(
            key=lambda r: (r["_prio"], r["KAW JAGAAN"], r["PARLIMEN"], r["LOKALITI"])
        )
        prev_st = None
        cnt = 0
        for r in active_rows:
            if r["STATUS WABAK"] != prev_st:
                cnt = 1
                prev_st = r["STATUS WABAK"]
            else:
                cnt += 1
            r["BIL"] = cnt

    return tamat_rows, active_rows


def render_daily_status_html(tamat_rows, active_rows):
    """Membina jadual HTML berstruktur penuh dengan pautan lokaliti boleh klik."""
    cols = [
        "BIL",
        "STATUS WABAK",
        "KAW JAGAAN",
        "PARLIMEN",
        "LOKALITI",
        "JUMLAH KES",
        "BIL EPISOD",
        "TEMPOH WABAK",
        "TARIKH MULA",
        "TARIKH TAMAT",
    ]
    header_cells = "".join(f'<th class="col-header">{c}</th>' for c in cols)

    def build_data_rows(rows):
        html_out = []
        for r in rows:
            q_lok = urllib.parse.quote(r["LOKALITI"])
            q_wno = urllib.parse.quote(r["Wabak_Str"])
            esc_lok = html.escape(r["LOKALITI"])
            link_html = (
                f'<a class="status-lok-link" href="?select_lok={q_lok}&select_wabak={q_wno}" '
                f'target="_self" title="Klik untuk melihat butiran analisis {esc_lok}">{esc_lok}</a>'
            )
            html_out.append(
                f"<tr>"
                f"<td>{r['BIL']}</td>"
                f"<td style=\"background-color: {r['status_bg']} !important;\">{html.escape(r['STATUS WABAK'])}</td>"
                f"<td style=\"background-color: {r['kaw_bg']} !important;\">{html.escape(r['KAW JAGAAN'])}</td>"
                f"<td style=\"background-color: {r['parl_bg']} !important;\">{html.escape(r['PARLIMEN'])}</td>"
                f'<td class="lok-cell">{link_html}</td>'
                f'<td class="num-cell">{r["JUMLAH KES"]}</td>'
                f'<td class="num-cell">{r["BIL EPISOD"]}</td>'
                f'<td class="num-cell">{r["TEMPOH WABAK"]}</td>'
                f'<td class="num-cell">{r["TARIKH MULA"]}</td>'
                f'<td class="num-cell">{r["TARIKH TAMAT"]}</td>'
                f"</tr>"
            )
        return "".join(html_out)

    tamat_body = (
        build_data_rows(tamat_rows)
        if tamat_rows
        else '<tr><td colspan="10" class="tiada-cell">TIADA</td></tr>'
    )
    aktif_body = (
        build_data_rows(active_rows)
        if active_rows
        else '<tr><td colspan="10" class="tiada-cell">TIADA</td></tr>'
    )

    return f"""
    <div class="status-wabak-wrapper">
        <table class="status-wabak-table">
            <thead>
                <tr><th colspan="10" class="banner-main">STATUS WABAK (DENGGI)</th></tr>
                <tr><th colspan="10" style="background:#FFFFFF !important; height:6px; padding:0;"></th></tr>
                <tr><th colspan="10" class="banner-tamat">WABAK TAMAT</th></tr>
                <tr>{header_cells}</tr>
            </thead>
            <tbody>
                {tamat_body}
                <tr><td colspan="10" style="background:#FFFFFF !important; height:14px; padding:0;"></td></tr>
                <tr><th colspan="10" class="banner-aktif">SENARAI WABAK AKTIF</th></tr>
                <tr>{header_cells}</tr>
                {aktif_body}
            </tbody>
        </table>
    </div>
    """


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


# --- PENGURUSAN STATE (MEMORI APLIKASI) ---
if "selected_lokaliti" not in st.session_state:
    st.session_state.selected_lokaliti = None
if "selected_wabak" not in st.session_state:
    st.session_state.selected_wabak = None
if "episode_filter" not in st.session_state:
    st.session_state.episode_filter = "Semua"
if "scroll_to_lokaliti" not in st.session_state:
    st.session_state.scroll_to_lokaliti = False


def set_lokaliti_dan_wabak(lokaliti, wabak_no):
    st.session_state.selected_lokaliti = lokaliti
    st.session_state.selected_wabak = f"Wabak No: {format_wabak_no(wabak_no)}"
    st.session_state.episode_filter = "Semua"


def set_lokaliti_sahaja(lokaliti):
    st.session_state.selected_lokaliti = lokaliti
    st.session_state.selected_wabak = None
    st.session_state.episode_filter = "Semua"


def set_chart_year_range(state_key, start_yr, end_yr):
    st.session_state[state_key] = (start_yr, end_yr)


# --- ANTARA MUKA UTAMA ---
st.title("🦟 Dashboard Analisis Kes Denggi (Spesifik Wabak)")

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

        # --- TANGKAP KLIK LOKALITI DARIPADA JADUAL STATUS WABAK (DENGGI) ---
        if "select_lok" in st.query_params:
            q_lok = st.query_params.get("select_lok")
            q_wabak = st.query_params.get("select_wabak")
            if q_lok in semua_lokaliti_list:
                st.session_state.selected_lokaliti = q_lok
                st.session_state.episode_filter = "Semua"
                if q_wabak:
                    st.session_state.selected_wabak = (
                        f"Wabak No: {format_wabak_no(q_wabak)}"
                    )
                else:
                    st.session_state.selected_wabak = None
                st.session_state.scroll_to_lokaliti = True
            st.query_params.clear()

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
            # Susun senarai wabak dari yang paling terkini (berdasarkan tarikh daftar terbaru)
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

                tarikh_akhir = pd.Timestamp.today().normalize()
                tempoh_h = (tarikh_akhir - tarikh_mula).days
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

        # ---------------------------------------------------------
        # JADUAL STATUS WABAK (DENGGI) HARIAN (UNTUK WHATSAPP & KLIK LOKALITI)
        # ---------------------------------------------------------
        st.markdown("---")
        today_report_dt = pd.Timestamp.today().normalize()
        today_report_str = today_report_dt.strftime("%d/%m/%Y")

        st.header(f"📋 Jadual Status Wabak (Denggi) — Laporan Semasa ({today_report_str})")
        st.caption(
            "💡 Klik pada mana-mana nama **LOKALITI** di dalam jadual untuk terus membuka analisis terperinci lokaliti tersebut, atau guna butang eksport di bawah untuk perkongsian WhatsApp."
        )

        tamat_rows, active_rows = build_daily_status_report(df, today_report_dt)

        # Render jadual HTML interaktif (sama sebiji dengan format laporan WhatsApp)
        status_table_html = render_daily_status_html(tamat_rows, active_rows)
        st.markdown(status_table_html, unsafe_allow_html=True)

        # Alat eksport / screenshot satu klik untuk WhatsApp (PNG berkualiti tinggi & Copy Image)
        report_payload = json.dumps(
            {
                "dateStr": today_report_dt.strftime("%d-%m-%Y"),
                "tamat": [
                    {
                        "bil": str(r["BIL"]),
                        "status": r["STATUS WABAK"],
                        "kaw": r["KAW JAGAAN"],
                        "parl": r["PARLIMEN"],
                        "lok": r["LOKALITI"],
                        "kes": str(r["JUMLAH KES"]),
                        "ep": str(r["BIL EPISOD"]),
                        "tempoh": str(r["TEMPOH WABAK"]),
                        "mula": r["TARIKH MULA"],
                        "tamat": r["TARIKH TAMAT"],
                        "statusBg": r["status_bg"],
                        "kawBg": r["kaw_bg"],
                        "parlBg": r["parl_bg"],
                    }
                    for r in tamat_rows
                ],
                "aktif": [
                    {
                        "bil": str(r["BIL"]),
                        "status": r["STATUS WABAK"],
                        "kaw": r["KAW JAGAAN"],
                        "parl": r["PARLIMEN"],
                        "lok": r["LOKALITI"],
                        "kes": str(r["JUMLAH KES"]),
                        "ep": str(r["BIL EPISOD"]),
                        "tempoh": str(r["TEMPOH WABAK"]),
                        "mula": r["TARIKH MULA"],
                        "tamat": r["TARIKH TAMAT"],
                        "statusBg": r["status_bg"],
                        "kawBg": r["kaw_bg"],
                        "parlBg": r["parl_bg"],
                    }
                    for r in active_rows
                ],
            }
        )

        components.html(
            f"""
            <div style="font-family: Arial, sans-serif; margin-top: 2px;">
                <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center;">
                    <button id="btnDownloadWa" style="background-color: #128C7E; color: white; border: none; padding: 9px 16px; border-radius: 7px; font-size: 13.5px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.12);">
                        📸 Muat Turun Gambar (PNG) untuk WhatsApp
                    </button>
                    <button id="btnCopyWa" style="background-color: #075E54; color: white; border: none; padding: 9px 16px; border-radius: 7px; font-size: 13.5px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.12);">
                        📋 Salin Gambar (Paste Terus di WhatsApp)
                    </button>
                    <button id="btnPreviewWa" style="background-color: #F1F5F9; color: #1E293B; border: 1px solid #CBD5E1; padding: 9px 14px; border-radius: 7px; font-size: 13px; font-weight: 600; cursor: pointer;">
                        🖼️ Pratonton Screenshot
                    </button>
                    <span id="waStatusMsg" style="font-size: 13px; font-weight: 600; color: #0F766E;"></span>
                </div>
                <div id="previewContainer" style="display:none; margin-top: 12px; border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px; background: #F8FAFC;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size:12.5px; font-weight:700; color:#334155;">Pratonton Gambar Laporan (Klik kanan → Save Image / Copy Image jika perlu):</span>
                        <button id="btnClosePreview" style="background:#E2E8F0; border:none; border-radius:4px; padding:3px 9px; cursor:pointer; font-weight:700;">✕ Tutup</button>
                    </div>
                    <img id="previewImg" style="max-width: 100%; height: auto; border: 1px solid #94A3B8; display: block;" />
                </div>
            </div>

            <script>
            (function() {{
                const reportData = {report_payload};
                const headers = ["BIL", "STATUS WABAK", "KAW JAGAAN", "PARLIMEN", "LOKALITI", "JUMLAH KES", "BIL EPISOD", "TEMPOH WABAK", "TARIKH MULA", "TARIKH TAMAT"];

                function buildTableCanvas() {{
                    const dpr = 2;
                    const measureCanvas = document.createElement("canvas");
                    const mCtx = measureCanvas.getContext("2d");

                    // Kira lebar kolum secara dinamik supaya semua teks muat kemas tanpa terpotong
                    mCtx.font = "bold 12px Arial, sans-serif";
                    let maxLokWidth = mCtx.measureText("LOKALITI").width;
                    mCtx.font = "13px Arial, sans-serif";
                    const allRows = [...reportData.tamat, ...reportData.aktif];
                    allRows.forEach(r => {{
                        const w = mCtx.measureText(r.lok).width;
                        if (w > maxLokWidth) maxLokWidth = w;
                    }});

                    const lokColWidth = Math.max(360, Math.ceil(maxLokWidth + 28));
                    const colWidths = [44, 165, 96, 92, lokColWidth, 72, 72, 76, 94, 94];
                    const totalWidth = colWidths.reduce((a, b) => a + b, 0);

                    const mainBannerH = 38;
                    const spacerTopH = 8;
                    const secBannerH = 26;
                    const colHeaderH = 36;
                    const rowH = 25;
                    const midGapH = 18;

                    const tamatRowCount = Math.max(reportData.tamat.length, 1);
                    const aktifRowCount = Math.max(reportData.aktif.length, 1);

                    const totalHeight =
                        mainBannerH +
                        spacerTopH +
                        secBannerH +
                        colHeaderH +
                        tamatRowCount * rowH +
                        midGapH +
                        secBannerH +
                        colHeaderH +
                        aktifRowCount * rowH +
                        2;

                    const canvas = document.createElement("canvas");
                    canvas.width = totalWidth * dpr;
                    canvas.height = totalHeight * dpr;
                    const ctx = canvas.getContext("2d");
                    ctx.scale(dpr, dpr);

                    // Latar belakang putih keseluruhan
                    ctx.fillStyle = "#FFFFFF";
                    ctx.fillRect(0, 0, totalWidth, totalHeight);

                    function drawCell(x, y, w, h, text, bg, fg, font, align, padX) {{
                        ctx.fillStyle = bg;
                        ctx.fillRect(x, y, w, h);
                        ctx.strokeStyle = "#000000";
                        ctx.lineWidth = 1;
                        ctx.strokeRect(x + 0.5, y + 0.5, w, h);

                        ctx.fillStyle = fg;
                        ctx.font = font;
                        ctx.textBaseline = "middle";
                        const cy = y + h / 2 + 0.5;
                        if (align === "left") {{
                            ctx.textAlign = "left";
                            ctx.fillText(text, x + (padX || 8), cy);
                        }} else if (align === "right") {{
                            ctx.textAlign = "right";
                            ctx.fillText(text, x + w - (padX || 8), cy);
                        }} else {{
                            ctx.textAlign = "center";
                            ctx.fillText(text, x + w / 2, cy);
                        }}
                    }}

                    function drawHeaderRow(y) {{
                        let cx = 0;
                        const twoLineMap = {{
                            "JUMLAH KES": ["JUMLAH", "KES"],
                            "BIL EPISOD": ["BIL", "EPISOD"],
                            "TEMPOH WABAK": ["TEMPOH", "WABAK"],
                            "TARIKH MULA": ["TARIKH", "MULA"],
                            "TARIKH TAMAT": ["TARIKH", "TAMAT"]
                        }};
                        headers.forEach((hText, idx) => {{
                            const cw = colWidths[idx];
                            ctx.fillStyle = "#F9CB9C";
                            ctx.fillRect(cx, y, cw, colHeaderH);
                            ctx.strokeStyle = "#000000";
                            ctx.lineWidth = 1;
                            ctx.strokeRect(cx + 0.5, y + 0.5, cw, colHeaderH);

                            ctx.fillStyle = "#000000";
                            ctx.font = "bold 11.5px Arial, sans-serif";
                            ctx.textAlign = "center";
                            ctx.textBaseline = "middle";
                            if (twoLineMap[hText]) {{
                                ctx.fillText(twoLineMap[hText][0], cx + cw / 2, y + colHeaderH * 0.34);
                                ctx.fillText(twoLineMap[hText][1], cx + cw / 2, y + colHeaderH * 0.68);
                            }} else {{
                                ctx.fillText(hText, cx + cw / 2, y + colHeaderH / 2 + 0.5);
                            }}
                            cx += cw;
                        }});
                    }}

                    function drawDataRows(rows, startY) {{
                        let cy = startY;
                        if (!rows.length) {{
                            drawCell(0, cy, totalWidth, rowH, "TIADA", "#FFFFFF", "#000000", "bold 13px Arial, sans-serif", "center", 0);
                            return cy + rowH;
                        }}
                        rows.forEach(r => {{
                            const vals = [r.bil, r.status, r.kaw, r.parl, r.lok, r.kes, r.ep, r.tempoh, r.mula, r.tamat];
                            const bgs = ["#FFFFFF", r.statusBg, r.kawBg, r.parlBg, "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"];
                            const aligns = ["center", "left", "center", "center", "left", "right", "right", "right", "right", "right"];
                            let cx = 0;
                            vals.forEach((v, idx) => {{
                                const cw = colWidths[idx];
                                drawCell(cx, cy, cw, rowH, String(v), bgs[idx], "#000000", "13px Arial, sans-serif", aligns[idx], 8);
                                cx += cw;
                            }});
                            cy += rowH;
                        }});
                        return cy;
                    }}

                    let curY = 0;
                    // Tajuk Utama
                    drawCell(0, curY, totalWidth, mainBannerH, "STATUS WABAK (DENGGI)", "#EAD1DC", "#000000", "bold 19px Arial, sans-serif", "center", 0);
                    curY += mainBannerH + spacerTopH;

                    // Bahagian 1: WABAK TAMAT
                    drawCell(0, curY, totalWidth, secBannerH, "WABAK TAMAT", "#980000", "#FFFFFF", "bold 13px Arial, sans-serif", "center", 0);
                    curY += secBannerH;
                    drawHeaderRow(curY);
                    curY += colHeaderH;
                    curY = drawDataRows(reportData.tamat, curY);

                    curY += midGapH;

                    // Bahagian 2: SENARAI WABAK AKTIF
                    drawCell(0, curY, totalWidth, secBannerH, "SENARAI WABAK AKTIF", "#783F04", "#FFFFFF", "bold 13px Arial, sans-serif", "center", 0);
                    curY += secBannerH;
                    drawHeaderRow(curY);
                    curY += colHeaderH;
                    drawDataRows(reportData.aktif, curY);

                    return canvas;
                }}

                const statusEl = document.getElementById("waStatusMsg");
                const previewBox = document.getElementById("previewContainer");
                const previewImg = document.getElementById("previewImg");

                document.getElementById("btnDownloadWa").addEventListener("click", () => {{
                    const canvas = buildTableCanvas();
                    const link = document.createElement("a");
                    link.download = "Status_Wabak_Denggi_" + reportData.dateStr + ".png";
                    link.href = canvas.toDataURL("image/png");
                    link.click();
                    statusEl.textContent = "✅ Gambar PNG dimuat turun! Sedia untuk dihantar ke WhatsApp.";
                }});

                document.getElementById("btnCopyWa").addEventListener("click", () => {{
                    const canvas = buildTableCanvas();
                    canvas.toBlob(async (blob) => {{
                        try {{
                            await navigator.clipboard.write([
                                new ClipboardItem({{ "image/png": blob }})
                            ]);
                            statusEl.textContent = "✅ Gambar disalin ke clipboard! Terus tekan Paste (Ctrl+V) di WhatsApp.";
                        }} catch (err) {{
                            previewImg.src = canvas.toDataURL("image/png");
                            previewBox.style.display = "block";
                            statusEl.textContent = "ℹ️ Pelayar menyekat auto-copy; klik kanan pada pratonton gambar di bawah dan pilih Copy Image.";
                        }}
                    }}, "image/png");
                }});

                document.getElementById("btnPreviewWa").addEventListener("click", () => {{
                    const canvas = buildTableCanvas();
                    previewImg.src = canvas.toDataURL("image/png");
                    previewBox.style.display = previewBox.style.display === "none" ? "block" : "none";
                }});

                document.getElementById("btnClosePreview").addEventListener("click", () => {{
                    previewBox.style.display = "none";
                }});
            }})();
            </script>
            """,
            height=68,
        )

        st.markdown("---")

        # ---------------------------------------------------------
        # ANALISIS LOKALITI & WABAK
        # ---------------------------------------------------------
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
                    tarikh_mula = pd.Timestamp.today().normalize()

                tarikh_mula_str = tarikh_mula.strftime("%d-%m-%Y")

                if "Tamat" in status_wabak_semasa:
                    tarikh_akhir = tarikh_kes[-1]
                else:
                    tarikh_akhir = pd.Timestamp.today().normalize()

                tempoh_wabak_hari = max((tarikh_akhir - tarikh_mula).days, 1)

            jumlah_kes = len(df_filter)
            pentadbir_lokaliti = (
                df_filter["Pihak Pentadbir Lokaliti"].mode()[0]
                if not df_filter["Pihak Pentadbir Lokaliti"].empty
                else "Tidak Dinyatakan"
            )
            rekod_episode_lokaliti = episode_map.get(pilihan_lokaliti, 0)

            st.markdown('<div id="analisis-lokaliti-anchor"></div>', unsafe_allow_html=True)
            if st.session_state.get("scroll_to_lokaliti", False):
                st.session_state.scroll_to_lokaliti = False
                components.html(
                    """
                    <script>
                    setTimeout(function() {
                        const el = window.parent.document.getElementById('analisis-lokaliti-anchor');
                        if (el) {
                            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                    }, 150);
                    </script>
                    """,
                    height=0,
                )

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
                            t_m = pd.Timestamp.today().normalize()

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
                            tempoh = max(
                                (pd.Timestamp.today().normalize() - t_m).days, 1
                            )
                            lbl_tarikh = "Anggaran Tarikh Tamat"
                            lbl_tempoh = "Tempoh (Sehingga Kini)"

                        # Titik tengah & lebar bar (dalam milisaat) supaya lebar bar sepadan tepat dengan bilangan hari episod
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

                        # Bina paksi minggu penuh untuk tempoh tahun dipilih supaya ruang kosong & label ME tepat
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

                        # Buang pertindihan label pada penghujung tahun sambil mengekalkan pemetaan masa tepat
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

                            # Bina graf dengan lebar setiap bar sepadan tepat dengan bilangan hari episod
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

                            # Jambatan masa nyata (real-time) supaya graf mengezum serta-merta semasa penanda slider digerakkan
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

                        # Jadual ringkasan semua episod supaya mudah disemak apabila banyak episod
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
