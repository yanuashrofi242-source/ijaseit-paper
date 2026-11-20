# Kamus data dan profil awal

Dihasilkan otomatis dari `raw/`. Kolom 'Arti' dan 'Peran' diisi manual; tanda (dugaan) perlu Anda konfirmasi.

## 1. data-opt_kecamatan-kalisat_2021-2026 (csv dan xlsx)

- Ukuran: 585 baris x 57 kolom
- **Peran di paper:** Ground truth serangan OPT (target) dan satu-satunya data lapang nyata; inti klaim N1.
- **Masalah:**
  - Cuaca bulanan sebagian besar tidak asli (hanya 29% bulan berubah; Patempuran 2 nilai suhu unik).
  - 71% bulan tanpa serangan; 17 kolom spesies bernilai nol semua. Spesies bermakna: Hdb, Pbp, Wbc, Blas, Tikus, Hpp, Tungro, Lalat Daun.
  - Tingkat_Keparahan dan Aktif_OPT diturunkan dari LKSJ; jangan jadi fitur. Versi xlsx dan csv beda di kolom ini saja.
  - Hanya 585 baris (9 desa x 65 bulan): perlu validasi hati-hati dan interval kepercayaan.

| Kolom | Tipe | Hilang | Rentang / contoh | Arti |
| --- | --- | --- | --- | --- |
| Desa | object | 0 | unik 9; mis. Ajung, Gambiran, Glagahwero | desa di Kecamatan Kalisat |
| Date | datetime64[ns] | 0 | 2021-01-01 s.d. 2026-05-01 | bulan pengamatan (tanggal 1) |
| Tahun | int64 | 0 | 2021 s.d. 2026, unik 6 |  |
| Bulan | int64 | 0 | 1 s.d. 12, unik 12 |  |
| LT | float64 | 0 | 0 s.d. 434, unik 57 | luas tanaman padi, ha (keterangan sumber) |
| SSR | float64 | 0 | 0 s.d. 2.4, unik 21 | serangan sangat ringan, ha, periode berjalan (keterangan sumber) |
| SSS | float64 | 0 | 0 s.d. 0.5, unik 4 | serangan sedang, ha (keterangan sumber) |
| SSB | float64 | 0 | 0 s.d. 0, unik 1 | serangan berat, ha (keterangan sumber) |
| SSP | float64 | 0 | 0 s.d. 0, unik 1 | serangan puso/gagal panen, ha (keterangan sumber) |
| SSJ | float64 | 0 | 0 s.d. 2.4, unik 21 | jumlah serangan periode berjalan = SSR+SSS+SSB+SSP (cocok 99,8% baris) |
| LKSJ | float64 | 0 | 0 s.d. 3.8, unik 32 | KONFLIK: keterangan sumber menyebut luas kendali jumlah, tetapi data berperilaku sebagai luas keadaan serangan (>= SSJ di 99,8% baris; kolom spesies LKSJ_* berjumlah tepat LKSJ; hanya 82% <= Jumlah pengendali). Perlu konfirmasi sumber; target utama |
| Terkendali | float64 | 0 | 0 s.d. 2, unik 17 | luas terkendali, ha |
| Kimia | float64 | 0 | 0 s.d. 10, unik 29 | pengendalian kimia, ha |
| Hayati | float64 | 0 | 0 s.d. 1.3, unik 5 | pengendalian hayati, ha |
| Eradikasi | float64 | 0 | 0 s.d. 0, unik 1 | eradikasi, ha |
| CL | float64 | 0 | 0 s.d. 0.75, unik 2 | metode pengendalian lain, ha (singkatan belum jelas: sumber menulis chemical liquid / kontak lokal) |
| Jumlah pengendali | float64 | 0 | 0 s.d. 10, unik 31 | jumlah luas pengendalian = Kimia+Hayati+Eradikasi+CL (cocok 99,5% baris) |
| LKSJ_Anjing Tanah | float64 | 0 | 0 s.d. 0, unik 1 |  |
| LKSJ_Bacterial Grain Rot (Busuk Bulir) | float64 | 0 | 0 s.d. 0, unik 1 |  |
| LKSJ_Belalang | float64 | 0 | 0 s.d. 0, unik 1 |  |
| LKSJ_Blas | float64 | 0 | 0 s.d. 2, unik 9 | serangan blas, ha |
| LKSJ_Bls | int64 | 0 | 0 s.d. 0, unik 1 |  |
| LKSJ_Brs | float64 | 0 | 0 s.d. 0, unik 1 |  |
| LKSJ_Burung | float64 | 0 | 0 s.d. 0, unik 1 |  |
| LKSJ_Gulma | float64 | 0 | 0 s.d. 0, unik 1 |  |
| LKSJ_Hawar Pelepah | float64 | 0 | 0 s.d. 0, unik 1 |  |
| LKSJ_Hdb | float64 | 0 | 0 s.d. 1.6, unik 16 | keadaan serangan Hdb (hawar daun bakteri), ha (keterangan sumber) |
| LKSJ_Hpp | float64 | 0 | 0 s.d. 2, unik 6 | keadaan serangan Hpp, ha (tidak ada di keterangan sumber; hama putih palsu masih dugaan) |
| LKSJ_Keong Mas | float64 | 0 | 0 s.d. 0, unik 1 |  |
| LKSJ_Kepinding Tanah | float64 | 0 | 0 s.d. 0, unik 1 |  |
| LKSJ_Kerdil Rumput | float64 | 0 | 0 s.d. 0, unik 1 |  |
| LKSJ_Lalat Bibit | int64 | 0 | 0 s.d. 0, unik 1 |  |
| LKSJ_Lalat Daun | float64 | 0 | 0 s.d. 2, unik 4 | serangan lalat daun, ha |
| LKSJ_Pbp | float64 | 0 | 0 s.d. 2, unik 17 | keadaan serangan Pbp (penggerek batang padi), ha (keterangan sumber) |
| LKSJ_Penyakit Hawar Pelepah (Rhizoctonia Oryzae) | float64 | 0 | 0 s.d. 0, unik 1 |  |
| LKSJ_Tikus | float64 | 0 | 0 s.d. 1.5, unik 5 | serangan tikus, ha |
| LKSJ_Tungro | float64 | 0 | 0 s.d. 1.5, unik 3 | serangan tungro, ha |
| LKSJ_Walang Sangit | float64 | 0 | 0 s.d. 0, unik 1 |  |
| LKSJ_Wbc | float64 | 0 | 0 s.d. 2.3, unik 15 | keadaan serangan Wbc (wereng batang coklat), ha (keterangan sumber) |
| Kecamatan | object | 0 | unik 3; mis. Ajung, Kalisat, Panti |  |
| Latitude | float64 | 0 | -8.246 s.d. -8.1, unik 9 | lintang desa |
| Longitude | float64 | 0 | 113.6 s.d. 113.8, unik 9 | bujur desa |
| temp | float64 | 0 | 20.56 s.d. 27, unik 121 | suhu bulanan (diragukan, lihat audit) |
| humidity | float64 | 0 | 75 s.d. 90.62, unik 120 | kelembapan (diragukan) |
| precip | float64 | 0 | 0.324 s.d. 21.03, unik 122 | curah hujan (diragukan) |
| windspeed | float64 | 0 | 3.71 s.d. 11.96, unik 111 | kecepatan angin (diragukan) |
| anomaly_score | float64 | 0 | 0 s.d. 0.06667, unik 7 | skor anomali (asal tidak diketahui; tidak dipakai) |
| temp_rolling_avg_7d | float64 | 0 | 20.6 s.d. 26.99, unik 122 |  |
| humidity_rolling_avg_7d | float64 | 0 | 75.21 s.d. 90.08, unik 121 |  |
| precip_rolling_avg_7d | float64 | 0 | 0.5046 s.d. 20.89, unik 122 |  |
| vpd | float64 | 0 | 0.2582 s.d. 0.7901, unik 122 | defisit tekanan uap, kPa (diragukan) |
| lwd | float64 | 0 | 0 s.d. 4.045, unik 122 | lama daun basah (diragukan) |
| Tingkat_Keparahan | object | 0 | unik 4; mis. Sedang, Agak Stabil, Stabil | kelas keparahan turunan LKSJ; bukan fitur (bocor) |
| Aktif_OPT | object | 0 | unik 80; mis. Pbp (1.5 ha), Tikus (0.3 ha), Tikus (0.3 ha), Tidak Ada | teks turunan LKSJ; bukan fitur (bocor) |
| longitude_fixed | float64 | 0 | 113.6 s.d. 113.8, unik 9 | koordinat alternatif |
| latitude_fixed | float64 | 0 | -8.215 s.d. -8.1, unik 9 | koordinat alternatif |
| coord_status | object | 0 | unik 2; mis. fixed, original | penanda koreksi koordinat |

## 2. data_terlabel.csv (BMKG harian, label Mongso)

- Ukuran: 7306 baris x 6 kolom
- **Peran di paper:** Bahan audit label (N4) dan, bila tanggalnya ditemukan, pra-latih prakiraan. Bukan target hama.
- **Masalah:**
  - Tidak ada kolom tanggal dan urutan baris acak: tidak bisa dipakai untuk deret waktu atau split kronologis.
  - 457 baris duplikat; 4 nilai hujan 999 (kode data hilang); kelas Kasadasa (155 baris) bercurah hujan rata-rata 225 mm/hari dan kelembapan persis rata-rata (diduga imputasi).
  - Mongso dapat ditebak pohon keputusan 98,7% (terutama dari kecepatan dan arah angin): label turunan aturan.

| Kolom | Tipe | Hilang | Rentang / contoh | Arti |
| --- | --- | --- | --- | --- |
| Temperatur | float64 | 0 | 24.2 s.d. 30.8, unik 138 | suhu, C |
| Kelembaban | float64 | 0 | 56 s.d. 97, unik 42 | RH, % |
| Curah Hujan (mm) | float64 | 0 | 0 s.d. 999, unik 1467 | hujan harian, mm (999 = kode hilang) |
| Arah Angin (derajat) | float64 | 0 | 0 s.d. 360, unik 45 | arah angin, derajat |
| Kecepatan Angin rata-rata (m/s) | float64 | 0 | 0 s.d. 8, unik 11 | kecepatan angin, m/s |
| Mongso | object | 0 | unik 12; mis. Kawolu, Dhesta, Kapitu | fase Pranata Mangsa (label) |

## 3. dataset_cuaca_hama_final_v2 (Open-Meteo per jam, 2022-2024)

- Ukuran: 26304 baris x 12 kolom
- **Peran di paper:** Bahan audit label (N4); cuacanya diganti unduhan ulang untuk model prakiraan.
- **Masalah:**
  - Hujan tahunan hanya 138, 13, 14 mm: kolom hujan tidak valid.
  - Kolom waktu diduga UTC (UV puncak pukul 05:00).
  - risk_score = fungsi linear fitur (R2 1,00); pest_type berpasangan tetap dengan risk_level: label buatan aturan.
  - Lokasi titik koordinat tidak tercatat.

| Kolom | Tipe | Hilang | Rentang / contoh | Arti |
| --- | --- | --- | --- | --- |
| time | datetime64[ns] | 0 | 2022-01-01 s.d. 2024-12-31 |  |
| temperature_2m (°C) | float64 | 0 | 21.8 s.d. 36.7, unik 144 |  |
| rain (mm) | float64 | 0 | 0 s.d. 13.8, unik 29 |  |
| wind_speed_10m (km/h) | float64 | 0 | 0 s.d. 24.8, unik 228 |  |
| temperature_80m (°C) | float64 | 0 | 21.6 s.d. 34.4, unik 129 | suhu 80 m |
| uv_index () | float64 | 0 | 0 s.d. 9.7, unik 195 | indeks UV |
| relative_humidity_2m (%) | int64 | 0 | 24 s.d. 96, unik 72 |  |
| wind_direction_10m (°) | int64 | 0 | 1 s.d. 360, unik 355 |  |
| risk_score | float64 | 0 | 17.87 s.d. 48.7, unik 3294 | skor risiko buatan aturan |
| risk_level | object | 0 | unik 3; mis. high, medium, low | low/medium/high dari skor |
| pest_type | object | 0 | unik 6; mis. Penggerek Batang, Tungro, Walang Sangit | jenis hama (buatan aturan) |
| risk_numeric | int64 | 0 | 0 s.d. 2, unik 3 | 0/1/2 dari risk_level |

## 4. dataset hasil cuacaPintar (sensor cuaca)

- Ukuran: 246 baris x 22 kolom
- **Peran di paper:** Data sensor lokal untuk fusi N3 dan validasi Open-Meteo; saat ini hanya contoh pendahuluan.
- **Masalah:**
  - 246 baris, 21-27 Oct 2026, celah hingga 53 jam; lokasi Surabaya (-7,34; 112,78), bukan Kalisat.
  - Kolom pred_temp, pred_humid, pred_wind_speed kosong semua.
  - Hujan nyaris nol; UV 4,7-25,5 bukan skala indeks UV.

| Kolom | Tipe | Hilang | Rentang / contoh | Arti |
| --- | --- | --- | --- | --- |
| captured_at | object | 0 | unik 142; mis. 2026-10-21 23:58:44, 2026-10-22 00:00:44, 2026-10-22 00:02:44 | waktu ambil data |
| time_wib | object | 0 | unik 142; mis. 2026-10-21 23:58:44, 2026-10-22 00:00:44, 2026-10-22 00:02:44 |  |
| sensor_valid | bool | 0 | 1 s.d. 1, unik 1 | penanda valid |
| temperature | float64 | 0 | 26.7 s.d. 38.9, unik 40 | suhu, C |
| pred_temp | float64 | 246 | nan s.d. nan, unik 0 |  |
| humidity | float64 | 0 | 38.6 s.d. 99.9, unik 86 | RH, % |
| pred_humid | float64 | 246 | nan s.d. nan, unik 0 |  |
| pressure | float64 | 0 | 1008 s.d. 1015, unik 41 | tekanan, hPa |
| uv | float64 | 0 | 4.7 s.d. 25.5, unik 51 | UV (skala tidak jelas) |
| wind_angle | int64 | 0 | 0 s.d. 315, unik 6 | arah angin |
| wind_rt | float64 | 0 | 0 s.d. 1.9, unik 7 | angin sesaat |
| pred_wind_speed | float64 | 246 | nan s.d. nan, unik 0 |  |
| wind_avg | float64 | 0 | 0 s.d. 1.3, unik 5 | angin rata-rata |
| wind_max | float64 | 0 | 0 s.d. 2.9, unik 9 | angin maksimum |
| rain_1m | int64 | 0 | 0 s.d. 0, unik 1 | hujan 1 menit |
| rain_1h | float64 | 0 | 0 s.d. 0.3, unik 2 | hujan 1 jam |
| rain_24h | float64 | 0 | 0 s.d. 0.3, unik 2 | hujan 24 jam |
| rain_total | int64 | 0 | 0 s.d. 1, unik 2 | hujan total |
| gps_hasFix | bool | 0 | 1 s.d. 1, unik 1 |  |
| gps_lat | float64 | 0 | -7.337 s.d. -7.337, unik 56 | lintang GPS |
| gps_lon | float64 | 0 | 112.8 s.d. 112.8, unik 68 | bujur GPS |
| gps_alt | float64 | 0 | 5.4 s.d. 50.5, unik 109 |  |

## 5. PROGRAM PREDIKSI.ipynb dan PROGRAM KLASIFIKASI.ipynb

- **Peran:** kode asal draft IES; dipakai hanya sebagai rujukan replikasi, tidak diteruskan.
- Prediksi membaca `Data20.csv` (tidak ada di folder) dan memakai split acak; klasifikasi membaca `data_terlabel.csv` dengan SMOTE sebelum split.
- Berkas `pranata_mangsa.csv`, `svm_model.pkl`, `prediksi1.keras` dirujuk tetapi tidak ada di folder.

