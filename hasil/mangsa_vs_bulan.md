# Pranata Mangsa vs bulan kalender (data Kalisat)

549 baris desa x bulan. Mangsa ditetapkan dari tanggal tengah bulan (versi umum Surakarta), jadi resolusi bulanan membatasi uji ini; ulangi dengan data harian bila ada.

## Serangan per mangsa (bulan berjalan)

| Mangsa | n | % bulan ada serangan | Rata-rata LKSJ (ha) |
| --- | --- | --- | --- |
| Kasa | 45.0 | 29.0 | 0.16 |
| Karo | 45.0 | 11.0 | 0.1 |
| Katelu | 45.0 | 13.0 | 0.14 |
| Kalima | 45.0 | 13.0 | 0.04 |
| Kanem | 90.0 | 28.0 | 0.18 |
| Kapitu | 45.0 | 33.0 | 0.21 |
| Kawolu | 45.0 | 44.0 | 0.35 |
| Kasanga | 45.0 | 42.0 | 0.18 |
| Kasadasa | 54.0 | 37.0 | 0.23 |
| Sadha | 90.0 | 32.0 | 0.24 |

Uji Kruskal-Wallis LKSJ antar kelompok: mangsa p = 0.001; bulan kalender p = 0.002.

## Prediksi serangan bulan berikutnya (logistik, rolling-origin 2023, 2024, 2025+)

| Prediktor | AUC | PR-AUC |
| --- | --- | --- |
| Pranata Mangsa saja (12 fase) | 0.579 | 0.341 |
| Bulan kalender saja (12 bulan) | 0.574 | 0.339 |
| Desa saja | 0.734 | 0.554 |
| Persistensi (bulan ini ada serangan) | 0.701 | 0.459 |
| Mangsa + riwayat serangan | 0.693 | 0.552 |
| Bulan + riwayat serangan | 0.687 | 0.546 |

Catatan: nilai AUC dekat 0,5 berarti penanda musim tidak informatif untuk prediksi lintas tahun. Uji kecil; baca bersama interval kepercayaan dari `06_model_risiko.py`.
