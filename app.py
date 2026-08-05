import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="Dashboard Analisis Denggi", layout="wide")

# --- CSS KHUSUS UNTUK CETAKAN PDF ---
st.markdown("""
    <style>
    @media print {
        header {visibility: hidden;}
        section[data-testid="stSidebar"] {display: none;}
        .stButton > button {display: none;}
        footer {visibility: hidden;}
        .stAlert {page-break-inside: avoid;}
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
    </style>
    """, unsafe_allow_html=True)

def parse_address(address):
    address = str(address).upper()
    blok, tingkat = "TIDAK PASTI", "TIDAK PASTI"
    
    match1 = re.search(r'([A-Z0-9]+)\s*-\s*(\d+)\s*-\s*\d+', address)
    if match1:
        blok, tingkat = match1.group(1), match1.group(2)
    else:
        match_blok = re.search(r'(?:BLOK|BLOCK)\s*([A-Z0-9]+)', address)
        if match_blok:
            blok = match_blok.group(1)
        match_tingkat = re.search(r'(?:TINGKAT|LEVEL|TGKT)\s*(\d+)', address)
        if match_tingkat:
            tingkat = match_tingkat.group(1)
            
    # Buang leading zeros untuk standardisasi awal
    if blok != "TIDAK PASTI":
        blok_clean = re.sub(r'^0+', '', blok)
        blok = blok_clean if blok_clean else '0'
        
    if tingkat != "TIDAK PASTI":
        tingkat_clean = re.sub(r'^0+', '', tingkat)
        tingkat = tingkat_clean if tingkat_clean else '0'
        
    return pd.Series([blok, tingkat])

# --- PENGURUSAN STATE (MEMORI APLIKASI) ---
if 'selected_lokaliti' not in st.session_state:
    st.session_state.selected_lokaliti = None
if 'selected_wabak' not in st.session_state:
    st.session_state.selected_wabak = None
if 'episode_filter' not in st.session_state:
    st.session_state.episode_filter = "Semua"

def set_lokaliti_dan_wabak(lokaliti, wabak_no):
    st.session_state.selected_lokaliti = lokaliti
    st.session_state.selected_wabak = f"Wabak No: {wabak_no}"
    st.session_state.episode_filter = "Semua" 

def set_lokaliti_sahaja(lokaliti):
    st.session_state.selected_lokaliti = lokaliti
    st.session_state.selected_wabak = None
    st.session_state.episode_filter = "Semua" 

# --- ANTARA MUKA UTAMA ---
st.title("🦟 Dashboard Analisis Kes Denggi (Spesifik Wabak)")

uploaded_file = st.file_uploader("Muat Naik Fail Excel Data Denggi", type=['xlsx', 'xls', 'csv'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        df['Tarikh Daftar'] = pd.to_datetime(df['Tarikh Daftar'], errors='coerce')
        df['Tarikh Onset'] = pd.to_datetime(df['Tarikh Onset'], errors='coerce')
        
        # --- PENGIRAAN KEKERAPAN EPISODE WABAK KESELURUHAN ---
        df_wabak_sahaja = df[df['Jenis Kes'] == 'Wabak'].dropna(subset=['Wabak No'])
        kekerapan_wabak = df_wabak_sahaja.groupby('Lokaliti (Alamat Semasa)')['Wabak No'].nunique()
        semua_lokaliti_list = sorted(df['Lokaliti (Alamat Semasa)'].dropna().unique())
        episode_map = {lok: kekerapan_wabak.get(lok, 0) for lok in semua_lokaliti_list}
        
        # ---------------------------------------------------------
        # PENGURUSAN MENU SIDEBAR
        # ---------------------------------------------------------
        st.sidebar.header("Tetapan Analisis")
        
        episodes_ada = sorted(list(set(episode_map.values())))
        pilihan_tapis_ep = ["Semua"] + [f"{int(e)} Episode" for e in episodes_ada if e > 0]
        
        try:
            ep_idx = pilihan_tapis_ep.index(st.session_state.episode_filter)
        except ValueError:
            ep_idx = 0
            
        pilihan_filter_episode = st.sidebar.selectbox("1. Tapis Kekerapan (Episode):", pilihan_tapis_ep, index=ep_idx)
        st.session_state.episode_filter = pilihan_filter_episode
        
        if pilihan_filter_episode == "Semua":
            senarai_lokaliti_tapis = semua_lokaliti_list
        else:
            ep_val = int(pilihan_filter_episode.split()[0])
            senarai_lokaliti_tapis = sorted([lok for lok, count in episode_map.items() if count == ep_val])
        
        if not senarai_lokaliti_tapis:
            st.sidebar.warning("Tiada lokaliti untuk kategori ini.")
            pilihan_lokaliti = None
            df_lok = pd.DataFrame()
        else:
            index_lokaliti = 0
            if st.session_state.selected_lokaliti in senarai_lokaliti_tapis:
                index_lokaliti = senarai_lokaliti_tapis.index(st.session_state.selected_lokaliti)
                
            pilihan_lokaliti = st.sidebar.selectbox("2. Pilih Lokaliti", senarai_lokaliti_tapis, index=index_lokaliti)
            
            if pilihan_lokaliti != st.session_state.selected_lokaliti:
                st.session_state.selected_lokaliti = pilihan_lokaliti
                st.session_state.selected_wabak = None
                
            df_lok = df[df['Lokaliti (Alamat Semasa)'] == pilihan_lokaliti].copy()
            
        pilihan_kategori = None
        if not df_lok.empty:
            pilihan_wabak_list = []
            wabak_unik = df_lok[df_lok['Jenis Kes'] == 'Wabak']['Wabak No'].dropna().unique()
            for w in wabak_unik:
                pilihan_wabak_list.append(f"Wabak No: {w}")
            
            if 'Satu Kes' in df_lok['Jenis Kes'].values:
                pilihan_wabak_list.append("Satu Kes (Kes Terpencil)")
                
            index_wabak = 0
            if st.session_state.selected_wabak in pilihan_wabak_list:
                index_wabak = pilihan_wabak_list.index(st.session_state.selected_wabak)
                
            pilihan_kategori = st.sidebar.selectbox("3. Kategori Kes/Wabak:", pilihan_wabak_list, index=index_wabak)
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
                height=0
            )
        st.sidebar.markdown("*Tekan butang di atas dan pilih 'Save as PDF' sebagai destinasi cetakan.*")
        st.sidebar.markdown("---")

        
        # ---------------------------------------------------------
        # HIGHLIGHT 1: WABAK AKTIF SEMASA (TOP 5)
        # ---------------------------------------------------------
        df_aktif = df[(df['Jenis Kes'] == 'Wabak') & 
                      (df['Wabak Status'].notna()) & 
                      (~df['Wabak Status'].astype(str).str.contains('Tamat', case=False, na=False))].copy()
        
        st.markdown("---")
        st.header("🚨 Highlight: Wabak Aktif Semasa (Top 5)")
        
        if not df_aktif.empty:
            data_wabak_aktif = []
            grouped = df_aktif.groupby(['Lokaliti (Alamat Semasa)', 'Wabak No'])
            
            for (lokaliti, wabak_no), group in grouped:
                jumlah_k = len(group)
                tarikh_kes = group['Tarikh Daftar'].dropna().sort_values().tolist()
                
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
                
                data_wabak_aktif.append({
                    'Lokaliti': lokaliti,
                    'Wabak No': wabak_no,
                    'Jumlah Kes': jumlah_k,
                    'Tempoh (Hari)': tempoh_h,
                    'Kadar Peningkatan (%)': pct_inc
                })
                
            df_highlight = pd.DataFrame(data_wabak_aktif)
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.subheader("🚀 Kadar Peningkatan (%)")
                top_kadar = df_highlight.nlargest(5, 'Kadar Peningkatan (%)')
                for _, row in top_kadar.iterrows():
                    st.button(f"{row['Kadar Peningkatan (%)']:.1f}% - {row['Lokaliti']}", 
                              key=f"kadar_{row['Wabak No']}", 
                              on_click=set_lokaliti_dan_wabak, 
                              args=(row['Lokaliti'], row['Wabak No']), 
                              use_container_width=True)

            with c2:
                st.subheader("🔥 Jumlah Kes Tertinggi")
                top_kes = df_highlight.nlargest(5, 'Jumlah Kes')
                for _, row in top_kes.iterrows():
                    st.button(f"{row['Jumlah Kes']} Kes - {row['Lokaliti']}", 
                              key=f"kes_{row['Wabak No']}", 
                              on_click=set_lokaliti_dan_wabak, 
                              args=(row['Lokaliti'], row['Wabak No']), 
                              use_container_width=True)

            with c3:
                st.subheader("⏳ Tempoh Wabak Terlama")
                top_tempoh = df_highlight.nlargest(5, 'Tempoh (Hari)')
                for _, row in top_tempoh.iterrows():
                    st.button(f"{row['Tempoh (Hari)']} Hari - {row['Lokaliti']}", 
                              key=f"tempoh_{row['Wabak No']}", 
                              on_click=set_lokaliti_dan_wabak, 
                              args=(row['Lokaliti'], row['Wabak No']), 
                              use_container_width=True)
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
            
            # Baris Pertama (sehingga 5)
            cols1 = st.columns(min(len(items), 5))
            for i in range(min(len(items), 5)):
                lokaliti, count = items[i]
                with cols1[i]:
                    st.button(f"**{count} Episode**\n\n{lokaliti}", 
                              key=f"kekerapan1_{lokaliti}", 
                              on_click=set_lokaliti_sahaja, 
                              args=(lokaliti,), 
                              use_container_width=True)
            
            # Baris Kedua (jika lebih dari 5)
            if len(items) > 5:
                cols2 = st.columns(len(items) - 5)
                for i in range(5, len(items)):
                    lokaliti, count = items[i]
                    with cols2[i - 5]:
                        st.button(f"**{count} Episode**\n\n{lokaliti}", 
                                  key=f"kekerapan2_{lokaliti}", 
                                  on_click=set_lokaliti_sahaja, 
                                  args=(lokaliti,), 
                                  use_container_width=True)
        else:
            st.info("Tiada rekod episode wabak dikesan buat masa ini.")
            
        st.markdown("---")
        
        # ---------------------------------------------------------
        # ANALISIS LOKALITI & WABAK
        # ---------------------------------------------------------
        if not df_lok.empty and pilihan_kategori:
            if pilihan_kategori == "Satu Kes (Kes Terpencil)":
                df_filter = df_lok[df_lok['Jenis Kes'] == 'Satu Kes'].copy()
                status_wabak_semasa = "Tiada (Satu Kes)"
                tempoh_wabak_hari = 1
                tarikh_mula_str = "N/A"
            else:
                w_no = float(pilihan_kategori.replace("Wabak No: ", ""))
                df_filter = df_lok[df_lok['Wabak No'] == w_no].copy()
                status_wabak_semasa = str(df_filter['Wabak Status'].iloc[0])
                
                tarikh_kes = df_filter['Tarikh Daftar'].dropna().sort_values().tolist()
                
                if len(tarikh_kes) >= 2:
                    tarikh_mula = tarikh_kes[1]
                elif len(tarikh_kes) == 1:
                    tarikh_mula = tarikh_kes[0]
                else:
                    tarikh_mula = pd.Timestamp.today().normalize()
                
                tarikh_mula_str = tarikh_mula.strftime('%d-%m-%Y')
                
                if 'Tamat' in status_wabak_semasa:
                    tarikh_akhir = tarikh_kes[-1]
                else:
                    tarikh_akhir = pd.Timestamp.today().normalize()
                    
                tempoh_wabak_hari = max((tarikh_akhir - tarikh_mula).days, 1)
            
            jumlah_kes = len(df_filter)
            pentadbir_lokaliti = df_filter['Pihak Pentadbir Lokaliti'].mode()[0] if not df_filter['Pihak Pentadbir Lokaliti'].empty else "Tidak Dinyatakan"
            rekod_episode_lokaliti = episode_map.get(pilihan_lokaliti, 0)
            
            st.header(f"📍 Analisis Lokaliti: {pilihan_lokaliti}")
            st.subheader(f"Wabak: {pilihan_kategori} | Status: {status_wabak_semasa} | Pentadbir: {pentadbir_lokaliti}")
            
            # --- NOTA SEJARAH EPISODE WABAK & GRAF TREND ---
            st.markdown(f"*(**Rekod Sejarah:** Lokaliti ini telah mencatatkan **{rekod_episode_lokaliti} episode penularan wabak** secara keseluruhan)*")
            
            if rekod_episode_lokaliti > 0:
                df_wabak_lok = df_lok[df_lok['Jenis Kes'] == 'Wabak'].copy()
                if not df_wabak_lok.empty:
                    # Hasilkan Cross-Tabulation: Paksi X (Minggu Epid), Data (Wabak No)
                    pivot_epid = pd.crosstab(df_wabak_lok['Epid Minggu (Tkh Daftar)'], df_wabak_lok['Wabak No'])
                    
                    fig_sejarah, ax_sejarah = plt.subplots(figsize=(12, 4))
                    pivot_epid.plot(kind='bar', stacked=True, ax=ax_sejarah, colormap='tab20', edgecolor='black')
                    
                    ax_sejarah.set_xlabel("Minggu Epid")
                    ax_sejarah.set_ylabel("Jumlah Kes")
                    ax_sejarah.set_title(f"Sejarah Trend & Kekerapan Episode Wabak di {pilihan_lokaliti}")
                    ax_sejarah.legend(title="No. Wabak", bbox_to_anchor=(1.01, 1), loc='upper left')
                    plt.tight_layout()
                    
                    st.pyplot(fig_sejarah)
            # -----------------------------------------------

            col1, col2, col3, col4 = st.columns(4)
            kadar_velocity = jumlah_kes / tempoh_wabak_hari
            peratus_increment = (kadar_velocity / jumlah_kes) * 100 if jumlah_kes > 0 else 0
            
            col1.metric("Jumlah Kes", jumlah_kes)
            col2.metric(f"Tempoh (Hari) *Bermula {tarikh_mula_str}*", tempoh_wabak_hari)
            col3.metric("Velocity (Kes/Hari)", f"{kadar_velocity:.2f}")
            col4.metric("Peningkatan (% Harian)", f"{peratus_increment:.1f}%")
            
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
            # TABURAN KES MINGGU EPID (Khusus Wabak Terpilih Sahaja)
            # ---------------------------------------------------------
            st.subheader(f"📈 Taburan Kes Mengikut Minggu Epid ({pilihan_kategori})")
            kes_epid = df_filter['Epid Minggu (Tkh Daftar)'].value_counts().sort_index()
            
            if not kes_epid.empty:
                fig, ax = plt.subplots(figsize=(10, 3))
                kes_epid.plot(kind='bar', ax=ax, color='lightcoral', edgecolor='black')
                ax.set_xlabel("Minggu Epid")
                ax.set_ylabel("Jumlah Kes")
                st.pyplot(fig)
                
                minggu_puncak_txt = str(kes_epid.idxmax())
                kes_puncak = kes_epid.max()
                purata_mingguan = kes_epid.mean()
                
                ulasan_epid = f"**Analisis Terperinci Mingguan:**\n"
                ulasan_epid += f"- Secara purata, terdapat **{purata_mingguan:.1f} kes** didaftarkan setiap minggu.\n"
                ulasan_epid += f"- Minggu puncak bagi penularan ini adalah pada **Minggu Epid {minggu_puncak_txt}** dengan rekod tertinggi **{kes_puncak} kes**.\n"
                
                if len(kes_epid) >= 2:
                    m_kini = kes_epid.iloc[-1]
                    m_lalu = kes_epid.iloc[-2]
                    perbezaan = m_kini - m_lalu
                    status_arah_txt = "meningkat" if perbezaan > 0 else "menurun" if perbezaan < 0 else "mendatar"
                    ulasan_epid += f"- Perbandingan minggu terkini menunjukkan trend **{status_arah_txt}** ({m_kini} kes vs {m_lalu} kes pada minggu sebelumnya)."
                st.info(ulasan_epid)
                
            st.markdown("---")
            
            # ---------------------------------------------------------
            # TABURAN BLOK & TINGKAT + PERINCIAN
            # ---------------------------------------------------------
            st.subheader("🏢 Taburan Kes Mengikut Blok dan Tingkat")
            df_filter[['Blok', 'Tingkat']] = df_filter['No Rumah'].apply(parse_address)
            
            if len(df_filter['Blok'].unique()) > 1 or 'TIDAK PASTI' not in df_filter['Blok'].values:
                crosstab_bt = pd.crosstab(df_filter['Tingkat'], df_filter['Blok'], margins=True, margins_name="JUMLAH")
                
                def pad_for_sort(s):
                    return re.sub(r'\d+', lambda m: m.group(0).zfill(5), str(s))
                
                tingkat_list = list(crosstab_bt.index[:-1])
                blok_list = list(crosstab_bt.columns[:-1])
                
                tingkat_sorted = sorted(tingkat_list, key=pad_for_sort, reverse=True)
                blok_sorted = sorted(blok_list, key=pad_for_sort)
                
                crosstab_bt = crosstab_bt.loc[tingkat_sorted + ['JUMLAH'], blok_sorted + ['JUMLAH']]

                idx_slice = pd.IndexSlice[crosstab_bt.index[:-1], crosstab_bt.columns[:-1]]
                styled_ct = crosstab_bt.style.background_gradient(cmap='Reds', subset=idx_slice)
                st.markdown(styled_ct.to_html(), unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                for t in crosstab_bt.index[:-1]:
                    for b in crosstab_bt.columns[:-1]:
                        if crosstab_bt.loc[t, b] > max_val_specific:
                            max_val_specific = crosstab_bt.loc[t, b]
                            max_b_specific = str(b)
                            max_t_specific = str(t)

                blok_totals = crosstab_bt.loc['JUMLAH'][:-1]
                if not blok_totals.empty and blok_totals.max() > 0:
                    blok_masalah_txt = str(blok_totals.idxmax())
                
                tingkat_totals = crosstab_bt.iloc[:-1]['JUMLAH']
                if not tingkat_totals.empty and tingkat_totals.max() > 0:
                    tingkat_masalah_txt = str(tingkat_totals.idxmax())

                if max_val_specific > 0:
                    st.warning(f"⚠️ **Sarang Penularan Spesifik:** Takungan vektor berjangkit (hotspot selular) dipercayai tertumpu secara spesifik di kediaman **Blok {max_b_specific}, Tingkat {max_t_specific}** yang menyumbang **{max_val_specific} kes**. Operasi pemusnahan sumber (S&D) dan semburan ruang disarankan untuk difokuskan bermula dari struktur radius ini terlebih dahulu sebelum diperluas ke tempat lain.")

                st.markdown("##### **Perincian Struktur (Keseluruhan Blok & Tingkat):**")
                
                blok_group_raw = df_filter[df_filter['Blok'] != 'TIDAK PASTI'].groupby('Blok').size()
                
                if not blok_group_raw.empty:
                    sorted_blok_keys = sorted(blok_group_raw.index, key=pad_for_sort)
                    for blok_name in sorted_blok_keys:
                        b_count = blok_group_raw[blok_name]
                        b_pct = (b_count / jumlah_kes) * 100
                        st.markdown(f"**🔹 Blok {blok_name}: {b_count} kes ({b_pct:.1f}% dari keseluruhan wabak)**")
                        
                        df_blok_ini = df_filter[(df_filter['Blok'] == blok_name) & (df_filter['Tingkat'] != 'TIDAK PASTI')]
                        if not df_blok_ini.empty:
                            tingkat_group_raw = df_blok_ini.groupby('Tingkat').size()
                            sorted_tingkat_keys = sorted(tingkat_group_raw.index, key=pad_for_sort, reverse=True)
                            
                            for tk_name in sorted_tingkat_keys:
                                t_count = tingkat_group_raw[tk_name]
                                t_pct_overall = (t_count / jumlah_kes) * 100
                                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;🔸 Tingkat {tk_name}: {t_count} kes ({t_pct_overall:.1f}%)")
                else:
                    st.write("Maklumat blok tidak cukup berstruktur.")
            else:
                st.info("Tiada struktur blok/tingkat yang jelas ditemui pada 'No Rumah'.")

            st.markdown("---")

            # ---------------------------------------------------------
            # 5 KES TERKINI DENGAN LOKASI (BLOK & TINGKAT)
            # ---------------------------------------------------------
            st.subheader("📍 Analisis 5 Kes Terkini")
            
            top5_daftar = df_filter.sort_values(by='Tarikh Daftar', ascending=False).head(5)
            top5_onset = df_filter.sort_values(by='Tarikh Onset', ascending=False).head(5)
            common_indices = set(top5_daftar.index).intersection(set(top5_onset.index))
            
            def highlight_common(row):
                return ['background-color: #ffd700; color: black' if row.name in common_indices else '' for _ in row]

            col_t1, col_t2 = st.columns(2)
            
            with col_t1:
                st.markdown("**Berdasarkan Tarikh Daftar (Terkini)**")
                st.markdown(top5_daftar[['Tarikh Daftar', 'No Rumah', 'Blok', 'Tingkat']].style.apply(highlight_common, axis=1).to_html(), unsafe_allow_html=True)
                
            with col_t2:
                st.markdown("**Berdasarkan Tarikh Onset (Terkini)**")
                st.markdown(top5_onset[['Tarikh Onset', 'No Rumah', 'Blok', 'Tingkat']].style.apply(highlight_common, axis=1).to_html(), unsafe_allow_html=True)
                
            st.markdown("<br>**Ulasan Terperinci Kes Terkini:**", unsafe_allow_html=True)
            
            daftar_locs = top5_daftar.apply(lambda x: f"Blok {x['Blok']} Tingkat {x['Tingkat']}", axis=1).tolist()
            onset_locs = top5_onset.apply(lambda x: f"Blok {x['Blok']} Tingkat {x['Tingkat']}", axis=1).tolist()
            
            st.write(f"- **Pendaftaran Terkini:** 5 kes terakhir bertumpu di **{', '.join(daftar_locs)}**.")
            st.write(f"- **Gejala (Onset) Terbaharu:** 5 pesakit terbaharu dikesan menetap di **{', '.join(onset_locs)}**.")
            
            if common_indices:
                st.info(f"💡 Terdapat **{len(common_indices)} kes (diwarnakan kuning)** yang saling bertindih di antara Pendaftaran Terkini dan Onset Terkini, menandakan penularan sangat aktif dan baru (fresh outbreak) sedang berlaku.")
            else:
                st.info("💡 Tiada pertindihan ketara dikesan di antara kes onset terkini dan pendaftaran terkini. Pendaftaran terkini berkemungkinan melibatkan kes tertangguh dari minggu sebelumnya.")
            
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
                fasiliti_count = df_filter['Kemudahan Kesihatan(Maklumat Pemberitahu)'].value_counts()
                if not fasiliti_count.empty:
                    fasiliti_utama_txt = fasiliti_count.index[0]
                for f, count in fasiliti_count.items():
                    pct = (count / jumlah_kes) * 100
                    st.write(f"- **{f}**: {count} ({pct:.1f}%)")
                    
            with c_info2:
                st.subheader("Kewarganegaraan")
                warga_count = df_filter['Status Kewarganegaraan'].value_counts()
                if not warga_count.empty:
                    top_warga = warga_count.index[0]
                for w, count in warga_count.items():
                    pct = (count / jumlah_kes) * 100
                    st.write(f"- **{w}**: {count} ({pct:.1f}%)")

            with c_info3:
                st.subheader("Pekerjaan")
                kerja_count = df_filter['Pekerjaan'].value_counts()
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
            zon_str = ', '.join(zon_bahaya_semasa) if zon_bahaya_semasa else "Tidak Dinyatakan"

            ayat_hotspot = f"Titik jangkitan tertumpu secara kritikal disahkan berada pada Blok {max_b_specific} Tingkat {max_t_specific}." if max_b_specific != "Tidak Dinyatakan" else ""

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
