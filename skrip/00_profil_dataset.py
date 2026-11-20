"""Kamus data + profil awal semua dataset (membaca raw/, menulis hasil/kamus_data.md).
Pakai: python 00_profil_dataset.py <folder kerja>"""
import sys
import numpy as np, pandas as pd
root = sys.argv[1]; raw = f"{root}/raw"
L = ["# Kamus data dan profil awal", "", "Dihasilkan otomatis dari `raw/`. Kolom 'Arti' dan 'Peran' diisi manual; tanda (dugaan) perlu Anda konfirmasi.", ""]

def table(df, notes=None, maxcols=80):
    notes = notes or {}
    rows = ["| Kolom | Tipe | Hilang | Rentang / contoh | Arti |", "| --- | --- | --- | --- | --- |"]
    for c in list(df.columns)[:maxcols]:
        s = df[c]
        if pd.api.types.is_numeric_dtype(s):
            rng = f"{s.min():.4g} s.d. {s.max():.4g}, unik {s.nunique()}"
        elif pd.api.types.is_datetime64_any_dtype(s):
            rng = f"{s.min():%Y-%m-%d} s.d. {s.max():%Y-%m-%d}"
        else:
            v = s.dropna().astype(str).unique()[:3]; rng = f"unik {s.nunique()}; mis. " + ", ".join(v)
        rows.append(f"| {c} | {s.dtype} | {int(s.isna().sum())} | {rng} | {notes.get(c, '')} |")
    return rows

def section(title, role, issues, df, notes=None):
    L.extend([f"## {title}", "", f"- Ukuran: {df.shape[0]} baris x {df.shape[1]} kolom", f"- **Peran di paper:** {role}", "- **Masalah:**"] + [f"  - {i}" for i in issues] + [""] + table(df, notes) + [""])

# 1 OPT Kalisat
o = pd.read_csv(f"{raw}/data-opt_kecamatan-kalisat_2021-2026.csv", parse_dates=["Date"])
notes = {"Desa": "desa di Kecamatan Kalisat", "Date": "bulan pengamatan (tanggal 1)", "LT": "luas tanaman padi, ha (keterangan sumber)",
         "SSR": "serangan sangat ringan, ha, periode berjalan (keterangan sumber)", "SSS": "serangan sedang, ha (keterangan sumber)", "SSB": "serangan berat, ha (keterangan sumber)", "SSP": "serangan puso/gagal panen, ha (keterangan sumber)",
         "SSJ": "jumlah serangan periode berjalan = SSR+SSS+SSB+SSP (cocok 99,8% baris)", "LKSJ": "KONFLIK: keterangan sumber menyebut luas kendali jumlah, tetapi data berperilaku sebagai luas keadaan serangan (>= SSJ di 99,8% baris; kolom spesies LKSJ_* berjumlah tepat LKSJ; hanya 82% <= Jumlah pengendali). Perlu konfirmasi sumber; target utama", "Terkendali": "luas terkendali, ha",
         "Kimia": "pengendalian kimia, ha", "Hayati": "pengendalian hayati, ha", "Eradikasi": "eradikasi, ha", "CL": "metode pengendalian lain, ha (singkatan belum jelas: sumber menulis chemical liquid / kontak lokal)",
         "Jumlah pengendali": "jumlah luas pengendalian = Kimia+Hayati+Eradikasi+CL (cocok 99,5% baris)", "LKSJ_Hdb": "keadaan serangan Hdb (hawar daun bakteri), ha (keterangan sumber)", "LKSJ_Pbp": "keadaan serangan Pbp (penggerek batang padi), ha (keterangan sumber)",
         "LKSJ_Wbc": "keadaan serangan Wbc (wereng batang coklat), ha (keterangan sumber)", "LKSJ_Blas": "serangan blas, ha", "LKSJ_Hpp": "keadaan serangan Hpp, ha (tidak ada di keterangan sumber; hama putih palsu masih dugaan)",
         "LKSJ_Tikus": "serangan tikus, ha", "LKSJ_Tungro": "serangan tungro, ha", "LKSJ_Lalat Daun": "serangan lalat daun, ha",
         "Latitude": "lintang desa", "Longitude": "bujur desa", "temp": "suhu bulanan (diragukan, lihat audit)", "humidity": "kelembapan (diragukan)",
         "precip": "curah hujan (diragukan)", "windspeed": "kecepatan angin (diragukan)", "vpd": "defisit tekanan uap, kPa (diragukan)", "lwd": "lama daun basah (diragukan)",
         "anomaly_score": "skor anomali (asal tidak diketahui; tidak dipakai)", "Tingkat_Keparahan": "kelas keparahan turunan LKSJ; bukan fitur (bocor)",
         "Aktif_OPT": "teks turunan LKSJ; bukan fitur (bocor)", "latitude_fixed": "koordinat alternatif", "longitude_fixed": "koordinat alternatif", "coord_status": "penanda koreksi koordinat"}
section("1. data-opt_kecamatan-kalisat_2021-2026 (csv dan xlsx)", "Ground truth serangan OPT (target) dan satu-satunya data lapang nyata; inti klaim N1.",
        ["Cuaca bulanan sebagian besar tidak asli (hanya 29% bulan berubah; Patempuran 2 nilai suhu unik).",
         "71% bulan tanpa serangan; 17 kolom spesies bernilai nol semua. Spesies bermakna: Hdb, Pbp, Wbc, Blas, Tikus, Hpp, Tungro, Lalat Daun.",
         "Tingkat_Keparahan dan Aktif_OPT diturunkan dari LKSJ; jangan jadi fitur. Versi xlsx dan csv beda di kolom ini saja.",
         "Hanya 585 baris (9 desa x 65 bulan): perlu validasi hati-hati dan interval kepercayaan."], o, notes)

# 2 data_terlabel
d = pd.read_csv(f"{raw}/data_terlabel.csv")
section("2. data_terlabel.csv (BMKG harian, label Mongso)", "Bahan audit label (N4) dan, bila tanggalnya ditemukan, pra-latih prakiraan. Bukan target hama.",
        ["Tidak ada kolom tanggal dan urutan baris acak: tidak bisa dipakai untuk deret waktu atau split kronologis.",
         "457 baris duplikat; 4 nilai hujan 999 (kode data hilang); kelas Kasadasa (155 baris) bercurah hujan rata-rata 225 mm/hari dan kelembapan persis rata-rata (diduga imputasi).",
         "Mongso dapat ditebak pohon keputusan 98,7% (terutama dari kecepatan dan arah angin): label turunan aturan."], d,
        {"Mongso": "fase Pranata Mangsa (label)", "Temperatur": "suhu, C", "Kelembaban": "RH, %", "Curah Hujan (mm)": "hujan harian, mm (999 = kode hilang)",
         "Arah Angin (derajat)": "arah angin, derajat", "Kecepatan Angin rata-rata (m/s)": "kecepatan angin, m/s"})

# 3 Open-Meteo per jam
h = pd.read_excel(f"{raw}/dataset_cuaca_hama_final_v2 (1).xlsx")
section("3. dataset_cuaca_hama_final_v2 (Open-Meteo per jam, 2022-2024)", "Bahan audit label (N4); cuacanya diganti unduhan ulang untuk model prakiraan.",
        ["Hujan tahunan hanya 138, 13, 14 mm: kolom hujan tidak valid.", "Kolom waktu diduga UTC (UV puncak pukul 05:00).",
         "risk_score = fungsi linear fitur (R2 1,00); pest_type berpasangan tetap dengan risk_level: label buatan aturan.",
         "Lokasi titik koordinat tidak tercatat."], h,
        {"risk_score": "skor risiko buatan aturan", "risk_level": "low/medium/high dari skor", "pest_type": "jenis hama (buatan aturan)", "risk_numeric": "0/1/2 dari risk_level",
         "temperature_80m (°C)": "suhu 80 m", "uv_index ()": "indeks UV"})

# 4 sensor
c = pd.read_excel(f"{raw}/dataset hasil cuacaPintar.xlsx")
section("4. dataset hasil cuacaPintar (sensor cuaca)", "Data sensor lokal untuk fusi N3 dan validasi Open-Meteo; saat ini hanya contoh pendahuluan.",
        ["246 baris, 21-27 Oct 2026, celah hingga 53 jam; lokasi Surabaya (-7,34; 112,78), bukan Kalisat.",
         "Kolom pred_temp, pred_humid, pred_wind_speed kosong semua.", "Hujan nyaris nol; UV 4,7-25,5 bukan skala indeks UV."], c,
        {"captured_at": "waktu ambil data", "sensor_valid": "penanda valid", "temperature": "suhu, C", "humidity": "RH, %", "pressure": "tekanan, hPa",
         "uv": "UV (skala tidak jelas)", "wind_angle": "arah angin", "wind_rt": "angin sesaat", "wind_avg": "angin rata-rata", "wind_max": "angin maksimum",
         "rain_1m": "hujan 1 menit", "rain_1h": "hujan 1 jam", "rain_24h": "hujan 24 jam", "rain_total": "hujan total", "gps_lat": "lintang GPS", "gps_lon": "bujur GPS"})

# 5 notebooks
L += ["## 5. PROGRAM PREDIKSI.ipynb dan PROGRAM KLASIFIKASI.ipynb", "",
      "- **Peran:** kode asal draft IES; dipakai hanya sebagai rujukan replikasi, tidak diteruskan.",
      "- Prediksi membaca `Data20.csv` (tidak ada di folder) dan memakai split acak; klasifikasi membaca `data_terlabel.csv` dengan SMOTE sebelum split.",
      "- Berkas `pranata_mangsa.csv`, `svm_model.pkl`, `prediksi1.keras` dirujuk tetapi tidak ada di folder.", ""]
open(f"{root}/hasil/kamus_data.md", "w", encoding="utf8").write("\n".join(L) + "\n")
print("ok", len(L), "baris")
