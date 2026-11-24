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

st.set_page_config(
    page_title="DengueWatch // Executive Intelligence Command",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MS_PER_DAY = 24 * 60 * 60 * 1000

# =========================================================
# LIQUID-GLASS UI/UX, AURORA AMBIENT MOTION & TOOLTIP SYSTEM
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

    :root {
        --glass-bg: rgba(255, 255, 255, 0.68);
        --glass-bg-strong: rgba(255, 255, 255, 0.86);
        --glass-border: rgba(255, 255, 255, 0.88);
        --glass-shadow: 0 10px 34px rgba(15, 23, 42, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.95);
        --glass-shadow-hover: 0 16px 42px rgba(14, 165, 233, 0.16), inset 0 1px 0 rgba(255, 255, 255, 1);
        --text-primary: #0f172a;
        --text-muted: #475569;
    }

    /* Sembunyikan Sidebar Kiri & Butang Pembangun Kanan Atas untuk paparan eksekutif skrin penuh */
    #MainMenu,
    footer,
    .stDeployButton,
    .stAppDeployButton,
    [data-testid="stToolbar"],
    [data-testid="stAppToolbar"],
    [data-testid="stHeaderActionElements"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    section[data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stExpandSidebarButton"],
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
        visibility: hidden !important;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* Keluarkan iframe skrip height=0 daripada aliran susun atur supaya tiada ruang kosong */
    [data-testid="stElementContainer"]:has(iframe[height="0"]),
    .element-container:has(iframe[height="0"]) {
        position: absolute !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        pointer-events: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Tipografi Global */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
    }
    h1, h2, h3, h4 {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        letter-spacing: -0.02em;
    }

    /* Latar Belakang Aurora Mesh Lembut & Animasi Halus */
    @keyframes auroraDrift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes floatSlow {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.45); }
        50% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 14%, rgba(56, 189, 248, 0.16), transparent 38%),
            radial-gradient(circle at 86% 18%, rgba(244, 63, 94, 0.12), transparent 40%),
            radial-gradient(circle at 52% 85%, rgba(99, 102, 241, 0.13), transparent 44%),
            linear-gradient(125deg, #f0f6ff 0%, #f8fafc 48%, #f3f4ff 100%);
        background-size: 160% 160%;
        animation: auroraDrift 22s ease infinite;
        transition: background-color 0.5s ease;
    }

    /* Kad Liquid-Glass Utama */
    .lg-banner {
        background: var(--glass-bg);
        backdrop-filter: blur(26px) saturate(185%);
        -webkit-backdrop-filter: blur(26px) saturate(185%);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 18px 24px;
        box-shadow: var(--glass-shadow);
        margin-bottom: 14px;
        transition: box-shadow 0.3s ease;
    }
    .lg-banner:hover {
        box-shadow: var(--glass-shadow-hover);
    }
    .lg-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #0369a1;
        background: rgba(14, 165, 233, 0.12);
        border: 1px solid rgba(14, 165, 233, 0.28);
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 8px;
    }
    .lg-live-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        display: inline-block;
        animation: pulseGlow 2s infinite;
    }
    .lg-hero-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.85rem;
        font-weight: 800;
        background: linear-gradient(120deg, #0f172a 0%, #0369a1 52%, #4f46e5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 4px 0;
        line-height: 1.2;
    }
    .lg-hero-sub {
        font-size: 0.92rem;
        color: var(--text-muted);
        margin: 0;
    }

    /* Sepanduk Penunjuk Episod Aktif yang Dipilih */
    .ep-active-banner {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
        background: linear-gradient(135deg, rgba(2, 132, 199, 0.14), rgba(79, 70, 229, 0.12));
        backdrop-filter: blur(18px);
        border: 1.5px solid rgba(2, 132, 199, 0.45);
        border-left: 5px solid #0284c7;
        border-radius: 14px;
        padding: 11px 16px;
        margin: 8px 0 14px 0;
        font-size: 0.88rem;
        color: #0f172a;
        box-shadow: 0 6px 20px rgba(2, 132, 199, 0.10);
    }

    /* Landing Hero Stage (Sebelum Fail Dimuat Naik) */
    .lg-landing-stage {
        background: rgba(255, 255, 255, 0.74);
        backdrop-filter: blur(30px) saturate(195%);
        -webkit-backdrop-filter: blur(30px) saturate(195%);
        border: 1.5px solid rgba(255, 255, 255, 0.92);
        border-radius: 28px;
        padding: 36px 32px 28px 32px;
        box-shadow: 0 24px 64px rgba(15, 23, 42, 0.08), inset 0 1px 0 rgba(255, 255, 255, 1);
        text-align: center;
        margin: 12px auto 18px auto;
        animation: floatSlow 6s ease-in-out infinite;
    }
    .lg-pill-row {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
        margin-top: 18px;
    }
    .lg-feature-pill {
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid rgba(203, 213, 225, 0.75);
        border-radius: 999px;
        padding: 6px 14px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #1e293b;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
    }

    /* Gaya Liquid-Glass untuk File Uploader (Drag & Drop Zone) */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.72) !important;
        backdrop-filter: blur(22px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(22px) saturate(180%) !important;
        border: 1.5px dashed rgba(14, 165, 233, 0.55) !important;
        border-radius: 18px !important;
        padding: 12px 16px !important;
        box-shadow: 0 10px 30px rgba(14, 165, 233, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.95) !important;
        transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1) !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #0284c7 !important;
        background: rgba(255, 255, 255, 0.90) !important;
        box-shadow: 0 14px 36px rgba(14, 165, 233, 0.16), inset 0 1px 0 rgba(255, 255, 255, 1) !important;
    }

    /* Gaya Liquid-Glass untuk Kotak Pilihan (Selectbox), Tarikh & Jarak Label */
    [data-testid="stSelectbox"] label,
    [data-testid="stDateInput"] label {
        font-weight: 600 !important;
        font-size: 0.86rem !important;
        color: #1e293b !important;
        margin-bottom: 6px !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stDateInput"] [data-baseweb="input"] {
        background: rgba(255, 255, 255, 0.84) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(203, 213, 225, 0.9) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div:hover,
    [data-testid="stDateInput"] [data-baseweb="input"]:hover {
        border-color: rgba(14, 165, 233, 0.6) !important;
        background: rgba(255, 255, 255, 0.98) !important;
    }

    /* Gaya Sub-Tab Liquid-Glass */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.62);
        backdrop-filter: blur(20px);
        padding: 6px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.88);
        box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 11px;
        padding: 8px 18px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        font-size: 0.9rem;
        transition: all 0.25s ease;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #0369a1 !important;
        box-shadow: 0 4px 14px rgba(14, 165, 233, 0.15) !important;
    }

    /* Butang Liquid-Glass & Butang Navigasi Aktif */
    .stButton > button, .stDownloadButton > button {
        background: rgba(255, 255, 255, 0.80) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.92) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05) !important;
        font-weight: 600 !important;
        color: #0f172a !important;
        transition: all 0.22s ease !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: rgba(255, 255, 255, 0.98) !important;
        border-color: rgba(14, 165, 233, 0.55) !important;
        box-shadow: 0 8px 22px rgba(14, 165, 233, 0.16) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.65) !important;
        box-shadow: 0 8px 22px rgba(2, 132, 199, 0.28) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0369a1 0%, #4338ca 100%) !important;
        color: #ffffff !important;
    }

    @media print {
        header {visibility: hidden;}
        section[data-testid="stSidebar"] {display: none;}
        .stButton > button {display: none;}
        footer {visibility: hidden;}
        .metric-tooltip-bubble, .ai-tooltip-bubble, #dw-global-tooltip-portal {display: none !important;}
        .metric-hover-card, .ai-hover-card {padding: 0 !important; box-shadow: none !important; background: transparent !important;}
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

    /* Jadual STATUS WABAK (DENGGI) - Paparan Harian Eksekutif */
    .sw-wrapper {
        width: 100%;
        overflow-x: auto;
        background: rgba(255, 255, 255, 0.94);
        padding: 8px;
        border: 1px solid rgba(255, 255, 255, 0.95);
        border-radius: 14px;
        box-shadow: var(--glass-shadow);
        margin-bottom: 12px;
    }
    .sw-title-banner {
        background-color: #eadbe2;
        color: #111111;
        font-weight: 800;
        font-size: 1.22rem;
        text-align: center;
        padding: 8px 12px;
        border: 1px solid #333333;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .sw-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Inter', Arial, sans-serif;
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
        color: #0f172a !important;
        font-weight: 600;
        transition: background-color 0.15s ease, color 0.15s ease;
    }
    .sw-lok-link:hover {
        background-color: #e0f2fe !important;
        color: #0369a1 !important;
        text-decoration: underline;
    }

    /* Keluarkan butang pencetus navigasi SW_JUMP_*, EP_JUMP_* dan RK_JUMP_* daripada aliran susun atur supaya 0px ruang kosong */
    [class*="st-key-sw_jump_trigger_"],
    [class*="st-key-ep_jump_trigger_"],
    [class*="st-key-rk_jump_trigger_"] {
        position: absolute !important;
        left: -9999px !important;
        top: 0 !important;
        width: 1px !important;
        height: 1px !important;
        overflow: hidden !important;
        opacity: 0.01 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Kad Metrik Liquid-Glass dengan Kesan Tonasi & Jarak Bawah Yang Jelas */
    .metric-hover-card {
        position: relative;
        background: var(--glass-bg-strong);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 13px 15px;
        box-shadow: var(--glass-shadow);
        transition: background-color 0.24s ease, border-color 0.24s ease, box-shadow 0.24s ease;
        cursor: help;
        margin-bottom: 14px;
    }
    .metric-hover-card:hover {
        background: rgba(240, 249, 255, 0.96);
        border-color: rgba(14, 165, 233, 0.65);
        box-shadow: var(--glass-shadow-hover);
    }
    .metric-hover-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-muted);
        line-height: 1.35;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 5px;
    }
    .metric-hover-badge {
        font-size: 0.68rem;
        color: #0369a1;
        background: rgba(14, 165, 233, 0.14);
        border: 1px solid rgba(14, 165, 233, 0.38);
        border-radius: 50%;
        width: 18px;
        height: 18px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        flex-shrink: 0;
    }
    .metric-hover-value {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.95rem;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1.15;
    }
    .metric-hover-sub {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 4px;
    }

    /* Kad interaktif bagi jadual & lencana metodologi graf dalam Pusat Analisis AI */
    .ai-hover-card {
        position: relative;
        padding: 12px 14px;
        border-radius: 16px;
        border: 1px solid var(--glass-border);
        background: var(--glass-bg-strong);
        box-shadow: var(--glass-shadow);
        transition: background-color 0.24s ease, border-color 0.24s ease, box-shadow 0.24s ease;
        cursor: help;
        margin-bottom: 10px;
    }
    .ai-hover-card:hover {
        background: rgba(240, 249, 255, 0.96);
        border-color: rgba(14, 165, 233, 0.65);
        box-shadow: var(--glass-shadow-hover);
    }
    .ai-graph-info-strip {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
        padding: 7px 12px;
        border-radius: 12px;
        border: 1px solid rgba(14, 165, 233, 0.32);
        background: rgba(255, 255, 255, 0.84);
        margin-bottom: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #0f172a;
        cursor: help;
        transition: background-color 0.2s ease, border-color 0.2s ease;
    }
    .ai-graph-info-strip:hover {
        background: rgba(224, 242, 254, 0.95);
        border-color: #0284c7;
    }
    .ai-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        font-size: 0.92rem;
    }
    .ai-card-pill {
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 9px;
        border-radius: 999px;
        background-color: rgba(14, 165, 233, 0.14);
        color: #0369a1;
        border: 1px solid rgba(14, 165, 233, 0.35);
        white-space: nowrap;
    }

    /* Templat kandungan tooltip tersembunyi (dipaparkan oleh Portal Terapung Paling Hadapan) */
    .metric-tooltip-bubble, .ai-tooltip-bubble {
        display: none !important;
    }

    .ai-data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.82rem;
        background-color: rgba(255, 255, 255, 0.95);
        color: #0f172a;
        border-radius: 8px;
        overflow: hidden;
    }
    .ai-data-table th {
        background-color: #f1f5f9;
        color: #0f172a;
        font-weight: 700;
        padding: 6px 8px;
        border: 1px solid #cbd5e1;
        text-align: center;
    }
    .ai-data-table td {
        padding: 5px 8px;
        border: 1px solid #e2e8f0;
        color: #0f172a;
    }
    .ai-data-table tr:nth-child(even) td {
        background-color: #f8fafc;
    }
    .ai-conclusion-box {
        background: rgba(255, 255, 255, 0.82);
        border-left: 4px solid #0284c7;
        border-top: 1px solid rgba(255, 255, 255, 0.92);
        border-right: 1px solid rgba(255, 255, 255, 0.92);
        border-bottom: 1px solid rgba(255, 255, 255, 0.92);
        border-radius: 0 12px 12px 0;
        padding: 10px 14px;
        margin: 4px 0 12px 0;
        font-size: 0.83rem;
        line-height: 1.5;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
        transition: background-color 0.24s ease, box-shadow 0.24s ease;
    }
    .ai-conclusion-box:hover {
        background: rgba(240, 249, 255, 0.96);
        box-shadow: 0 8px 22px rgba(2, 132, 199, 0.14);
    }
    .ai-conclusion-title {
        font-weight: 700;
        font-size: 0.84rem;
        color: #0369a1;
        margin-bottom: 3px;
    }
    .ai-table-conclusion {
        margin-top: 8px;
        padding: 8px 10px;
        border-radius: 0 8px 8px 0;
        background-color: rgba(14, 165, 233, 0.08);
        border-left: 3px solid #0284c7;
        font-size: 0.81rem;
        line-height: 1.48;
    }

    /* Lencana Kesiapsiagaan Kawalan Lapangan (PTP / SRT / ULV) */
    .ops-pill-ok {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.14);
        color: #065f46;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 5px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .ops-pill-miss {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(244, 63, 94, 0.14);
        color: #9f1239;
        border: 1px solid rgba(244, 63, 94, 0.4);
        padding: 5px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 700;
    }

    /* Executive Live Risk Radar Grid (Shimmer Loop & Clickable Cards) */
    @keyframes riskSheenSweep {
        0% { transform: translateX(-140%) skewX(-22deg); }
        42%, 100% { transform: translateX(320%) skewX(-22deg); }
    }
    @keyframes critHaloPulse {
        0%, 100% { box-shadow: 0 6px 18px rgba(220, 38, 38, 0.16), 0 0 0 0 rgba(239, 68, 68, 0.35); }
        50% { box-shadow: 0 8px 24px rgba(220, 38, 38, 0.28), 0 0 0 5px rgba(239, 68, 68, 0); }
    }
    .risk-radar-strip {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.86), rgba(241, 245, 249, 0.80));
        backdrop-filter: blur(24px) saturate(185%);
        -webkit-backdrop-filter: blur(24px) saturate(185%);
        border: 1px solid rgba(255, 255, 255, 0.96);
        border-radius: 18px;
        padding: 14px 16px 16px 16px;
        margin: 4px 0 12px 0;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06), inset 0 1px 0 rgba(255, 255, 255, 1);
    }
    .risk-radar-header {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
        padding-bottom: 10px;
        margin-bottom: 12px;
        border-bottom: 1px solid rgba(203, 213, 225, 0.65);
    }
    .risk-radar-title-group {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 8px;
    }
    .risk-radar-eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.07em;
        color: #0369a1;
        background: rgba(14, 165, 233, 0.13);
        border: 1px solid rgba(14, 165, 233, 0.30);
        padding: 3px 8px;
        border-radius: 6px;
    }
    .risk-radar-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.94rem;
        font-weight: 800;
        color: #0f172a;
    }
    .risk-radar-sub {
        font-size: 0.76rem;
        color: #64748b;
    }
    .risk-radar-counts {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.76rem;
        font-weight: 700;
    }
    .rc-chip {
        padding: 3px 10px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(203, 213, 225, 0.8);
    }
    .rc-krit { color: #b91c1c; }
    .rc-tinggi { color: #b45309; }
    .rc-sed { color: #0369a1; }

    .risk-radar-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        justify-content: center;
    }
    @media (max-width: 1100px) {
        .risk-radar-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 640px) {
        .risk-radar-grid { grid-template-columns: minmax(0, 1fr); }
    }
    .risk-exec-card {
        position: relative !important;
        overflow: hidden !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        background: rgba(255, 255, 255, 0.94) !important;
        border: 1px solid rgba(226, 232, 240, 0.95) !important;
        border-radius: 13px !important;
        padding: 10px 12px !important;
        margin: 0 !important;
        cursor: pointer !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
    }
    .risk-exec-card:hover {
        transform: translateY(-2px) !important;
        background: #ffffff !important;
        border-color: #0284c7 !important;
        box-shadow: 0 10px 24px rgba(2, 132, 199, 0.16) !important;
    }
    .risk-card-kritikal {
        border-left: 4px solid #dc2626 !important;
        animation: critHaloPulse 2.6s ease-in-out infinite;
    }
    .risk-card-tinggi {
        border-left: 4px solid #d97706 !important;
    }
    .risk-card-sederhana {
        border-left: 4px solid #0284c7 !important;
    }
    .risk-card-shine {
        position: absolute;
        top: 0;
        left: 0;
        width: 38%;
        height: 100%;
        background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(186,230,253,0.42) 50%, rgba(255,255,255,0) 100%);
        animation: riskSheenSweep 4.2s ease-in-out infinite;
        pointer-events: none;
    }
    .risk-card-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 6px;
        margin-bottom: 5px;
    }
    .risk-card-rank {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748b;
    }
    .risk-card-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.66rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        padding: 2px 7px;
        border-radius: 999px;
    }
    .risk-card-score {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.95rem;
        font-weight: 800;
        color: #0f172a;
        margin-left: auto;
    }
    .risk-card-score small {
        font-size: 0.68rem;
        font-weight: 600;
        color: #64748b;
    }
    .risk-card-lok {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.79rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.3;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        min-height: 2.05em;
        margin-bottom: 6px;
    }
    .risk-card-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.72rem;
        color: #475569;
        padding-top: 5px;
        border-top: 1px dashed #e2e8f0;
    }
    .risk-card-proj {
        color: #0369a1;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# PORTAL TERAPUNG GLOBAL UNTUK GELEMBUNG INFO (TANPA MENGHALANG DATA & BOLEH SKROL)
# =========================================================
components.html(
    """
    <script>
    (function() {
        const doc = window.parent.document;
        const win = window.parent;

        if (!doc.getElementById('dw-portal-style')) {
            const st = doc.createElement('style');
            st.id = 'dw-portal-style';
            st.textContent = `
                #dw-global-tooltip-portal {
                    position: fixed;
                    z-index: 2147483647;
                    pointer-events: auto;
                    width: 420px;
                    max-width: 90vw;
                    max-height: 76vh;
                    overflow-y: auto;
                    overscroll-behavior: contain;
                    scrollbar-width: thin;
                    scrollbar-color: #38bdf8 rgba(255, 255, 255, 0.12);
                    background: rgba(15, 23, 42, 0.97);
                    backdrop-filter: blur(22px) saturate(180%);
                    -webkit-backdrop-filter: blur(22px) saturate(180%);
                    color: #f8fafc;
                    padding: 15px 17px 16px 17px;
                    border-radius: 14px;
                    box-shadow: 0 22px 48px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(125, 211, 252, 0.36);
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    font-size: 0.82rem;
                    line-height: 1.5;
                    text-align: left;
                    opacity: 0;
                    visibility: hidden;
                    transform: translateY(4px);
                    transition: opacity 0.16s ease, transform 0.16s ease, visibility 0.16s ease;
                }
                #dw-global-tooltip-portal::-webkit-scrollbar {
                    width: 7px;
                }
                #dw-global-tooltip-portal::-webkit-scrollbar-track {
                    background: rgba(255, 255, 255, 0.08);
                    border-radius: 8px;
                }
                #dw-global-tooltip-portal::-webkit-scrollbar-thumb {
                    background: #38bdf8;
                    border-radius: 8px;
                }
                #dw-global-tooltip-portal.dw-visible {
                    opacity: 1;
                    visibility: visible;
                    transform: translateY(0);
                }
                #dw-global-tooltip-portal .dw-portal-close-bar {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-size: 0.71rem;
                    color: #94a3b8;
                    margin-bottom: 6px;
                    padding-bottom: 4px;
                    border-bottom: 1px dashed rgba(148, 163, 184, 0.25);
                }
                #dw-global-tooltip-portal .dw-portal-close-btn {
                    background: rgba(255, 255, 255, 0.12);
                    color: #e2e8f0;
                    border: none;
                    border-radius: 6px;
                    padding: 1px 7px;
                    font-size: 0.75rem;
                    font-weight: 700;
                    cursor: pointer;
                }
                #dw-global-tooltip-portal .dw-portal-close-btn:hover {
                    background: rgba(239, 68, 68, 0.75);
                    color: #ffffff;
                }
                #dw-global-tooltip-portal .tooltip-title {
                    font-size: 0.92rem;
                    font-weight: 700;
                    color: #7dd3fc;
                    margin-bottom: 6px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.16);
                    padding-bottom: 5px;
                }
                #dw-global-tooltip-portal .tooltip-section {
                    margin-bottom: 7px;
                }
                #dw-global-tooltip-portal .tooltip-formula {
                    background-color: rgba(255, 255, 255, 0.10);
                    padding: 6px 9px;
                    border-radius: 7px;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.78rem;
                    color: #fde68a;
                    margin: 4px 0 6px 0;
                }
                #dw-global-tooltip-portal .tooltip-current {
                    background-color: rgba(56, 189, 248, 0.18);
                    border-left: 3px solid #38bdf8;
                    padding: 7px 9px;
                    border-radius: 5px;
                    margin-top: 6px;
                    color: #e0f2fe;
                }
            `;
            doc.head.appendChild(st);
        }

        let portal = doc.getElementById('dw-global-tooltip-portal');
        if (!portal) {
            portal = doc.createElement('div');
            portal.id = 'dw-global-tooltip-portal';
            doc.body.appendChild(portal);
        }

        let activeHost = null;
        let hideTimer = null;

        function clearHideTimer() {
            if (hideTimer) {
                clearTimeout(hideTimer);
                hideTimer = null;
            }
        }

        function hidePortalNow() {
            clearHideTimer();
            if (portal) portal.classList.remove('dw-visible');
            activeHost = null;
        }

        function scheduleHidePortal() {
            clearHideTimer();
            hideTimer = setTimeout(() => {
                if (portal && portal.matches(':hover')) return;
                if (activeHost && activeHost.matches(':hover')) return;
                hidePortalNow();
            }, 280);
        }

        function positionPortalSideBySide(anchorRect, isKpiCard) {
            const pad = 14;
            const gap = 14;
            const pWidth = Math.min(420, win.innerWidth - pad * 2);
            portal.style.width = pWidth + 'px';

            const pRect = portal.getBoundingClientRect();
            const pHeight = Math.min(pRect.height || 260, win.innerHeight * 0.76);

            if (isKpiCard) {
                let left = anchorRect.left;
                if (left + pWidth > win.innerWidth - pad) {
                    left = win.innerWidth - pWidth - pad;
                }
                if (left < pad) left = pad;
                let top = anchorRect.bottom + 8;
                if (top + pHeight > win.innerHeight - pad) {
                    top = Math.max(pad, anchorRect.top - pHeight - 8);
                }
                portal.style.left = Math.round(left) + 'px';
                portal.style.top = Math.round(top) + 'px';
                return;
            }

            const anchorCenterX = anchorRect.left + anchorRect.width / 2;
            const isLeftColumn = anchorCenterX < (win.innerWidth * 0.52);

            let left;
            if (isLeftColumn) {
                left = anchorRect.right + gap;
                if (left + pWidth > win.innerWidth - pad) {
                    left = win.innerWidth - pWidth - pad;
                }
            } else {
                left = anchorRect.left - pWidth - gap;
                if (left < pad) {
                    left = pad;
                }
            }

            let top = anchorRect.top;
            if (top + pHeight > win.innerHeight - pad) {
                top = win.innerHeight - pHeight - pad;
            }
            if (top < pad) top = pad;

            portal.style.left = Math.round(left) + 'px';
            portal.style.top = Math.round(top) + 'px';
        }

        function findPrecedingChartBubble(chartContainer) {
            if (!chartContainer) return null;
            let el = chartContainer.closest('[data-testid="stElementContainer"], .element-container') || chartContainer;
            let prev = el.previousElementSibling;
            let hops = 0;
            while (prev && hops < 3) {
                const strip = prev.querySelector('.ai-graph-info-strip');
                if (strip) {
                    const bubble = strip.querySelector('.ai-tooltip-bubble');
                    if (bubble) return bubble;
                }
                prev = prev.previousElementSibling;
                hops += 1;
            }
            return null;
        }

        function renderBubbleIntoPortal(hostEl, bubbleEl, isKpiCard) {
            clearHideTimer();
            if (activeHost !== hostEl) {
                activeHost = hostEl;
                portal.innerHTML =
                    '<div class="dw-portal-close-bar">' +
                    '<span>↕️ Arah kursor ke sini & skrol untuk baca penuh</span>' +
                    '<button type="button" class="dw-portal-close-btn" title="Tutup">✕</button>' +
                    '</div>' +
                    bubbleEl.innerHTML;
                portal.scrollTop = 0;
                portal.classList.add('dw-visible');
                const closeBtn = portal.querySelector('.dw-portal-close-btn');
                if (closeBtn) {
                    closeBtn.addEventListener('click', function(ev) {
                        ev.stopPropagation();
                        hidePortalNow();
                    });
                }
            }
            positionPortalSideBySide(hostEl.getBoundingClientRect(), isKpiCard);
        }

        function showPortalForTarget(target) {
            if (!target || !target.closest) return;

            if (target === portal || portal.contains(target)) {
                clearHideTimer();
                return;
            }

            const kpiCard = target.closest('.metric-hover-card');
            if (kpiCard) {
                const bubble = kpiCard.querySelector('.metric-tooltip-bubble');
                if (bubble) {
                    renderBubbleIntoPortal(kpiCard, bubble, true);
                    return;
                }
            }

            const aiCard = target.closest('.ai-hover-card, .ai-graph-info-strip');
            if (aiCard) {
                const bubble = aiCard.querySelector('.ai-tooltip-bubble');
                if (bubble) {
                    renderBubbleIntoPortal(aiCard, bubble, false);
                    return;
                }
            }

            const chartEl = target.closest('[data-testid="stPlotlyChart"]');
            if (chartEl) {
                const bubble = findPrecedingChartBubble(chartEl);
                if (bubble) {
                    renderBubbleIntoPortal(chartEl, bubble, false);
                    return;
                }
            }

            if (activeHost) {
                scheduleHidePortal();
            }
        }

        if (!win._dwTooltipPortalBound) {
            win._dwTooltipPortalBound = true;
            portal.addEventListener('mouseenter', clearHideTimer);
            portal.addEventListener('mouseleave', scheduleHidePortal);

            doc.addEventListener('mouseover', function(e) {
                showPortalForTarget(e.target);
            }, true);
            doc.addEventListener('mouseleave', scheduleHidePortal, true);
            win.addEventListener('scroll', function(e) {
                if (e && e.target && (e.target === portal || (portal && portal.contains(e.target)))) {
                    return;
                }
                hidePortalNow();
            }, true);
            doc.addEventListener('click', function(e) {
                if (e.target && (e.target.closest('[data-baseweb="tab"]') || e.target.closest('button:not(.dw-portal-close-btn)'))) {
                    hidePortalNow();
                }
            }, true);
        }
    })();
    </script>
    """,
    height=0,
)


def get_embedded_gemini_key():
    """Membaca kunci GEMINI_API_KEY yang tertanam dalam Streamlit Secrets atau pembolehubah persekitaran."""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            val = str(st.secrets["GEMINI_API_KEY"]).strip()
            if val:
                return val
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "").strip()


def get_today_malaysia():
    """Mengesan tarikh semasa secara automatik mengikut zon waktu Malaysia (Asia/Kuala_Lumpur)."""
    try:
        return pd.Timestamp.now(tz="Asia/Kuala_Lumpur").tz_localize(None).normalize()
    except Exception:
        return pd.Timestamp.today().normalize()


def get_dataset_anchor_date(df, fallback_today):
    """Mengesan tarikh laporan sebenar berdasarkan rekod terkini dalam dataset yang dimuat naik."""
    candidates = []
    for col in ["Tarikh Daftar", "Tkh Notifikasi"]:
        if col in df.columns and df[col].notna().any():
            candidates.append(df[col].max().normalize())
    if candidates:
        return max(candidates)
    return fallback_today


def format_wabak_no(val):
    """Memformat nombor wabak supaya bersih tanpa '.0' di hujung."""
    try:
        f_val = float(val)
        if f_val.is_integer():
            return str(int(f_val))
        return str(f_val)
    except Exception:
        return str(val).strip()


def clean_locality_display(lok):
    """Memastikan kurungan terbuka pada nama lokaliti ditutup dengan kemas untuk paparan jadual."""
    s = str(lok).strip()
    if s.count("(") > s.count(")"):
        s += ")" * (s.count("(") - s.count(")"))
    return s


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


def get_status_style(st_str):
    """Mengembalikan (warna_latar, warna_teks) sepadan dengan format jadual harian PKD."""
    s = str(st_str).upper()
    if "BARU" in s:
        return "#00ffff", "#000000"
    if "HOTSPOT" in s:
        return "#fe0000", "#ffffff"
    if "TAK TERKAWAL" in s:
        return "#3e85c7", "#ffffff"
    if "TERKAWAL" in s:
        return "#f4cccc", "#000000"
    if "TAMAT" in s:
        return "#ffffff", "#000000"
    return "#ffffff", "#000000"


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


def render_ai_conclusion_box(title, body_html):
    """Menjana blok kesimpulan automatik berasaskan data di bawah setiap graf atau visualisasi."""
    return (
        f'<div class="ai-conclusion-box">'
        f'<div class="ai-conclusion-title">📌 {html.escape(title)}</div>'
        f"<div>{body_html}</div>"
        f"</div>"
    )


def build_glass_kpi_html(
    label,
    value_str,
    sub_str,
    tooltip_title,
    relevance_html,
    formula_html,
    current_calc_html,
    accent_color="#0f172a",
):
    """Membina kad KPI Liquid-Glass dengan kesan tonasi & gelembung info apabila kursor diarahkan."""
    return (
        f'<div class="metric-hover-card">'
        f'<div class="metric-hover-label"><span>{html.escape(label)}</span><span class="metric-hover-badge">?</span></div>'
        f'<div class="metric-hover-value" style="color:{accent_color};">{html.escape(str(value_str))}</div>'
        f'<div class="metric-hover-sub">{sub_str}</div>'
        f'<div class="metric-tooltip-bubble">'
        f'<div class="tooltip-title">{tooltip_title}</div>'
        f'<div class="tooltip-section"><b>Maksud & Relevansi:</b> {relevance_html}</div>'
        f'<div class="tooltip-section"><b>Formula & Cara Kira:</b>'
        f'<div class="tooltip-formula">{formula_html}</div></div>'
        f'<div class="tooltip-current">{current_calc_html}</div>'
        f"</div>"
        f"</div>"
    )


def build_graph_info_strip_html(
    strip_title,
    tooltip_title,
    relevance_html,
    formula_html,
    current_calc_html,
):
    """Jalur lencana metodologi & formula di bahagian atas graf AI (juga aktif bila kursor di atas kawasan data graf)."""
    return (
        f'<div class="ai-graph-info-strip">'
        f"<span>{html.escape(strip_title)}</span>"
        f'<span class="ai-card-pill">? Formula & Relevansi</span>'
        f'<div class="ai-tooltip-bubble">'
        f'<div class="tooltip-title">{tooltip_title}</div>'
        f'<div class="tooltip-section"><b>Maksud & Relevansi:</b> {relevance_html}</div>'
        f'<div class="tooltip-section"><b>Formula & Cara Kira:</b>'
        f'<div class="tooltip-formula">{formula_html}</div></div>'
        f'<div class="tooltip-current">{current_calc_html}</div>'
        f"</div>"
        f"</div>"
    )


def df_to_styled_html_table(df_in, badge_cols=None):
    """Menukar DataFrame kepada jadual HTML kemas dengan lencana warna pilihan."""
    if df_in is None or df_in.empty:
        return '<div style="padding:8px; font-size:0.84rem; opacity:0.8;">Tiada data tersedia untuk paparan ini.</div>'
    badge_cols = badge_cols or {}
    ths = "".join(f"<th>{html.escape(str(c))}</th>" for c in df_in.columns)
    rows_html = []
    for _, r in df_in.iterrows():
        tds = []
        for c in df_in.columns:
            val = r[c]
            val_str = "-" if pd.isna(val) else str(val)
            if c in badge_cols and val_str in badge_cols[c]:
                bg, fg = badge_cols[c][val_str]
                tds.append(
                    f'<td style="text-align:center;"><span style="background:{bg};color:{fg};padding:2px 8px;border-radius:999px;font-weight:700;font-size:0.76rem;display:inline-block;">{html.escape(val_str)}</span></td>'
                )
            else:
                align = (
                    "right"
                    if isinstance(val, (int, float, np.integer, np.floating))
                    and not pd.isna(val)
                    else "left"
                )
                tds.append(
                    f'<td style="text-align:{align};">{html.escape(val_str)}</td>'
                )
        rows_html.append(f"<tr>{''.join(tds)}</tr>")
    return (
        '<div style="overflow-x:auto;">'
        f'<table class="ai-data-table"><thead><tr>{ths}</tr></thead><tbody>{"".join(rows_html)}</tbody></table>'
        "</div>"
    )


def build_ai_hover_card_html(
    zone_id,
    card_title,
    body_html,
    tooltip_title,
    relevance_html,
    formula_html,
    current_calc_html,
    conclusion_html="",
):
    """Membina kad interaktif dengan kesan tonasi, kesimpulan data di bahagian bawah & gelembung info."""
    conc_block = (
        f'<div class="ai-table-conclusion">{conclusion_html}</div>'
        if conclusion_html
        else ""
    )
    return (
        f'<div class="ai-hover-card" data-ai-zone="{html.escape(zone_id)}">'
        f'<div class="ai-card-header">'
        f"<span>{html.escape(card_title)}</span>"
        f'<span class="ai-card-pill">? Info & Formula</span>'
        f"</div>"
        f"{body_html}"
        f"{conc_block}"
        f'<div class="ai-tooltip-bubble">'
        f'<div class="tooltip-title">{tooltip_title}</div>'
        f'<div class="tooltip-section"><b>Maksud & Relevansi:</b> {relevance_html}</div>'
        f'<div class="tooltip-section"><b>Formula & Cara Kira:</b>'
        f'<div class="tooltip-formula">{formula_html}</div></div>'
        f'<div class="tooltip-current">{current_calc_html}</div>'
        f"</div>"
        f"</div>"
    )


def build_status_wabak_tables(df, report_date):
    """Menjana jadual WABAK TAMAT dan SENARAI WABAK AKTIF mengikut logik harian PKD."""
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
        "WABAK BARU": 0,
        "WABAK TERKAWAL": 1,
        "WABAK TAK TERKAWAL": 2,
        "HOTSPOT": 3,
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
        lok_raw = str(lok).strip()
        lok_disp = clean_locality_display(lok_raw)

        if "TAMAT" in status_upper:
            if (report_date - pd.Timedelta(days=1)) <= t_tamat.normalize() <= report_date:
                tempoh = max((t_tamat - t_mula).days, 1)
                tamat_rows.append(
                    {
                        "Wabak No": w_no,
                        "STATUS WABAK": "WABAK TAMAT (WT)",
                        "KAW JAGAAN": kaw_val,
                        "PARLIMEN": parl_val,
                        "LOKALITI": lok_disp,
                        "_lok_raw": lok_raw,
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
                    "LOKALITI": lok_disp,
                    "_lok_raw": lok_raw,
                    "JUMLAH KES": jumlah_kes,
                    "BIL EPISOD": bil_episod,
                    "TEMPOH WABAK": tempoh,
                    "TARIKH MULA": fmt_date_short(t_mula),
                    "TARIKH TAMAT": fmt_date_short(t_tamat),
                    "_rank": status_rank_map.get(status_upper, 4),
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


def render_front_risk_radar_html(df, report_date):
    """Membina grid eksekutif 'Radar Tahap Risiko Eskalasi' bercahaya (shimmer loop) & boleh klik terus ke Analisis Lokaliti."""
    report_date = pd.Timestamp(report_date).normalize()
    df_act = df[
        (df["Jenis Kes"] == "Wabak")
        & (df["Wabak Status"].notna())
        & (~df["Wabak Status"].astype(str).str.contains("Tamat", case=False, na=False))
    ].dropna(subset=["Wabak No"]).copy()

    if df_act.empty:
        return "", []

    cards_html = []
    clickable_items = []
    risk_items = []

    for (w_no, lok), grp in df_act.groupby(["Wabak No", "Lokaliti (Alamat Semasa)"]):
        st_w = str(grp["Wabak Status"].iloc[0]).strip()
        st_up = st_w.upper()
        t_ser = (
            grp["Tkh Notifikasi"].fillna(grp["Tarikh Daftar"])
            if "Tkh Notifikasi" in grp.columns
            else grp["Tarikh Daftar"]
        )
        t_list = t_ser.dropna().sort_values().tolist()
        if not t_list:
            continue
        t_mula = t_list[1] if len(t_list) >= 2 else t_list[0]
        tempoh = max((report_date - t_mula).days, 1)
        kes = len(grp)
        vel = kes / tempoh

        c_7d = int(
            ((t_ser >= (report_date - pd.Timedelta(days=6))) & (t_ser <= report_date)).sum()
        )
        c_prev7d = int(
            (
                (t_ser >= (report_date - pd.Timedelta(days=13)))
                & (t_ser <= (report_date - pd.Timedelta(days=7)))
            ).sum()
        )
        mom_pct = ((c_7d - c_prev7d) / max(c_prev7d, 1)) * 100.0
        mom_str = (
            f"+{c_7d} kes baharu"
            if (c_prev7d == 0 and c_7d > 0)
            else f"{mom_pct:+.1f}%"
        )

        p_vel = min(vel * 35.0, 35.0)
        p_c7 = min(c_7d * 8.0, 30.0)
        p_dur = min(tempoh * 0.6, 20.0)
        p_bon = 15 if "HOTSPOT" in st_up else (10 if "TAK TERKAWAL" in st_up else 0)
        score = min(100, int(round(p_vel + p_c7 + p_dur + p_bon)))

        rate_daily = max(c_7d / 7.0, vel * 0.5)
        proj_14d = rate_daily * 14.0
        ci_l = max(0.0, proj_14d - 1.96 * np.sqrt(max(proj_14d, 0.5)))
        ci_u = proj_14d + 1.96 * np.sqrt(max(proj_14d, 0.5))

        if score >= 70:
            tier = "KRITIKAL"
            tier_cls = "risk-card-kritikal"
            tier_icon = "🔴"
            badge_bg = "#fee2e2"
            badge_fg = "#991b1b"
            tier_reason = "Skor ≥70 (Julat 70–100): Penularan berkelajuan tinggi, lonjakan kes 7 hari terkini, atau tempoh wabak berpanjangan. Memerlukan mobilisasi kecemasan segera (PTP/S&D intensif, ulangan SRT/ULV & ACD)."
        elif score >= 45:
            tier = "TINGGI"
            tier_cls = "risk-card-tinggi"
            tier_icon = "🟠"
            badge_bg = "#fef3c7"
            badge_fg = "#92400e"
            tier_reason = "Skor 45–69: Berisiko tinggi untuk meningkat ke Wabak Tak Terkawal atau Hotspot dalam tempoh 14 hari jika kawalan susulan tidak dipercepatkan."
        else:
            tier = "SEDERHANA"
            tier_cls = "risk-card-sederhana"
            tier_icon = "🔵"
            badge_bg = "#e0f2fe"
            badge_fg = "#075985"
            tier_reason = "Skor 0–44: Wabak fasa awal atau terkawal dengan halaju rendah. Kekalkan jadual kawalan vektor piawai KKM/POA dan pantau sebarang lonjakan 7 hari."

        risk_items.append(
            {
                "score": score,
                "vel": vel,
                "lok_raw": str(lok).strip(),
                "w_no_raw": w_no,
                "lok_disp": clean_locality_display(lok),
                "w_no": format_wabak_no(w_no),
                "st_w": st_w,
                "tier": tier,
                "tier_cls": tier_cls,
                "tier_icon": tier_icon,
                "badge_bg": badge_bg,
                "badge_fg": badge_fg,
                "tier_reason": tier_reason,
                "kes": kes,
                "tempoh": tempoh,
                "c_7d": c_7d,
                "c_prev7d": c_prev7d,
                "mom_str": mom_str,
                "p_vel": p_vel,
                "p_c7": p_c7,
                "p_dur": p_dur,
                "p_bon": p_bon,
                "rate_daily": rate_daily,
                "proj_14d": proj_14d,
                "ci_l": ci_l,
                "ci_u": ci_u,
                "t_mula_str": fmt_date_short(t_mula),
            }
        )

    risk_items.sort(key=lambda x: (x["score"], x["vel"]), reverse=True)

    for idx_rk, it in enumerate(risk_items):
        clickable_items.append((it["lok_raw"], it["w_no_raw"]))
        lok_esc = html.escape(it["lok_disp"])
        bubble_html = (
            f'<div class="ai-tooltip-bubble">'
            f'<div class="tooltip-title">{it["tier_icon"]} #{idx_rk + 1} {lok_esc} — {it["tier"]} ({it["score"]}/100)</div>'
            f'<div class="tooltip-section"><b>Mengapa Tahap {it["tier"]}?</b><br>{it["tier_reason"]}</div>'
            f'<div class="tooltip-section"><b>Pecahan Kiraan Skor Risiko (0–100):</b>'
            f'<div class="tooltip-formula">'
            f'• Halaju / Velocity ({it["vel"]:.2f} kes/hari): <b>{it["p_vel"]:.1f} / 35</b><br>'
            f'• Lonjakan 7 Hari Terkini ({it["c_7d"]} kes): <b>{it["p_c7"]:.1f} / 30</b><br>'
            f'• Tempoh Wabak ({it["tempoh"]} hari): <b>{it["p_dur"]:.1f} / 20</b><br>'
            f'• Bonus Status KKM ({html.escape(it["st_w"])}): <b>+{it["p_bon"]} / 15</b><br>'
            f'<b>Jumlah Skor = {it["score"]} / 100 ({it["tier"]})</b>'
            f'</div></div>'
            f'<div class="tooltip-current">'
            f'<b>📈 Unjuran Poisson (+14 Hari) & Statistik Lokaliti:</b><br>'
            f'• <b>Unjuran Kes Baharu (+14h):</b> <b>{it["proj_14d"]:.1f} kes</b> (95% CI: <b>{it["ci_l"]:.1f} – {it["ci_u"]:.1f} kes</b>)<br>'
            f'• <b>Kadar Harian (λ):</b> {it["rate_daily"]:.2f} kes/hari | <b>Momentum 7H:</b> {it["mom_str"]} ({it["c_7d"]} vs {it["c_prev7d"]})<br>'
            f'• <b>Rekod Episod #{it["w_no"]}:</b> {it["kes"]} kes terkumpul sejak {it["t_mula_str"]} ({it["tempoh"]} hari)<br>'
            f'<div style="margin-top:6px;color:#7dd3fc;font-weight:700;">👆 Klik kad ini untuk membuka Analisis Lokaliti penuh →</div>'
            f'</div>'
            f'</div>'
        )
        cards_html.append(
            f'<div class="ai-hover-card risk-exec-card {it["tier_cls"]}" data-rk-idx="{idx_rk}" title="Klik untuk membuka Analisis Lokaliti bagi {lok_esc}">'
            f'<span class="risk-card-shine"></span>'
            f'<div class="risk-card-top">'
            f'<span class="risk-card-rank">#{idx_rk + 1}</span>'
            f'<span class="risk-card-badge" style="background:{it["badge_bg"]};color:{it["badge_fg"]};">{it["tier"]}</span>'
            f'<span class="risk-card-score">{it["score"]}<small>/100</small></span>'
            f'</div>'
            f'<div class="risk-card-lok">{lok_esc}</div>'
            f'<div class="risk-card-meta">'
            f'<span><b>{it["kes"]}</b> kes • <b>{it["vel"]:.2f}</b>/h</span>'
            f'<span class="risk-card-proj">+14h: <b>{it["proj_14d"]:.1f}</b> ↗</span>'
            f'</div>'
            f'{bubble_html}'
            f'</div>'
        )

    n_k = sum(1 for x in risk_items if x["tier"] == "KRITIKAL")
    n_t = sum(1 for x in risk_items if x["tier"] == "TINGGI")
    n_s = sum(1 for x in risk_items if x["tier"] == "SEDERHANA")

    radar_html = (
        '<div class="risk-radar-strip">'
        '<div class="risk-radar-header">'
        '<div class="risk-radar-title-group">'
        '<span class="risk-radar-eyebrow">LIVE TRIAGE</span>'
        '<span class="risk-radar-title">Radar Tahap Risiko Eskalasi Wabak Aktif</span>'
        '<span class="risk-radar-sub">(Arah kursor untuk audit skor • Klik kad untuk buka lokaliti)</span>'
        '</div>'
        '<div class="risk-radar-counts">'
        f'<span class="rc-chip rc-krit">● {n_k} Kritikal</span>'
        f'<span class="rc-chip rc-tinggi">● {n_t} Tinggi</span>'
        f'<span class="rc-chip rc-sed">● {n_s} Sederhana</span>'
        '</div>'
        '</div>'
        f'<div class="risk-radar-grid">{"".join(cards_html)}</div>'
        '</div>'
    )
    return radar_html, clickable_items


def render_status_wabak_html(df_tamat, df_aktif):
    """Membina paparan jadual HTML STATUS WABAK (DENGGI) berkejelasan tinggi dengan lokaliti boleh klik."""
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
            lok_disp = str(r["LOKALITI"])
            lok_raw = str(r.get("_lok_raw", lok_disp))
            s_bg, s_fg = get_status_style(st_val)
            fw = "700" if (s_fg == "#ffffff" or "BARU" in st_val) else "600"
            k_bg = get_kaw_bg(kaw_val)
            p_bg = get_parl_bg(parl_val)

            clickable_rows.append((lok_raw, r["Wabak No"]))
            cur_idx = row_idx
            row_idx += 1

            html_parts.append(
                f"<tr>"
                f'<td style="background-color:{s_bg}; color:{s_fg}; font-weight:{fw}; text-align:right;">{int(r["BIL"])}</td>'
                f'<td style="background-color:{s_bg}; color:{s_fg}; font-weight:{fw}; text-align:left;">{html.escape(st_val)}</td>'
                f'<td style="background-color:{k_bg}; color:#000000; text-align:center;">{html.escape(kaw_val)}</td>'
                f'<td style="background-color:{p_bg}; color:#000000; text-align:center;">{html.escape(parl_val)}</td>'
                f'<td class="sw-lok-link" data-sw-idx="{cur_idx}" title="Klik untuk membuka Analisis Lokaliti bagi {html.escape(lok_disp)}">{html.escape(lok_disp)}</td>'
                f'<td style="background-color:#ffffff; color:#000000; text-align:right;">{int(r["JUMLAH KES"])}</td>'
                f'<td style="background-color:#ffffff; color:#000000; text-align:right;">{int(r["BIL EPISOD"])}</td>'
                f'<td style="background-color:#ffffff; color:#000000; text-align:right;">{int(r["TEMPOH WABAK"])}</td>'
                f'<td style="background-color:#ffffff; color:#000000; text-align:right;">{html.escape(str(r["TARIKH MULA"]))}</td>'
                f'<td style="background-color:#ffffff; color:#000000; text-align:right;">{html.escape(str(r["TARIKH TAMAT"]))}</td>'
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
                s_color, s_fg = get_status_style(st_val)
                s_font = (
                    f_cell_bold
                    if (s_fg == "#ffffff" or "BARU" in st_val)
                    else f_cell
                )

                row_specs = [
                    (str(int(r["BIL"])), s_color, s_fg, "right", s_font),
                    (st_val, s_color, s_fg, "left", s_font),
                    (kaw_val, get_kaw_bg(kaw_val), "#000000", "center", f_cell),
                    (parl_val, get_parl_bg(parl_val), "#000000", "center", f_cell),
                    (str(r["LOKALITI"]), "#ffffff", "#000000", "left", f_cell),
                    (str(int(r["JUMLAH KES"])), "#ffffff", "#000000", "right", f_cell),
                    (str(int(r["BIL EPISOD"])), "#ffffff", "#000000", "right", f_cell),
                    (str(int(r["TEMPOH WABAK"])), "#ffffff", "#000000", "right", f_cell),
                    (str(r["TARIKH MULA"]), "#ffffff", "#000000", "right", f_cell),
                    (str(r["TARIKH TAMAT"]), "#ffffff", "#000000", "right", f_cell),
                ]

                for cw, (txt, bg, fg, align, fnt) in zip(col_widths, row_specs):
                    draw.rectangle(
                        [cx, y, cx + cw, y + h_row],
                        fill=bg,
                        outline=border_col,
                        width=lw,
                    )
                    box = (cx, y, cx + cw, y + h_row)
                    if align == "center":
                        draw_centered_text(box, [txt], fnt, fg)
                    elif align == "right":
                        draw_right_text(box, txt, fnt, fg)
                    else:
                        draw_left_text(box, txt, fnt, fg)
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

    for col in [
        "Jenis Kes",
        "Wabak Status",
        "Lokaliti (Alamat Semasa)",
        "Pihak Pentadbir Lokaliti",
        "Kemudahan Kesihatan(Maklumat Pemberitahu)",
        "Jenis Kemudahan Kesihatan(Maklumat Pemberitahu)",
    ]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r"\s+", " ", regex=True)
                .str.strip()
                .replace({"nan": pd.NA, "None": pd.NA, "": pd.NA})
            )

    date_cols = [
        "Tarikh Daftar",
        "Tarikh Onset",
        "Tkh Notifikasi",
        "Tkh Input Notifikasi",
        "Tarikh Diagnosis",
        "Tarikh Siasatan Kes",
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
# ENJIN AI EPIDEMIOLOGI, PENCAPAIAN KPI POA & AUDIT PESALAH NOTIFIKASI LEWAT
# =========================================================
def classify_facility_sector(jenis_val, fac_name):
    """Mengelaskan fasiliti pemberitahu kepada sektor AWAM atau SWASTA mengikut piawaian POA DNTI."""
    j = str(jenis_val).upper()
    f = str(fac_name).upper()
    if "SWASTA" in j or "PRIVATE" in j:
        return "SWASTA"
    if any(
        k in j
        for k in [
            "KERAJAAN",
            "KESIHATAN",
            "AWAM",
            "UNIVERSITI",
            "DBKL",
            "POLIKLINIK KERAJAAN",
        ]
    ) or any(
        k in f
        for k in [
            "HOSPITAL AMPANG",
            "CANSELOR",
            "HUKM",
            "HCTM",
            "KLINIK KESIHATAN",
            "PKD",
            "HOSPITAL KUALA LUMPUR",
            "HOSPITAL SETIU",
            "DBKL",
        ]
    ):
        return "AWAM"
    return (
        "SWASTA"
        if ("KLINIK" in f or "MEDICAL" in f or "HOSPITAL" in f)
        else "LAIN-LAIN"
    )


def compute_late_notification_offenders(df_period, df_all_history):
    """Mengenal pasti fasiliti notifikasi lewat (>24 jam dari Tarikh Diagnosis) serta status pesalah berulang (POA A1)."""
    empty_meta = {
        "total_late": 0,
        "total_facilities": 0,
        "n_repeated_period": 0,
        "n_repeated_hist": 0,
        "n_public": 0,
        "n_private": 0,
    }
    if (
        df_period is None
        or df_period.empty
        or "Tkh Notifikasi" not in df_period.columns
        or "Tarikh Diagnosis" not in df_period.columns
    ):
        return pd.DataFrame(), pd.DataFrame(), empty_meta

    fac_col = "Kemudahan Kesihatan(Maklumat Pemberitahu)"
    jenis_col = "Jenis Kemudahan Kesihatan(Maklumat Pemberitahu)"

    hist_late_map = {}
    if (
        df_all_history is not None
        and not df_all_history.empty
        and "Tkh Notifikasi" in df_all_history.columns
        and "Tarikh Diagnosis" in df_all_history.columns
        and fac_col in df_all_history.columns
    ):
        d_hist = (
            df_all_history["Tkh Notifikasi"] - df_all_history["Tarikh Diagnosis"]
        ).dt.days
        df_h_late = df_all_history[d_hist.notna() & (d_hist > 1)].copy()
        if not df_h_late.empty:
            hist_late_map = (
                df_h_late[fac_col]
                .fillna("TIDAK DINYATAKAN")
                .astype(str)
                .str.strip()
                .value_counts()
                .to_dict()
            )

    df_p = df_period.copy()
    df_p["_delay_days"] = (df_p["Tkh Notifikasi"] - df_p["Tarikh Diagnosis"]).dt.days
    df_late = df_p[df_p["_delay_days"].notna() & (df_p["_delay_days"] > 1)].copy()
    if df_late.empty:
        return pd.DataFrame(), pd.DataFrame(), empty_meta

    df_late["_Fasiliti"] = (
        df_late[fac_col].fillna("TIDAK DINYATAKAN").astype(str).str.strip()
        if fac_col in df_late.columns
        else "TIDAK DINYATAKAN"
    )
    df_late["_Jenis"] = (
        df_late[jenis_col].fillna("-").astype(str).str.strip()
        if jenis_col in df_late.columns
        else "-"
    )
    df_late["_Sektor"] = [
        classify_facility_sector(j, f)
        for j, f in zip(df_late["_Jenis"], df_late["_Fasiliti"])
    ]

    summary_rows = []
    for (fac, sektor), grp in df_late.groupby(["_Fasiliti", "_Sektor"]):
        cnt_period = int(len(grp))
        cnt_hist = int(hist_late_map.get(fac, cnt_period))
        max_d = int(grp["_delay_days"].max())
        last_dt = grp["Tkh Notifikasi"].max()

        if cnt_period >= 2:
            status_off = "PESALAH BERULANG"
            cadangan = "Surat Teguran & Emel Rasmi"
            rank = 0
        elif cnt_hist >= 2:
            status_off = "BERULANG (SEJARAH)"
            cadangan = "Surat Peringatan & Pemantauan"
            rank = 1
        else:
            status_off = "KESALAHAN PERTAMA"
            cadangan = "Makluman Pematuhan DNTI"
            rank = 2

        summary_rows.append(
            {
                "Fasiliti Pemberitahu": fac,
                "Sektor": sektor,
                "Bil. Lewat": cnt_period,
                "Sejarah (5 Thn)": cnt_hist,
                "Maks (Hari)": max_d,
                "Tkh Terakhir": fmt_date_short(last_dt),
                "Status Pesalah": status_off,
                "Cadangan Tindakan": cadangan,
                "_rank": rank,
            }
        )

    df_off_sum = (
        pd.DataFrame(summary_rows)
        .sort_values(
            by=["_rank", "Bil. Lewat", "Sejarah (5 Thn)", "Maks (Hari)"],
            ascending=[True, False, False, False],
        )
        .drop(columns=["_rank"])
        .reset_index(drop=True)
    )

    df_detail = df_late.sort_values(
        by=["_delay_days", "Tkh Notifikasi"], ascending=[False, False]
    ).copy()
    df_detail_out = pd.DataFrame(
        {
            "Bil": range(1, len(df_detail) + 1),
            "Fasiliti Pemberitahu": df_detail["_Fasiliti"].values,
            "Sektor": df_detail["_Sektor"].values,
            "No. Notifikasi": df_detail["Notifikasi No"].astype(str).values
            if "Notifikasi No" in df_detail.columns
            else "-",
            "Tkh Diagnosis": df_detail["Tarikh Diagnosis"].dt.strftime("%d/%m/%Y").values,
            "Tkh Notifikasi": df_detail["Tkh Notifikasi"].dt.strftime("%d/%m/%Y").values,
            "Lengah (Hari)": df_detail["_delay_days"].astype(int).values,
            "Lokaliti": df_detail["Lokaliti (Alamat Semasa)"]
            .fillna("-")
            .astype(str)
            .apply(clean_locality_display)
            .values
            if "Lokaliti (Alamat Semasa)" in df_detail.columns
            else "-",
        }
    )

    meta_off = {
        "total_late": int(len(df_late)),
        "total_facilities": int(len(df_off_sum)),
        "n_repeated_period": int(
            (df_off_sum["Status Pesalah"] == "PESALAH BERULANG").sum()
        ),
        "n_repeated_hist": int(
            (df_off_sum["Status Pesalah"] == "BERULANG (SEJARAH)").sum()
        ),
        "n_public": int((df_late["_Sektor"] == "AWAM").sum()),
        "n_private": int((df_late["_Sektor"] == "SWASTA").sum()),
    }
    return df_off_sum, df_detail_out, meta_off


def compute_poa_kpi_summary(df_sub):
    """Mengira pencapaian KPI POA Denggi sebenar (Indikator 1/A1, Indikator 4/A2, Indikator 9/C1 & Indikator 10/C1)."""
    if df_sub is None or df_sub.empty:
        return pd.DataFrame(), {
            "sporadik_total": 0,
            "sporadik_kkm": 0,
            "target_premises_med": 0,
            "daftar_24j_pct": 0.0,
            "daftar_24j_num": 0,
            "daftar_24j_den": 0,
            "daftar_24j_gap": 0,
        }

    # Indikator 1 (A1): Notifikasi denggi oleh fasiliti kesihatan dalam tempoh 24 jam (DNTI) — Sasaran 100%
    if "Tkh Notifikasi" in df_sub.columns and "Tarikh Diagnosis" in df_sub.columns:
        d1 = (df_sub["Tkh Notifikasi"] - df_sub["Tarikh Diagnosis"]).dt.days
        v1 = d1.notna()
        num1 = int((d1[v1] <= 1).sum())
        den1 = int(v1.sum())
    elif "Tkh Input Notifikasi" in df_sub.columns and "Tkh Notifikasi" in df_sub.columns:
        d1 = (df_sub["Tkh Input Notifikasi"] - df_sub["Tkh Notifikasi"]).dt.days
        v1 = d1.notna()
        num1 = int((d1[v1] <= 1).sum())
        den1 = int(v1.sum())
    else:
        num1, den1 = len(df_sub), len(df_sub)
    pct1 = round((num1 / max(den1, 1)) * 100, 1)
    gap1 = num1 - int(np.ceil(1.00 * den1))

    # Indikator 4 (A2): Siasatan dan pendaftaran kes dalam tempoh 24 jam daripada tarikh notifikasi — Sasaran 85%
    if "Tkh Input Notifikasi" in df_sub.columns:
        ref_notif = df_sub["Tkh Input Notifikasi"].fillna(df_sub["Tkh Notifikasi"])
    else:
        ref_notif = df_sub["Tkh Notifikasi"]
    d4 = (df_sub["Tarikh Daftar"] - ref_notif).dt.days
    v4 = d4.notna()
    num4 = int((d4[v4] <= 1).sum())
    den4 = int(v4.sum())
    pct4 = round((num4 / max(den4, 1)) * 100, 1)
    gap4 = num4 - int(np.ceil(0.85 * den4))

    # Kes Sporadik ('Satu Kes') untuk Indikator 9 & 10 (Strategi C1)
    spor = df_sub[df_sub["Jenis Kes"] == "Satu Kes"].copy()
    spor_kkm = spor[
        spor["Pihak Pentadbir Lokaliti"]
        .astype(str)
        .str.contains("PKD|KKM", case=False, na=False)
    ].copy()

    # Indikator 9(i) & 9(ii) (C1): PTP <= 24 jam daripada Tarikh Daftar untuk kes sporadik (Sasaran: 70% Semua, 80% KKM)
    den9_all = len(spor)
    d9_all = (
        (spor["Tkh PTP Aktiviti Pertama"] - spor["Tarikh Daftar"]).dt.days
        if "Tkh PTP Aktiviti Pertama" in spor.columns
        else pd.Series(dtype=float)
    )
    num9_all = int((d9_all.notna() & (d9_all <= 1)).sum()) if den9_all > 0 else 0
    pct9_all = round((num9_all / max(den9_all, 1)) * 100, 1) if den9_all > 0 else 0.0
    gap9_all = num9_all - int(np.ceil(0.70 * den9_all))

    den9_kkm = len(spor_kkm)
    d9_kkm = (
        (spor_kkm["Tkh PTP Aktiviti Pertama"] - spor_kkm["Tarikh Daftar"]).dt.days
        if "Tkh PTP Aktiviti Pertama" in spor_kkm.columns
        else pd.Series(dtype=float)
    )
    num9_kkm = int((d9_kkm.notna() & (d9_kkm <= 1)).sum()) if den9_kkm > 0 else 0
    pct9_kkm = round((num9_kkm / max(den9_kkm, 1)) * 100, 1) if den9_kkm > 0 else 0.0
    gap9_kkm = num9_kkm - int(np.ceil(0.80 * den9_kkm))

    # Indikator 10(i) & 10(ii) (C1): SRT <= 24 jam daripada Tarikh Daftar untuk kes sporadik (Sasaran: 60% Semua, 80% KKM)
    den10_all = len(spor)
    d10_all = (
        (spor["Tkh SRT Aktiviti Pertama"] - spor["Tarikh Daftar"]).dt.days
        if "Tkh SRT Aktiviti Pertama" in spor.columns
        else pd.Series(dtype=float)
    )
    num10_all = int((d10_all.notna() & (d10_all <= 1)).sum()) if den10_all > 0 else 0
    pct10_all = round((num10_all / max(den10_all, 1)) * 100, 1) if den10_all > 0 else 0.0
    gap10_all = num10_all - int(np.ceil(0.60 * den10_all))

    den10_kkm = len(spor_kkm)
    d10_kkm = (
        (spor_kkm["Tkh SRT Aktiviti Pertama"] - spor_kkm["Tarikh Daftar"]).dt.days
        if "Tkh SRT Aktiviti Pertama" in spor_kkm.columns
        else pd.Series(dtype=float)
    )
    num10_kkm = int((d10_kkm.notna() & (d10_kkm <= 1)).sum()) if den10_kkm > 0 else 0
    pct10_kkm = round((num10_kkm / max(den10_kkm, 1)) * 100, 1) if den10_kkm > 0 else 0.0
    gap10_kkm = num10_kkm - int(np.ceil(0.80 * den10_kkm))

    target_prem_med = 0
    if "Rumah/Kedai" in spor.columns and spor["Rumah/Kedai"].notna().any():
        target_prem_med = int(
            round(float(pd.to_numeric(spor["Rumah/Kedai"], errors="coerce").median()))
        )

    poa_rows = [
        {
            "Kod": "Ind 1 (A1)",
            "Indikator POA": "Notifikasi Fasiliti ≤ 24 Jam (DNTI)",
            "Pencapaian (%)": pct1,
            "Sasaran (%)": 100.0,
            "Bilangan": f"{num1:,}/{den1:,}",
            "Varians": f"{gap1:+d}",
            "Status POA": "TERCAPAI" if pct1 >= 100.0 else "TIDAK TERCAPAI",
        },
        {
            "Kod": "Ind 4 (A2)",
            "Indikator POA": "Siasatan & Daftar Kes ≤ 24 Jam",
            "Pencapaian (%)": pct4,
            "Sasaran (%)": 85.0,
            "Bilangan": f"{num4:,}/{den4:,}",
            "Varians": f"{gap4:+d}",
            "Status POA": "TERCAPAI" if pct4 >= 85.0 else "TIDAK TERCAPAI",
        },
        {
            "Kod": "Ind 9(i) (C1)",
            "Indikator POA": "PTP ≤ 24 Jam (Sporadik - Semua)",
            "Pencapaian (%)": pct9_all,
            "Sasaran (%)": 70.0,
            "Bilangan": f"{num9_all:,}/{den9_all:,}",
            "Varians": f"{gap9_all:+d}",
            "Status POA": "TERCAPAI" if pct9_all >= 70.0 else "TIDAK TERCAPAI",
        },
        {
            "Kod": "Ind 9(ii) (C1)",
            "Indikator POA": "PTP ≤ 24 Jam (Sporadik - KKM)",
            "Pencapaian (%)": pct9_kkm,
            "Sasaran (%)": 80.0,
            "Bilangan": f"{num9_kkm:,}/{den9_kkm:,}",
            "Varians": f"{gap9_kkm:+d}",
            "Status POA": "TERCAPAI" if pct9_kkm >= 80.0 else "TIDAK TERCAPAI",
        },
        {
            "Kod": "Ind 10(i) (C1)",
            "Indikator POA": "SRT ≤ 24 Jam (Sporadik - Semua)",
            "Pencapaian (%)": pct10_all,
            "Sasaran (%)": 60.0,
            "Bilangan": f"{num10_all:,}/{den10_all:,}",
            "Varians": f"{gap10_all:+d}",
            "Status POA": "TERCAPAI" if pct10_all >= 60.0 else "TIDAK TERCAPAI",
        },
        {
            "Kod": "Ind 10(ii) (C1)",
            "Indikator POA": "SRT ≤ 24 Jam (Sporadik - KKM)",
            "Pencapaian (%)": pct10_kkm,
            "Sasaran (%)": 80.0,
            "Bilangan": f"{num10_kkm:,}/{den10_kkm:,}",
            "Varians": f"{gap10_kkm:+d}",
            "Status POA": "TERCAPAI" if pct10_kkm >= 80.0 else "TIDAK TERCAPAI",
        },
    ]
    meta = {
        "sporadik_total": den9_all,
        "sporadik_kkm": den9_kkm,
        "target_premises_med": target_prem_med,
        "daftar_24j_pct": pct4,
        "daftar_24j_num": num4,
        "daftar_24j_den": den4,
        "daftar_24j_gap": gap4,
    }
    return pd.DataFrame(poa_rows), meta


def compute_ai_epidemiological_analytics(
    df, df_lok, pilihan_lokaliti, today_my, poa_period_code="ALL"
):
    """Mengira ramalan 4 minggu (95% CI), pencapaian KPI POA, audit pesalah notifikasi lewat, matriks risiko & korelasi."""
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

    forecast_rows = []
    slope_per_week = 0.0
    s_err = 0.0
    r_squared = 0.0
    n_fit_weeks = 0
    if len(weekly_df) >= 4:
        recent = weekly_df.tail(min(12, len(weekly_df))).copy()
        n_fit_weeks = len(recent)
        x = np.arange(n_fit_weeks, dtype=float)
        y = recent["Kes"].values.astype(float)
        slope_per_week, intercept = np.polyfit(x, y, 1)
        y_hat = intercept + slope_per_week * x
        resid = y - y_hat
        dof = max(n_fit_weeks - 2, 1)
        s_err = float(np.sqrt(np.sum(resid**2) / dof))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r_squared = float(1.0 - np.sum(resid**2) / ss_tot) if ss_tot > 1e-6 else 0.0
        x_mean = float(np.mean(x))
        sxx = float(np.sum((x - x_mean) ** 2))
        t_crit = 2.228 if dof >= 10 else (2.306 if dof >= 8 else 2.776)

        last_yr = int(recent["_yr"].iloc[-1])
        last_me = int(recent["_me"].iloc[-1])

        for step in range(1, 5):
            xf = float(n_fit_weeks - 1 + step)
            yf = max(0.0, float(intercept + slope_per_week * xf))
            se_pred = s_err * np.sqrt(
                1.0 + 1.0 / n_fit_weeks + ((xf - x_mean) ** 2) / max(sxx, 1e-6)
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

    # Tapis data tahun semasa mengikut tempoh POA dipilih (Keseluruhan / Q1 / Q2 / Q3 / Q4 / Q1-Q3)
    target_yr = (
        int(df_calc["_yr"].dropna().max())
        if df_calc["_yr"].notna().any()
        else today_my.year
    )
    df_poa_base = df_calc[df_calc["_yr"] == target_yr].copy()
    if poa_period_code == "Q1":
        df_poa_base = df_poa_base[df_poa_base["_me"].between(1, 13)]
    elif poa_period_code == "Q2":
        df_poa_base = df_poa_base[df_poa_base["_me"].between(14, 26)]
    elif poa_period_code == "Q3":
        df_poa_base = df_poa_base[df_poa_base["_me"].between(27, 39)]
    elif poa_period_code == "Q4":
        df_poa_base = df_poa_base[df_poa_base["_me"].between(40, 53)]
    elif poa_period_code == "Q1_Q3":
        df_poa_base = df_poa_base[df_poa_base["_me"].between(1, 39)]

    df_poa_kpis, poa_meta = compute_poa_kpi_summary(df_poa_base)
    df_offenders_sum, df_offenders_det, offenders_meta = (
        compute_late_notification_offenders(df_poa_base, df_calc)
    )

    # Analisis Korelasi Status Wabak vs Saiz Kes, Kepantasan Daftar 24j (POA A2) & Lengah Epidemiologi (Onset)
    status_comp_rows = []
    pearson_rows = []
    df_w_all = df_calc[df_calc["Jenis Kes"] == "Wabak"].dropna(subset=["Wabak No"]).copy()
    if not df_w_all.empty:
        if "Tarikh Onset" in df_w_all.columns and "Tkh Notifikasi" in df_w_all.columns:
            df_w_all["_onset_lag"] = (
                df_w_all["Tkh Notifikasi"] - df_w_all["Tarikh Onset"]
            ).dt.days
        else:
            df_w_all["_onset_lag"] = np.nan

        ref_n_w = (
            df_w_all["Tkh Input Notifikasi"].fillna(df_w_all["Tkh Notifikasi"])
            if "Tkh Input Notifikasi" in df_w_all.columns
            else df_w_all["Tkh Notifikasi"]
        )
        df_w_all["_daftar_24j"] = (
            (df_w_all["Tarikh Daftar"] - ref_n_w).dt.days <= 1
        ).astype(float) * 100.0

        for st_name, grp in df_w_all.groupby("Wabak Status"):
            o_valid = grp["_onset_lag"][
                (grp["_onset_lag"] >= 0) & (grp["_onset_lag"] <= 45)
            ].dropna()
            status_comp_rows.append(
                {
                    "Status Wabak": str(st_name),
                    "Bil. Episod": int(grp["Wabak No"].nunique()),
                    "Purata Kes / Episod": round(
                        len(grp) / max(grp["Wabak No"].nunique(), 1), 1
                    ),
                    "Kadar Daftar ≤24j (%)": round(float(grp["_daftar_24j"].mean()), 1),
                    "Lengah Onset→Notif (Hari)": round(float(o_valid.mean()), 1)
                    if not o_valid.empty
                    else None,
                }
            )

        w_ep_stats = df_w_all.groupby("Wabak No").agg(
            kes=("Notifikasi No", "count"),
            daftar_pct=("_daftar_24j", "mean"),
            onset_l=("_onset_lag", lambda s: s[(s >= 0) & (s <= 45)].mean()),
            t_min=("Tarikh Daftar", "min"),
            t_max=("Tarikh Daftar", "max"),
        )
        w_ep_stats["tempoh_h"] = (w_ep_stats["t_max"] - w_ep_stats["t_min"]).dt.days.clip(lower=1)

        for p_label, p_col in [
            ("Saiz Wabak vs Tempoh Wabak (Hari)", "tempoh_h"),
            ("Saiz Wabak vs Kadar Daftar ≤24j (POA A2)", "daftar_pct"),
            ("Saiz Wabak vs Lengah Onset→Notif (Epidemiologi)", "onset_l"),
        ]:
            sub_p = w_ep_stats[["kes", p_col]].dropna()
            if len(sub_p) >= 3 and sub_p[p_col].std() > 0:
                r_val = float(sub_p["kes"].corr(sub_p[p_col]))
                strength = (
                    "Kuat"
                    if abs(r_val) >= 0.5
                    else ("Sederhana" if abs(r_val) >= 0.25 else "Lemah")
                )
                pearson_rows.append(
                    {
                        "Pasangan Pembolehubah": p_label,
                        "Pekali Korelasi (r)": round(r_val, 3),
                        "Kekuatan Hubungan": strength,
                        "Bil. Episod (n)": int(len(sub_p)),
                    }
                )

    df_status_corr = pd.DataFrame(status_comp_rows)
    df_pearson = pd.DataFrame(pearson_rows)

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
                    "Lokaliti": clean_locality_display(lok),
                    "Status Semasa": st_w,
                    "Jumlah Kes": kes,
                    "Tempoh (Hari)": tempoh,
                    "Velocity (Kes/Hari)": round(vel, 2),
                    "Kes 7 Hari Terkini": c_7d,
                    "Kes 7-14 Hari Lalu": c_prev7d,
                    "Unjuran +14 Hari": round(proj_14d, 1),
                    "CI Bawah": round(ci_l, 1),
                    "CI Atas": round(ci_u, 1),
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

    lok_summary = {}
    if df_lok is not None and not df_lok.empty and pilihan_lokaliti:
        df_l = df_lok.copy()
        df_l[["_Blok", "_Tingkat"]] = df_l["No Rumah"].apply(parse_address)
        valid_bt = df_l[
            (df_l["_Blok"] != "TIDAK PASTI") & (df_l["_Tingkat"] != "TIDAK PASTI")
        ]
        top_cluster = "Tiada kluster bertingkat dikenal pasti"
        if not valid_bt.empty:
            grp_bt = (
                valid_bt.groupby(["_Blok", "_Tingkat"])
                .size()
                .sort_values(ascending=False)
            )
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
            round(
                float(pd.to_numeric(df_l["Umur (Tahun)"], errors="coerce").median()), 1
            )
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
        "s_err": s_err,
        "r_squared": r_squared,
        "n_fit_weeks": n_fit_weeks,
        "df_poa_kpis": df_poa_kpis,
        "poa_meta": poa_meta,
        "df_offenders_sum": df_offenders_sum,
        "df_offenders_det": df_offenders_det,
        "offenders_meta": offenders_meta,
        "target_yr": target_yr,
        "df_status_corr": df_status_corr,
        "df_pearson": df_pearson,
        "df_active_risk": df_active_risk,
        "lok_summary": lok_summary,
    }


def call_gemini_thinking_free_tier(key_clean, system_prompt, user_prompt):
    """Memanggil model Gemini Free Tier terkini secara automatik."""
    models_to_try = [
        ("gemini-3.8-flash", True, "Gemini 3.8"),
        ("gemini-3.6-flash", True, "Gemini 3.6"),
        ("gemini-3.5-flash-lite", False, "Gemini 3.5"),
        ("gemini-2.5-flash", True, "Gemini 2.5"),
    ]
    last_http_code = None
    for model_id, use_thinking, label in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={key_clean}"
            gen_cfg = {"temperature": 0.0}
            if use_thinking:
                gen_cfg["thinkingConfig"] = {"thinkingBudget": 1024}
            payload = {
                "systemInstruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                "generationConfig": gen_cfg,
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
                return text_out, label, None
        except urllib.error.HTTPError as he:
            last_http_code = he.code
            if he.code == 429:
                return "", None, 429
            continue
        except Exception:
            continue
    return "", None, last_http_code


def render_ai_qa_visuals_and_response(question, analytics, today_my, embedded_api_key):
    """Memaparkan jadual kemas, visualisasi grafikal interaktif (dengan kesimpulan data & jalur info) serta jawapan AI."""
    q_lower = question.lower().strip()
    df_forecast = analytics["df_forecast"]
    df_poa_kpis = analytics["df_poa_kpis"]
    poa_meta = analytics["poa_meta"]
    df_offenders_sum = analytics.get("df_offenders_sum", pd.DataFrame())
    df_status_corr = analytics["df_status_corr"]
    df_pearson = analytics["df_pearson"]
    df_active_risk = analytics["df_active_risk"]
    lok_sum = analytics["lok_summary"]
    slope = analytics["slope_per_week"]
    s_err = analytics["s_err"]
    r_sq = analytics["r_squared"]
    n_fit = analytics["n_fit_weeks"]

    is_forecast_q = any(
        k in q_lower
        for k in ["ramal", "predict", "forecast", "ci", "trend", "minggu", "unjuran"]
    )
    is_poa_or_corr_q = any(
        k in q_lower
        for k in [
            "poa",
            "kpi",
            "daftar",
            "24",
            "sporadik",
            "ptp",
            "srt",
            "korelasi",
            "correlation",
            "punca",
            "sebab",
            "lewat",
            "pesalah",
            "offender",
            "dnti",
            "fasiliti",
        ]
    )

    c_qa1, c_qa2 = st.columns([1.15, 1.0])

    # MODE 1: RAMALAN 4 MINGGU & 95% CI
    if is_forecast_q:
        with c_qa1:
            fc_table_html = df_to_styled_html_table(df_forecast)
            if not df_forecast.empty:
                tot_fc = round(float(df_forecast["Unjuran Kes"].sum()), 1)
                tot_lo = round(float(df_forecast["95% CI Bawah"].sum()), 1)
                tot_hi = round(float(df_forecast["95% CI Atas"].sum()), 1)
                first_fc = df_forecast.iloc[0]
                last_fc = df_forecast.iloc[-1]
                top_fc_txt = (
                    f"Minggu <b>{first_fc['Minggu']}</b>: <b>{first_fc['Unjuran Kes']} kes</b> "
                    f"(95% CI: {first_fc['95% CI Bawah']} – {first_fc['95% CI Atas']})"
                )
                fc_tbl_conc = (
                    f"<b>📌 Kesimpulan Jadual Unjuran:</b> Dalam tempoh 4 minggu hadapan "
                    f"(<b>{html.escape(str(first_fc['Minggu']))}</b> hingga <b>{html.escape(str(last_fc['Minggu']))}</b>), "
                    f"jumlah keseluruhan kes diunjurkan sebanyak <b>{tot_fc} kes</b> "
                    f"(julat kumulatif 95% CI: <b>{tot_lo} – {tot_hi} kes</b>), bergerak daripada "
                    f"<b>{first_fc['Unjuran Kes']} kes</b> kepada <b>{last_fc['Unjuran Kes']} kes</b>."
                )
            else:
                top_fc_txt = "Tiada unjuran"
                fc_tbl_conc = "<b>📌 Kesimpulan Jadual Unjuran:</b> Data mingguan tidak mencukupi untuk menjana jadual ramalan."

            card_fc_qa = build_ai_hover_card_html(
                zone_id="ai_qa_left",
                card_title="📅 Jadual Unjuran Kes 4 Minggu Hadapan (95% CI)",
                body_html=fc_table_html,
                tooltip_title="📈 Unjuran Trend Mingguan & 95% CI",
                relevance_html="Menganggarkan beban kes denggi mingguan untuk 4 minggu epid akan datang berserta batas atas dan bawah pada tahap keyakinan 95% bagi perancangan sumber manusia dan logistik.",
                formula_html="ŷ<sub>t+k</sub> = a + b(x<sub>n</sub> + k)  |  95% CI = ŷ ± t<sub>α/2</sub> · s<sub>e</sub>√(1 + 1/n + (x−x̄)²/S<sub>xx</sub>)",
                current_calc_html=(
                    f"<b>Pengiraan Semasa ({n_fit} minggu terakhir):</b><br>"
                    f"Kecerunan (b) = <b>{slope:+.2f} kes/minggu</b> | Ralat Piawai (s<sub>e</sub>) = <b>{s_err:.2f}</b> | R² = <b>{r_sq:.3f}</b><br>"
                    f"Seterusnya → {top_fc_txt}"
                ),
                conclusion_html=fc_tbl_conc,
            )
            st.markdown(card_fc_qa, unsafe_allow_html=True)

        with c_qa2:
            if not df_active_risk.empty:
                top_proj = df_active_risk.head(8).copy()
                top1 = top_proj.iloc[0]
                st.markdown(
                    build_graph_info_strip_html(
                        strip_title="📊 Graf Unjuran Kes Baharu (+14 Hari) & Julat 95% CI",
                        tooltip_title="🎯 Unjuran Poisson +14 Hari (95% CI)",
                        relevance_html="Mengira jangkaan pertambahan kes baharu bagi setiap lokaliti aktif dalam tempoh 14 hari akan datang berdasarkan kadar kes 7 hari terakhir dan halaju penularan.",
                        formula_html="λ<sub>harian</sub> = max(Kes<sub>7h</sub>/7, Velocity×0.5)  |  Unjuran = 14λ ± 1.96√(14λ)",
                        current_calc_html=(
                            f"<b>Tertinggi Semasa — {html.escape(top1['Lokaliti'])}:</b><br>"
                            f"Kes 7h = <b>{top1['Kes 7 Hari Terkini']}</b> | Unjuran +14h = <b>{top1['Unjuran +14 Hari']} kes</b> (95% CI: <b>{top1['95% CI (+14 Hari)']}</b>)"
                        ),
                    ),
                    unsafe_allow_html=True,
                )
                fig_qa_fc = go.Figure()
                fig_qa_fc.add_trace(
                    go.Bar(
                        x=top_proj["Lokaliti"],
                        y=top_proj["Unjuran +14 Hari"],
                        marker_color="#ef4444",
                        error_y=dict(
                            type="data",
                            symmetric=False,
                            array=(
                                top_proj["CI Atas"] - top_proj["Unjuran +14 Hari"]
                            ).tolist(),
                            arrayminus=(
                                top_proj["Unjuran +14 Hari"] - top_proj["CI Bawah"]
                            ).tolist(),
                            color="#1e293b",
                            thickness=1.6,
                            width=5,
                        ),
                        name="Unjuran +14 Hari (95% CI)",
                    )
                )
                fig_qa_fc.update_layout(
                    xaxis_title="",
                    yaxis_title="Unjuran Kes (+14 Hari)",
                    height=330,
                    margin=dict(t=16, b=10, l=10, r=10),
                    paper_bgcolor="rgba(255,255,255,0.75)",
                    plot_bgcolor="rgba(255,255,255,0.55)",
                )
                st.plotly_chart(
                    fig_qa_fc, use_container_width=True, key="qa_forecast_bar"
                )
                tot_top_proj = round(float(top_proj["Unjuran +14 Hari"].sum()), 1)
                st.markdown(
                    render_ai_conclusion_box(
                        "Kesimpulan Graf & Titik Plot Unjuran +14 Hari",
                        f"Daripada <b>{len(top_proj)} lokaliti aktif</b> yang diplot, titik tertinggi ialah "
                        f"<b>{html.escape(str(top1['Lokaliti']))}</b> dengan unjuran <b>{top1['Unjuran +14 Hari']} kes baharu</b> "
                        f"(batas 95% CI: <b>{top1['95% CI (+14 Hari)']} kes</b>). Secara gabungan, lokaliti teratas ini dijangka "
                        f"menyumbang <b>{tot_top_proj} kes</b> dalam 14 hari akan datang jika tiada intervensi intensif dijalankan.",
                    ),
                    unsafe_allow_html=True,
                )

    # MODE 2: PENCAPAIAN KPI POA DENGGI & KORELASI WABAK
    elif is_poa_or_corr_q:
        with c_qa1:
            poa_badge = {
                "Status POA": {
                    "TERCAPAI": ("#dcfce7", "#166534"),
                    "TIDAK TERCAPAI": ("#fee2e2", "#991b1b"),
                }
            }
            poa_tbl = df_to_styled_html_table(df_poa_kpis, badge_cols=poa_badge)
            p_tbl = (
                "<br><b>Pekali Korelasi Pearson (r):</b>"
                + df_to_styled_html_table(df_pearson)
                if not df_pearson.empty
                else ""
            )
            d24_pct = poa_meta.get("daftar_24j_pct", 0.0)
            d24_num = poa_meta.get("daftar_24j_num", 0)
            d24_den = poa_meta.get("daftar_24j_den", 0)
            d24_gap = poa_meta.get("daftar_24j_gap", 0)
            unmet_list = (
                df_poa_kpis[df_poa_kpis["Status POA"] == "TIDAK TERCAPAI"][
                    "Indikator POA"
                ].tolist()
                if not df_poa_kpis.empty
                else []
            )
            unmet_note = (
                f"Indikator di bawah sasaran POA: <b>{html.escape(', '.join(unmet_list))}</b>."
                if unmet_list
                else "Kesemua indikator POA mencapai sasaran yang ditetapkan."
            )
            poa_tbl_conc = (
                f"<b>📌 Kesimpulan Jadual KPI POA Denggi:</b> Pendaftaran kes dalam tempoh 24 jam daripada notifikasi "
                f"(<b>Ind 4 / A2</b>) mencapai <b>{d24_pct}% ({d24_num:,}/{d24_den:,}; varians {d24_gap:+d} kes berbanding sasaran 85%)</b>. "
                f"{unmet_note}"
            )
            card_poa_qa = build_ai_hover_card_html(
                zone_id="ai_qa_left",
                card_title="📋 Jadual Pencapaian KPI POA Denggi & Korelasi (r)",
                body_html=poa_tbl + p_tbl,
                tooltip_title="📋 Sasaran & Formula KPI POA Denggi (KKM / PKD)",
                relevance_html=(
                    "Mengukur pematuhan operasi survelan dan kawalan kes sporadik mengikut Pelan Tindakan (POA) Denggi:<br>"
                    "• <b>Ind 1 (A1):</b> Notifikasi fasiliti kesihatan dalam tempoh 24 jam (Sasaran 100%).<br>"
                    "• <b>Ind 4 (A2):</b> Siasatan & pendaftaran kes dalam tempoh 24 jam dari tarikh notifikasi (Sasaran 85%).<br>"
                    "• <b>Ind 9 & 10 (C1):</b> Aktiviti PTP (Sasaran 70% Semua / 80% KKM) & SRT (Sasaran 60% Semua / 80% KKM) dalam 24 jam dari <b>Tarikh Daftar</b> bagi kes sporadik (<code>Satu Kes</code>)."
                ),
                formula_html=(
                    "A2 Daftar ≤24j = (Kes Daftar ≤1h dari Notif ÷ Jumlah Kes Daftar) × 100<br>"
                    "C1 PTP/SRT ≤24j = (Sporadik PTP/SRT ≤1h dari Tkh Daftar ÷ Bil. Sporadik) × 100"
                ),
                current_calc_html=(
                    f"<b>Prestasi Semasa Ind 4 (A2 — Daftar ≤24j):</b> <b>{d24_pct}%</b> ({d24_num:,}/{d24_den:,}, varians <b>{d24_gap:+d} kes</b> dari sasaran 85%)<br>"
                    f"<b>Sampel Kes Sporadik (Satu Kes):</b> <b>{poa_meta.get('sporadik_total', 0)} kes</b> keseluruhan (<b>{poa_meta.get('sporadik_kkm', 0)} kes</b> lokaliti KKM)."
                ),
                conclusion_html=poa_tbl_conc,
            )
            st.markdown(card_poa_qa, unsafe_allow_html=True)

        with c_qa2:
            if not df_poa_kpis.empty:
                st.markdown(
                    build_graph_info_strip_html(
                        strip_title="📊 Graf Pencapaian Semasa vs Sasaran POA Denggi (%)",
                        tooltip_title="📊 Perbandingan Pencapaian Semasa vs Sasaran POA (%)",
                        relevance_html="Membandingkan peratus pencapaian sebenar setiap indikator POA dengan sasaran KPI PKD/JKN bagi mengenal pasti jurang prestasi survelan (A1/A2) dan kawalan kes sporadik (C1).",
                        formula_html="Pencapaian (%) = (Bil. Kes Patuh ≤24j ÷ Bil. Kes Layak) × 100  |  Varians = Bil. Patuh − ⌈Sasaran% × N⌉",
                        current_calc_html=(
                            f"<b>Ringkasan Semasa:</b> <b>{int((df_poa_kpis['Status POA'] == 'TERCAPAI').sum())} daripada {len(df_poa_kpis)} indikator POA</b> mencapai sasaran."
                        ),
                    ),
                    unsafe_allow_html=True,
                )
                fig_qa_poa = go.Figure()
                fig_qa_poa.add_trace(
                    go.Bar(
                        x=df_poa_kpis["Kod"],
                        y=df_poa_kpis["Pencapaian (%)"],
                        name="Pencapaian Semasa (%)",
                        marker_color=[
                            "#10b981" if s == "TERCAPAI" else "#ef4444"
                            for s in df_poa_kpis["Status POA"]
                        ],
                        text=df_poa_kpis["Pencapaian (%)"].apply(lambda v: f"{v:.1f}%"),
                        textposition="outside",
                    )
                )
                fig_qa_poa.add_trace(
                    go.Scatter(
                        x=df_poa_kpis["Kod"],
                        y=df_poa_kpis["Sasaran (%)"],
                        name="Sasaran POA (%)",
                        mode="lines+markers",
                        line=dict(color="#0f172a", width=2.2, dash="dash"),
                        marker=dict(size=8, symbol="diamond"),
                    )
                )
                fig_qa_poa.update_yaxes(range=[0, 114])
                fig_qa_poa.update_layout(
                    height=330,
                    xaxis_title="",
                    yaxis_title="Peratus (%)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                    margin=dict(t=16, b=10, l=10, r=10),
                    paper_bgcolor="rgba(255,255,255,0.75)",
                    plot_bgcolor="rgba(255,255,255,0.55)",
                )
                st.plotly_chart(
                    fig_qa_poa, use_container_width=True, key="qa_poa_bar"
                )
                best_poa = df_poa_kpis.loc[df_poa_kpis["Pencapaian (%)"].idxmax()]
                low_poa = df_poa_kpis.loc[df_poa_kpis["Pencapaian (%)"].idxmin()]
                st.markdown(
                    render_ai_conclusion_box(
                        "Kesimpulan Graf Perbandingan KPI POA Denggi",
                        f"Pencapaian tertinggi direkodkan pada <b>{html.escape(str(best_poa['Indikator POA']))}</b> "
                        f"(<b>{best_poa['Pencapaian (%)']}%</b> berbanding sasaran <b>{best_poa['Sasaran (%)']}%</b>), manakala "
                        f"jurang terendah ialah <b>{html.escape(str(low_poa['Indikator POA']))}</b> "
                        f"(<b>{low_poa['Pencapaian (%)']}%</b> vs sasaran <b>{low_poa['Sasaran (%)']}%</b>). Mempercepatkan "
                        f"pendaftaran kes ≤24 jam (A2) serta semburan SRT kes sporadik di kawasan PBT meningkatkan perlindungan komuniti daripada tercetusnya wabak baharu.",
                    ),
                    unsafe_allow_html=True,
                )

    # MODE 3: PELAN TINDAKAN TAKTIKAL & LOKALITI (DEFAULT)
    else:
        lok_name = lok_sum.get("lokaliti", "Lokaliti Dipilih")
        kluster_txt = lok_sum.get("kluster_utama", "Radius 200m kes indeks")
        occ_txt = lok_sum.get("pekerjaan_dominan", "Penduduk setempat")
        nat_txt = lok_sum.get("kewarganegaraan_dominan", "Semua penduduk")

        top_risk_lok = (
            f"{df_active_risk.iloc[0]['Lokaliti']} (Skor {df_active_risk.iloc[0]['Skor Risiko']}/100)"
            if not df_active_risk.empty
            else lok_name
        )

        plan_df = pd.DataFrame(
            [
                {
                    "Keutamaan": "KEUTAMAAN 1 (POA A2)",
                    "Tindakan Operasi": "Siasatan & Pendaftaran Kes ≤ 24 Jam (Sasaran 85%)",
                    "Sasaran Spesifik (Data)": f"Pencapaian semasa: {poa_meta.get('daftar_24j_pct', 0.0)}% ({poa_meta.get('daftar_24j_num', 0):,}/{poa_meta.get('daftar_24j_den', 0):,})",
                    "Tempoh / KPI": "≤ 24 Jam dari Notifikasi",
                    "Justifikasi Data": "Memastikan siasatan kes & pengisytiharan wabak tidak tertangguh",
                },
                {
                    "Keutamaan": "KEUTAMAAN 2 (POA C1)",
                    "Tindakan Operasi": "PTP & SRT ≤ 24 Jam dari Tarikh Daftar (Kes Sporadik & Wabak)",
                    "Sasaran Spesifik (Data)": f"{lok_name} — Fokus {kluster_txt}",
                    "Tempoh / KPI": "≤ 24 Jam dari Tarikh Daftar",
                    "Justifikasi Data": "Menghalang kes sporadik (Satu Kes) daripada berkembang menjadi wabak",
                },
                {
                    "Keutamaan": "KEUTAMAAN 3",
                    "Tindakan Operasi": "Kawalan Wabak Aktif, ACD & Promosi Kesihatan",
                    "Sasaran Spesifik (Data)": f"Zon tertinggi: {top_risk_lok} | {nat_txt} ({occ_txt})",
                    "Tempoh / KPI": "Serta-merta & Ulangan Hari ke-7–10",
                    "Justifikasi Data": f"{lok_sum.get('jumlah_kes_sejarah', 0)} kes sejarah ({lok_sum.get('bil_episod_wabak', 0)} episod) di lokaliti",
                },
            ]
        )

        with c_qa1:
            plan_badge = {
                "Keutamaan": {
                    "KEUTAMAAN 1 (POA A2)": ("#fee2e2", "#991b1b"),
                    "KEUTAMAAN 2 (POA C1)": ("#fef3c7", "#92400e"),
                    "KEUTAMAAN 3": ("#e0f2fe", "#075985"),
                }
            }
            plan_html = df_to_styled_html_table(plan_df, badge_cols=plan_badge)
            plan_tbl_conc = (
                f"<b>📌 Kesimpulan Jadual Pelan Tindakan POA:</b> Keutamaan survelan ialah memastikan "
                f"<b>Pendaftaran Kes ≤ 24 Jam (Sasaran POA A2: 85%)</b> dan pelaksanaan <b>PTP/SRT ≤ 24 Jam dari Tarikh Daftar</b> "
                f"di titik tumpuan <b>{html.escape(kluster_txt)} ({html.escape(lok_name)})</b>."
            )
            card_plan_qa = build_ai_hover_card_html(
                zone_id="ai_qa_left",
                card_title=f"🎯 Jadual Pelan Tindakan Taktikal (POA): {lok_name}",
                body_html=plan_html,
                tooltip_title="🎯 Matriks Pelan Tindakan Berpandukan POA & Data",
                relevance_html="Menyusun keutamaan tindakan lapangan mengikut piawaian POA Denggi (A2 Pendaftaran ≤24j dari Notifikasi; C1 PTP/SRT ≤24j dari Tarikh Daftar) dan kluster struktur bangunan (Blok & Tingkat).",
                formula_html="A2: T<sub>Daftar</sub> − T<sub>Notif</sub> ≤ 24j (Sasaran 85%)  |  C1: T<sub>PTP/SRT</sub> − T<sub>Daftar</sub> ≤ 24j",
                current_calc_html=(
                    f"<b>Lokaliti Sasaran:</b> {html.escape(lok_name)}<br>"
                    f"<b>Kluster Utama:</b> {html.escape(kluster_txt)} | <b>Daftar ≤24j Semasa:</b> {poa_meta.get('daftar_24j_pct', 0.0)}%"
                ),
                conclusion_html=plan_tbl_conc,
            )
            st.markdown(card_plan_qa, unsafe_allow_html=True)

        with c_qa2:
            if not df_active_risk.empty:
                top1 = df_active_risk.iloc[0]
                t1_vel = float(top1["Jumlah Kes"]) / max(
                    float(top1["Tempoh (Hari)"]), 1.0
                )
                p1_vel = min(t1_vel * 35.0, 35.0)
                p1_c7 = min(float(top1["Kes 7 Hari Terkini"]) * 8.0, 30.0)
                p1_dur = min(float(top1["Tempoh (Hari)"]) * 0.6, 20.0)
                st1_up = str(top1["Status Semasa"]).upper()
                p1_bon = (
                    15
                    if "HOTSPOT" in st1_up
                    else (10 if "TAK TERKAWAL" in st1_up else 0)
                )
                st.markdown(
                    build_graph_info_strip_html(
                        strip_title="📊 Graf Kedudukan Skor Risiko Eskalasi Wabak Aktif (0–100)",
                        tooltip_title="🚨 Indeks Skor Risiko Eskalasi (0–100)",
                        relevance_html=(
                            "Indeks triaj berwajaran deterministik (<b>0–100 mata</b>) daripada 4 komponen:<br>"
                            "• <b>Velocity (Maks 35):</b> Kelajuan penularan (maks pada ≥1.0 kes/hari).<br>"
                            "• <b>Kes 7 Hari Terkini (Maks 30):</b> Lonjakan semasa (maks pada ≥4 kes/7h).<br>"
                            "• <b>Tempoh Wabak (Maks 20):</b> Ketahanan sarang pembiakan (maks pada ≥34 hari).<br>"
                            "• <b>Bonus Status KKM (Maks 15):</b> Hotspot +15, Tak Terkawal +10, Terkawal/Baru +0.<br>"
                            "<b>Julat Tahap:</b> <span style='color:#fca5a5;'>KRITIKAL (70–100)</span> | "
                            "<span style='color:#fde68a;'>TINGGI (45–69)</span> | "
                            "<span style='color:#7dd3fc;'>SEDERHANA (0–44)</span>."
                        ),
                        formula_html="Skor = min(100, round(min(Vel×35, 35) + min(Kes<sub>7h</sub>×8, 30) + min(Tempoh×0.6, 20) + Bonus Status))",
                        current_calc_html=(
                            f"<b>Keutamaan #1 Semasa — {html.escape(str(top1['Lokaliti']))}:</b><br>"
                            f"Velocity ({p1_vel:.1f}/35) + Kes 7h ({p1_c7:.1f}/30) + Tempoh ({p1_dur:.1f}/20) + Bonus (+{p1_bon}/15) = "
                            f"<b>{top1['Skor Risiko']}/100 ({top1['Tahap Risiko']})</b>"
                        ),
                    ),
                    unsafe_allow_html=True,
                )
                top_r_bar = df_active_risk.head(8).sort_values(
                    by="Skor Risiko", ascending=True
                )
                fig_qa_risk = px.bar(
                    top_r_bar,
                    x="Skor Risiko",
                    y="Lokaliti",
                    orientation="h",
                    color="Tahap Risiko",
                    text="Skor Risiko",
                    color_discrete_map={
                        "KRITIKAL": "#dc2626",
                        "TINGGI": "#f59e0b",
                        "SEDERHANA": "#0ea5e9",
                    },
                )
                fig_qa_risk.update_traces(textposition="outside")
                fig_qa_risk.update_xaxes(range=[0, 112])
                fig_qa_risk.update_layout(
                    height=330,
                    xaxis_title="Skor Risiko (0–100)",
                    yaxis_title="",
                    legend_title="",
                    margin=dict(t=16, b=10, l=10, r=10),
                    paper_bgcolor="rgba(255,255,255,0.75)",
                    plot_bgcolor="rgba(255,255,255,0.55)",
                )
                st.plotly_chart(
                    fig_qa_risk, use_container_width=True, key="qa_risk_hbar"
                )
                n_crit_high = int(
                    df_active_risk["Tahap Risiko"].isin(["KRITIKAL", "TINGGI"]).sum()
                )
                st.markdown(
                    render_ai_conclusion_box(
                        "Kesimpulan Graf Kedudukan Skor Risiko",
                        f"Terdapat <b>{n_crit_high} daripada {len(df_active_risk)} lokaliti aktif</b> berada pada tahap "
                        f"<b>KRITIKAL / TINGGI</b>. Lokaliti keutamaan #1 ialah <b>{html.escape(str(top1['Lokaliti']))}</b> "
                        f"(Skor <b>{top1['Skor Risiko']}/100</b>, Velocity <b>{top1['Velocity (Kes/Hari)']} kes/hari</b>) dan perlu "
                        f"diberi mobilisasi sumber kawalan vektor paling awal.",
                    ),
                    unsafe_allow_html=True,
                )

    # Panggil Gemini API yang tertanam dalam Secrets (dengan cache sesi untuk menjimatkan kuota percuma harian)
    if embedded_api_key:
        fact_packet = {
            "tarikh_laporan": fmt_date_short(today_my),
            "trend_mingguan_kes_per_minggu": round(slope, 2),
            "ramalan_4_minggu_95CI": df_forecast.to_dict(orient="records")
            if not df_forecast.empty
            else [],
            "pencapaian_kpi_poa_denggi": df_poa_kpis.to_dict(orient="records")
            if not df_poa_kpis.empty
            else [],
            "fasiliti_notifikasi_lewat_dan_pesalah_berulang": df_offenders_sum.head(10).to_dict(
                orient="records"
            )
            if not df_offenders_sum.empty
            else [],
            "korelasi_pearson": df_pearson.to_dict(orient="records")
            if not df_pearson.empty
            else [],
            "perbandingan_status_wabak": df_status_corr.to_dict(orient="records")
            if not df_status_corr.empty
            else [],
            "wabak_aktif_risiko_tertinggi": df_active_risk.head(8).to_dict(
                orient="records"
            )
            if not df_active_risk.empty
            else [],
            "ringkasan_lokaliti_dipilih": lok_sum,
        }
        cache_key = (
            f"{question.strip()}|{fmt_date_short(today_my)}|"
            f"{lok_sum.get('lokaliti', '')}|{lok_sum.get('jumlah_kes_sejarah', 0)}"
        )
        if "ai_response_cache" not in st.session_state:
            st.session_state.ai_response_cache = {}

        if cache_key in st.session_state.ai_response_cache:
            text_out, active_model_label = st.session_state.ai_response_cache[cache_key]
            err_code = None
        else:
            system_prompt = (
                "Anda ialah Pakar Epidemiologi Denggi KKM. Jawab soalan pengguna HANYA berdasarkan fakta "
                "dan angka dalam JSON DATA_SAHIH di bawah. Patuhi definisi POA Denggi: Indikator 1 (A1) Notifikasi <=24j (Sasaran 100%), "
                "Indikator 4 (A2) Daftar Kes <=24j dari Notifikasi (Sasaran 85%), Indikator 9 (C1) PTP Sporadik <=24j dari Tarikh Daftar (Sasaran 70% Semua / 80% KKM), "
                "Indikator 10 (C1) SRT Sporadik <=24j dari Tarikh Daftar (Sasaran 60% Semua / 80% KKM). JANGAN reka angka yang tiada dalam JSON."
            )
            user_prompt = (
                f"DATA_SAHIH:\n{json.dumps(fact_packet, ensure_ascii=False, indent=2)}\n\n"
                f"SOALAN PENGGUNA: {question}"
            )
            text_out, active_model_label, err_code = call_gemini_thinking_free_tier(
                embedded_api_key, system_prompt, user_prompt
            )
            if text_out and active_model_label:
                st.session_state.ai_response_cache[cache_key] = (
                    text_out,
                    active_model_label,
                )

        if text_out:
            st.caption(
                f"⚙️ Ulasan Tambahan AI: **{active_model_label} (based on Grounded on Data)**"
            )
            st.markdown(text_out)
        elif err_code == 429:
            st.warning(
                "⚠️ Had kuota percuma harian Gemini dicapai buat sementara waktu (akan reset secara automatik). Paparan jadual & graf di atas dijana terus oleh Enjin AI Statistik Terbina Dalam."
            )
        else:
            st.caption(
                "⚙️ Sumber Analisis: **Enjin AI Statistik Terbina Dalam (100% Data-Driven, Sifar Halusinasi)**"
            )
    else:
        st.caption(
            "⚙️ Sumber Analisis: **Enjin AI Statistik Terbina Dalam (100% Data-Driven, Sifar Halusinasi)** — Arahkan kursor pada mana-mana graf atau jadual untuk membuka gelembung naratif di sisi tanpa menghalang data."
        )


# --- PENGURUSAN STATE (MEMORI APLIKASI) ---
VIEW_DAILY = "📋 Status Harian & Peta GPS"
VIEW_LOCALITY = "📍 Analisis Lokaliti & Struktur"
VIEW_AI = "🧠 Pusat Analisis AI & Ramalan (95% CI)"

if "selected_lokaliti" not in st.session_state:
    st.session_state.selected_lokaliti = None
if "selected_wabak" not in st.session_state:
    st.session_state.selected_wabak = None
if "episode_filter" not in st.session_state:
    st.session_state.episode_filter = "Semua"
if "active_workspace_view" not in st.session_state:
    st.session_state.active_workspace_view = VIEW_DAILY
if "scroll_to_view_top" not in st.session_state:
    st.session_state.scroll_to_view_top = False
if "last_sejarah_click_sig" not in st.session_state:
    st.session_state.last_sejarah_click_sig = None
if "ai_custom_question" not in st.session_state:
    st.session_state.ai_custom_question = (
        "Jana pelan tindakan taktikal dan ramalan risiko wabak semasa."
    )


def set_workspace_view(view_name):
    st.session_state.active_workspace_view = view_name


def set_lokaliti_dan_wabak(lokaliti, wabak_no):
    st.session_state.selected_lokaliti = lokaliti
    st.session_state.selected_wabak = f"Wabak No: {format_wabak_no(wabak_no)}"
    st.session_state.episode_filter = "Semua"
    st.session_state.active_workspace_view = VIEW_LOCALITY
    st.session_state.scroll_to_view_top = True
    st.session_state.last_sejarah_click_sig = None


def select_wabak_episode_only(wabak_no_str):
    target_val = f"Wabak No: {format_wabak_no(wabak_no_str)}"
    st.session_state.selected_wabak = target_val
    st.session_state["locality_episode_selector"] = target_val
    st.session_state.last_sejarah_click_sig = None


def jump_to_lokaliti_from_table(lokaliti, wabak_no):
    st.session_state.selected_lokaliti = lokaliti
    st.session_state.selected_wabak = f"Wabak No: {format_wabak_no(wabak_no)}"
    st.session_state.episode_filter = "Semua"
    st.session_state.active_workspace_view = VIEW_LOCALITY
    st.session_state.scroll_to_view_top = True
    st.session_state.last_sejarah_click_sig = None


def set_lokaliti_sahaja(lokaliti):
    st.session_state.selected_lokaliti = lokaliti
    st.session_state.selected_wabak = None
    st.session_state.episode_filter = "Semua"
    st.session_state.active_workspace_view = VIEW_LOCALITY
    st.session_state.scroll_to_view_top = True
    st.session_state.last_sejarah_click_sig = None


def on_quick_search_select():
    chosen = st.session_state.get("main_quick_search_lokaliti")
    if chosen and chosen != "-- Taip atau Pilih Lokaliti untuk Analisis --":
        st.session_state.selected_lokaliti = chosen
        st.session_state.selected_wabak = None
        st.session_state.active_workspace_view = VIEW_LOCALITY
        st.session_state.scroll_to_view_top = True
        st.session_state.last_sejarah_click_sig = None


def on_locality_episode_dropdown_change():
    chosen_ep = st.session_state.get("locality_episode_selector")
    if chosen_ep:
        st.session_state.selected_wabak = chosen_ep
        st.session_state.last_sejarah_click_sig = None


def set_chart_year_range(state_key, start_yr, end_yr):
    st.session_state[state_key] = (start_yr, end_yr)


def set_ai_prompt(prompt_text):
    st.session_state.ai_custom_question = prompt_text


# =========================================================
# ANTARA MUKA UTAMA & HERO COMMAND PORTAL
# =========================================================
today_my = get_today_malaysia()
df_hist, hist_filename = load_historical_data()

if df_hist is None:
    st.markdown(
        f"""
        <div class="lg-landing-stage">
            <div class="lg-eyebrow"><span class="lg-live-dot"></span> KKM / PKD VECTOR SURVEILLANCE INTELLIGENCE • {fmt_date_short(today_my)}</div>
            <h1 class="lg-hero-title">🦟 DengueWatch Executive Intelligence</h1>
            <p class="lg-hero-sub">Platform Pemantauan Wabak Denggi Masa Nyata, Pemetaan Hotspot GPS, Analisis Struktur Bertingkat & Ramalan AI (95% CI).</p>
            <div class="lg-pill-row">
                <span class="lg-feature-pill">📋 Jadual Harian STATUS WABAK & Eksport WhatsApp</span>
                <span class="lg-feature-pill">🗺️ Peta Kluster GPS & Matriks Blok/Tingkat</span>
                <span class="lg-feature-pill">🧠 Ramalan AI 95% CI & KPI POA Denggi</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
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
    st.markdown(
        f"""
        <div class="lg-banner">
            <div class="lg-eyebrow"><span class="lg-live-dot"></span> PANGKALAN DATA SEJARAH AKTIF • {html.escape(str(hist_filename))} ({len(df_hist):,} REKOD: {min_yr}–{max_yr})</div>
            <h1 class="lg-hero-title">🦟 DengueWatch Executive Intelligence</h1>
            <p class="lg-hero-sub">Muat naik fail harian tahun semasa di bawah untuk menyatukan rekod terkini secara automatik.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

uploaded_file = st.file_uploader(
    "Seret & Lepas (Drag & Drop) Fail Harian e-Denggi (.xlsx, .xls, atau .csv) di sini",
    type=["xlsx", "xls", "csv"],
)

if uploaded_file is not None or df_hist is not None:
    try:
        df_current = load_data(uploaded_file) if uploaded_file is not None else None
        df = merge_datasets(df_hist, df_current)

        # Tetapkan tarikh rujukan laporan mengikut rekod terkini dalam dataset (mengelak percanggahan selepas 12:00 tengah malam)
        data_ref_date = get_dataset_anchor_date(
            df_current if df_current is not None else df, today_my
        )

        if uploaded_file is not None and df_hist is not None:
            st.success(
                f"✅ **Data Disatukan:** Rekod sejarah 5 tahun + fail terkini `{uploaded_file.name}` berjaya digabungkan (**{len(df):,} jumlah rekod**)."
            )

        # --- PENGIRAAN KEKERAPAN EPISODE WABAK KESELURUHAN ---
        df_wabak_sahaja = df[df["Jenis Kes"] == "Wabak"].dropna(subset=["Wabak No"])
        kekerapan_wabak = df_wabak_sahaja.groupby("Lokaliti (Alamat Semasa)")[
            "Wabak No"
        ].nunique()
        semua_lokaliti_list = sorted(df["Lokaliti (Alamat Semasa)"].dropna().unique())
        episode_map = {lok: kekerapan_wabak.get(lok, 0) for lok in semua_lokaliti_list}

        embedded_gemini_key = get_embedded_gemini_key()

        # =========================================================
        # JALUR KPI EKSEKUTIF TERATAS (5 KAD LIQUID-GLASS)
        # =========================================================
        curr_yr = data_ref_date.year
        df_curr_yr = df[df["Tarikh Daftar"].dt.year == curr_yr].copy()
        if df_curr_yr.empty:
            df_curr_yr = df.copy()
            yr_disp = "Keseluruhan"
        else:
            yr_disp = str(curr_yr)

        tot_kes_yr = len(df_curr_yr)
        kes_wabak_cnt = int((df_curr_yr["Jenis Kes"] == "Wabak").sum())
        kes_satu_cnt = int((df_curr_yr["Jenis Kes"] == "Satu Kes").sum())

        df_aktif_all = df[
            (df["Jenis Kes"] == "Wabak")
            & (df["Wabak Status"].notna())
            & (
                ~df["Wabak Status"]
                .astype(str)
                .str.contains("Tamat", case=False, na=False)
            )
        ].copy()
        n_active_outbreaks = int(df_aktif_all["Wabak No"].nunique())
        n_hotspot = int(
            df_aktif_all[
                df_aktif_all["Wabak Status"]
                .astype(str)
                .str.contains("Hotspot", case=False, na=False)
            ]["Wabak No"].nunique()
        )
        n_tak_terkawal = int(
            df_aktif_all[
                df_aktif_all["Wabak Status"]
                .astype(str)
                .str.contains("Tak Terkawal", case=False, na=False)
            ]["Wabak No"].nunique()
        )
        n_crit_tier = n_hotspot + n_tak_terkawal

        t_ref_global = (
            df["Tkh Notifikasi"].fillna(df["Tarikh Daftar"])
            if "Tkh Notifikasi" in df.columns
            else df["Tarikh Daftar"]
        )
        c_last7 = int(
            (
                (t_ref_global >= (data_ref_date - pd.Timedelta(days=6)))
                & (t_ref_global <= data_ref_date)
            ).sum()
        )
        c_prev7 = int(
            (
                (t_ref_global >= (data_ref_date - pd.Timedelta(days=13)))
                & (t_ref_global <= (data_ref_date - pd.Timedelta(days=7)))
            ).sum()
        )
        mom_7d_pct = ((c_last7 - c_prev7) / max(c_prev7, 1)) * 100
        mom_7d_str = f"{mom_7d_pct:+.1f}%"
        mom_color = (
            "#e11d48"
            if mom_7d_pct > 10
            else ("#059669" if mom_7d_pct < -5 else "#0f172a")
        )

        # Indikator 4 (POA A2): Siasatan dan pendaftaran kes dalam tempoh 24 jam daripada tarikh notifikasi (Sasaran 85%)
        _, top_poa_meta = compute_poa_kpi_summary(df_curr_yr)
        d24_pct_top = top_poa_meta["daftar_24j_pct"]
        d24_num_top = top_poa_meta["daftar_24j_num"]
        d24_den_top = top_poa_meta["daftar_24j_den"]
        d24_gap_top = top_poa_meta["daftar_24j_gap"]

        ek1, ek2, ek3, ek4, ek5 = st.columns(5)
        with ek1:
            st.markdown(
                build_glass_kpi_html(
                    label=f"Jumlah Kes ({yr_disp})",
                    value_str=f"{tot_kes_yr:,}",
                    sub_str=f"Wabak: <b>{kes_wabak_cnt:,}</b> • Satu Kes: <b>{kes_satu_cnt:,}</b>",
                    tooltip_title=f"📊 Jumlah Kes Berdaftar ({yr_disp})",
                    relevance_html="Mengukur beban keseluruhan kes denggi yang disahkan dan didaftarkan dalam kawasan pentadbiran bagi tahun semasa.",
                    formula_html="Jumlah Kes = Bil. Kes Wabak + Bil. Satu Kes",
                    current_calc_html=f"<b>Angka Semasa ({yr_disp}):</b> {kes_wabak_cnt:,} kes wabak + {kes_satu_cnt:,} kes terpencil = <b>{tot_kes_yr:,} kes</b>.",
                ),
                unsafe_allow_html=True,
            )
        with ek2:
            st.markdown(
                build_glass_kpi_html(
                    label="Wabak Aktif Semasa",
                    value_str=str(n_active_outbreaks),
                    sub_str=f"Terkawal/Baru: <b>{max(n_active_outbreaks - n_crit_tier, 0)}</b> • Eskalasi: <b>{n_crit_tier}</b>",
                    tooltip_title="🚨 Bilangan Episod Wabak Aktif",
                    relevance_html="Menunjukkan jumlah rantaian penularan aktif yang masih dalam tempoh pemantauan 14 hari KKM dan memerlukan operasi kawalan vektor.",
                    formula_html="Count(Distinct Wabak No) bagi Status ≠ Wabak Tamat",
                    current_calc_html=f"<b>Pecahan Semasa:</b> {max(n_active_outbreaks - n_crit_tier, 0)} Terkawal/Baru, {n_tak_terkawal} Tak Terkawal, {n_hotspot} Hotspot = <b>{n_active_outbreaks} aktif</b>.",
                ),
                unsafe_allow_html=True,
            )
        with ek3:
            st.markdown(
                build_glass_kpi_html(
                    label="Hotspot & Tak Terkawal",
                    value_str=str(n_crit_tier),
                    sub_str=f"Hotspot: <b>{n_hotspot}</b> • Tak Terkawal: <b>{n_tak_terkawal}</b>",
                    tooltip_title="🔥 Wabak Eskalasi Kritikal",
                    relevance_html="Mengenal pasti lokaliti yang telah melepasi kawalan fasa awal (>14 hari atau penularan berterusan) yang memerlukan intervensi ULV dan penguatkuasaan bersepadu.",
                    formula_html="Bil. Wabak Tak Terkawal + Bil. Lokaliti Hotspot",
                    current_calc_html=f"<b>Angka Semasa:</b> {n_hotspot} Hotspot + {n_tak_terkawal} Wabak Tak Terkawal = <b>{n_crit_tier} lokaliti kritikal</b>.",
                    accent_color="#e11d48" if n_crit_tier > 0 else "#059669",
                ),
                unsafe_allow_html=True,
            )
        with ek4:
            st.markdown(
                build_glass_kpi_html(
                    label="Momentum 7-Hari",
                    value_str=mom_7d_str,
                    sub_str=f"7H Kini: <b>{c_last7}</b> vs 7H Lalu: <b>{c_prev7}</b>",
                    tooltip_title="📈 Momentum Kes 7-Hari (Acceleration)",
                    relevance_html="Membandingkan jumlah notifikasi kes baharu dalam 7 hari terkini berbanding 7 hari sebelumnya bagi mengesan pecutan atau penyusutan penularan daerah secara masa nyata.",
                    formula_html="((Kes<sub>7H Kini</sub> − Kes<sub>7H Lalu</sub>) ÷ max(Kes<sub>7H Lalu</sub>, 1)) × 100",
                    current_calc_html=f"<b>Pengiraan Semasa:</b> ({c_last7} − {c_prev7}) ÷ {max(c_prev7, 1)} × 100 = <b>{mom_7d_str}</b>.",
                    accent_color=mom_color,
                ),
                unsafe_allow_html=True,
            )
        with ek5:
            st.markdown(
                build_glass_kpi_html(
                    label=f"Daftar Kes ≤24j ({yr_disp})",
                    value_str=f"{d24_pct_top:.1f}%",
                    sub_str=f"Sasaran POA A2: <b>85.0%</b> ({d24_num_top:,}/{d24_den_top:,})",
                    tooltip_title="⏱️ KPI POA Indikator 4 (A2): Daftar Kes ≤ 24 Jam",
                    relevance_html="Memastikan setiap notifikasi denggi yang diterima disiasat dan didaftarkan dalam sistem e-Denggi dalam tempoh 24 jam daripada tarikh notifikasi (Sasaran POA PKD: 85%).",
                    formula_html="(Bil. kes daftar dalam tempoh 24 jam ÷ Bil. kes daftar) × 100",
                    current_calc_html=f"<b>Pencapaian Semasa ({yr_disp}):</b> <b>{d24_num_top:,} / {d24_den_top:,} kes</b> = <b>{d24_pct_top:.1f}%</b> (Varians: <b>{d24_gap_top:+d} kes</b> berbanding sasaran 85%).",
                    accent_color="#059669" if d24_pct_top >= 85.0 else "#d97706",
                ),
                unsafe_allow_html=True,
            )

        # Jarak pernafasan yang jelas antara 5 kotak KPI di atas dan bar carian/tapisan di bawah
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

        # =========================================================
        # BAR KAWALAN UTAMA: TAPIS EPISOD, CARIAN PANTAS LOKALITI & CETAK PDF
        # =========================================================
        episodes_ada = sorted(list(set(episode_map.values())))
        pilihan_tapis_ep = ["Semua"] + [
            f"{int(e)} Episode" for e in episodes_ada if e > 0
        ]
        try:
            ep_idx = pilihan_tapis_ep.index(st.session_state.episode_filter)
        except ValueError:
            ep_idx = 0

        qs_c1, qs_c2, qs_c3 = st.columns([1.15, 2.35, 1.0])
        with qs_c1:
            pilihan_filter_episode = st.selectbox(
                "📊 Tapis Kekerapan Episod:",
                options=pilihan_tapis_ep,
                index=ep_idx,
                key="main_episode_filter_box",
            )
            st.session_state.episode_filter = pilihan_filter_episode

        if pilihan_filter_episode == "Semua":
            senarai_lokaliti_tapis = semua_lokaliti_list
        else:
            ep_val = int(pilihan_filter_episode.split()[0])
            senarai_lokaliti_tapis = sorted(
                [lok for lok, count in episode_map.items() if count == ep_val]
            )

        with qs_c2:
            search_options = [
                "-- Taip atau Pilih Lokaliti untuk Analisis --"
            ] + senarai_lokaliti_tapis
            st.selectbox(
                "🔍 Carian Pantas Lokaliti (Taip nama taman / flat / kondo):",
                options=search_options,
                index=0,
                key="main_quick_search_lokaliti",
                on_change=on_quick_search_select,
            )

        with qs_c3:
            st.markdown("<div style='height:31px;'></div>", unsafe_allow_html=True)
            if st.button(
                "🖨️ Cetak / Simpan PDF",
                key="main_print_pdf_btn",
                use_container_width=True,
            ):
                components.html(
                    """
                    <script>
                    window.parent.print();
                    </script>
                    """,
                    height=0,
                )

        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

        if not senarai_lokaliti_tapis:
            pilihan_lokaliti = None
            df_lok = pd.DataFrame()
        else:
            if st.session_state.selected_lokaliti not in senarai_lokaliti_tapis:
                st.session_state.selected_lokaliti = senarai_lokaliti_tapis[0]
                st.session_state.selected_wabak = None
            pilihan_lokaliti = st.session_state.selected_lokaliti
            df_lok = df[df["Lokaliti (Alamat Semasa)"] == pilihan_lokaliti].copy()

        pilihan_wabak_list = []
        pilihan_kategori = None
        if not df_lok.empty:
            df_w_only = df_lok[df_lok["Jenis Kes"] == "Wabak"].dropna(subset=["Wabak No"])
            if not df_w_only.empty:
                t_ref_w = (
                    df_w_only["Tkh Notifikasi"].fillna(df_w_only["Tarikh Daftar"])
                    if "Tkh Notifikasi" in df_w_only.columns
                    else df_w_only["Tarikh Daftar"]
                )
                df_w_only = df_w_only.assign(_t_sort=t_ref_w)
                wabak_ordered = (
                    df_w_only.groupby("Wabak No")["_t_sort"]
                    .max()
                    .sort_values(ascending=False)
                    .index.tolist()
                )
                for w in wabak_ordered:
                    pilihan_wabak_list.append(f"Wabak No: {format_wabak_no(w)}")

            if "Satu Kes" in df_lok["Jenis Kes"].values:
                pilihan_wabak_list.append("Satu Kes (Kes Terpencil)")

            if pilihan_wabak_list:
                if st.session_state.selected_wabak not in pilihan_wabak_list:
                    st.session_state.selected_wabak = pilihan_wabak_list[0]
                pilihan_kategori = st.session_state.selected_wabak

        # =========================================================
        # NAVIGASI RUANG KERJA LIQUID-GLASS (100% STATE-DRIVEN)
        # =========================================================
        st.markdown('<div id="dw-workspace-top-anchor"></div>', unsafe_allow_html=True)

        if st.session_state.scroll_to_view_top:
            st.session_state.scroll_to_view_top = False
            components.html(
                """
                <script>
                setTimeout(function() {
                    const el = window.parent.document.getElementById('dw-workspace-top-anchor');
                    if (el) {
                        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }, 100);
                </script>
                """,
                height=0,
            )

        nav_c1, nav_c2, nav_c3 = st.columns(3)
        with nav_c1:
            st.button(
                VIEW_DAILY,
                key="nav_btn_daily",
                type="primary"
                if st.session_state.active_workspace_view == VIEW_DAILY
                else "secondary",
                on_click=set_workspace_view,
                args=(VIEW_DAILY,),
                use_container_width=True,
            )
        with nav_c2:
            st.button(
                VIEW_LOCALITY,
                key="nav_btn_locality",
                type="primary"
                if st.session_state.active_workspace_view == VIEW_LOCALITY
                else "secondary",
                on_click=set_workspace_view,
                args=(VIEW_LOCALITY,),
                use_container_width=True,
            )
        with nav_c3:
            st.button(
                VIEW_AI,
                key="nav_btn_ai",
                type="primary"
                if st.session_state.active_workspace_view == VIEW_AI
                else "secondary",
                on_click=set_workspace_view,
                args=(VIEW_AI,),
                use_container_width=True,
            )

        st.markdown("---")

# =========================================================
        # PAPARAN 1: JADUAL HARIAN STATUS WABAK, PETA GPS & HIGHLIGHT
        # =========================================================
        if st.session_state.active_workspace_view == VIEW_DAILY:
            try:
                bar_c1, bar_c2, bar_c3 = st.columns([1.9, 1.9, 1.4])
                with bar_c3:
                    selected_rep_date = st.date_input(
                        "📅 Tarikh Laporan Jadual:",
                        value=data_ref_date.date(),
                        key=f"sw_report_date_{data_ref_date.strftime('%Y%m%d')}_{len(df)}",
                    )
                active_rep_ts = pd.Timestamp(selected_rep_date).normalize()

                df_sw_tamat, df_sw_aktif = build_status_wabak_tables(df, active_rep_ts)
                sw_png_bytes = render_status_wabak_png(df_sw_tamat, df_sw_aktif)
                sw_html, sw_clickable_rows = render_status_wabak_html(
                    df_sw_tamat, df_sw_aktif
                )

                with bar_c1:
                    st.markdown("<div style='height:31px;'></div>", unsafe_allow_html=True)
                    st.download_button(
                        label="📸 Muat Turun Gambar Table (WhatsApp)",
                        data=sw_png_bytes,
                        file_name=f"Status_Wabak_Denggi_{active_rep_ts.strftime('%d-%m-%Y')}.png",
                        mime="image/png",
                        use_container_width=True,
                    )
                with bar_c2:
                    st.markdown("<div style='height:31px;'></div>", unsafe_allow_html=True)
                    with st.popover(
                        "🖼️ Paparan Screenshot Penuh (WhatsApp)", use_container_width=True
                    ):
                        st.caption(
                            "Klik kanan pada gambar di bawah dan pilih **Copy Image** atau **Save Image As** untuk terus tampal ke WhatsApp."
                        )
                        st.image(sw_png_bytes, use_container_width=True)

                front_risk_radar_html, rk_clickable_items = render_front_risk_radar_html(
                    df, active_rep_ts
                )
                if front_risk_radar_html:
                    st.markdown(front_risk_radar_html, unsafe_allow_html=True)

                st.markdown(sw_html, unsafe_allow_html=True)

                if rk_clickable_items:
                    for idx_rk, (lok_rk, w_no_rk) in enumerate(rk_clickable_items):
                        st.button(
                            f"RK_JUMP_{idx_rk}",
                            key=f"rk_jump_trigger_{idx_rk}_{format_wabak_no(w_no_rk)}",
                            on_click=jump_to_lokaliti_from_table,
                            args=(lok_rk, w_no_rk),
                        )

                if sw_clickable_rows:
                    for idx_sw, (lok_sw, w_no_sw) in enumerate(sw_clickable_rows):
                        st.button(
                            f"SW_JUMP_{idx_sw}",
                            key=f"sw_jump_trigger_{idx_sw}_{format_wabak_no(w_no_sw)}",
                            on_click=jump_to_lokaliti_from_table,
                            args=(lok_sw, w_no_sw),
                        )

                if sw_clickable_rows or rk_clickable_items:
                    components.html(
                        """
                        <script>
                        (function() {
                            const doc = window.parent.document;

                            function hideJumpButtons() {
                                const buttons = doc.querySelectorAll('button');
                                buttons.forEach(btn => {
                                    const txt = (btn.textContent || '').trim();
                                    if (txt.startsWith('SW_JUMP_') || txt.startsWith('RK_JUMP_')) {
                                        const container = btn.closest('[data-testid="stElementContainer"], .element-container') || btn.parentElement;
                                        if (container) {
                                            container.style.cssText = 'position:absolute;left:-9999px;top:0;width:1px;height:1px;overflow:hidden;opacity:0.01;margin:0;padding:0;';
                                        }
                                    }
                                });
                            }

                            function bindTableAndRadarClicks() {
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
                                            if ((btn.textContent || '').trim() === targetLabel) {
                                                btn.click();
                                                break;
                                            }
                                        }
                                    });
                                });

                                const rkCards = doc.querySelectorAll('.risk-exec-card[data-rk-idx]');
                                rkCards.forEach(card => {
                                    if (card.dataset.rkBound === '1') return;
                                    card.dataset.rkBound = '1';
                                    card.addEventListener('click', function() {
                                        const idx = this.getAttribute('data-rk-idx');
                                        const targetLabel = 'RK_JUMP_' + idx;
                                        const buttons = doc.querySelectorAll('button');
                                        for (const btn of buttons) {
                                            if ((btn.textContent || '').trim() === targetLabel) {
                                                btn.click();
                                                break;
                                            }
                                        }
                                    });
                                });
                            }

                            bindTableAndRadarClicks();
                            const timer = setInterval(bindTableAndRadarClicks, 250);
                            setTimeout(() => clearInterval(timer), 6000);
                        })();
                        </script>
                        """,
                        height=0,
                    )

                # --- PETA INTERAKTIF KLUSTER & HOTSPOT GPS MALAYSIA (SERASI PLOTLY 5 & 6) ---
                st.markdown("---")
                st.subheader("🗺️ Peta Interaktif Kluster & Hotspot GPS Malaysia (Spatial Surveillance)")

                if "Latitud (ISO)" in df.columns and "Lngitud (ISO)" in df.columns:
                    df_map_src = df.copy()
                    df_map_src["_lat"] = pd.to_numeric(df_map_src["Latitud (ISO)"], errors="coerce")
                    df_map_src["_lng"] = pd.to_numeric(df_map_src["Lngitud (ISO)"], errors="coerce")
                    df_map_valid = df_map_src[
                        (df_map_src["_lat"] > 1.0)
                        & (df_map_src["_lat"] < 8.0)
                        & (df_map_src["_lng"] > 99.0)
                        & (df_map_src["_lng"] < 120.0)
                    ].copy()

                    if not df_map_valid.empty:
                        df_map_valid["Status Peta"] = (
                            df_map_valid["Wabak Status"].fillna("Satu Kes").astype(str).str.strip()
                        )
                        map_c1, map_c2, map_c3 = st.columns([2.2, 1.0, 0.9])
                        with map_c1:
                            map_filter_mode = st.radio(
                                "Tapis Lapisan Peta:",
                                [
                                    "Wabak Aktif Sahaja (Terkawal, Tak Terkawal & Hotspot)",
                                    "Semua Episod Wabak (Aktif & Tamat)",
                                    "Semua Kes (Termasuk Satu Kes)",
                                ],
                                horizontal=True,
                                key="gps_map_filter_mode",
                            )
                        with map_c2:
                            map_scope_choice = st.selectbox(
                                "Skala Peta Malaysia:",
                                ["Fokus Daerah / Lokaliti (KL)", "Seluruh Malaysia"],
                                index=0,
                                key="gps_map_scope_choice",
                            )
                        with map_c3:
                            map_style_choice = st.selectbox(
                                "Gaya Peta:",
                                ["carto-positron", "open-street-map"],
                                index=0,
                                key="gps_map_style_choice",
                            )

                        if "Wabak Aktif Sahaja" in map_filter_mode:
                            df_map_filtered = df_map_valid[
                                (df_map_valid["Jenis Kes"] == "Wabak")
                                & (~df_map_valid["Status Peta"].str.contains("Tamat", case=False, na=False))
                            ]
                        elif "Semua Episod Wabak" in map_filter_mode:
                            df_map_filtered = df_map_valid[df_map_valid["Jenis Kes"] == "Wabak"]
                        else:
                            df_map_filtered = df_map_valid

                        if not df_map_filtered.empty:
                            lok_gps = df_map_filtered.groupby(
                                ["Lokaliti (Alamat Semasa)", "Status Peta"], as_index=False
                            ).agg(
                                Lat=("_lat", "median"),
                                Lng=("_lng", "median"),
                                Jumlah_Kes=("Notifikasi No", "count"),
                                Pentadbir=(
                                    "Pihak Pentadbir Lokaliti",
                                    lambda s: s.dropna().iloc[0] if not s.dropna().empty else "-",
                                ),
                            )
                            lok_gps["Lokaliti (Alamat Semasa)"] = lok_gps[
                                "Lokaliti (Alamat Semasa)"
                            ].apply(clean_locality_display)

                            # Tetapkan pusat koordinat Malaysia secara eksplisit supaya peta tidak pernah terzum ke negara lain / lautan
                            if map_scope_choice == "Seluruh Malaysia":
                                center_lat, center_lon = 4.2105, 108.9758
                                map_zoom = 5.4
                            else:
                                center_lat = float(lok_gps["Lat"].median()) if not lok_gps.empty else 3.1106
                                center_lon = float(lok_gps["Lng"].median()) if not lok_gps.empty else 101.7221
                                map_zoom = 11.8

                            map_color_discrete = {
                                "Wabak Baru": "#00bcd4",
                                "Hotspot": "#fe0000",
                                "Wabak Tak Terkawal": "#2563eb",
                                "Wabak Terkawal": "#f97316",
                                "Wabak Tamat": "#10b981",
                                "Satu Kes": "#64748b",
                            }
                            if hasattr(px, "scatter_map"):
                                fig_map = px.scatter_map(
                                    lok_gps,
                                    lat="Lat",
                                    lon="Lng",
                                    color="Status Peta",
                                    size="Jumlah_Kes",
                                    size_max=26,
                                    center={"lat": center_lat, "lon": center_lon},
                                    zoom=map_zoom,
                                    map_style=map_style_choice,
                                    hover_name="Lokaliti (Alamat Semasa)",
                                    hover_data={
                                        "Status Peta": True,
                                        "Jumlah_Kes": True,
                                        "Pentadbir": True,
                                        "Lat": ":.5f",
                                        "Lng": ":.5f",
                                    },
                                    color_discrete_map=map_color_discrete,
                                )
                                fig_map.update_layout(
                                    map=dict(
                                        center=dict(lat=center_lat, lon=center_lon),
                                        zoom=map_zoom,
                                        style=map_style_choice,
                                    )
                                )
                            else:
                                fig_map = px.scatter_mapbox(
                                    lok_gps,
                                    lat="Lat",
                                    lon="Lng",
                                    color="Status Peta",
                                    size="Jumlah_Kes",
                                    size_max=26,
                                    center={"lat": center_lat, "lon": center_lon},
                                    zoom=map_zoom,
                                    mapbox_style=map_style_choice,
                                    hover_name="Lokaliti (Alamat Semasa)",
                                    hover_data={
                                        "Status Peta": True,
                                        "Jumlah_Kes": True,
                                        "Pentadbir": True,
                                        "Lat": ":.5f",
                                        "Lng": ":.5f",
                                    },
                                    color_discrete_map=map_color_discrete,
                                )
                                fig_map.update_layout(
                                    mapbox=dict(
                                        center=dict(lat=center_lat, lon=center_lon),
                                        zoom=map_zoom,
                                        style=map_style_choice,
                                    )
                                )

                            fig_map.update_layout(
                                height=450,
                                margin=dict(l=0, r=0, t=10, b=0),
                                legend=dict(
                                    title="Status Lokaliti (Malaysia)",
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.01,
                                    x=0,
                                ),
                            )
                            st.plotly_chart(
                                fig_map,
                                use_container_width=True,
                                key=f"gps_hotspot_map_{map_filter_mode}_{map_scope_choice}_{map_style_choice}",
                            )
                        else:
                            st.info("Tiada koordinat GPS untuk lapisan tapisan ini.")
                    else:
                        st.info("Koordinat GPS sah Malaysia tidak ditemui dalam fail yang dimuat naik.")

                # --- HIGHLIGHT 1: WABAK AKTIF SEMASA (TOP 5) ---
                df_aktif = df[
                    (df["Jenis Kes"] == "Wabak")
                    & (df["Wabak Status"].notna())
                    & (~df["Wabak Status"].astype(str).str.contains("Tamat", case=False, na=False))
                ].copy()

                st.markdown("---")
                st.subheader("🚨 Highlight: Wabak Aktif Semasa (Top 5)")

                if not df_aktif.empty:
                    data_wabak_aktif = []
                    grouped = df_aktif.groupby(["Lokaliti (Alamat Semasa)", "Wabak No"])

                    for (lokaliti, wabak_no), group in grouped:
                        jumlah_k = len(group)
                        t_ser = (
                            group["Tkh Notifikasi"].fillna(group["Tarikh Daftar"])
                            if "Tkh Notifikasi" in group.columns
                            else group["Tarikh Daftar"]
                        )
                        tarikh_kes = t_ser.dropna().sort_values().tolist()

                        if len(tarikh_kes) >= 2:
                            tarikh_mula = tarikh_kes[1]
                        elif len(tarikh_kes) == 1:
                            tarikh_mula = tarikh_kes[0]
                        else:
                            continue

                        tempoh_h = max((active_rep_ts - tarikh_mula).days, 1)
                        vel = jumlah_k / tempoh_h
                        c_7d = int((t_ser >= (active_rep_ts - pd.Timedelta(days=6))).sum())

                        data_wabak_aktif.append(
                            {
                                "Lokaliti": lokaliti,
                                "Wabak No": wabak_no,
                                "Jumlah Kes": jumlah_k,
                                "Tempoh (Hari)": tempoh_h,
                                "Velocity": vel,
                                "Kes 7H": c_7d,
                            }
                        )

                    df_highlight = pd.DataFrame(data_wabak_aktif)
                    c1, c2, c3 = st.columns(3)

                    with c1:
                        st.markdown("**🚀 Velocity Tertinggi (Kes/Hari)**")
                        top_vel = df_highlight.nlargest(5, "Velocity")
                        for _, row in top_vel.iterrows():
                            st.button(
                                f"{row['Velocity']:.2f} kes/hari - {row['Lokaliti']}",
                                key=f"vel_{row['Wabak No']}",
                                on_click=set_lokaliti_dan_wabak,
                                args=(row["Lokaliti"], row["Wabak No"]),
                                use_container_width=True,
                            )

                    with c2:
                        st.markdown("**🔥 Jumlah Kes Tertinggi**")
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
                        st.markdown("**⏳ Tempoh Wabak Terlama**")
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

                # --- HIGHLIGHT 2: EPISODE WABAK TERTINGGI (TOP 10) ---
                st.markdown("---")
                st.subheader("🔁 Highlight: Kekerapan Episode Wabak Tertinggi (Top 10)")

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
            except Exception as tab1_err:
                st.error(f"Ralat pada paparan Status Harian / Peta: {tab1_err}")

        # =========================================================
        # PAPARAN 2: ANALISIS LOKALITI, STRUKTUR BERTINGKAT & KLINIKAL
        # =========================================================
        elif st.session_state.active_workspace_view == VIEW_LOCALITY:
            try:
                if not df_lok.empty and pilihan_kategori:
                    # Segerakkan pemilih episod SEBELUM widget st.selectbox dicipta
                    st.session_state["locality_episode_selector"] = pilihan_kategori

                    lok_bar_c1, lok_bar_c2 = st.columns([1.4, 2.6])
                    with lok_bar_c1:
                        st.markdown("<div style='height:31px;'></div>", unsafe_allow_html=True)
                        st.button(
                            "⬅️ Kembali ke Status Harian & Peta GPS",
                            key="btn_back_to_daily",
                            on_click=set_workspace_view,
                            args=(VIEW_DAILY,),
                            use_container_width=True,
                        )
                    with lok_bar_c2:
                        st.selectbox(
                            "🎯 Episod Wabak / Kategori Kes Dipilih:",
                            options=pilihan_wabak_list,
                            key="locality_episode_selector",
                            on_change=on_locality_episode_dropdown_change,
                        )

                    # --- NOTA SEJARAH EPISODE WABAK & GRAF TREND INTERAKTIF (BAR & LEGENDA BOLEH KLIK) ---
                    rekod_episode_lokaliti = episode_map.get(pilihan_lokaliti, 0)
                    if rekod_episode_lokaliti > 0:
                        df_wabak_lok = df_lok[df_lok["Jenis Kes"] == "Wabak"].copy()

                        if not df_wabak_lok.empty:
                            wabak_summary = []

                            df_wabak_lok["Wabak_Str"] = df_wabak_lok["Wabak No"].apply(format_wabak_no)
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

                            for w_no_str, group in df_wabak_lok.groupby("Wabak_Str"):
                                j_kes = len(group)
                                t_ser_g = (
                                    group["Tkh Notifikasi"].fillna(group["Tarikh Daftar"])
                                    if "Tkh Notifikasi" in group.columns
                                    else group["Tarikh Daftar"]
                                )
                                group_sorted = group.assign(_t_ref=t_ser_g).sort_values(by="_t_ref")
                                t_kes = group_sorted["_t_ref"].dropna().tolist()

                                if len(t_kes) >= 2:
                                    t_m = t_kes[1]
                                    mula_row = group_sorted.dropna(subset=["_t_ref"]).iloc[1]
                                elif len(t_kes) == 1:
                                    t_m = t_kes[0]
                                    mula_row = group_sorted.dropna(subset=["_t_ref"]).iloc[0]
                                else:
                                    t_m = data_ref_date
                                    mula_row = group_sorted.iloc[0]

                                status_w = str(group["Wabak Status"].iloc[0])
                                t_last = max(t_kes) if t_kes else t_m
                                t_last_str = t_last.strftime("%d-%m-%Y")
                                t_tamat_rasmi = t_last + pd.Timedelta(days=14)

                                if "Tamat" in status_w:
                                    t_a = t_tamat_rasmi
                                    t_a_str = t_a.strftime("%d-%m-%Y")
                                    tempoh = max((t_a - t_m).days, 1)
                                    lbl_tarikh = "Tarikh Tamat Rasmi (+14h)"
                                    lbl_tempoh = "Tempoh Wabak"
                                else:
                                    t_a_str = t_tamat_rasmi.strftime("%d-%m-%Y")
                                    tempoh = max((data_ref_date - t_m).days, 1)
                                    lbl_tarikh = "Anggaran Tarikh Tamat"
                                    lbl_tempoh = "Tempoh (Sehingga Kini)"

                                width_ms = tempoh * MS_PER_DAY
                                center_dt = t_m + pd.Timedelta(milliseconds=width_ms / 2)
                                end_dt_visual = t_m + pd.Timedelta(days=tempoh)

                                m_val = (
                                    mula_row["Epid Minggu (Tkh Daftar)"]
                                    if pd.notnull(mula_row["Epid Minggu (Tkh Daftar)"])
                                    else t_m.isocalendar().week
                                )
                                y_val = (
                                    int(mula_row["Epid Tahun (Tkh Daftar)"])
                                    if "Epid Tahun (Tkh Daftar)" in group.columns
                                    and pd.notnull(mula_row["Epid Tahun (Tkh Daftar)"])
                                    else t_m.year
                                )
                                m_label = f"{y_val}-ME{int(m_val):02d}"

                                wabak_summary.append(
                                    {
                                        "Wabak_Str": w_no_str,
                                        "Tahun": y_val,
                                        "Jumlah Kes": j_kes,
                                        "Tarikh Mula": t_m,
                                        "End_Dt_Visual": end_dt_visual,
                                        "Center_Dt": center_dt,
                                        "Width_Ms": width_ms,
                                        "Tarikh Mula Str": t_m.strftime("%d-%m-%Y"),
                                        "Tarikh Notif Akhir Str": t_last_str,
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
                                    df_plot["Period"] = df_plot["Tarikh Mula"].dt.to_period("W-SAT")
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
                                                "end_ms": int((p.end_time + pd.Timedelta(seconds=1)).timestamp() * 1000),
                                                "start_iso": p.start_time.strftime("%Y-%m-%d"),
                                                "end_iso": (p.end_time + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
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

                                    active_w_clean = (
                                        st.session_state.selected_wabak.replace("Wabak No: ", "").strip()
                                        if st.session_state.selected_wabak
                                        and "Wabak No:" in st.session_state.selected_wabak
                                        else ""
                                    )

                                    fig_sejarah = go.Figure()
                                    trace_wabak_list = []
                                    for _, row in df_plot.sort_values(
                                        by=["Tarikh Mula", "Wabak_Str"]
                                    ).iterrows():
                                        w_str = row["Wabak_Str"]
                                        trace_wabak_list.append(w_str)
                                        is_selected_bar = w_str == active_w_clean
                                        fig_sejarah.add_trace(
                                            go.Bar(
                                                x=[row["Center_Dt"]],
                                                y=[row["Jumlah Kes"]],
                                                width=[row["Width_Ms"]],
                                                name=w_str,
                                                marker=dict(
                                                    color=color_map[w_str],
                                                    line=dict(
                                                        width=2.6 if is_selected_bar else 0.8,
                                                        color="#0f172a" if is_selected_bar else "rgba(0,0,0,0.55)",
                                                    ),
                                                ),
                                                opacity=1.0 if (not active_w_clean or is_selected_bar) else 0.65,
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
                                                        row["Tarikh Notif Akhir Str"],
                                                    ]
                                                ],
                                                hovertemplate="<br>".join(
                                                    [
                                                        "<b>Wabak No:</b> %{customdata[3]} <i>(Klik bar/legenda)</i>",
                                                        "<b>Jumlah Kes:</b> %{customdata[6]} Kes",
                                                        "<b>Tarikh Mula:</b> %{customdata[0]}",
                                                        "<b>Tarikh Notif Terakhir:</b> %{customdata[7]}",
                                                        "<b>%{customdata[4]}:</b> %{customdata[1]}",
                                                        "<b>%{customdata[5]}:</b> %{customdata[2]} Hari",
                                                        "<extra></extra>",
                                                    ]
                                                ),
                                            )
                                        )

                                    for y_div in range(yr_start, yr_end + 1):
                                        jan1_str = f"{y_div}-01-01"
                                        fig_sejarah.add_vline(
                                            x=jan1_str,
                                            line_width=1,
                                            line_dash="dot",
                                            line_color="rgba(100, 116, 139, 0.45)",
                                        )
                                        fig_sejarah.add_annotation(
                                            x=jan1_str,
                                            y=1.02,
                                            yref="paper",
                                            text=str(y_div),
                                            showarrow=False,
                                            font=dict(size=10, color="rgba(71, 85, 105, 0.85)"),
                                            xanchor="left",
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
                                        title="Tahun & Minggu Epid (Klik mana-mana bar atau legenda No. Wabak untuk paparan butiran)",
                                        rangeslider=dict(visible=False),
                                    )
                                    fig_sejarah.update_yaxes(title="Jumlah Kes Terkumpul", rangemode="tozero")
                                    fig_sejarah.update_layout(
                                        title=f"Garis Masa Kekerapan, Saiz & Tempoh Setiap Wabak di {pilihan_lokaliti} ({tajuk_tempoh})",
                                        barmode="overlay",
                                        height=430,
                                        margin=dict(t=42, b=10, l=10, r=10),
                                        dragmode="zoom",
                                        clickmode="event+select",
                                        paper_bgcolor="rgba(255,255,255,0.75)",
                                        plot_bgcolor="rgba(255,255,255,0.55)",
                                        legend=dict(
                                            title="No. Wabak (Klik / Skrol ▲▼)",
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

                                    chart_key = f"plotly_sejarah_{pilihan_lokaliti}_{yr_start}_{yr_end}"
                                    selected_data = st.plotly_chart(
                                        fig_sejarah,
                                        on_select="rerun",
                                        selection_mode="points",
                                        use_container_width=True,
                                        key=chart_key,
                                    )

                                    # Proses klik pada bar terus melalui seleksi asli Streamlit
                                    if selected_data:
                                        pts = getattr(getattr(selected_data, "selection", None), "points", None)
                                        if pts:
                                            pt = pts[0]
                                            curve_idx = pt.get("curve_number")
                                            if curve_idx is None:
                                                curve_idx = pt.get("curveNumber")
                                            pt_idx = pt.get("point_number", pt.get("pointNumber", 0))
                                            click_sig = f"{chart_key}:{curve_idx}:{pt_idx}:{pt.get('x')}:{pt.get('y')}"
                                            if st.session_state.last_sejarah_click_sig != click_sig:
                                                st.session_state.last_sejarah_click_sig = click_sig
                                                clicked_w_no_str = None
                                                cdata = pt.get("customdata")
                                                if isinstance(cdata, (list, tuple)) and len(cdata) > 3:
                                                    clicked_w_no_str = str(cdata[3])
                                                elif curve_idx is not None and 0 <= int(curve_idx) < len(trace_wabak_list):
                                                    clicked_w_no_str = trace_wabak_list[int(curve_idx)]
                                                if clicked_w_no_str:
                                                    target_w_str = f"Wabak No: {clicked_w_no_str}"
                                                    if st.session_state.selected_wabak != target_w_str:
                                                        st.session_state.selected_wabak = target_w_str
                                                        st.rerun()

                                    # Butang pencetus tersembunyi (position:absolute, 0px gap) untuk klik pada Legenda
                                    for w_opt_str in unique_wabaks_str:
                                        st.button(
                                            f"EP_JUMP_{w_opt_str}",
                                            key=f"ep_jump_trigger_{pilihan_lokaliti}_{w_opt_str}",
                                            on_click=select_wabak_episode_only,
                                            args=(w_opt_str,),
                                        )

                                    period_items_json = json.dumps(period_items)
                                    has_zoom_slider = "true" if len(x_labels) > 10 else "false"
                                    components.html(
                                        f"""
                                        <script>
                                        (function() {{
                                            const periodItems = {period_items_json};
                                            const hasZoomSlider = {has_zoom_slider};
                                            const doc = window.parent.document;
                                            const win = window.parent;
                                            let rafId = null;

                                            function hideEpJumpButtons() {{
                                                const buttons = doc.querySelectorAll('button');
                                                buttons.forEach(btn => {{
                                                    const txt = (btn.textContent || '').trim();
                                                    if (txt.startsWith('EP_JUMP_')) {{
                                                        const container = btn.closest('[data-testid="stElementContainer"], .element-container') || btn.parentElement;
                                                        if (container) {{
                                                            container.style.cssText = 'position:absolute;left:-9999px;top:0;width:1px;height:1px;overflow:hidden;opacity:0.01;margin:0;padding:0;';
                                                        }}
                                                    }}
                                                }});
                                            }}

                                            function triggerEpisodeSelect(wabakNoStr) {{
                                                if (!wabakNoStr) return;
                                                const cleanId = String(wabakNoStr).trim();
                                                const targetLabel = 'EP_JUMP_' + cleanId;
                                                const buttons = doc.querySelectorAll('button');
                                                for (const btn of buttons) {{
                                                    if ((btn.textContent || '').trim() === targetLabel) {{
                                                        btn.click();
                                                        return;
                                                    }}
                                                }}
                                            }}

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
                                                if (!hasZoomSlider) return;
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

                                            function bindAll() {{
                                                hideEpJumpButtons();
                                                const sliderEl = findZoomSlider();
                                                if (hasZoomSlider && sliderEl && sliderEl.dataset.rtBound !== '1') {{
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

                                                const plotEl = findHistoryPlot(sliderEl);
                                                if (plotEl && plotEl.dataset.legBound !== '1') {{
                                                    plotEl.dataset.legBound = '1';

                                                    plotEl.addEventListener('click', function(e) {{
                                                        const traceNode = e.target && e.target.closest ? e.target.closest('.legend .traces') : null;
                                                        if (traceNode) {{
                                                            e.stopPropagation();
                                                            e.preventDefault();
                                                            const txtEl = traceNode.querySelector('.legendtext');
                                                            if (txtEl && txtEl.textContent) {{
                                                                triggerEpisodeSelect(txtEl.textContent.trim());
                                                            }}
                                                        }}
                                                    }}, true);

                                                    if (typeof plotEl.on === 'function') {{
                                                        plotEl.on('plotly_legendclick', function(ev) {{
                                                            if (ev && ev.data && typeof ev.curveNumber === 'number') {{
                                                                const trace = ev.data[ev.curveNumber];
                                                                if (trace && trace.name) {{
                                                                    triggerEpisodeSelect(trace.name);
                                                                }}
                                                            }}
                                                            return false;
                                                        }});
                                                        plotEl.on('plotly_legenddoubleclick', function() {{
                                                            return false;
                                                        }});
                                                    }}
                                                }}
                                            }}

                                            bindAll();
                                            const retryTimer = setInterval(bindAll, 250);
                                            setTimeout(() => clearInterval(retryTimer), 6000);
                                        }})();
                                        </script>
                                        """,
                                        height=0,
                                    )
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
                                            "Tarikh Notif Akhir Str",
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
                                            "Tarikh Notif Akhir Str": "Notif Terakhir",
                                            "Tarikh Akhir Str": "Tarikh Tamat (+14h)",
                                        }
                                    )
                                    st.dataframe(
                                        df_ep_table,
                                        use_container_width=True,
                                        hide_index=True,
                                    )

                                if (
                                    st.session_state.selected_wabak
                                    and "Wabak No:" in st.session_state.selected_wabak
                                ):
                                    current_w_str = (
                                        st.session_state.selected_wabak.replace("Wabak No: ", "").strip()
                                    )
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

                    # Baca pilihan_kategori terkini selepas sebarang klik graf/legenda
                    pilihan_kategori_aktif = st.session_state.selected_wabak or pilihan_kategori

                    tarikh_kes = []
                    if pilihan_kategori_aktif == "Satu Kes (Kes Terpencil)":
                        df_filter = df_lok[df_lok["Jenis Kes"] == "Satu Kes"].copy()
                        status_wabak_semasa = "Tiada (Satu Kes)"
                        tempoh_wabak_hari = 1
                        tarikh_mula_str = "N/A"
                        tarikh_mula = data_ref_date
                        tarikh_akhir = data_ref_date
                    else:
                        w_no = float(pilihan_kategori_aktif.replace("Wabak No: ", ""))
                        df_filter = df_lok[df_lok["Wabak No"] == w_no].copy()
                        status_wabak_semasa = str(df_filter["Wabak Status"].iloc[0])

                        t_ser_f = (
                            df_filter["Tkh Notifikasi"].fillna(df_filter["Tarikh Daftar"])
                            if "Tkh Notifikasi" in df_filter.columns
                            else df_filter["Tarikh Daftar"]
                        )
                        tarikh_kes = t_ser_f.dropna().sort_values().tolist()

                        if len(tarikh_kes) >= 2:
                            tarikh_mula = tarikh_kes[1]
                        elif len(tarikh_kes) == 1:
                            tarikh_mula = tarikh_kes[0]
                        else:
                            tarikh_mula = data_ref_date

                        tarikh_mula_str = tarikh_mula.strftime("%d-%m-%Y")

                        if "Tamat" in status_wabak_semasa:
                            tarikh_akhir = (
                                tarikh_kes[-1] + pd.Timedelta(days=14)
                                if tarikh_kes
                                else data_ref_date
                            )
                        else:
                            tarikh_akhir = data_ref_date

                        tempoh_wabak_hari = max((tarikh_akhir - tarikh_mula).days, 1)

                    jumlah_kes = len(df_filter)
                    pentadbir_lokaliti = (
                        df_filter["Pihak Pentadbir Lokaliti"].mode()[0]
                        if not df_filter["Pihak Pentadbir Lokaliti"].empty
                        else "Tidak Dinyatakan"
                    )

                    st.header(f"📍 Analisis Lokaliti: {pilihan_lokaliti}")
                    st.subheader(
                        f"Wabak: {pilihan_kategori_aktif} | Status: {status_wabak_semasa} | Pentadbir: {pentadbir_lokaliti}"
                    )
                    st.markdown(
                        f"*(**Rekod Sejarah:** Lokaliti ini telah mencatatkan **{rekod_episode_lokaliti} episode penularan wabak** secara keseluruhan)*"
                    )

                    tarikh_akhir_str = (
                        tarikh_akhir.strftime("%d-%m-%Y")
                        if pilihan_kategori_aktif != "Satu Kes (Kes Terpencil)"
                        else "N/A"
                    )
                    lbl_tamat_banner = "Tamat" if "Tamat" in status_wabak_semasa else "Anggaran Tamat"
                    t_tamat_banner_str = (
                        tarikh_akhir_str
                        if "Tamat" in status_wabak_semasa
                        else (
                            (tarikh_kes[-1] + pd.Timedelta(days=14)).strftime("%d-%m-%Y")
                            if pilihan_kategori_aktif != "Satu Kes (Kes Terpencil)" and tarikh_kes
                            else "N/A"
                        )
                    )

                    # --- SEPANDUK JELAS MENUNJUKKAN EPISOD YANG SEDANG DIPAPARKAN DI BAWAH GRAF ---
                    st.markdown(
                        f'<div class="ep-active-banner">'
                        f'<span>🔎 <b>Sedang Memaparkan Butiran Episod:</b> <span style="color:#0369a1; font-weight:800;">{html.escape(str(pilihan_kategori_aktif))}</span> • <b>{html.escape(str(pilihan_lokaliti))}</b></span>'
                        f'<span>Status: <b>{html.escape(str(status_wabak_semasa))}</b> • Mula: <b>{html.escape(str(tarikh_mula_str))}</b> • {lbl_tamat_banner}: <b>{html.escape(str(t_tamat_banner_str))}</b> • <b>{jumlah_kes} Kes</b></span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                    # --- SEMAKAN KESIAPSIAGAAN KAWALAN VEKTOR LAPANGAN (PTP, SRT, ULV) ---
                    ptp_dt = (
                        df_filter["Tkh PTP Aktiviti Pertama"].dropna().min()
                        if "Tkh PTP Aktiviti Pertama" in df_filter.columns
                        else pd.NaT
                    )
                    srt_dt = (
                        df_filter["Tkh SRT Aktiviti Pertama"].dropna().min()
                        if "Tkh SRT Aktiviti Pertama" in df_filter.columns
                        else pd.NaT
                    )
                    ulv_dt = (
                        df_filter["Tkh ULV Aktiviti Pertama"].dropna().min()
                        if "Tkh ULV Aktiviti Pertama" in df_filter.columns
                        else pd.NaT
                    )

                    ptp_badge = (
                        f'<span class="ops-pill-ok">✅ PTP (Larviciding): {fmt_date_short(ptp_dt)}</span>'
                        if pd.notna(ptp_dt)
                        else '<span class="ops-pill-miss">⚠️ PTP (Larviciding): BELUM DIREKOD</span>'
                    )
                    srt_badge = (
                        f'<span class="ops-pill-ok">✅ SRT (Fogging): {fmt_date_short(srt_dt)}</span>'
                        if pd.notna(srt_dt)
                        else '<span class="ops-pill-miss">⚠️ SRT (Fogging): BELUM DIREKOD</span>'
                    )
                    ulv_badge = (
                        f'<span class="ops-pill-ok">✅ ULV: {fmt_date_short(ulv_dt)}</span>'
                        if pd.notna(ulv_dt)
                        else '<span class="ops-pill-miss">ℹ️ ULV: Tiada / Belum Perlu</span>'
                    )
                    st.markdown(
                        f'<div style="display:flex; flex-wrap:wrap; gap:10px; margin: 6px 0 12px 0;">{ptp_badge}{srt_badge}{ulv_badge}</div>',
                        unsafe_allow_html=True,
                    )

                    if (
                        "Tamat" not in status_wabak_semasa
                        and "Satu Kes" not in status_wabak_semasa
                        and (pd.isna(ptp_dt) or pd.isna(srt_dt))
                    ):
                        missing_acts = []
                        if pd.isna(ptp_dt):
                            missing_acts.append("PTP (Pemusnahan Tempat Pembiakan)")
                        if pd.isna(srt_dt):
                            missing_acts.append("SRT (Semburan Ruang Termal)")
                        st.warning(
                            f"🚨 **Amaran Jurang Kawalan Lapangan:** Wabak aktif ini masih belum merekodkan tarikh aktiviti pertama bagi **{', '.join(missing_acts)}**. Tindakan segera diperlukan untuk menyekat rantaian penularan."
                        )

                    # --- 4 KAD METRIK LOKALITI LIQUID-GLASS (DISERAGAMKAN + MOMENTUM 7-HARI) ---
                    kadar_velocity = jumlah_kes / tempoh_wabak_hari
                    t_ref_lok = (
                        df_filter["Tkh Notifikasi"].fillna(df_filter["Tarikh Daftar"])
                        if "Tkh Notifikasi" in df_filter.columns
                        else df_filter["Tarikh Daftar"]
                    )
                    mom_anchor_dt = (
                        t_ref_lok.max()
                        if ("Tamat" in status_wabak_semasa and t_ref_lok.notna().any())
                        else data_ref_date
                    )
                    lok_c7 = int(
                        (
                            (t_ref_lok >= (mom_anchor_dt - pd.Timedelta(days=6)))
                            & (t_ref_lok <= mom_anchor_dt)
                        ).sum()
                    )
                    lok_prev7 = int(
                        (
                            (t_ref_lok >= (mom_anchor_dt - pd.Timedelta(days=13)))
                            & (t_ref_lok <= (mom_anchor_dt - pd.Timedelta(days=7)))
                        ).sum()
                    )
                    lok_mom_pct = ((lok_c7 - lok_prev7) / max(lok_prev7, 1)) * 100
                    lok_mom_disp = (
                        f"+{lok_c7} kes baharu"
                        if (lok_prev7 == 0 and lok_c7 > 0)
                        else f"{lok_mom_pct:+.1f}%"
                    )
                    mom_sub_txt = (
                        f"7H Akhir: <b>{lok_c7}</b> vs 7H Sblm: <b>{lok_prev7}</b> (Episod Tamat)"
                        if "Tamat" in status_wabak_semasa
                        else f"7H Kini: <b>{lok_c7}</b> vs 7H Lalu: <b>{lok_prev7}</b>"
                    )

                    safe_lokaliti = html.escape(str(pilihan_lokaliti))
                    safe_kategori = html.escape(str(pilihan_kategori_aktif))

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(
                            build_glass_kpi_html(
                                label="Jumlah Kes",
                                value_str=str(jumlah_kes),
                                sub_str=f"Rekod Sejarah: <b>{rekod_episode_lokaliti} episod</b>",
                                tooltip_title="📋 Jumlah Kes Terkumpul",
                                relevance_html="Jumlah keseluruhan kes disahkan yang didaftarkan di bawah episod wabak atau kategori yang dipilih.",
                                formula_html="Count(Notifikasi No) bagi pilihan semasa",
                                current_calc_html=f"<b>Lokaliti ({safe_lokaliti}):</b> <b>{jumlah_kes} kes</b> direkodkan bagi {safe_kategori}.",
                            ),
                            unsafe_allow_html=True,
                        )
                    with col2:
                        st.markdown(
                            build_glass_kpi_html(
                                label="Tempoh Wabak (Hari)",
                                value_str=f"{tempoh_wabak_hari} hari",
                                sub_str=f"Mula (Notif Kes ke-2): <b>{tarikh_mula_str}</b>",
                                tooltip_title="⏳ Tempoh Penularan Wabak",
                                relevance_html="Tempoh masa wabak berlangsung bermula dari tarikh notifikasi kes ke-2 (pencetus rasmi wabak) sehingga tarikh semasa atau tarikh tamat rasmi (+14 hari dari notifikasi terakhir).",
                                formula_html="Tarikh Tamat Rasmi (+14h) / Semasa − Tkh Notifikasi Kes ke-2",
                                current_calc_html=f"<b>Pengiraan Semasa:</b> Bermula <b>{tarikh_mula_str}</b> hingga <b>{t_tamat_banner_str}</b> = <b>{tempoh_wabak_hari} hari</b>.",
                            ),
                            unsafe_allow_html=True,
                        )
                    with col3:
                        st.markdown(
                            build_glass_kpi_html(
                                label="Velocity (Kes/Hari)",
                                value_str=f"{kadar_velocity:.2f}",
                                sub_str="Purata kes baharu setiap hari",
                                tooltip_title="🚀 Velocity (Kes/Hari)",
                                relevance_html="Mengukur kelajuan penularan wabak (purata kes baharu sehari). Nilai tinggi (> 1.0 kes/hari) menandakan penularan agresif yang memerlukan kawalan kecemasan segera.",
                                formula_html="Jumlah Kes ÷ Tempoh Wabak (Hari)",
                                current_calc_html=f"<b>Pengiraan Semasa ({safe_lokaliti} — {safe_kategori}):</b><br>{jumlah_kes} kes ÷ {tempoh_wabak_hari} hari = <b>{kadar_velocity:.2f} kes/hari</b>",
                            ),
                            unsafe_allow_html=True,
                        )
                    with col4:
                        st.markdown(
                            build_glass_kpi_html(
                                label="Momentum 7-Hari",
                                value_str=lok_mom_disp,
                                sub_str=mom_sub_txt,
                                tooltip_title="📈 Momentum 7-Hari (7-Day Acceleration)",
                                relevance_html="Mengukur perubahan kes baharu dalam 7 hari terakhir berbanding 7 hari sebelumnya (bagi wabak tamat, diukur pada 14 hari terakhir episod tersebut).",
                                formula_html="((Kes<sub>7H Kini</sub> − Kes<sub>7H Lalu</sub>) ÷ max(Kes<sub>7H Lalu</sub>, 1)) × 100",
                                current_calc_html=f"<b>Pengiraan Semasa ({safe_lokaliti}):</b><br>7H Terkini/Akhir = <b>{lok_c7} kes</b> vs 7H Lalu/Sblm = <b>{lok_prev7} kes</b> (<b>{lok_mom_disp}</b>)",
                                accent_color="#e11d48" if lok_c7 > lok_prev7 else "#059669",
                            ),
                            unsafe_allow_html=True,
                        )

                    st.markdown("---")
minggu_puncak_txt = "Tiada"
                    kes_puncak = 0
                    status_arah_txt = "tidak dapat dipastikan"

                    max_val_specific = -1
                    max_b_specific = "Tidak Dinyatakan"
                    max_t_specific = "Tidak Dinyatakan"
                    blok_masalah_txt = "Tidak Dinyatakan"
                    tingkat_masalah_txt = "Tidak Dinyatakan"

                    # --- KELUK EPIDEMIK DWI-SIRI (MINGGU ONSET VS MINGGU DAFTAR) ---
                    st.subheader(f"📈 Keluk Epidemik Dwi-Siri: Minggu Onset vs Minggu Daftar ({pilihan_kategori_aktif})")
                    kes_epid = df_filter["Epid Minggu (Tkh Daftar)"].dropna().astype(int).value_counts().sort_index()
                    kes_onset_epid = (
                        df_filter["Epid Minggu (Tkh Onset)"].dropna().astype(int).value_counts().sort_index()
                        if "Epid Minggu (Tkh Onset)" in df_filter.columns
                        else pd.Series(dtype=int)
                    )

                    if not kes_epid.empty:
                        all_wks = sorted(list(set(kes_epid.index.tolist()).union(set(kes_onset_epid.index.tolist()))))

                        def build_week_case_hover(sub_df, mode="daftar"):
                            if sub_df.empty:
                                return "Tiada kes pada minggu ini"
                            sort_col = "Tarikh Daftar" if mode == "daftar" else "Tarikh Onset"
                            sub_s = sub_df.sort_values(by=sort_col, ascending=True)
                            grouped_counts = {}
                            for _, r in sub_s.iterrows():
                                d_daf = r["Tarikh Daftar"].strftime("%d/%m/%Y") if pd.notna(r.get("Tarikh Daftar")) else "-"
                                d_not = (
                                    r["Tkh Notifikasi"].strftime("%d/%m/%Y")
                                    if "Tkh Notifikasi" in sub_s.columns and pd.notna(r.get("Tkh Notifikasi"))
                                    else "-"
                                )
                                d_ons = (
                                    r["Tarikh Onset"].strftime("%d/%m/%Y")
                                    if "Tarikh Onset" in sub_s.columns and pd.notna(r.get("Tarikh Onset"))
                                    else "-"
                                )
                                if mode == "daftar":
                                    key = f"• Daftar: <b>{d_daf}</b> | Notif: {d_not}"
                                else:
                                    key = f"• Onset: <b>{d_ons}</b> | Notif: {d_not} | Daftar: {d_daf}"
                                grouped_counts[key] = grouped_counts.get(key, 0) + 1

                            lines = [f"{k} <b>({cnt} kes)</b>" if cnt > 1 else k for k, cnt in grouped_counts.items()]
                            return "<br>".join(lines)

                        daftar_hover_list, onset_hover_list = [], []
                        df_tmp_ep = df_filter.copy()
                        df_tmp_ep["_wk_daf"] = pd.to_numeric(df_tmp_ep["Epid Minggu (Tkh Daftar)"], errors="coerce")
                        df_tmp_ep["_wk_ons"] = (
                            pd.to_numeric(df_tmp_ep["Epid Minggu (Tkh Onset)"], errors="coerce")
                            if "Epid Minggu (Tkh Onset)" in df_tmp_ep.columns
                            else np.nan
                        )

                        for w in all_wks:
                            daftar_hover_list.append(build_week_case_hover(df_tmp_ep[df_tmp_ep["_wk_daf"] == w], mode="daftar"))
                            onset_hover_list.append(build_week_case_hover(df_tmp_ep[df_tmp_ep["_wk_ons"] == w], mode="onset"))

                        df_dual_ep = pd.DataFrame({
                            "Minggu Epid": [f"ME {int(w):02d}" for w in all_wks],
                            "Kes Mengikut Minggu Daftar": [int(kes_epid.get(w, 0)) for w in all_wks],
                            "Kes Mengikut Minggu Onset (Gejala)": [int(kes_onset_epid.get(w, 0)) for w in all_wks],
                            "Hover_Daftar": daftar_hover_list,
                            "Hover_Onset": onset_hover_list,
                        })

                        fig_epid = go.Figure()
                        fig_epid.add_trace(go.Bar(
                            x=df_dual_ep["Minggu Epid"],
                            y=df_dual_ep["Kes Mengikut Minggu Daftar"],
                            name="Minggu Daftar",
                            marker_color="rgba(244, 63, 94, 0.78)",
                            text=df_dual_ep["Kes Mengikut Minggu Daftar"],
                            textposition="outside",
                            customdata=df_dual_ep["Hover_Daftar"],
                            hovertemplate="<b>%{x} — Minggu Daftar: %{y} Kes</b><br>%{customdata}<extra></extra>",
                        ))
                        fig_epid.add_trace(go.Scatter(
                            x=df_dual_ep["Minggu Epid"],
                            y=df_dual_ep["Kes Mengikut Minggu Onset (Gejala)"],
                            name="Minggu Onset (Mula Gejala)",
                            mode="lines+markers",
                            line=dict(color="#0284c7", width=3),
                            marker=dict(size=8, symbol="circle"),
                            customdata=df_dual_ep["Hover_Onset"],
                            hovertemplate="<b>%{x} — Minggu Onset: %{y} Kes</b><br>%{customdata}<extra></extra>",
                        ))
                        fig_epid.update_xaxes(type="category")
                        fig_epid.update_layout(
                            xaxis_title="Minggu Epid (Arah kursor pada bar/titik untuk tarikh tepat setiap kes)",
                            yaxis_title="Jumlah Kes",
                            height=360,
                            paper_bgcolor="rgba(255,255,255,0.75)",
                            plot_bgcolor="rgba(255,255,255,0.55)",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                        )
                        st.plotly_chart(fig_epid, use_container_width=True, key="graf_minggu_epid")

                        minggu_puncak_txt = str(int(kes_epid.idxmax()))
                        kes_puncak = int(kes_epid.max())
                        purata_mingguan = kes_epid.mean()

                        ulasan_epid = "**Analisis Terperinci Keluk Epidemik:**\n"
                        ulasan_epid += f"- **Beban & Puncak Pendaftaran:** Purata **{purata_mingguan:.1f} kes/minggu aktif**, dengan puncak pendaftaran pada **Minggu Epid {minggu_puncak_txt}** (**{kes_puncak} kes**).\n"

                        if not kes_onset_epid.empty:
                            puncak_onset_wk = int(kes_onset_epid.idxmax())
                            puncak_onset_cnt = int(kes_onset_epid.max())
                            last_onset_wk = int(kes_onset_epid.index.max())
                            last_onset_cnt = int(kes_onset_epid.iloc[-1])
                            last_onset_dt = df_filter["Tarikh Onset"].dropna().max() if "Tarikh Onset" in df_filter.columns else pd.NaT
                            last_onset_dt_str = last_onset_dt.strftime("%d/%m/%Y") if pd.notna(last_onset_dt) else "-"
                            ulasan_epid += f"- **Penularan Sebenar (Onset Gejala):** Kemuncak jangkitan sebenar berlaku pada **Minggu Epid {puncak_onset_wk}** (**{puncak_onset_cnt} kes**), dengan gejala terbaharu dikesan pada **Minggu Epid {last_onset_wk}** (**{last_onset_cnt} kes**, tarikh onset terakhir: **{last_onset_dt_str}**).\n"

                        if len(kes_epid) >= 2:
                            m_kini, m_lalu = kes_epid.iloc[-1], kes_epid.iloc[-2]
                            perbezaan = m_kini - m_lalu
                            status_arah_txt = "meningkat" if perbezaan > 0 else ("menurun" if perbezaan < 0 else "mendatar")
                            ulasan_epid += f"- **Arah Trend Mingguan:** Pendaftaran minggu terakhir menunjukkan trend **{status_arah_txt}** (**{m_kini} kes** vs **{m_lalu} kes** minggu sebelumnya).\n"

                        if "Tarikh Onset" in df_filter.columns and "Tkh Notifikasi" in df_filter.columns:
                            lag_on_not = (df_filter["Tkh Notifikasi"] - df_filter["Tarikh Onset"]).dt.days
                            lag_valid = lag_on_not[(lag_on_not >= 0) & (lag_on_not <= 45)].dropna()
                            if not lag_valid.empty:
                                ulasan_epid += f"- **Jurang Lengah Epidemiologi (Onset → Notifikasi):** Median **{lag_valid.median():.1f} hari** (maksimum **{int(lag_valid.max())} hari**). Jurang ini menjelaskan perbezaan fasa antara garisan biru (*Onset*) dan bar merah (*Daftar*)."

                        st.info(ulasan_epid)

                    st.markdown("---")

                    # --- TABURAN BLOK & TINGKAT (ATAU PETA JALAN KEDIAMAN BERTANAH) ---
                    st.subheader("🏢 Taburan Kes Mengikut Blok dan Tingkat")
                    df_filter[["Blok", "Tingkat"]] = df_filter["No Rumah"].apply(parse_address)
                    is_highrise = len(df_filter["Blok"].unique()) > 1 or "TIDAK PASTI" not in df_filter["Blok"].values

                    if is_highrise:
                        crosstab_bt = pd.crosstab(df_filter["Tingkat"], df_filter["Blok"], margins=True, margins_name="JUMLAH")

                        def pad_for_sort(s):
                            return re.sub(r"\d+", lambda m: m.group(0).zfill(5), str(s))

                        tingkat_sorted = sorted(list(crosstab_bt.index[:-1]), key=pad_for_sort, reverse=True)
                        blok_sorted = sorted(list(crosstab_bt.columns[:-1]), key=pad_for_sort)
                        crosstab_bt = crosstab_bt.loc[tingkat_sorted + ["JUMLAH"], blok_sorted + ["JUMLAH"]]

                        data_matrix = crosstab_bt.iloc[:-1, :-1]
                        global_max_cell = max(int(data_matrix.values.max()) if not data_matrix.empty else 1, 1)

                        def get_heat_colors(val, g_max):
                            if val <= 0:
                                return "#ffffff", "#64748b"
                            ratio = val / g_max
                            if ratio >= 0.85:
                                return "#7f1d1d", "#ffffff"
                            if ratio >= 0.65:
                                return "#b91c1c", "#ffffff"
                            if ratio >= 0.45:
                                return "#ef4444", "#ffffff"
                            if ratio >= 0.25:
                                return "#fca5a5", "#0f172a"
                            return "#fee2e2", "#0f172a"

                        def build_cell_patient_bubble(sub_p, blok_lbl, tingkat_lbl):
                            sub_s = sub_p.sort_values(by="Tarikh Daftar", ascending=False)
                            cards = []
                            for idx_p, (_, rp) in enumerate(sub_s.iterrows(), start=1):
                                no_rmh = html.escape(str(rp.get("No Rumah", "-")).strip())
                                umur_v = rp.get("Umur (Tahun)", "-")
                                umur_str = f"{int(float(umur_v))} thn" if pd.notna(umur_v) and str(umur_v).replace(".", "", 1).isdigit() else "-"
                                jantina = html.escape(str(rp.get("Jantina", "")).strip()) if "Jantina" in sub_s.columns and pd.notna(rp.get("Jantina")) else ""
                                demo_age = f"{umur_str} ({jantina})" if jantina else umur_str
                                warga = html.escape(str(rp.get("Status Kewarganegaraan", "-")).strip()) if "Status Kewarganegaraan" in sub_s.columns and pd.notna(rp.get("Status Kewarganegaraan")) else "-"
                                kerja = html.escape(str(rp.get("Pekerjaan", "-")).strip()) if "Pekerjaan" in sub_s.columns and pd.notna(rp.get("Pekerjaan")) else "-"
                                d_ons = rp["Tarikh Onset"].strftime("%d/%m/%Y") if "Tarikh Onset" in sub_s.columns and pd.notna(rp.get("Tarikh Onset")) else "-"
                                d_not = rp["Tkh Notifikasi"].strftime("%d/%m/%Y") if "Tkh Notifikasi" in sub_s.columns and pd.notna(rp.get("Tkh Notifikasi")) else "-"
                                d_daf = rp["Tarikh Daftar"].strftime("%d/%m/%Y") if "Tarikh Daftar" in sub_s.columns and pd.notna(rp.get("Tarikh Daftar")) else "-"
                                rawat = (
                                    html.escape(str(rp.get("Tempat Rawatan(Maklumat Pemberitahu)", "-")).strip())
                                    if "Tempat Rawatan(Maklumat Pemberitahu)" in sub_s.columns and pd.notna(rp.get("Tempat Rawatan(Maklumat Pemberitahu)"))
                                    else "-"
                                )
                                u_rapid = str(rp.get("Ujian Rapid", "")) if "Ujian Rapid" in sub_s.columns else ""
                                u_elisa = str(rp.get("Ujian ELISA", "")) if "Ujian ELISA" in sub_s.columns else ""
                                ns1_tag = (
                                    " <span style='background:#ef4444;color:#fff;padding:1px 5px;border-radius:4px;font-size:0.7rem;'>NS1+</span>"
                                    if ("NS1 POSITIF" in u_rapid.upper() or "NS1 POSITIF" in u_elisa.upper())
                                    else ""
                                )
                                cards.append(
                                    f"<div style='background:rgba(255,255,255,0.07);border-left:3px solid #38bdf8;border-radius:6px;padding:6px 8px;margin-bottom:6px;'>"
                                    f"<div style='font-weight:700;color:#fde68a;margin-bottom:2px;'>#{idx_p} • Unit: {no_rmh}{ns1_tag}</div>"
                                    f"<div><b>Umur:</b> {demo_age} • <b>Warganegara:</b> {warga}</div>"
                                    f"<div><b>Pekerjaan:</b> {kerja}</div>"
                                    f"<div><b>Onset:</b> {d_ons} • <b>Notif:</b> {d_not} • <b>Daftar:</b> {d_daf}</div>"
                                    f"<div style='color:#cbd5e1;font-size:0.76rem;'><b>Rawatan:</b> {rawat}</div></div>"
                                )
                            return (
                                f'<div class="ai-tooltip-bubble">'
                                f'<div class="tooltip-title">🏢 Blok {html.escape(str(blok_lbl))}, Tingkat {html.escape(str(tingkat_lbl))} ({len(sub_s)} Kes)</div>'
                                f'<div class="tooltip-section">{"".join(cards)}</div></div>'
                            )

                        hdr_cols = "".join(
                            f'<th style="background:#f1f5f9;color:#0f172a;font-weight:700;padding:7px 10px;border:1px solid #cbd5e1;">{html.escape(str(c))}</th>'
                            for c in crosstab_bt.columns
                        )
                        body_rows = []
                        for t_lbl in crosstab_bt.index:
                            is_total_row = t_lbl == "JUMLAH"
                            row_bg = "#f8fafc" if is_total_row else "#ffffff"
                            fw_row = "700" if is_total_row else "600"
                            tds = [f'<td style="background:{row_bg};color:#0f172a;font-weight:{fw_row};text-align:left;padding:6px 10px;border:1px solid #e2e8f0;">{html.escape(str(t_lbl))}</td>']
                            for b_lbl in crosstab_bt.columns:
                                val = int(crosstab_bt.loc[t_lbl, b_lbl])
                                if is_total_row or b_lbl == "JUMLAH":
                                    tds.append(f'<td style="background:#f8fafc;color:#0f172a;font-weight:700;text-align:center;padding:6px 10px;border:1px solid #e2e8f0;">{val}</td>')
                                elif val > 0:
                                    bg_c, fg_c = get_heat_colors(val, global_max_cell)
                                    sub_p = df_filter[(df_filter["Blok"] == b_lbl) & (df_filter["Tingkat"] == t_lbl)]
                                    bubble_html = build_cell_patient_bubble(sub_p, b_lbl, t_lbl)
                                    tds.append(
                                        f'<td class="ai-hover-card" style="background:{bg_c};color:{fg_c};font-weight:700;text-align:center;padding:6px 10px;border:1px solid #e2e8f0;border-radius:0;margin:0;box-shadow:none;cursor:pointer;">{val}{bubble_html}</td>'
                                    )
                                else:
                                    tds.append('<td style="background:#ffffff;color:#94a3b8;text-align:center;padding:6px 10px;border:1px solid #e2e8f0;">0</td>')
                            body_rows.append(f"<tr>{''.join(tds)}</tr>")

                        bt_table_html = (
                            '<div style="overflow-x:auto;background:rgba(255,255,255,0.92);border-radius:14px;padding:8px;border:1px solid #e2e8f0;box-shadow:0 6px 20px rgba(15,23,42,0.05);">'
                            '<div style="font-size:0.78rem;color:#475569;margin-bottom:6px;">💡 <i>Arahkan kursor pada mana-mana sel berwarna (>0 kes) untuk melihat senarai penuh profil pesakit (boleh skrol di dalam gelembung).</i></div>'
                            '<table style="width:100%;border-collapse:collapse;font-size:0.86rem;">'
                            f'<thead><tr><th style="background:#f1f5f9;color:#0f172a;font-weight:700;padding:7px 10px;border:1px solid #cbd5e1;text-align:left;">Tingkat \\ Blok</th>{hdr_cols}</tr></thead>'
                            f'<tbody>{"".join(body_rows)}</tbody></table></div>'
                        )
                        st.markdown(bt_table_html, unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)

                        tied_hotspots = []
                        for t in crosstab_bt.index[:-1]:
                            for b in crosstab_bt.columns[:-1]:
                                v_cell = int(crosstab_bt.loc[t, b])
                                if v_cell > max_val_specific:
                                    max_val_specific = v_cell
                                    max_b_specific, max_t_specific = str(b), str(t)
                                    tied_hotspots = [(str(b), str(t))]
                                elif v_cell == max_val_specific and v_cell > 0:
                                    tied_hotspots.append((str(b), str(t)))

                        blok_totals = crosstab_bt.loc["JUMLAH"][:-1]
                        if not blok_totals.empty and blok_totals.max() > 0:
                            blok_masalah_txt = str(blok_totals.idxmax())

                        tingkat_totals = crosstab_bt.iloc[:-1]["JUMLAH"]
                        if not tingkat_totals.empty and tingkat_totals.max() > 0:
                            tingkat_masalah_txt = str(tingkat_totals.idxmax())

                        if max_val_specific > 0:
                            hotspot_lbls = " & ".join(f"**Blok {b}, Tingkat {t}**" for b, t in tied_hotspots)
                            st.warning(
                                f"⚠️ **Sarang Penularan Spesifik:** Takungan vektor berjangkit (hotspot selular) dipercayai tertumpu secara spesifik di kediaman {hotspot_lbls} yang menyumbang **{max_val_specific} kes**{' setiap satu' if len(tied_hotspots) > 1 else ''}. Operasi pemusnahan sumber (S&D) dan semburan ruang disarankan untuk difokuskan bermula dari struktur radius ini terlebih dahulu sebelum diperluas ke tempat lain."
                            )

                        st.markdown("##### **Perincian Struktur (Keseluruhan Blok & Tingkat):**")
                        blok_group_raw = df_filter[df_filter["Blok"] != "TIDAK PASTI"].groupby("Blok").size()
                        if not blok_group_raw.empty:
                            for blok_name in sorted(blok_group_raw.index, key=pad_for_sort):
                                b_count = blok_group_raw[blok_name]
                                st.markdown(f"**🔹 Blok {blok_name}: {b_count} kes ({(b_count / jumlah_kes) * 100:.1f}% dari keseluruhan wabak)**")
                                df_blok_ini = df_filter[(df_filter["Blok"] == blok_name) & (df_filter["Tingkat"] != "TIDAK PASTI")]
                                if not df_blok_ini.empty:
                                    tingkat_group_raw = df_blok_ini.groupby("Tingkat").size()
                                    for tk_name in sorted(tingkat_group_raw.index, key=pad_for_sort, reverse=True):
                                        t_count = tingkat_group_raw[tk_name]
                                        st.write(f"    🔸 Tingkat {tk_name}: {t_count} kes ({(t_count / jumlah_kes) * 100:.1f}%)")
                        else:
                            st.write("Maklumat blok tidak cukup berstruktur.")
                    else:
                        st.markdown("#### 🏡 Peta Jalan / Lorong & Kluster Kediaman Bertanah (Landed Locality)")
                        st.caption("Lokaliti ini dikesan sebagai kawasan kediaman bertanah (tiada struktur Blok/Tingkat). Paparan automatik beralih kepada pemetaan GPS aras jalan (Zoom 17–18, radius 50m & 200m KKM) serta pecahan mengikut Jalan/Lorong.")

                        def extract_street_name(row):
                            addr_parts = [str(row[c]).strip() for c in ["No Rumah", "Alamat Semasa", "Nama Jalan", "Alamat"] if c in row.index and pd.notna(row[c])]
                            full_txt = " ".join(addr_parts).upper()
                            m_st = re.search(r"\b((?:JALAN|JLN|LORONG|LRG|PERSIARAN|PSRN|LEBUH|LENGKOK|TAMAN|TMN)\s+[A-Z0-9/\-\s]{2,40})", full_txt)
                            if m_st:
                                st_clean = re.split(r",|\b(?:CHERAS|KUALA LUMPUR|AMPANG|SELANGOR|\d{5})\b", m_st.group(1))[0].strip(" ,.-")
                                if st_clean:
                                    return st_clean
                            no_r = str(row.get("No Rumah", "-")).strip()
                            return no_r if no_r and no_r.upper() != "NAN" else "ALAMAT TIDAK DINYATAKAN"

                        df_land = df_filter.copy()
                        df_land["_Jalan"] = df_land.apply(extract_street_name, axis=1)

                        if "Latitud (ISO)" in df_land.columns and "Lngitud (ISO)" in df_land.columns:
                            df_land["_lat"] = pd.to_numeric(df_land["Latitud (ISO)"], errors="coerce")
                            df_land["_lng"] = pd.to_numeric(df_land["Lngitud (ISO)"], errors="coerce")
                            df_gps_land = df_land[(df_land["_lat"] > 1.0) & (df_land["_lat"] < 8.0) & (df_land["_lng"] > 99.0) & (df_land["_lng"] < 120.0)].copy()
                        else:
                            df_gps_land = pd.DataFrame()

                        col_l_map, col_l_tbl = st.columns([1.35, 1.0])

                        with col_l_map:
                            if not df_gps_land.empty:
                                c_lat, c_lng = float(df_gps_land["_lat"].median()), float(df_gps_land["_lng"].median())
                                t_ref_l = df_gps_land["Tkh Notifikasi"].fillna(df_gps_land["Tarikh Daftar"]) if "Tkh Notifikasi" in df_gps_land.columns else df_gps_land["Tarikh Daftar"]
                                max_dt_l = t_ref_l.max() if t_ref_l.notna().any() else data_ref_date

                                markers_payload = []
                                for _, r_g in df_gps_land.iterrows():
                                    dt_case = r_g["Tkh Notifikasi"] if "Tkh Notifikasi" in df_gps_land.columns and pd.notna(r_g.get("Tkh Notifikasi")) else r_g.get("Tarikh Daftar")
                                    age_days = int((max_dt_l - dt_case).days) if pd.notna(dt_case) else 99
                                    if age_days <= 7:
                                        pin_col, rec_lbl = "#dc2626", "Terkini (≤7 hari)"
                                    elif age_days <= 14:
                                        pin_col, rec_lbl = "#f97316", "Aktif (8–14 hari)"
                                    else:
                                        pin_col, rec_lbl = "#2563eb", "Terdahulu (>14 hari)"

                                    no_rmh = html.escape(str(r_g.get("No Rumah", "-")).strip())
                                    umur_v = r_g.get("Umur (Tahun)", "-")
                                    umur_s = f"{int(float(umur_v))} thn" if pd.notna(umur_v) and str(umur_v).replace(".", "", 1).isdigit() else "-"
                                    warga_s = html.escape(str(r_g.get("Status Kewarganegaraan", "-")).strip())
                                    kerja_s = html.escape(str(r_g.get("Pekerjaan", "-")).strip())
                                    d_ons = r_g["Tarikh Onset"].strftime("%d/%m/%Y") if "Tarikh Onset" in df_gps_land.columns and pd.notna(r_g.get("Tarikh Onset")) else "-"
                                    d_daf = r_g["Tarikh Daftar"].strftime("%d/%m/%Y") if pd.notna(r_g.get("Tarikh Daftar")) else "-"
                                    u_r, u_e = str(r_g.get("Ujian Rapid", "")), str(r_g.get("Ujian ELISA", ""))
                                    ns1_b = " <span style='background:#ef4444;color:#fff;padding:1px 5px;border-radius:4px;font-size:10px;'>NS1+</span>" if ("NS1 POSITIF" in u_r.upper() or "NS1 POSITIF" in u_e.upper()) else ""
                                    popup_html = (
                                        f"<div style='font-family:Inter,sans-serif;font-size:12px;line-height:1.45;'>"
                                        f"<div style='font-weight:700;color:#0f172a;margin-bottom:3px;'>🏡 {no_rmh}{ns1_b}</div>"
                                        f"<div><b>Status Masa:</b> <span style='color:{pin_col};font-weight:700;'>{rec_lbl}</span></div>"
                                        f"<div><b>Umur:</b> {umur_s} • <b>Warganegara:</b> {warga_s}</div>"
                                        f"<div><b>Pekerjaan:</b> {kerja_s}</div>"
                                        f"<div><b>Onset:</b> {d_ons} • <b>Daftar:</b> {d_daf}</div></div>"
                                    )
                                    markers_payload.append({"lat": float(r_g["_lat"]), "lng": float(r_g["_lng"]), "color": pin_col, "popup": popup_html})

                                markers_json = json.dumps(markers_payload)
                                leaflet_html = f"""
                                <!DOCTYPE html>
                                <html>
                                <head>
                                    <meta charset="utf-8" />
                                    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
                                    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                                    <style>
                                        html, body, #landed-map {{ margin: 0; padding: 0; width: 100%; height: 420px; border-radius: 14px; font-family: Inter, sans-serif; }}
                                        .legend-box {{ background: rgba(255,255,255,0.92); padding: 6px 10px; border-radius: 8px; font-size: 11px; line-height: 1.5; box-shadow: 0 2px 8px rgba(0,0,0,0.18); }}
                                    </style>
                                </head>
                                <body>
                                    <div id="landed-map"></div>
                                    <script>
                                        const map = L.map('landed-map', {{ zoomControl: true }}).setView([{c_lat}, {c_lng}], 17);
                                        const osm = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ maxZoom: 19, attribution: '© OpenStreetMap' }}).addTo(map);
                                        const sat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{ maxZoom: 19, attribution: 'Tiles © Esri' }});
                                        L.control.layers({{ "🗺️ Peta Jalan (OSM)": osm, "🛰️ Satelit (Esri)": sat }}).addTo(map);
                                        L.circle([{c_lat}, {c_lng}], {{ radius: 200, color: '#dc2626', weight: 1.8, dashArray: '6,6', fillColor: '#ef4444', fillOpacity: 0.06 }}).addTo(map).bindTooltip('Radius Kawalan KKM 200m');
                                        L.circle([{c_lat}, {c_lng}], {{ radius: 50, color: '#f97316', weight: 1.5, dashArray: '3,4', fillColor: '#fb923c', fillOpacity: 0.10 }}).addTo(map).bindTooltip('Zon Teras 50m');
                                        const pts = {markers_json};
                                        const bounds = [];
                                        pts.forEach(p => {{
                                            const m = L.circleMarker([p.lat, p.lng], {{ radius: 8, fillColor: p.color, color: '#ffffff', weight: 2, opacity: 1, fillOpacity: 0.92 }}).addTo(map);
                                            m.bindPopup(p.popup, {{ maxWidth: 280 }});
                                            m.bindTooltip(p.popup, {{ direction: 'top', opacity: 0.96 }});
                                            bounds.push([p.lat, p.lng]);
                                        }});
                                        if (bounds.length > 1) {{ map.fitBounds(bounds, {{ padding: [36, 36], maxZoom: 18 }}); }}
                                        const legend = L.control({{ position: 'bottomleft' }});
                                        legend.onAdd = function() {{
                                            const div = L.DomUtil.create('div', 'legend-box');
                                            div.innerHTML = '<b>Petunjuk Kes (GPS):</b><br><span style="color:#dc2626;">●</span> Terkini (≤7 hari)<br><span style="color:#f97316;">●</span> Aktif (8–14 hari)<br><span style="color:#2563eb;">●</span> Terdahulu (>14 hari)<br><span style="color:#dc2626;">---</span> Radius 200m / 50m KKM';
                                            return div;
                                        }};
                                        legend.addTo(map);
                                    </script>
                                </body>
                                </html>
                                """
                                components.html(leaflet_html, height=430)
                                st.link_button(
                                    "📍 Buka Lokasi Kluster di Google Maps (Navigasi Lapangan)",
                                    url=f"https://www.google.com/maps?q={c_lat:.6f},{c_lng:.6f}",
                                    use_container_width=True,
                                )
                            else:
                                st.info("Koordinat GPS sah tidak ditemui bagi episod ini untuk memaparkan peta jalan.")

                        with col_l_tbl:
                            st_counts = df_land.groupby("_Jalan").size().sort_values(ascending=False)
                            st_rows_html = []
                            for st_name, cnt_st in st_counts.items():
                                sub_st = df_land[df_land["_Jalan"] == st_name].sort_values(by="Tarikh Daftar", ascending=False)
                                p_cards = []
                                for idx_s, (_, rs) in enumerate(sub_st.iterrows(), start=1):
                                    no_r_s = html.escape(str(rs.get("No Rumah", "-")).strip())
                                    um_v = rs.get("Umur (Tahun)", "-")
                                    um_s = f"{int(float(um_v))} thn" if pd.notna(um_v) and str(um_v).replace(".", "", 1).isdigit() else "-"
                                    wg_s = html.escape(str(rs.get("Status Kewarganegaraan", "-")).strip())
                                    kj_s = html.escape(str(rs.get("Pekerjaan", "-")).strip())
                                    d_o = rs["Tarikh Onset"].strftime("%d/%m/%Y") if "Tarikh Onset" in sub_st.columns and pd.notna(rs.get("Tarikh Onset")) else "-"
                                    d_d = rs["Tarikh Daftar"].strftime("%d/%m/%Y") if pd.notna(rs.get("Tarikh Daftar")) else "-"
                                    p_cards.append(
                                        f"<div style='background:rgba(255,255,255,0.07);border-left:3px solid #38bdf8;border-radius:6px;padding:6px 8px;margin-bottom:6px;'>"
                                        f"<div style='font-weight:700;color:#fde68a;'>#{idx_s} • {no_r_s}</div>"
                                        f"<div><b>Umur:</b> {um_s} • <b>Warganegara:</b> {wg_s}</div>"
                                        f"<div><b>Pekerjaan:</b> {kj_s}</div>"
                                        f"<div><b>Onset:</b> {d_o} • <b>Daftar:</b> {d_d}</div></div>"
                                    )
                                st_bubble = (
                                    f'<div class="ai-tooltip-bubble">'
                                    f'<div class="tooltip-title">🛣️ {html.escape(str(st_name))} ({int(cnt_st)} Kes)</div>'
                                    f'<div class="tooltip-section">{"".join(p_cards)}</div></div>'
                                )
                                pct_st = (cnt_st / max(len(df_land), 1)) * 100
                                st_rows_html.append(
                                    f'<tr><td class="ai-hover-card" style="text-align:left;padding:6px 8px;border:1px solid #e2e8f0;border-radius:0;margin:0;box-shadow:none;background:#fff;cursor:pointer;font-weight:600;">{html.escape(str(st_name))}{st_bubble}</td>'
                                    f'<td style="text-align:center;padding:6px 8px;border:1px solid #e2e8f0;font-weight:700;color:#b91c1c;">{int(cnt_st)}</td>'
                                    f'<td style="text-align:right;padding:6px 8px;border:1px solid #e2e8f0;">{pct_st:.1f}%</td></tr>'
                                )

                            land_tbl_html = (
                                '<div style="background:rgba(255,255,255,0.92);border-radius:14px;padding:10px;border:1px solid #e2e8f0;box-shadow:0 6px 20px rgba(15,23,42,0.05);">'
                                '<div style="font-weight:700;font-size:0.9rem;margin-bottom:4px;">🛣️ Pecahan Kes Mengikut Jalan / Lorong</div>'
                                '<div style="font-size:0.76rem;color:#475569;margin-bottom:6px;">💡 <i>Arahkan kursor pada nama jalan untuk senarai penuh pesakit (boleh skrol).</i></div>'
                                '<table style="width:100%;border-collapse:collapse;font-size:0.83rem;">'
                                '<thead><tr><th style="background:#f1f5f9;padding:6px 8px;border:1px solid #cbd5e1;text-align:left;">Jalan / Lorong / No. Rumah</th>'
                                '<th style="background:#f1f5f9;padding:6px 8px;border:1px solid #cbd5e1;width:54px;">Kes</th>'
                                '<th style="background:#f1f5f9;padding:6px 8px;border:1px solid #cbd5e1;width:62px;">%</th></tr></thead>'
                                f'<tbody>{"".join(st_rows_html)}</tbody></table></div>'
                            )
                            st.markdown(land_tbl_html, unsafe_allow_html=True)

                            if not st_counts.empty:
                                top_st_name, top_st_cnt = str(st_counts.index[0]), int(st_counts.iloc[0])
                                blok_masalah_txt = top_st_name
                                st.warning(
                                    f"⚠️ **Tumpuan Jalan Utama:** Kes paling banyak tertumpu di **{top_st_name}** (**{top_st_cnt} kes**). Fokuskan operasi PTP/S&D (longkang, lorong belakang, premis kosong) serta SRT dalam radius 200m dari jalan ini."
                                )

                    st.markdown("---")

                    # --- 5 KES TERKINI DENGAN LOKASI ---
                    st.subheader("📍 Analisis 5 Kes Terkini")
                    top5_daftar = df_filter.sort_values(by="Tarikh Daftar", ascending=False).head(5)
                    top5_onset = df_filter.sort_values(by="Tarikh Onset", ascending=False).head(5)
                    common_indices = set(top5_daftar.index).intersection(set(top5_onset.index))

                    def highlight_common(row):
                        return ["background-color: #ffd700; color: black" if row.name in common_indices else "" for _ in row]

                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        st.markdown("**Berdasarkan Tarikh Daftar (Terkini)**")
                        st.markdown(top5_daftar[["Tarikh Daftar", "No Rumah", "Blok", "Tingkat"]].style.apply(highlight_common, axis=1).to_html(), unsafe_allow_html=True)
                    with col_t2:
                        st.markdown("**Berdasarkan Tarikh Onset (Terkini)**")
                        st.markdown(top5_onset[["Tarikh Onset", "No Rumah", "Blok", "Tingkat"]].style.apply(highlight_common, axis=1).to_html(), unsafe_allow_html=True)

                    st.markdown("<br>**Ulasan Terperinci Kes Terkini:**", unsafe_allow_html=True)

                    def fmt_case_loc(x):
                        if x["Blok"] == "TIDAK PASTI" and x["Tingkat"] == "TIDAK PASTI":
                            return str(x.get("No Rumah", "Tidak Dinyatakan")).strip()
                        return f"Blok {x['Blok']} Tingkat {x['Tingkat']}"

                    daftar_locs = top5_daftar.apply(fmt_case_loc, axis=1).tolist()
                    onset_locs = top5_onset.apply(fmt_case_loc, axis=1).tolist()

                    st.write(f"- **Pendaftaran Terkini:** 5 kes terakhir bertumpu di **{', '.join(daftar_locs)}**.")
                    st.write(f"- **Gejala (Onset) Terbaharu:** 5 pesakit terbaharu dikesan menetap di **{', '.join(onset_locs)}**.")

                    if common_indices:
                        st.info(f"💡 Terdapat **{len(common_indices)} kes (diwarnakan kuning)** yang saling bertindih di antara Pendaftaran Terkini dan Onset Terkini, menandakan penularan sangat aktif dan baru (fresh outbreak) sedang berlaku.")
                    else:
                        st.info("💡 Tiada pertindihan ketara dikesan di antara kes onset terkini dan pendaftaran terkini. Pendaftaran terkini berkemungkinan melibatkan kes tertangguh dari minggu sebelumnya.")

                    st.markdown("---")

                    # --- PROFIL KLINIKAL, UJIAN MAKMAL & DEMOGRAFI ---
                    st.subheader("🩺 Profil Klinikal, Makmal & Demografi Pesakit")
                    c_clin1, c_clin2 = st.columns(2)

                    with c_clin1:
                        st.markdown("**🏥 Tempat Rawatan & Diagnosis Klinikal**")
                        if "Tempat Rawatan(Maklumat Pemberitahu)" in df_filter.columns:
                            for r_place, cnt in df_filter["Tempat Rawatan(Maklumat Pemberitahu)"].value_counts().items():
                                st.write(f"- **{r_place}**: {cnt} ({(cnt / jumlah_kes) * 100:.1f}%)")
                        if "Sub Diagnosis" in df_filter.columns:
                            diag_str = ", ".join(f"{d}: {c}" for d, c in df_filter["Sub Diagnosis"].value_counts().items())
                            st.write(f"- **Sub Diagnosis:** {diag_str}")

                    with c_clin2:
                        st.markdown("**🧪 Pengesanan Makmal (NS1 / IgM / IgG)**")
                        ns1_r = df_filter["Ujian Rapid"].astype(str).str.contains("NS1 Positif", case=False, na=False) if "Ujian Rapid" in df_filter.columns else pd.Series(False, index=df_filter.index)
                        ns1_e = df_filter["Ujian ELISA"].astype(str).str.contains("NS1 Positif", case=False, na=False) if "Ujian ELISA" in df_filter.columns else pd.Series(False, index=df_filter.index)
                        ns1_tot = int((ns1_r | ns1_e).sum())
                        ns1_pct = (ns1_tot / jumlah_kes) * 100 if jumlah_kes > 0 else 0
                        st.write(f"- **NS1 Antigen Positif (Viremia Aktif):** **{ns1_tot}/{jumlah_kes} kes ({ns1_pct:.1f}%)**")
                        if "Umur (Tahun)" in df_filter.columns:
                            ages = pd.to_numeric(df_filter["Umur (Tahun)"], errors="coerce").dropna()
                            if not ages.empty:
                                st.write(f"- **Julat Umur Pesakit:** Median **{ages.median():.0f} tahun** (Min {ages.min():.0f} – Maks {ages.max():.0f} tahun)")

                    st.markdown("<br>", unsafe_allow_html=True)
                    c_info1, c_info2, c_info3 = st.columns(3)

                    fasiliti_utama_txt, top_warga, top_pekerjaan = "Tidak Dinyatakan", "Tidak Dinyatakan", "Tidak Dinyatakan"

                    with c_info1:
                        st.markdown("**Kemudahan Kesihatan**")
                        fasiliti_count = df_filter["Kemudahan Kesihatan(Maklumat Pemberitahu)"].value_counts()
                        if not fasiliti_count.empty:
                            fasiliti_utama_txt = fasiliti_count.index[0]
                        for f, count in fasiliti_count.items():
                            st.write(f"- **{f}**: {count} ({(count / jumlah_kes) * 100:.1f}%)")

                    with c_info2:
                        st.markdown("**Kewarganegaraan**")
                        warga_count = df_filter["Status Kewarganegaraan"].value_counts()
                        if not warga_count.empty:
                            top_warga = warga_count.index[0]
                        for w, count in warga_count.items():
                            st.write(f"- **{w}**: {count} ({(count / jumlah_kes) * 100:.1f}%)")

                    with c_info3:
                        st.markdown("**Pekerjaan**")
                        kerja_count = df_filter["Pekerjaan"].value_counts()
                        if not kerja_count.empty:
                            top_pekerjaan = kerja_count.index[0]
                        for k, count in kerja_count.items():
                            st.write(f"- **{k}**: {count} ({(count / jumlah_kes) * 100:.1f}%)")

                    st.markdown("---")

                    # --- KESIMPULAN & RUMUSAN AI KESELURUHAN ---
                    st.header("📝 Kesimpulan & Rumusan Eksekutif Lokaliti")
                    zon_bahaya_semasa = list(dict.fromkeys(onset_locs))
                    zon_str = ", ".join(zon_bahaya_semasa) if zon_bahaya_semasa else "Tidak Dinyatakan"

                    if is_highrise:
                        ayat_hotspot = f"Titik jangkitan tertumpu secara kritikal disahkan berada pada Blok {max_b_specific} Tingkat {max_t_specific}." if max_b_specific != "Tidak Dinyatakan" else ""
                        butiran_struktur = f"Secara kumulatif, **Blok {blok_masalah_txt}** adalah kawasan yang mencatatkan jumlah pesakit teramai manakala takungan penyakit paling banyak dikesan berkumpul di **Tingkat {tingkat_masalah_txt}**. {ayat_hotspot}"
                        fokus_saringan = f"keseluruhan **Blok {blok_masalah_txt}**"
                    else:
                        butiran_struktur = f"Lokaliti kediaman bertanah ini menunjukkan tumpuan kes utama di sepanjang **{blok_masalah_txt}** dalam lingkungan radius operasi 200m KKM."
                        fokus_saringan = f"jajaran **{blok_masalah_txt}** (radius 200m)"

                    kesimpulan_ai = f"""
                    Berdasarkan data harian terkini bagi **{pilihan_lokaliti}** ({pilihan_kategori_aktif} - **{status_wabak_semasa}**):
                    
                    *   **Keterukan Wabak:** Secara teknikal, rantaian penularan ini mula tercetus pada **{tarikh_mula_str}** (notifikasi kes ke-2), bertahan selama **{tempoh_wabak_hari} hari**, dan telah merekodkan sejumlah **{jumlah_kes} kes**. Kelajuan penularan berada pada tahap **{kadar_velocity:.2f} kes sehari** dengan momentum 7-hari **{lok_mom_disp}**. Secara kumulatif, lokaliti ini merekodkan sejarah **{rekod_episode_lokaliti} episode wabak**.
                    *   **Trend Epidemiologi:** Jumlah kes memuncak pada **Minggu Epid {minggu_puncak_txt}** ({kes_puncak} kes). Analisis menunjukkan trend kes mingguan terkini sedang **{status_arah_txt}**.
                    *   **Tumpuan Struktur / Spatial (Hotspot Dalaman):** {butiran_struktur}
                    *   **Zon Jangkitan Aktif Terkini:** Mangsa-mangsa dengan episod gejala (onset) paling baharu (newly active vectors) mendiami kawasan **{zon_str}**. 
                    *   **Demografi Klinikal:** Kes paling banyak melibatkan kumpulan **{top_warga}** berkerjaya **{top_pekerjaan}**. Fasiliti yang paling banyak menotifikasikan kes dari wabak ini ialah **{fasiliti_utama_txt}**.
                    
                    **🎯 Rumusan Tindakan:** Fokus S&D dan kawalan semburan nyamuk dewasa wajar dihalakan secara spesifik ke zon jangkitan aktif terkini di **{zon_str}** serta saringan menyeluruh ke atas {fokus_saringan} sebagai kawasan risiko tertinggi.
                    """
                    st.success(kesimpulan_ai)
            except Exception as tab2_err:
                st.error(f"Ralat pada paparan Analisis Lokaliti: {tab2_err}")

        # =========================================================
        # PAPARAN 3: PUSAT ANALISIS AI & RAMALAN EPIDEMIOLOGI (95% CI & POA KPI)
        # =========================================================
        elif st.session_state.active_workspace_view == VIEW_AI:
            try:
                st.header("🧠 Pusat Analisis AI & Ramalan Epidemiologi (Data-Driven)")
                st.caption("Arahkan kursor pada mana-mana graf atau jadual — gelembung naratif akan muncul di sebelah bersebelahan tanpa menutup data, dan anda boleh menggerakkan kursor ke dalam gelembung untuk skrol bacaan penuh.")

                poa_period_options = {
                    "Keseluruhan Tahun Semasa": "ALL",
                    "Q1 (ME01 – ME13)": "Q1",
                    "Q2 (ME14 – ME26)": "Q2",
                    "Q3 (ME27 – ME39)": "Q3",
                    "Q4 (ME40 – ME52)": "Q4",
                    "Kumulatif Q1–Q3 (ME01 – ME39)": "Q1_Q3",
                }
                sel_poa_period_lbl = st.selectbox(
                    "📅 Tempoh Penilaian KPI POA Denggi (Memperkukuh Survelan & Kawalan Sporadik):",
                    options=list(poa_period_options.keys()),
                    index=0,
                    key="ai_poa_period_selector",
                )
                sel_poa_code = poa_period_options[sel_poa_period_lbl]

                ai_analytics = compute_ai_epidemiological_analytics(
                    df, df_lok, pilihan_lokaliti, data_ref_date, poa_period_code=sel_poa_code
                )

                ai_tab1, ai_tab2, ai_tab3 = st.tabs([
                    "📈 Ramalan Trend & 95% Confidence Interval",
                    "📋 Pencapaian KPI POA & Audit Pesalah Lewat",
                    "🎯 Soal Jawab AI & Pelan Tindakan",
                ])

                with ai_tab1:
                    col_ai_f1, col_ai_f2 = st.columns([1.45, 1.0])

                    with col_ai_f1:
                        weekly_df = ai_analytics["weekly_df"]
                        df_forecast = ai_analytics["df_forecast"]
                        slope_val = ai_analytics["slope_per_week"]
                        s_err_val = ai_analytics["s_err"]
                        r_sq_val = ai_analytics["r_squared"]
                        n_fit_val = ai_analytics["n_fit_weeks"]

                        if not weekly_df.empty and not df_forecast.empty:
                            hist_tail = weekly_df.tail(16)
                            last_wk_lbl = str(hist_tail["Minggu"].iloc[-1])
                            last_wk_kes = int(hist_tail["Kes"].iloc[-1])
                            next_fc = df_forecast.iloc[0]

                            st.markdown(
                                build_graph_info_strip_html(
                                    strip_title="📈 Unjuran Kes Mingguan (4 Minggu Hadapan dengan 95% CI)",
                                    tooltip_title="📈 Ramalan Trend Mingguan & 95% CI",
                                    relevance_html="Mengunjurkan trajektori kes denggi mingguan untuk 4 minggu epid hadapan menggunakan regresi linear pada data terkini bagi mengesan awal gelombang peningkatan kes serta julat ketidakpastian statistik pada tahap keyakinan 95%.",
                                    formula_html="ŷ<sub>t+k</sub> = a + b(x<sub>n</sub> + k)  |  95% CI = ŷ<sub>t+k</sub> ± t<sub>α/2, n−2</sub> · s<sub>e</sub>√(1 + 1/n + (x<sub>n+k</sub>−x̄)²/S<sub>xx</sub>)",
                                    current_calc_html=(
                                        f"<b>Pengiraan Semasa ({n_fit_val} minggu terkini):</b><br>"
                                        f"Minggu Terkini ({html.escape(last_wk_lbl)}) = <b>{last_wk_kes} kes</b> | Kecerunan (b) = <b>{slope_val:+.2f} kes/minggu</b><br>"
                                        f"Ralat Piawai (s<sub>e</sub>) = <b>{s_err_val:.2f}</b> | R² = <b>{r_sq_val:.3f}</b><br>"
                                        f"Unjuran Minggu {html.escape(str(next_fc['Minggu']))}: <b>{next_fc['Unjuran Kes']} kes</b> (95% CI: <b>{next_fc['95% CI Bawah']} – {next_fc['95% CI Atas']}</b>)"
                                    ),
                                ),
                                unsafe_allow_html=True,
                            )

                            fig_fc = go.Figure()
                            fig_fc.add_trace(go.Scatter(
                                x=hist_tail["Minggu"], y=hist_tail["Kes"], mode="lines+markers",
                                name="Kes Sebenar (Mingguan)", line=dict(color="#2563eb", width=2.5), marker=dict(size=7),
                            ))
                            conn_x = [hist_tail["Minggu"].iloc[-1]] + df_forecast["Minggu"].tolist()
                            conn_y = [float(hist_tail["Kes"].iloc[-1])] + df_forecast["Unjuran Kes"].tolist()
                            conn_hi = [float(hist_tail["Kes"].iloc[-1])] + df_forecast["95% CI Atas"].tolist()
                            conn_lo = [float(hist_tail["Kes"].iloc[-1])] + df_forecast["95% CI Bawah"].tolist()

                            fig_fc.add_trace(go.Scatter(
                                x=conn_x + conn_x[::-1], y=conn_hi + conn_lo[::-1], fill="toself",
                                fillcolor="rgba(239, 68, 68, 0.16)", line=dict(color="rgba(255,255,255,0)"),
                                hoverinfo="skip", name="Selang Keyakinan 95% (95% CI)",
                            ))
                            fig_fc.add_trace(go.Scatter(
                                x=conn_x, y=conn_y, mode="lines+markers", name="Unjuran AI (4 Minggu)",
                                line=dict(color="#dc2626", width=2.5, dash="dash"), marker=dict(size=8, symbol="diamond"),
                            ))
                            fig_fc.update_layout(
                                xaxis_title="Minggu Epid", yaxis_title="Jumlah Kes", height=360,
                                margin=dict(t=16, b=10, l=10, r=10), paper_bgcolor="rgba(255,255,255,0.75)",
                                plot_bgcolor="rgba(255,255,255,0.55)", legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                            )
                            st.plotly_chart(fig_fc, use_container_width=True, key="ai_forecast_chart")

                            peak_pt = hist_tail.loc[hist_tail["Kes"].idxmax()]
                            low_pt = hist_tail.loc[hist_tail["Kes"].idxmin()]
                            end_fc = df_forecast.iloc[-1]
                            arah_fc = "menurun" if slope_val < -0.2 else ("meningkat" if slope_val > 0.2 else "mendatar")

                            st.markdown(
                                render_ai_conclusion_box(
                                    "Kesimpulan Graf & Titik Plot Ramalan Mingguan",
                                    f"Sepanjang <b>{len(hist_tail)} minggu</b> titik plot sebenar, kes memuncak pada "
                                    f"<b>{html.escape(str(peak_pt['Minggu']))} ({int(peak_pt['Kes'])} kes)</b> dan menyusut ke titik terendah pada "
                                    f"<b>{html.escape(str(low_pt['Minggu']))} ({int(low_pt['Kes'])} kes)</b>. Garis regresi ({n_fit_val} minggu terkini) "
                                    f"menunjukkan arah <b>{arah_fc} ({slope_val:+.2f} kes/minggu, R² = {r_sq_val:.3f})</b>, dengan titik unjuran bergerak "
                                    f"daripada <b>{last_wk_kes} kes ({html.escape(last_wk_lbl)})</b> kepada <b>{end_fc['Unjuran Kes']} kes</b> "
                                    f"menjelang <b>{html.escape(str(end_fc['Minggu']))}</b> (95% CI: <b>{end_fc['95% CI Bawah']} – {end_fc['95% CI Atas']} kes</b>).",
                                ),
                                unsafe_allow_html=True,
                            )

                            tot_4w_fc = round(float(df_forecast["Unjuran Kes"].sum()), 1)
                            avg_4w_fc = round(float(df_forecast["Unjuran Kes"].mean()), 1)
                            tot_4w_lo = round(float(df_forecast["95% CI Bawah"].sum()), 1)
                            tot_4w_hi = round(float(df_forecast["95% CI Atas"].sum()), 1)

                            fc_tbl_html = df_to_styled_html_table(df_forecast)
                            fc_table_conc = (
                                f"<b>📌 Kesimpulan Jadual Ramalan 4 Minggu:</b> Jumlah kumulatif kes yang dijangka bagi 4 minggu hadapan ialah "
                                f"<b>{tot_4w_fc} kes</b> (purata <b>{avg_4w_fc} kes/minggu</b>), dengan julat keyakinan 95% keseluruhan antara "
                                f"<b>{tot_4w_lo} hingga {tot_4w_hi} kes</b> sebagai panduan perancangan kapasiti logistik & kawalan vektor."
                            )
                            card_fc_html = build_ai_hover_card_html(
                                zone_id="ai_zone_forecast",
                                card_title="📅 Jadual Ramalan Kes 4 Minggu Hadapan (95% CI)",
                                body_html=fc_tbl_html,
                                tooltip_title="📈 Ramalan Trend Mingguan & 95% CI",
                                relevance_html="Mengunjurkan trajektori kes denggi mingguan untuk 4 minggu epid hadapan menggunakan regresi linear pada data terkini bagi mengesan awal gelombang peningkatan kes serta julat ketidakpastian statistik pada tahap keyakinan 95%.",
                                formula_html="ŷ<sub>t+k</sub> = a + b(x<sub>n</sub> + k)  |  95% CI = ŷ<sub>t+k</sub> ± t<sub>α/2, n−2</sub> · s<sub>e</sub>√(1 + 1/n + (x<sub>n+k</sub>−x̄)²/S<sub>xx</sub>)",
                                current_calc_html=(
                                    f"<b>Pengiraan Semasa ({n_fit_val} minggu terkini):</b><br>"
                                    f"Minggu Terkini ({html.escape(last_wk_lbl)}) = <b>{last_wk_kes} kes</b> | Kecerunan (b) = <b>{slope_val:+.2f} kes/minggu</b><br>"
                                    f"Ralat Piawai (s<sub>e</sub>) = <b>{s_err_val:.2f}</b> | R² = <b>{r_sq_val:.3f}</b><br>"
                                    f"Unjuran Minggu {html.escape(str(next_fc['Minggu']))}: <b>{next_fc['Unjuran Kes']} kes</b> (95% CI: <b>{next_fc['95% CI Bawah']} – {next_fc['95% CI Atas']}</b>)"
                                ),
                                conclusion_html=fc_table_conc,
                            )
                            st.markdown(card_fc_html, unsafe_allow_html=True)
                        else:
                            st.info("Data mingguan tidak mencukupi untuk menjana unjuran 4 minggu.")

                    with col_ai_f2:
                        df_ar = ai_analytics["df_active_risk"]
                        if not df_ar.empty:
                            top_r = df_ar.iloc[0]
                            top_vel_exact = float(top_r["Jumlah Kes"]) / max(float(top_r["Tempoh (Hari)"]), 1.0)
                            p_vel_top = min(top_vel_exact * 35.0, 35.0)
                            p_c7_top = min(float(top_r["Kes 7 Hari Terkini"]) * 8.0, 30.0)
                            p_dur_top = min(float(top_r["Tempoh (Hari)"]) * 0.6, 20.0)
                            st_top_up = str(top_r["Status Semasa"]).upper()
                            p_bon_top = 15 if "HOTSPOT" in st_top_up else (10 if "TAK TERKAWAL" in st_top_up else 0)

                            risk_tooltip_rel = (
                                "Indeks triaj berwajaran deterministik (<b>0–100 mata</b>) bagi menyusun keutamaan mobilisasi lapangan untuk wabak aktif:<br>"
                                "• <b>1. Halaju / Velocity (Maks 35 mata):</b> Mengukur kelajuan penularan (<code>Kes ÷ Tempoh</code>; maks pada ≥1.0 kes/hari).<br>"
                                "• <b>2. Lonjakan 7 Hari Terkini (Maks 30 mata):</b> Mengukur momentum semasa (maks pada ≥4 kes dalam 7 hari terakhir).<br>"
                                "• <b>3. Tempoh Wabak (Maks 20 mata):</b> Mengukur ketahanan wabak & sarang pembiakan tersembunyi (maks pada ≥34 hari).<br>"
                                "• <b>4. Bonus Status Rasmi KKM (Maks 15 mata):</b> Hotspot <b>+15</b>, Wabak Tak Terkawal <b>+10</b>, Terkawal/Baru <b>+0</b>.<br>"
                                "<b>Klasifikasi Tahap Risiko & Julat Skor:</b><br>"
                                "• <span style='color:#fca5a5;font-weight:700;'>KRITIKAL (70–100):</span> Mobilisasi kecemasan segera (PTP/S&D intensif, ulangan SRT/ULV & ACD Blok/Tingkat).<br>"
                                "• <span style='color:#fde68a;font-weight:700;'>TINGGI (45–69):</span> Risiko tinggi eskalasi dalam 14 hari; kawalan susulan pantas diperlukan.<br>"
                                "• <span style='color:#7dd3fc;font-weight:700;'>SEDERHANA (0–44):</span> Terkawal / fasa awal; kekalkan jadual kawalan piawai KKM/POA."
                            )
                            risk_tooltip_form = (
                                "Skor = min(100, round(min(Vel×35, 35) + min(Kes<sub>7h</sub>×8, 30) + min(Tempoh×0.6, 20) + Bonus Status))<br>"
                                "λ<sub>harian</sub> = max(Kes<sub>7h</sub>/7, 0.5×Vel)<br>"
                                "Unjuran<sub>14h</sub> = 14λ  |  95% CI = 14λ ± 1.96√(14λ)"
                            )
                            risk_tooltip_curr = (
                                f"<b>Contoh Kiraan Semasa #1 — {html.escape(str(top_r['Lokaliti']))}:</b><br>"
                                f"• Velocity ({top_r['Velocity (Kes/Hari)']} kes/hari): <b>{p_vel_top:.1f} / 35</b><br>"
                                f"• Kes 7 Hari Terkini ({int(top_r['Kes 7 Hari Terkini'])} kes): <b>{p_c7_top:.1f} / 30</b><br>"
                                f"• Tempoh ({int(top_r['Tempoh (Hari)'])} hari): <b>{p_dur_top:.1f} / 20</b><br>"
                                f"• Bonus Status ({html.escape(str(top_r['Status Semasa']))}): <b>+{p_bon_top} / 15</b><br>"
                                f"<b>Jumlah Skor: {top_r['Skor Risiko']}/100 ({top_r['Tahap Risiko']})</b> | "
                                f"Unjuran +14 Hari = <b>{top_r['Unjuran +14 Hari']} kes</b> (95% CI: <b>{top_r['95% CI (+14 Hari)']}</b>)"
                            )

                            st.markdown(
                                build_graph_info_strip_html(
                                    strip_title="🎯 Matriks Risiko Eskalasi Wabak Aktif",
                                    tooltip_title="🎯 Matriks Risiko Eskalasi (0–100) & Unjuran Poisson +14 Hari",
                                    relevance_html=risk_tooltip_rel,
                                    formula_html=risk_tooltip_form,
                                    current_calc_html=risk_tooltip_curr,
                                ),
                                unsafe_allow_html=True,
                            )

                            fig_risk = px.scatter(
                                df_ar, x="Tempoh (Hari)", y="Velocity (Kes/Hari)", size="Unjuran +14 Hari",
                                color="Status Semasa", hover_name="Lokaliti",
                                hover_data={"No. Wabak": True, "Jumlah Kes": True, "Unjuran +14 Hari": True, "95% CI (+14 Hari)": True, "Skor Risiko": True},
                                color_discrete_map={"Wabak Baru": "#00bcd4", "Wabak Terkawal": "#e06666", "Wabak Tak Terkawal": "#3e85c7", "Hotspot": "#fe0000"},
                            )
                            fig_risk.update_layout(
                                height=360, margin=dict(t=16, b=10, l=10, r=10),
                                paper_bgcolor="rgba(255,255,255,0.75)", plot_bgcolor="rgba(255,255,255,0.55)",
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                            )
                            st.plotly_chart(fig_risk, use_container_width=True, key="ai_risk_scatter")

                            max_vel_pt = df_ar.loc[df_ar["Velocity (Kes/Hari)"].idxmax()]
                            max_dur_pt = df_ar.loc[df_ar["Tempoh (Hari)"].idxmax()]
                            max_proj_pt = df_ar.loc[df_ar["Unjuran +14 Hari"].idxmax()]
                            avg_vel_all = round(float(df_ar["Velocity (Kes/Hari)"].mean()), 2)
                            avg_dur_all = round(float(df_ar["Tempoh (Hari)"].mean()), 1)

                            st.markdown(
                                render_ai_conclusion_box(
                                    "Kesimpulan Plot Taburan Matriks Risiko Eskalasi",
                                    f"Daripada <b>{len(df_ar)} titik plot wabak aktif</b> (purata halaju <b>{avg_vel_all} kes/hari</b>, "
                                    f"purata tempoh <b>{avg_dur_all} hari</b>), titik halaju tertinggi ialah <b>{html.escape(str(max_vel_pt['Lokaliti']))}</b> "
                                    f"(<b>{max_vel_pt['Velocity (Kes/Hari)']} kes/hari</b>), tempoh terlama ialah <b>{html.escape(str(max_dur_pt['Lokaliti']))}</b> "
                                    f"(<b>{int(max_dur_pt['Tempoh (Hari)'])} hari</b>), manakala gelembung unjuran +14 hari terbesar tertumpu di "
                                    f"<b>{html.escape(str(max_proj_pt['Lokaliti']))}</b> (<b>{max_proj_pt['Unjuran +14 Hari']} kes</b>; 95% CI: <b>{max_proj_pt['95% CI (+14 Hari)']}</b>).",
                                ),
                                unsafe_allow_html=True,
                            )

                            risk_display_df = df_ar[["Lokaliti", "Tahap Risiko", "Skor Risiko", "Unjuran +14 Hari", "95% CI (+14 Hari)"]]
                            risk_badges = {"Tahap Risiko": {"KRITIKAL": ("#fee2e2", "#991b1b"), "TINGGI": ("#fef3c7", "#92400e"), "SEDERHANA": ("#e0f2fe", "#075985")}}
                            risk_tbl_html = df_to_styled_html_table(risk_display_df, badge_cols=risk_badges)
                            n_krit = int((df_ar["Tahap Risiko"] == "KRITIKAL").sum())
                            n_tinggi = int((df_ar["Tahap Risiko"] == "TINGGI").sum())
                            n_sed = int((df_ar["Tahap Risiko"] == "SEDERHANA").sum())
                            tot_14d = round(float(df_ar["Unjuran +14 Hari"].sum()), 1)
                            tot_14d_lo = round(float(df_ar["CI Bawah"].sum()), 1)
                            tot_14d_hi = round(float(df_ar["CI Atas"].sum()), 1)

                            risk_table_conc = (
                                f"<b>📌 Kesimpulan Jadual Skor Risiko:</b> Pecahan tahap risiko wabak aktif ialah "
                                f"<b>{n_krit} Kritikal</b>, <b>{n_tinggi} Tinggi</b>, dan <b>{n_sed} Sederhana</b>. "
                                f"Keseluruhan wabak aktif diunjurkan menjana <b>{tot_14d} kes baharu</b> dalam +14 hari "
                                f"(julat 95% CI: <b>{tot_14d_lo} – {tot_14d_hi} kes</b>), dengan keutamaan #1 di <b>{html.escape(str(top_r['Lokaliti']))}</b>."
                            )
                            card_risk_html = build_ai_hover_card_html(
                                zone_id="ai_zone_risk",
                                card_title="🚨 Jadual Skor Risiko Eskalasi & Unjuran +14 Hari",
                                body_html=risk_tbl_html,
                                tooltip_title="🎯 Matriks Risiko Eskalasi (0–100) & Unjuran Poisson +14 Hari",
                                relevance_html=risk_tooltip_rel,
                                formula_html=risk_tooltip_form,
                                current_calc_html=risk_tooltip_curr,
                                conclusion_html=risk_table_conc,
                            )
                            st.markdown(card_risk_html, unsafe_allow_html=True)
                        else:
                            st.success("Tiada wabak aktif semasa untuk pemodelan risiko.")

                with ai_tab2:
                    c_corr1, c_corr2 = st.columns([1.18, 1.0])
                    with c_corr1:
                        df_poa_kpis = ai_analytics["df_poa_kpis"]
                        poa_meta = ai_analytics["poa_meta"]
                        target_yr_disp = ai_analytics["target_yr"]
                        if not df_poa_kpis.empty:
                            poa_lines = "<br>".join(
                                f"• <b>{html.escape(str(r['Kod']))}</b> ({html.escape(str(r['Indikator POA']))}): "
                                f"<b>{r['Pencapaian (%)']}%</b> ({r['Bilangan']}, Sasaran {r['Sasaran (%)']}%, Varians <b>{r['Varians']}</b>)"
                                for _, r in df_poa_kpis.iterrows()
                            )
                            prem_note = (
                                f"Median premis sasaran (<code>Rumah/Kedai</code>) sekitar kes sporadik: <b>{poa_meta['target_premises_med']} premis</b> (Rujukan Ind 11 / C1: Liputan PTP ≥ 50% dalam radius 50m/200m)."
                                if poa_meta.get("target_premises_med", 0) > 0
                                else "Rujukan Ind 11 (C1): Liputan PTP ≥ 50% (Semua) / ≥ 60% (KKM) dalam radius 50m/200m."
                            )
                            poa_tooltip_rel = (
                                "Penilaian pencapaian rasmi berdasarkan <b>Pelan Tindakan (POA) Denggi KKM / PKD</b>:<br>"
                                "• <b>Ind 1 (A1) Notifikasi ≤24j (DNTI):</b> Memastikan fasiliti kesihatan menotifikasi kes dalam 24 jam (Sasaran 100%).<br>"
                                "• <b>Ind 4 (A2) Daftar Kes ≤24j:</b> Memastikan notifikasi disiasat & didaftarkan dalam 24 jam dari tarikh notifikasi (Sasaran 85%).<br>"
                                "• <b>Ind 9 & 10 (C1) Kawalan Kes Sporadik (<code>Satu Kes</code>):</b> Pelaksanaan PTP (Sasaran 70% Semua / 80% KKM) dan SRT (Sasaran 60% Semua / 80% KKM) dalam 24 jam dari <b>Tarikh Daftar</b> bagi mencegah kes terpencil bertukar menjadi wabak.<br>"
                                f"• <i>Nota:</i> <code>Tarikh Onset</code> adalah petunjuk epidemiologi pesakit mendapatkan rawatan (bukan KPI staf PKD). {prem_note}"
                            )
                            poa_tooltip_form = (
                                "A1: (Notifikasi ≤24j ÷ Jumlah Notifikasi) × 100 [Sasaran: 100%]<br>"
                                "A2: (Kes Daftar ≤24j dari Notifikasi ÷ Bil. Kes Daftar) × 100 [Sasaran: 85%]<br>"
                                "C1 Ind 9: (Sporadik PTP ≤24j dari Tkh Daftar ÷ Bil. Sporadik) × 100 [70% / 80%]<br>"
                                "C1 Ind 10: (Sporadik SRT ≤24j dari Tkh Daftar ÷ Bil. Sporadik) × 100 [60% / 80%]"
                            )
                            poa_tooltip_curr = f"<b>Pencapaian Semasa ({html.escape(sel_poa_period_lbl)} — Tahun {target_yr_disp}):</b><br>{poa_lines}"

                            st.markdown(
                                build_graph_info_strip_html(
                                    strip_title=f"📋 Pencapaian KPI POA Denggi vs Sasaran PKD ({sel_poa_period_lbl})",
                                    tooltip_title="📋 Metodologi & Formula Indikator POA Denggi",
                                    relevance_html=poa_tooltip_rel,
                                    formula_html=poa_tooltip_form,
                                    current_calc_html=poa_tooltip_curr,
                                ),
                                unsafe_allow_html=True,
                            )

                            fig_poa = go.Figure()
                            fig_poa.add_trace(go.Bar(
                                x=df_poa_kpis["Kod"], y=df_poa_kpis["Pencapaian (%)"], name="Pencapaian Semasa (%)",
                                marker_color=["#10b981" if s == "TERCAPAI" else "#ef4444" for s in df_poa_kpis["Status POA"]],
                                text=df_poa_kpis["Pencapaian (%)"].apply(lambda v: f"{v:.1f}%"), textposition="outside",
                                customdata=df_poa_kpis[["Indikator POA", "Bilangan", "Sasaran (%)", "Varians", "Status POA"]].values,
                                hovertemplate=(
                                    "<b>%{customdata[0]}</b><br>Pencapaian: <b>%{y:.1f}%</b> (%{customdata[1]})<br>"
                                    "Sasaran POA: <b>%{customdata[2]:.1f}%</b><br>Varians: <b>%{customdata[3]} kes</b> (%{customdata[4]})<extra></extra>"
                                ),
                            ))
                            fig_poa.add_trace(go.Scatter(
                                x=df_poa_kpis["Kod"], y=df_poa_kpis["Sasaran (%)"], name="Sasaran POA (%)",
                                mode="lines+markers", line=dict(color="#0f172a", width=2.2, dash="dash"), marker=dict(size=8, symbol="diamond"),
                            ))
                            fig_poa.update_yaxes(range=[0, 114])
                            fig_poa.update_layout(
                                height=330, xaxis_title="", yaxis_title="Peratus (%)",
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), margin=dict(t=16, b=10, l=10, r=10),
                                paper_bgcolor="rgba(255,255,255,0.75)", plot_bgcolor="rgba(255,255,255,0.55)",
                            )
                            st.plotly_chart(fig_poa, use_container_width=True, key="ai_poa_kpi_chart")

                            n_achieved = int((df_poa_kpis["Status POA"] == "TERCAPAI").sum())
                            unmet_df = df_poa_kpis[df_poa_kpis["Status POA"] == "TIDAK TERCAPAI"]
                            unmet_str = (
                                ", ".join(f"{r['Kod']} ({r['Pencapaian (%)']}% vs {r['Sasaran (%)']}%, varians {r['Varians']})" for _, r in unmet_df.iterrows())
                                if not unmet_df.empty
                                else "Tiada — semua indikator mencapai sasaran"
                            )

                            st.markdown(
                                render_ai_conclusion_box(
                                    "Kesimpulan Graf Pencapaian KPI POA Denggi",
                                    f"Bagi tempoh <b>{html.escape(sel_poa_period_lbl)} ({target_yr_disp})</b>, sebanyak "
                                    f"<b>{n_achieved} daripada {len(df_poa_kpis)} indikator POA</b> telah mencapai sasaran. "
                                    f"Indikator yang memerlukan tindakan penambahbaikan: <b>{html.escape(unmet_str)}</b>.",
                                ),
                                unsafe_allow_html=True,
                            )

                            poa_badges = {"Status POA": {"TERCAPAI": ("#dcfce7", "#166534"), "TIDAK TERCAPAI": ("#fee2e2", "#991b1b")}}
                            poa_tbl_html = df_to_styled_html_table(df_poa_kpis, badge_cols=poa_badges)
                            poa_table_conc = (
                                f"<b>📌 Kesimpulan Jadual Prestasi POA:</b> Kawalan kes sporadik di lokaliti KKM "
                                f"(<b>Ind 9(ii) PTP: {df_poa_kpis.iloc[3]['Pencapaian (%)']}%</b> & "
                                f"<b>Ind 10(ii) SRT: {df_poa_kpis.iloc[5]['Pencapaian (%)']}%</b>) melepasi sasaran 80%, "
                                f"manakala fokus utama operasi adalah meningkatkan <b>Pendaftaran Kes ≤24j (Ind 4 / A2: {df_poa_kpis.iloc[1]['Pencapaian (%)']}% vs 85%)</b>."
                            )
                            card_poa_html = build_ai_hover_card_html(
                                zone_id="ai_zone_poa",
                                card_title=f"📋 Jadual Pencapaian KPI POA Denggi ({sel_poa_period_lbl})",
                                body_html=poa_tbl_html,
                                tooltip_title="📋 Metodologi & Formula Indikator POA Denggi",
                                relevance_html=poa_tooltip_rel,
                                formula_html=poa_tooltip_form,
                                current_calc_html=poa_tooltip_curr,
                                conclusion_html=poa_table_conc,
                            )
                            st.markdown(card_poa_html, unsafe_allow_html=True)
                        else:
                            st.info("Tiada rekod kes bagi tempoh POA yang dipilih.")

                    with c_corr2:
                        df_sc = ai_analytics["df_status_corr"]
                        df_pearson = ai_analytics["df_pearson"]
                        if not df_sc.empty:
                            p_summary_lines = (
                                "<br>".join(
                                    f"• {html.escape(str(r['Pasangan Pembolehubah']))}: <b>r = {r['Pekali Korelasi (r)']}</b> ({r['Kekuatan Hubungan']}, n={r['Bil. Episod (n)']})"
                                    for _, r in df_pearson.iterrows()
                                )
                                if not df_pearson.empty
                                else f"Jumlah episod dianalisis: <b>{int(df_sc['Bil. Episod'].sum())} episod</b>"
                            )
                            corr_rel_html = (
                                "Membandingkan purata saiz kes setiap episod, pematuhan pendaftaran 24 jam (<b>POA A2</b>), dan "
                                "tempoh lengah pesakit mendapatkan rawatan (<code>Tarikh Onset → Notifikasi</code> sebagai <i>petunjuk epidemiologi</i>) "
                                "merentas status wabak bagi menilai faktor yang memacu eskalasi wabak."
                            )
                            corr_form_html = (
                                "Purata Kes/Episod = ΣKes ÷ Bil. Episod<br>"
                                "r = Σ(x<sub>i</sub>−x̄)(y<sub>i</sub>−ȳ) ÷ √[Σ(x<sub>i</sub>−x̄)²Σ(y<sub>i</sub>−ȳ)²]"
                            )
                            st.markdown(
                                build_graph_info_strip_html(
                                    strip_title="📊 Korelasi Status Wabak vs Saiz Kes & Pendaftaran 24j",
                                    tooltip_title="🔗 Korelasi Status Wabak & Pekali Pearson (r)",
                                    relevance_html=corr_rel_html,
                                    formula_html=corr_form_html,
                                    current_calc_html=f"<b>Dapatan Korelasi Semasa:</b><br>{p_summary_lines}",
                                ),
                                unsafe_allow_html=True,
                            )

                            fig_sc = px.bar(
                                df_sc, x="Status Wabak", y=["Purata Kes / Episod", "Lengah Onset→Notif (Hari)"],
                                barmode="group", text_auto=True, color_discrete_sequence=["#ef4444", "#3b82f6"],
                            )
                            fig_sc.update_layout(
                                height=330, xaxis_title="", yaxis_title="Nilai Purata", legend_title="",
                                margin=dict(t=16, b=10, l=10, r=10), paper_bgcolor="rgba(255,255,255,0.75)", plot_bgcolor="rgba(255,255,255,0.55)",
                            )
                            st.plotly_chart(fig_sc, use_container_width=True, key="ai_status_corr_chart")

                            max_sz = df_sc.loc[df_sc["Purata Kes / Episod"].idxmax()]
                            min_sz = df_sc.loc[df_sc["Purata Kes / Episod"].idxmin()]
                            ratio_sz = round(float(max_sz["Purata Kes / Episod"]) / max(float(min_sz["Purata Kes / Episod"]), 0.1), 1)

                            st.markdown(
                                render_ai_conclusion_box(
                                    "Kesimpulan Graf Status Wabak vs Saiz & Lengah Epidemiologi",
                                    f"Episod berstatus <b>{html.escape(str(max_sz['Status Wabak']))}</b> merekodkan purata saiz kes "
                                    f"<b>{ratio_sz}× lebih besar</b> (<b>{max_sz['Purata Kes / Episod']} kes/episod</b>) berbanding "
                                    f"<b>{html.escape(str(min_sz['Status Wabak']))}</b> (<b>{min_sz['Purata Kes / Episod']} kes/episod</b>). "
                                    f"Pengesanan awal kes dan pendaftaran dalam tempoh 24 jam (POA A2) membolehkan kawalan vektor dimulakan sebelum penularan generasi kedua.",
                                ),
                                unsafe_allow_html=True,
                            )

                            sc_tbl_html = df_to_styled_html_table(df_sc)
                            pearson_section_html = (
                                "<div style='margin-top:8px; font-weight:700; font-size:0.84rem;'>Pekali Korelasi Pearson (r):</div>"
                                + df_to_styled_html_table(df_pearson)
                                if not df_pearson.empty
                                else ""
                            )
                            if not df_pearson.empty:
                                best_p = df_pearson.loc[df_pearson["Pekali Korelasi (r)"].abs().idxmax()]
                                corr_table_conc = (
                                    f"<b>📌 Kesimpulan Jadual Korelasi Pearson (r):</b> Hubungan linear tertinggi dengan saiz kes wabak "
                                    f"ialah <b>{html.escape(str(best_p['Pasangan Pembolehubah']))}</b> dengan pekali "
                                    f"<b>r = {best_p['Pekali Korelasi (r)']} ({best_p['Kekuatan Hubungan']}, n={best_p['Bil. Episod (n)']})</b>."
                                )
                            else:
                                corr_table_conc = (
                                    f"<b>📌 Kesimpulan Jadual Status Wabak:</b> Sebanyak <b>{int(df_sc['Bil. Episod'].sum())} episod wabak</b> "
                                    f"telah dibandingkan merentas <b>{len(df_sc)} kategori status</b>."
                                )
                            card_corr_html = build_ai_hover_card_html(
                                zone_id="ai_zone_corr",
                                card_title="📊 Jadual Korelasi Status Wabak & Pekali Pearson (r)",
                                body_html=sc_tbl_html + pearson_section_html,
                                tooltip_title="🔗 Korelasi Status Wabak & Pekali Pearson (r)",
                                relevance_html=corr_rel_html,
                                formula_html=corr_form_html,
                                current_calc_html=f"<b>Dapatan Korelasi Semasa:</b><br>{p_summary_lines}",
                                conclusion_html=corr_table_conc,
                            )
                            st.markdown(card_corr_html, unsafe_allow_html=True)
                        else:
                            st.info("Tiada rekod wabak untuk perbandingan status.")

                    # =========================================================
                    # AUDIT NOTIFIKASI LEWAT (>24 JAM / DNTI) & PENGESANAN PESALAH BERULANG (POA A1)
                    # =========================================================
                    st.markdown("---")
                    st.subheader(f"🚨 Audit Notifikasi Lewat (>24 Jam / DNTI) & Pengesanan Pesalah Berulang ({sel_poa_period_lbl})")

                    df_off_sum = ai_analytics.get("df_offenders_sum", pd.DataFrame())
                    df_off_det = ai_analytics.get("df_offenders_det", pd.DataFrame())
                    off_meta = ai_analytics.get("offenders_meta", {})

                    ok1, ok2, ok3, ok4 = st.columns(4)
                    with ok1:
                        st.markdown(
                            build_glass_kpi_html(
                                label="Jumlah Notifikasi Lewat (>24j)",
                                value_str=str(off_meta.get("total_late", 0)),
                                sub_str=f"Melibatkan <b>{off_meta.get('total_facilities', 0)} fasiliti</b> pemberitahu",
                                tooltip_title="🚨 Notifikasi Lewat (>24 Jam / DNTI)",
                                relevance_html="Mengenal pasti kes denggi yang dinotifikasi melebihi 24 jam daripada Tarikh Diagnosis oleh hospital atau klinik (POA Indikator 1 / A1: Sasaran 100%).",
                                formula_html="Lengah = Tkh Notifikasi − Tarikh Diagnosis > 1 hari",
                                current_calc_html=f"<b>Tempoh {html.escape(sel_poa_period_lbl)}:</b> <b>{off_meta.get('total_late', 0)} kes lewat</b> daripada <b>{off_meta.get('total_facilities', 0)} fasiliti</b>.",
                                accent_color="#e11d48" if off_meta.get("total_late", 0) > 0 else "#059669",
                            ),
                            unsafe_allow_html=True,
                        )
                    with ok2:
                        st.markdown(
                            build_glass_kpi_html(
                                label="Pecahan Sektor (Awam vs Swasta)",
                                value_str=f"{off_meta.get('n_public', 0)} / {off_meta.get('n_private', 0)}",
                                sub_str=f"Awam: <b>{off_meta.get('n_public', 0)}</b> • Swasta: <b>{off_meta.get('n_private', 0)}</b>",
                                tooltip_title="🏥 Pecahan Sektor Pemberitahu (Jadual 2a POA)",
                                relevance_html="Membezakan notifikasi lewat antara fasiliti Sektor Awam (Hospital Kerajaan/KK/Universiti) dan Sektor Swasta (Klinik/Hospital Swasta) untuk tindakan surat teguran atau emel rasmi.",
                                formula_html="Pengelasan mengikut Jenis & Nama Kemudahan Kesihatan Pemberitahu",
                                current_calc_html=f"<b>Angka Semasa:</b> <b>{off_meta.get('n_public', 0)} kes Awam</b> dan <b>{off_meta.get('n_private', 0)} kes Swasta</b>.",
                            ),
                            unsafe_allow_html=True,
                        )
                    with ok3:
                        st.markdown(
                            build_glass_kpi_html(
                                label="Pesalah Berulang (Tempoh Ini)",
                                value_str=str(off_meta.get("n_repeated_period", 0)),
                                sub_str="Fasiliti ≥ 2 kali lewat tempoh dipilih",
                                tooltip_title="🔁 Pesalah Berulang (Repeated Offenders)",
                                relevance_html="Mengenal pasti fasiliti yang melakukan kesalahan notifikasi lewat sekurang-kurangnya 2 kali dalam tempoh penilaian semasa dan memerlukan Surat Teguran & Emel Rasmi segera.",
                                formula_html="Count(Fasiliti dengan Bil. Lewat Tempoh Semasa ≥ 2)",
                                current_calc_html=f"<b>Status Semasa:</b> <b>{off_meta.get('n_repeated_period', 0)} fasiliti</b> dikelaskan sebagai <b>PESALAH BERULANG</b>.",
                                accent_color="#dc2626" if off_meta.get("n_repeated_period", 0) > 0 else "#059669",
                            ),
                            unsafe_allow_html=True,
                        )
                    with ok4:
                        st.markdown(
                            build_glass_kpi_html(
                                label="Berulang (Sejarah 5 Tahun)",
                                value_str=str(off_meta.get("n_repeated_hist", 0)),
                                sub_str="Pernah lewat sebelum ini (2021–2026)",
                                tooltip_title="🗂️ Pesalah Berulang Merentas Sejarah 5 Tahun",
                                relevance_html="Menyemak sama ada fasiliti yang baru melakukan 1 kesalahan dalam tempoh semasa pernah mempunyai rekod notifikasi lewat dalam pangkalan data sejarah 5 tahun.",
                                formula_html="Bil. Lewat Tempoh Semasa = 1 TETAPI Sejarah 5 Tahun ≥ 2",
                                current_calc_html=f"<b>Status Semasa:</b> <b>{off_meta.get('n_repeated_hist', 0)} fasiliti</b> dikesan pernah lewat pada tempoh terdahulu.",
                                accent_color="#d97706" if off_meta.get("n_repeated_hist", 0) > 0 else "#0f172a",
                            ),
                            unsafe_allow_html=True,
                        )

                    if not df_off_sum.empty:
                        c_off1, c_off2 = st.columns([0.95, 1.35])
                        top_off = df_off_sum.iloc[0]
                        off_rel_html = (
                            "Audit pematuhan <b>POA Indikator 1 (A1 — DNTI ≤24 Jam)</b> mengikut format Jadual 2a:<br>"
                            "• <b>PESALAH BERULANG:</b> ≥2 notifikasi lewat dalam tempoh dipilih → <i>Surat Teguran & Emel Rasmi</i>.<br>"
                            "• <b>BERULANG (SEJARAH):</b> 1 kali lewat dalam tempoh ini tetapi ≥2 kali dalam rekod 5 tahun → <i>Surat Peringatan & Pemantauan</i>.<br>"
                            "• <b>KESALAHAN PERTAMA:</b> 1 kali lewat keseluruhan → <i>Makluman Pematuhan DNTI</i>."
                        )
                        off_form_html = "Notifikasi Lewat = (Tkh Notifikasi − Tarikh Diagnosis) > 1 hari (>24 jam)"
                        off_curr_html = (
                            f"<b>Fasiliti Keutamaan #1:</b> {html.escape(str(top_off['Fasiliti Pemberitahu']))} ({top_off['Sektor']})<br>"
                            f"Lewat Tempoh Ini = <b>{top_off['Bil. Lewat']} kes</b> | Sejarah 5 Thn = <b>{top_off['Sejarah (5 Thn)']} kes</b> | Maks = <b>{top_off['Maks (Hari)']} hari</b><br>"
                            f"Status: <b>{top_off['Status Pesalah']}</b> → {html.escape(str(top_off['Cadangan Tindakan']))}"
                        )

                        with c_off1:
                            st.markdown(
                                build_graph_info_strip_html(
                                    strip_title="📊 Graf Fasiliti Notifikasi Lewat (>24 Jam) Mengikut Sektor",
                                    tooltip_title="🚨 Audit Fasiliti Notifikasi Lewat (POA A1)",
                                    relevance_html=off_rel_html,
                                    formula_html=off_form_html,
                                    current_calc_html=off_curr_html,
                                ),
                                unsafe_allow_html=True,
                            )
                            plot_off = df_off_sum.head(12).sort_values(by=["Bil. Lewat", "Maks (Hari)"], ascending=[True, True])
                            fig_off = px.bar(
                                plot_off, x="Bil. Lewat", y="Fasiliti Pemberitahu", orientation="h",
                                color="Sektor", text="Bil. Lewat",
                                hover_data={"Sejarah (5 Thn)": True, "Maks (Hari)": True, "Status Pesalah": True, "Cadangan Tindakan": True},
                                color_discrete_map={"AWAM": "#2563eb", "SWASTA": "#ef4444", "LAIN-LAIN": "#64748b"},
                            )
                            fig_off.update_traces(textposition="outside")
                            fig_off.update_layout(
                                height=340, xaxis_title="Bilangan Notifikasi Lewat (>24 Jam)", yaxis_title="", legend_title="Sektor",
                                margin=dict(t=16, b=10, l=10, r=18), paper_bgcolor="rgba(255,255,255,0.75)", plot_bgcolor="rgba(255,255,255,0.55)",
                            )
                            st.plotly_chart(fig_off, use_container_width=True, key="ai_poa_offenders_bar")
                            st.markdown(
                                render_ai_conclusion_box(
                                    "Kesimpulan Audit Notifikasi Lewat (>24 Jam)",
                                    f"Sebanyak <b>{off_meta.get('total_late', 0)} kes notifikasi lewat</b> direkodkan daripada "
                                    f"<b>{off_meta.get('total_facilities', 0)} fasiliti</b> (<b>{off_meta.get('n_public', 0)} Awam</b>, "
                                    f"<b>{off_meta.get('n_private', 0)} Swasta</b>). Fasiliti keutamaan audit ialah "
                                    f"<b>{html.escape(str(top_off['Fasiliti Pemberitahu']))}</b> (<b>{top_off['Bil. Lewat']} kes lewat</b>, "
                                    f"maksimum <b>{top_off['Maks (Hari)']} hari</b>; <b>{top_off['Status Pesalah']}</b>).",
                                ),
                                unsafe_allow_html=True,
                            )

                        with c_off2:
                            off_badges = {
                                "Status Pesalah": {"PESALAH BERULANG": ("#fee2e2", "#991b1b"), "BERULANG (SEJARAH)": ("#fef3c7", "#92400e"), "KESALAHAN PERTAMA": ("#e0f2fe", "#075985")},
                                "Sektor": {"AWAM": ("#dbeafe", "#1e40af"), "SWASTA": ("#fce7f3", "#9d174d"), "LAIN-LAIN": ("#f1f5f9", "#334155")},
                            }
                            off_tbl_html = df_to_styled_html_table(df_off_sum, badge_cols=off_badges)
                            off_conc_html = (
                                f"<b>📌 Cadangan Tindakan Pentadbiran:</b> "
                                f"<b>{off_meta.get('n_repeated_period', 0)} fasiliti</b> berstatus <i>PESALAH BERULANG</i> dan "
                                f"<b>{off_meta.get('n_repeated_hist', 0)} fasiliti</b> berstatus <i>BERULANG (SEJARAH)</i> perlu diberi "
                                f"<b>Surat Teguran / Peringatan & Emel Rasmi</b> oleh Unit Survelan PKD."
                            )
                            card_off_html = build_ai_hover_card_html(
                                zone_id="ai_zone_offenders",
                                card_title="📋 Senarai Fasiliti Notifikasi Lewat & Status Pesalah Berulang (Jadual 2a)",
                                body_html=off_tbl_html,
                                tooltip_title="🚨 Audit Pesalah Notifikasi Lewat (POA A1 / DNTI)",
                                relevance_html=off_rel_html,
                                formula_html=off_form_html,
                                current_calc_html=off_curr_html,
                                conclusion_html=off_conc_html,
                            )
                            st.markdown(card_off_html, unsafe_allow_html=True)

                        with st.expander(f"📑 Log Terperinci Kes Notifikasi Lewat (>24 Jam) untuk Tindakan Surat/Emel ({len(df_off_det)} Kes)"):
                            st.dataframe(df_off_det, use_container_width=True, hide_index=True)
                            csv_off_bytes = df_off_det.to_csv(index=False).encode("utf-8-sig")
                            st.download_button(
                                label="📥 Muat Turun Log Audit Notifikasi Lewat (.CSV)",
                                data=csv_off_bytes,
                                file_name=f"Audit_Notifikasi_Lewat_POA_{sel_poa_code}_{target_yr_disp}.csv",
                                mime="text/csv",
                                key=f"dl_offenders_csv_{sel_poa_code}",
                            )
                    else:
                        st.success(f"✅ Tiada notifikasi lewat (>24 jam dari Tarikh Diagnosis) direkodkan bagi tempoh **{sel_poa_period_lbl}** — Pematuhan DNTI 100%!")

                with ai_tab3:
                    q_cols = st.columns(3)
                    with q_cols[0]:
                        st.button(
                            "📈 Ramalan 4 Minggu & 95% CI",
                            key="btn_ai_q1",
                            on_click=set_ai_prompt,
                            args=("Berikan ramalan trend kes 4 minggu hadapan berserta Selang Keyakinan 95% (95% CI) dan lokaliti aktif paling berisiko.",),
                            use_container_width=True,
                        )
                    with q_cols[1]:
                        st.button(
                            "📋 Pencapaian KPI POA & Pesalah Lewat",
                            key="btn_ai_q2",
                            on_click=set_ai_prompt,
                            args=("Analisis pencapaian KPI POA Denggi (Pendaftaran kes ≤24 jam, PTP & SRT kes sporadik ≤24 jam) serta senarai fasiliti notifikasi lewat (>24 jam) dan pesalah berulang.",),
                            use_container_width=True,
                        )
                    with q_cols[2]:
                        st.button(
                            "🎯 Pelan Tindakan Lokaliti Ini",
                            key="btn_ai_q3",
                            on_click=set_ai_prompt,
                            args=(f"Jana pelan tindakan operasi terperinci berdasarkan POA Denggi dan data bagi lokaliti {pilihan_lokaliti}.",),
                            use_container_width=True,
                        )

                    user_ai_q = st.text_input(
                        "Tanya AI tentang data, pencapaian KPI POA, pesalah notifikasi lewat, ramalan (95% CI) atau pelan tindakan:",
                        key="ai_custom_question",
                    )
                    if user_ai_q:
                        render_ai_qa_visuals_and_response(user_ai_q, ai_analytics, data_ref_date, embedded_gemini_key)
            except Exception as tab3_err:
                st.error(f"Ralat pada Pusat Analisis AI: {tab3_err}")

    except Exception as e:
        st.error(f"Ralat sistem: {e}")
