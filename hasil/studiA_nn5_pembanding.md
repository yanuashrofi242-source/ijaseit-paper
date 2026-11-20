# Studi A, tahap 5: BiGRU-Attention kuantil vs pembanding sederhana

Residual NWP (ECMWF, arsip Open-Meteo) terhadap reanalisis; BiGRU dua arah (16 unit) dengan atensi aditif, jendela 14 hari, keluaran kuantil 5/50/95%, rata-rata 2 seed, refit tiap 30 hari dengan jendela 540 hari. Uji sama dengan tahap 4 (mulai 2025-07-01, hari yang sama untuk semua metode di tiap sel).

| Lokasi | Variabel | Lead | n | NWP mentah | Bias bergulir | Ridge walk-forward | BiGRU median | p DM vs Ridge | p DM vs bias bergulir |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Kalisat | suhu (C) | 1 | 473 | 0.63 | 0.34 | **0.32** | 0.34 | 0.015 | 0.410 |
| Kalisat | rh (%) | 1 | 473 | 4.64 | 2.71 | **2.52** | 2.69 | 0.000 | 0.724 |
| Kalisat | angin (km/h) | 1 | 473 | 2.48 | 1.88 | **1.54** | 1.84 | 0.000 | 0.354 |
| Kalisat | suhu (C) | 3 | 494 | 0.66 | 0.45 | **0.45** | 0.45 | 0.421 | 0.732 |
| Kalisat | rh (%) | 3 | 494 | 5.11 | 3.32 | **3.22** | 3.30 | 0.158 | 0.796 |
| Kalisat | angin (km/h) | 3 | 494 | 2.48 | **1.87** | 1.87 | 1.88 | 0.805 | 0.818 |
| Kalisat | suhu (C) | 7 | 487 | 0.73 | 0.56 | 0.56 | **0.55** | 0.111 | 0.633 |
| Kalisat | rh (%) | 7 | 487 | 5.72 | 4.06 | 3.76 | **3.65** | 0.153 | 0.008 |
| Kalisat | angin (km/h) | 7 | 487 | 2.70 | 2.03 | 2.08 | **2.00** | 0.095 | 0.676 |
| Surabaya | suhu (C) | 1 | 473 | 0.41 | 0.29 | **0.25** | 0.26 | 0.094 | 0.000 |
| Surabaya | rh (%) | 1 | 473 | 2.15 | 1.82 | **1.69** | 1.72 | 0.437 | 0.031 |
| Surabaya | angin (km/h) | 1 | 473 | 1.52 | 1.07 | **0.99** | 1.03 | 0.153 | 0.143 |
| Surabaya | suhu (C) | 3 | 494 | 0.50 | 0.39 | 0.35 | **0.34** | 0.383 | 0.002 |
| Surabaya | rh (%) | 3 | 494 | 2.93 | 2.56 | 2.56 | **2.48** | 0.133 | 0.346 |
| Surabaya | angin (km/h) | 3 | 494 | 1.79 | 1.31 | 1.32 | **1.30** | 0.305 | 0.819 |
| Surabaya | suhu (C) | 7 | 487 | 0.61 | 0.53 | 0.47 | **0.46** | 0.529 | 0.009 |
| Surabaya | rh (%) | 7 | 487 | 3.72 | 3.48 | 3.42 | **3.26** | 0.066 | 0.117 |
| Surabaya | angin (km/h) | 7 | 487 | 2.11 | **1.59** | 1.61 | 1.60 | 0.860 | 0.916 |

## Interval 90% dari BiGRU

Kuantil langsung = kuantil 5% dan 95% keluaran jaringan. Adaptif = konformal adaptif (sama seperti tahap 4) pada median jaringan.

| Lokasi | Variabel | Lead | PICP kuantil langsung | MPIW kuantil langsung | PICP adaptif | MPIW adaptif |
| --- | --- | --- | --- | --- | --- | --- |
| Kalisat | suhu (C) | 1 | 82% | 1.18 | 91% | 1.46 |
| Kalisat | rh (%) | 1 | 83% | 9.11 | 90% | 12.44 |
| Kalisat | angin (km/h) | 1 | 86% | 6.43 | 91% | 7.78 |
| Kalisat | suhu (C) | 3 | 79% | 1.51 | 89% | 1.99 |
| Kalisat | rh (%) | 3 | 82% | 11.20 | 90% | 15.49 |
| Kalisat | angin (km/h) | 3 | 86% | 6.59 | 91% | 7.81 |
| Kalisat | suhu (C) | 7 | 79% | 1.74 | 89% | 2.34 |
| Kalisat | rh (%) | 7 | 83% | 12.26 | 90% | 18.46 |
| Kalisat | angin (km/h) | 7 | 87% | 7.01 | 90% | 8.45 |
| Surabaya | suhu (C) | 1 | 88% | 0.93 | 90% | 1.12 |
| Surabaya | rh (%) | 1 | 86% | 6.31 | 90% | 7.59 |
| Surabaya | angin (km/h) | 1 | 85% | 3.75 | 90% | 4.53 |
| Surabaya | suhu (C) | 3 | 89% | 1.31 | 90% | 1.48 |
| Surabaya | rh (%) | 3 | 85% | 8.45 | 90% | 10.33 |
| Surabaya | angin (km/h) | 3 | 84% | 4.39 | 91% | 6.46 |
| Surabaya | suhu (C) | 7 | 85% | 1.72 | 89% | 2.24 |
| Surabaya | rh (%) | 7 | 83% | 11.08 | 90% | 13.68 |
| Surabaya | angin (km/h) | 7 | 82% | 5.20 | 92% | 8.14 |

BiGRU lebih baik dari Ridge walk-forward di 9 dari 18 sel (MAE); yang bermakna (p DM < 0,05 dan MAE lebih kecil): 0.
