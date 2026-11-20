# Studi A, tahap 5: BiGRU-Attention kuantil vs pembanding sederhana

Residual NWP (ECMWF, arsip Open-Meteo) terhadap reanalisis; BiGRU dua arah (16 unit) dengan atensi aditif, jendela 14 hari, keluaran kuantil 5/50/95%, rata-rata 2 seed, refit tiap 30 hari dengan jendela 540 hari. Uji sama dengan tahap 4 (mulai 2025-07-01, hari yang sama untuk semua metode di tiap sel).

| Lokasi | Variabel | Lead | n | NWP mentah | Bias bergulir | Ridge walk-forward | BiGRU median | p DM vs Ridge | p DM vs bias bergulir |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Kalisat | suhu (C) | 1 | 473 | 0.63 | 0.34 | **0.32** | 0.34 | 0.014 | 0.469 |
| Kalisat | rh (%) | 1 | 473 | 4.64 | 2.71 | **2.52** | 2.71 | 0.000 | 0.903 |
| Kalisat | angin (km/h) | 1 | 473 | 2.48 | 1.88 | **1.54** | 1.85 | 0.000 | 0.524 |
| Kalisat | suhu (C) | 3 | 494 | 0.66 | 0.45 | **0.45** | 0.45 | 0.414 | 0.731 |
| Kalisat | rh (%) | 3 | 494 | 5.11 | 3.32 | **3.22** | 3.31 | 0.137 | 0.840 |
| Kalisat | angin (km/h) | 3 | 494 | 2.48 | **1.87** | 1.87 | 1.88 | 0.761 | 0.792 |
| Kalisat | suhu (C) | 7 | 487 | 0.73 | 0.56 | 0.56 | **0.55** | 0.270 | 0.802 |
| Kalisat | rh (%) | 7 | 487 | 5.72 | 4.06 | 3.76 | **3.66** | 0.174 | 0.009 |
| Kalisat | angin (km/h) | 7 | 487 | 2.70 | 2.03 | 2.08 | **2.01** | 0.128 | 0.762 |
| Surabaya | suhu (C) | 1 | 473 | 0.41 | 0.29 | **0.25** | 0.26 | 0.168 | 0.000 |
| Surabaya | rh (%) | 1 | 473 | 2.15 | 1.82 | **1.69** | 1.71 | 0.518 | 0.024 |
| Surabaya | angin (km/h) | 1 | 473 | 1.52 | 1.07 | **0.99** | 1.04 | 0.026 | 0.461 |
| Surabaya | suhu (C) | 3 | 494 | 0.50 | 0.39 | 0.35 | **0.34** | 0.663 | 0.004 |
| Surabaya | rh (%) | 3 | 494 | 2.93 | 2.56 | 2.56 | **2.50** | 0.233 | 0.449 |
| Surabaya | angin (km/h) | 3 | 494 | 1.79 | **1.31** | 1.32 | 1.31 | 0.644 | 0.948 |
| Surabaya | suhu (C) | 7 | 487 | 0.61 | 0.53 | 0.47 | **0.47** | 0.760 | 0.016 |
| Surabaya | rh (%) | 7 | 487 | 3.72 | 3.48 | 3.42 | **3.27** | 0.097 | 0.152 |
| Surabaya | angin (km/h) | 7 | 487 | 2.11 | **1.59** | 1.61 | 1.63 | 0.668 | 0.691 |

## Interval 90% dari BiGRU

Kuantil langsung = kuantil 5% dan 95% keluaran jaringan. Adaptif = konformal adaptif (sama seperti tahap 4) pada median jaringan.

| Lokasi | Variabel | Lead | PICP kuantil langsung | MPIW kuantil langsung | PICP adaptif | MPIW adaptif |
| --- | --- | --- | --- | --- | --- | --- |
| Kalisat | suhu (C) | 1 | 82% | 1.17 | 91% | 1.46 |
| Kalisat | rh (%) | 1 | 83% | 9.14 | 90% | 12.57 |
| Kalisat | angin (km/h) | 1 | 86% | 6.45 | 91% | 7.57 |
| Kalisat | suhu (C) | 3 | 79% | 1.51 | 89% | 1.94 |
| Kalisat | rh (%) | 3 | 82% | 11.15 | 90% | 15.67 |
| Kalisat | angin (km/h) | 3 | 86% | 6.63 | 91% | 7.75 |
| Kalisat | suhu (C) | 7 | 79% | 1.75 | 89% | 2.39 |
| Kalisat | rh (%) | 7 | 82% | 12.22 | 90% | 18.36 |
| Kalisat | angin (km/h) | 7 | 87% | 7.05 | 90% | 8.47 |
| Surabaya | suhu (C) | 1 | 87% | 0.93 | 90% | 1.10 |
| Surabaya | rh (%) | 1 | 87% | 6.33 | 90% | 7.48 |
| Surabaya | angin (km/h) | 1 | 84% | 3.76 | 90% | 4.61 |
| Surabaya | suhu (C) | 3 | 87% | 1.30 | 90% | 1.51 |
| Surabaya | rh (%) | 3 | 84% | 8.37 | 90% | 10.44 |
| Surabaya | angin (km/h) | 3 | 82% | 4.40 | 91% | 6.29 |
| Surabaya | suhu (C) | 7 | 84% | 1.70 | 90% | 2.20 |
| Surabaya | rh (%) | 7 | 83% | 11.03 | 90% | 14.28 |
| Surabaya | angin (km/h) | 7 | 81% | 5.20 | 92% | 8.14 |

BiGRU lebih baik dari Ridge walk-forward di 8 dari 18 sel (MAE); yang bermakna (p DM < 0,05 dan MAE lebih kecil): 0.
