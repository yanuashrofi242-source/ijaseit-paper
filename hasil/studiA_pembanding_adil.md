# Studi A, tahap 4: pembanding adil, konformal adaptif, uji DM

Arsip NWP: ECMWF IFS 0,25 derajat (Open-Meteo Previous Runs), kebenaran = reanalisis Open-Meteo (bukan stasiun). Uji dari 2025-07-01 (n hari per sel: 487). MAE dalam satuan asli; skill = 1 - MAE/MAE NWP mentah.
Ridge walk-forward: refit tiap 30 hari dengan jendela 540 hari terakhir yang sudah terverifikasi pada saat prakiraan dibuat. Persistensi dan bias bergulir memakai informasi yang sama (tertunda L hari).

## Kalisat: MAE per metode

| Variabel | Lead | NWP mentah | Persistensi | Bias bergulir 30 hari | Rata-rata (bias bergulir, persistensi) | Ridge tetap | Ridge walk-forward | LightGBM residu walk-forward |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| suhu (C) | 1 | 0.64 | 0.51 | 0.34 | 0.35 | 0.33 | **0.33** | 0.34 |
| suhu (C) | 3 | 0.66 | 0.72 | 0.45 | 0.48 | **0.43** | 0.45 | 0.47 |
| suhu (C) | 7 | 0.73 | 0.82 | **0.56** | 0.59 | 0.61 | 0.56 | 0.57 |
| rh (%) | 1 | 4.76 | 3.66 | 2.76 | 2.73 | 2.62 | **2.58** | 2.71 |
| rh (%) | 3 | 5.11 | 4.79 | 3.32 | 3.55 | 3.50 | **3.22** | 3.28 |
| rh (%) | 7 | 5.72 | 5.75 | 4.06 | 4.23 | 3.87 | **3.76** | 3.79 |
| angin (km/h) | 1 | 2.48 | 1.71 | 1.87 | **1.53** | 1.59 | 1.54 | 1.61 |
| angin (km/h) | 3 | 2.48 | 2.61 | **1.87** | 2.00 | 2.04 | 1.87 | 1.90 |
| angin (km/h) | 7 | 2.70 | 2.87 | **2.03** | 2.24 | 2.67 | 2.08 | 2.17 |
| hujan (mm) | 1 | 4.25 | 4.25 | 3.99 | **3.62** | 3.91 | 4.10 | 4.12 |
| hujan (mm) | 3 | 4.25 | 4.71 | 4.23 | **3.85** | 5.27 | 4.20 | 4.32 |
| hujan (mm) | 7 | 4.57 | 5.07 | 4.43 | 4.31 | 5.75 | **4.26** | 4.62 |

## Surabaya: MAE per metode

| Variabel | Lead | NWP mentah | Persistensi | Bias bergulir 30 hari | Rata-rata (bias bergulir, persistensi) | Ridge tetap | Ridge walk-forward | LightGBM residu walk-forward |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| suhu (C) | 1 | 0.42 | 0.39 | 0.30 | 0.27 | 0.28 | **0.25** | 0.28 |
| suhu (C) | 3 | 0.50 | 0.60 | 0.39 | 0.39 | 0.42 | **0.35** | 0.36 |
| suhu (C) | 7 | 0.61 | 0.70 | 0.53 | 0.50 | 0.51 | **0.47** | 0.49 |
| rh (%) | 1 | 2.18 | 2.67 | 1.83 | 1.79 | 2.27 | **1.70** | 1.81 |
| rh (%) | 3 | 2.93 | 4.44 | 2.56 | 2.88 | 3.30 | 2.56 | **2.53** |
| rh (%) | 7 | 3.72 | 5.24 | 3.48 | 3.57 | 4.60 | 3.42 | **3.25** |
| angin (km/h) | 1 | 1.53 | 1.47 | 1.06 | 1.04 | 1.01 | **1.00** | 1.01 |
| angin (km/h) | 3 | 1.79 | 2.30 | **1.31** | 1.53 | 1.37 | 1.32 | 1.32 |
| angin (km/h) | 7 | 2.11 | 2.69 | **1.59** | 1.86 | 1.71 | 1.61 | 1.64 |
| hujan (mm) | 1 | **2.43** | 3.31 | 2.54 | 2.61 | 3.05 | 2.58 | 2.59 |
| hujan (mm) | 3 | **2.72** | 3.84 | 2.88 | 2.95 | 3.58 | 2.96 | 2.91 |
| hujan (mm) | 7 | **2.98** | 3.95 | 3.07 | 3.17 | 3.98 | 3.15 | 3.33 |

## Uji Diebold-Mariano (galat absolut, koreksi Harvey-Leybourne-Newbold)

Model terbaik per sel (di antara metode terkoreksi) dibandingkan dengan tiga pembanding. p < 0,05 berarti selisih MAE bermakna secara statistik (satu sel uji, tanpa koreksi perbandingan ganda).

| Lokasi | Variabel | Lead | Model terbaik | Pembanding | MAE terbaik | MAE pembanding | p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Kalisat | suhu | 1 | Ridge walk-forward | NWP mentah | 0.33 | 0.64 | 0.000 |
| Kalisat | suhu | 1 | Ridge walk-forward | Persistensi | 0.33 | 0.51 | 0.000 |
| Kalisat | suhu | 1 | Ridge walk-forward | Bias bergulir 30 hari | 0.33 | 0.34 | 0.019 |
| Kalisat | suhu | 3 | Ridge tetap | NWP mentah | 0.43 | 0.66 | 0.000 |
| Kalisat | suhu | 3 | Ridge tetap | Persistensi | 0.43 | 0.72 | 0.000 |
| Kalisat | suhu | 3 | Ridge tetap | Bias bergulir 30 hari | 0.43 | 0.45 | 0.077 |
| Kalisat | suhu | 7 | Bias bergulir 30 hari | NWP mentah | 0.56 | 0.73 | 0.000 |
| Kalisat | suhu | 7 | Bias bergulir 30 hari | Persistensi | 0.56 | 0.82 | 0.000 |
| Kalisat | rh | 1 | Ridge walk-forward | NWP mentah | 2.58 | 4.76 | 0.000 |
| Kalisat | rh | 1 | Ridge walk-forward | Persistensi | 2.58 | 3.66 | 0.000 |
| Kalisat | rh | 1 | Ridge walk-forward | Bias bergulir 30 hari | 2.58 | 2.76 | 0.002 |
| Kalisat | rh | 3 | Ridge walk-forward | NWP mentah | 3.22 | 5.11 | 0.000 |
| Kalisat | rh | 3 | Ridge walk-forward | Persistensi | 3.22 | 4.79 | 0.000 |
| Kalisat | rh | 3 | Ridge walk-forward | Bias bergulir 30 hari | 3.22 | 3.32 | 0.234 |
| Kalisat | rh | 7 | Ridge walk-forward | NWP mentah | 3.76 | 5.72 | 0.000 |
| Kalisat | rh | 7 | Ridge walk-forward | Persistensi | 3.76 | 5.75 | 0.000 |
| Kalisat | rh | 7 | Ridge walk-forward | Bias bergulir 30 hari | 3.76 | 4.06 | 0.041 |
| Kalisat | angin | 1 | Rata-rata (bias bergulir, persistensi) | NWP mentah | 1.53 | 2.48 | 0.000 |
| Kalisat | angin | 1 | Rata-rata (bias bergulir, persistensi) | Persistensi | 1.53 | 1.71 | 0.000 |
| Kalisat | angin | 1 | Rata-rata (bias bergulir, persistensi) | Bias bergulir 30 hari | 1.53 | 1.87 | 0.000 |
| Kalisat | angin | 3 | Bias bergulir 30 hari | NWP mentah | 1.87 | 2.48 | 0.000 |
| Kalisat | angin | 3 | Bias bergulir 30 hari | Persistensi | 1.87 | 2.61 | 0.000 |
| Kalisat | angin | 7 | Bias bergulir 30 hari | NWP mentah | 2.03 | 2.70 | 0.000 |
| Kalisat | angin | 7 | Bias bergulir 30 hari | Persistensi | 2.03 | 2.87 | 0.000 |
| Kalisat | hujan | 1 | Rata-rata (bias bergulir, persistensi) | NWP mentah | 3.62 | 4.25 | 0.001 |
| Kalisat | hujan | 1 | Rata-rata (bias bergulir, persistensi) | Persistensi | 3.62 | 4.25 | 0.000 |
| Kalisat | hujan | 1 | Rata-rata (bias bergulir, persistensi) | Bias bergulir 30 hari | 3.62 | 3.99 | 0.024 |
| Kalisat | hujan | 3 | Rata-rata (bias bergulir, persistensi) | NWP mentah | 3.85 | 4.25 | 0.079 |
| Kalisat | hujan | 3 | Rata-rata (bias bergulir, persistensi) | Persistensi | 3.85 | 4.71 | 0.000 |
| Kalisat | hujan | 3 | Rata-rata (bias bergulir, persistensi) | Bias bergulir 30 hari | 3.85 | 4.23 | 0.049 |
| Kalisat | hujan | 7 | Ridge walk-forward | NWP mentah | 4.26 | 4.57 | 0.274 |
| Kalisat | hujan | 7 | Ridge walk-forward | Persistensi | 4.26 | 5.07 | 0.030 |
| Kalisat | hujan | 7 | Ridge walk-forward | Bias bergulir 30 hari | 4.26 | 4.43 | 0.502 |
| Surabaya | suhu | 1 | Ridge walk-forward | NWP mentah | 0.25 | 0.42 | 0.000 |
| Surabaya | suhu | 1 | Ridge walk-forward | Persistensi | 0.25 | 0.39 | 0.000 |
| Surabaya | suhu | 1 | Ridge walk-forward | Bias bergulir 30 hari | 0.25 | 0.30 | 0.000 |
| Surabaya | suhu | 3 | Ridge walk-forward | NWP mentah | 0.35 | 0.50 | 0.000 |
| Surabaya | suhu | 3 | Ridge walk-forward | Persistensi | 0.35 | 0.60 | 0.000 |
| Surabaya | suhu | 3 | Ridge walk-forward | Bias bergulir 30 hari | 0.35 | 0.39 | 0.005 |
| Surabaya | suhu | 7 | Ridge walk-forward | NWP mentah | 0.47 | 0.61 | 0.000 |
| Surabaya | suhu | 7 | Ridge walk-forward | Persistensi | 0.47 | 0.70 | 0.000 |
| Surabaya | suhu | 7 | Ridge walk-forward | Bias bergulir 30 hari | 0.47 | 0.53 | 0.058 |
| Surabaya | rh | 1 | Ridge walk-forward | NWP mentah | 1.70 | 2.18 | 0.000 |
| Surabaya | rh | 1 | Ridge walk-forward | Persistensi | 1.70 | 2.67 | 0.000 |
| Surabaya | rh | 1 | Ridge walk-forward | Bias bergulir 30 hari | 1.70 | 1.83 | 0.011 |
| Surabaya | rh | 3 | LightGBM residu walk-forward | NWP mentah | 2.53 | 2.93 | 0.000 |
| Surabaya | rh | 3 | LightGBM residu walk-forward | Persistensi | 2.53 | 4.44 | 0.000 |
| Surabaya | rh | 3 | LightGBM residu walk-forward | Bias bergulir 30 hari | 2.53 | 2.56 | 0.745 |
| Surabaya | rh | 7 | LightGBM residu walk-forward | NWP mentah | 3.25 | 3.72 | 0.001 |
| Surabaya | rh | 7 | LightGBM residu walk-forward | Persistensi | 3.25 | 5.24 | 0.000 |
| Surabaya | rh | 7 | LightGBM residu walk-forward | Bias bergulir 30 hari | 3.25 | 3.48 | 0.167 |
| Surabaya | angin | 1 | Ridge walk-forward | NWP mentah | 1.00 | 1.53 | 0.000 |
| Surabaya | angin | 1 | Ridge walk-forward | Persistensi | 1.00 | 1.47 | 0.000 |
| Surabaya | angin | 1 | Ridge walk-forward | Bias bergulir 30 hari | 1.00 | 1.06 | 0.037 |
| Surabaya | angin | 3 | Bias bergulir 30 hari | NWP mentah | 1.31 | 1.79 | 0.000 |
| Surabaya | angin | 3 | Bias bergulir 30 hari | Persistensi | 1.31 | 2.30 | 0.000 |
| Surabaya | angin | 7 | Bias bergulir 30 hari | NWP mentah | 1.59 | 2.11 | 0.000 |
| Surabaya | angin | 7 | Bias bergulir 30 hari | Persistensi | 1.59 | 2.69 | 0.000 |
| Surabaya | hujan | 1 | Bias bergulir 30 hari | NWP mentah | 2.54 | 2.43 | 0.044 |
| Surabaya | hujan | 1 | Bias bergulir 30 hari | Persistensi | 2.54 | 3.31 | 0.000 |
| Surabaya | hujan | 3 | Bias bergulir 30 hari | NWP mentah | 2.88 | 2.72 | 0.013 |
| Surabaya | hujan | 3 | Bias bergulir 30 hari | Persistensi | 2.88 | 3.84 | 0.000 |
| Surabaya | hujan | 7 | Bias bergulir 30 hari | NWP mentah | 3.07 | 2.98 | 0.230 |
| Surabaya | hujan | 7 | Bias bergulir 30 hari | Persistensi | 3.07 | 3.95 | 0.000 |

## Interval 90%: konformal adaptif vs statis (Ridge walk-forward)

Statis = satu kuantil dari galat Mar-Jun 2025. Adaptif = kuantil jendela 120 hari yang bergulir dengan pembaruan level (Gibbs dan Candes, gamma 0,02), memakai hanya galat yang sudah terverifikasi.

| Lokasi | Variabel | Lead | PICP statis | MPIW statis | PICP adaptif | MPIW adaptif |
| --- | --- | --- | --- | --- | --- | --- |
| Kalisat | suhu (C) | 1 | 82% | 1.09 | 90% | 1.42 |
| Kalisat | suhu (C) | 3 | 79% | 1.42 | 90% | 1.94 |
| Kalisat | suhu (C) | 7 | 79% | 1.84 | 90% | 2.49 |
| Kalisat | rh (%) | 1 | 84% | 9.17 | 90% | 11.14 |
| Kalisat | rh (%) | 3 | 88% | 13.15 | 90% | 15.60 |
| Kalisat | rh (%) | 7 | 86% | 13.30 | 89% | 17.71 |
| Kalisat | angin (km/h) | 1 | 86% | 5.88 | 91% | 6.69 |
| Kalisat | angin (km/h) | 3 | 89% | 7.72 | 90% | 7.78 |
| Kalisat | angin (km/h) | 7 | 91% | 8.34 | 90% | 8.62 |
| Surabaya | suhu (C) | 1 | 93% | 1.20 | 90% | 1.06 |
| Surabaya | suhu (C) | 3 | 95% | 1.84 | 89% | 1.53 |
| Surabaya | suhu (C) | 7 | 91% | 2.39 | 88% | 2.23 |
| Surabaya | rh (%) | 1 | 95% | 9.14 | 90% | 7.44 |
| Surabaya | rh (%) | 3 | 95% | 12.17 | 89% | 10.98 |
| Surabaya | rh (%) | 7 | 93% | 14.91 | 90% | 14.86 |
| Surabaya | angin (km/h) | 1 | 85% | 3.74 | 90% | 4.55 |
| Surabaya | angin (km/h) | 3 | 84% | 4.81 | 91% | 6.11 |
| Surabaya | angin (km/h) | 7 | 87% | 6.33 | 91% | 7.39 |

## Kejadian hujan (>= 1 mm), LightGBM walk-forward

| Lokasi | Lead | Frekuensi hujan uji | AUC NWP | AUC klimatologi | AUC LightGBM | Brier klimatologi | Brier LightGBM |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Kalisat | 1 | 0.47 | 0.879 | 0.806 | 0.894 | 0.184 | 0.133 |
| Kalisat | 3 | 0.47 | 0.839 | 0.801 | 0.851 | 0.188 | 0.157 |
| Kalisat | 7 | 0.47 | 0.841 | 0.806 | 0.856 | 0.184 | 0.155 |
| Surabaya | 1 | 0.43 | 0.951 | 0.858 | 0.953 | 0.143 | 0.089 |
| Surabaya | 3 | 0.44 | 0.922 | 0.858 | 0.930 | 0.143 | 0.096 |
| Surabaya | 7 | 0.43 | 0.912 | 0.858 | 0.899 | 0.143 | 0.114 |
