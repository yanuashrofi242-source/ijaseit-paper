# Studi A, tahap 6: N-BEATS-lite kuantil vs pembanding sederhana

Residual NWP (ECMWF, arsip Open-Meteo) terhadap reanalisis; N-BEATS-lite (3 blok FC 64 unit, backcast/forecast), jendela 14 hari, keluaran kuantil 5/50/95%, rata-rata 2 seed, refit tiap 30 hari dengan jendela 540 hari. Uji sama dengan tahap 4 (mulai 2025-07-01, hari yang sama untuk semua metode di tiap sel).

| Lokasi | Variabel | Lead | n | NWP mentah | Bias bergulir | Ridge walk-forward | N-BEATS-lite median | p DM vs Ridge | p DM vs bias bergulir |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Kalisat | suhu (C) | 1 | 473 | 0.63 | 0.34 | 0.32 | **0.32** | 0.679 | 0.003 |
| Kalisat | rh (%) | 1 | 473 | 4.64 | 2.71 | **2.52** | 2.57 | 0.314 | 0.024 |
| Kalisat | angin (km/h) | 1 | 473 | 2.48 | 1.88 | **1.54** | 1.69 | 0.000 | 0.000 |
| Kalisat | suhu (C) | 3 | 494 | 0.66 | 0.45 | **0.45** | 0.45 | 0.788 | 0.928 |
| Kalisat | rh (%) | 3 | 494 | 5.11 | 3.32 | **3.22** | 3.32 | 0.194 | 0.937 |
| Kalisat | angin (km/h) | 3 | 494 | 2.48 | 1.87 | 1.87 | **1.81** | 0.103 | 0.231 |
| Kalisat | suhu (C) | 7 | 487 | 0.73 | 0.56 | 0.56 | **0.55** | 0.214 | 0.597 |
| Kalisat | rh (%) | 7 | 487 | 5.72 | 4.06 | **3.76** | 3.81 | 0.674 | 0.051 |
| Kalisat | angin (km/h) | 7 | 487 | 2.70 | 2.03 | 2.08 | **1.99** | 0.108 | 0.377 |
| Surabaya | suhu (C) | 1 | 473 | 0.41 | 0.29 | **0.25** | 0.27 | 0.000 | 0.014 |
| Surabaya | rh (%) | 1 | 473 | 2.15 | 1.82 | **1.69** | 1.77 | 0.059 | 0.221 |
| Surabaya | angin (km/h) | 1 | 473 | 1.52 | 1.07 | **0.99** | 1.01 | 0.580 | 0.003 |
| Surabaya | suhu (C) | 3 | 494 | 0.50 | 0.39 | **0.35** | 0.38 | 0.006 | 0.526 |
| Surabaya | rh (%) | 3 | 494 | 2.93 | 2.56 | **2.56** | 2.61 | 0.405 | 0.499 |
| Surabaya | angin (km/h) | 3 | 494 | 1.79 | **1.31** | 1.32 | 1.32 | 0.956 | 0.696 |
| Surabaya | suhu (C) | 7 | 487 | 0.61 | 0.53 | **0.47** | 0.54 | 0.000 | 0.486 |
| Surabaya | rh (%) | 7 | 487 | 3.72 | 3.48 | **3.42** | 3.46 | 0.717 | 0.924 |
| Surabaya | angin (km/h) | 7 | 487 | 2.11 | 1.59 | 1.61 | **1.58** | 0.680 | 0.889 |

## Interval 90% dari N-BEATS-lite

Kuantil langsung = kuantil 5% dan 95% keluaran jaringan. Adaptif = konformal adaptif (sama seperti tahap 4) pada median jaringan.

| Lokasi | Variabel | Lead | PICP kuantil langsung | MPIW kuantil langsung | PICP adaptif | MPIW adaptif |
| --- | --- | --- | --- | --- | --- | --- |
| Kalisat | suhu (C) | 1 | 77% | 0.95 | 91% | 1.41 |
| Kalisat | rh (%) | 1 | 74% | 7.34 | 90% | 12.02 |
| Kalisat | angin (km/h) | 1 | 80% | 5.46 | 91% | 7.27 |
| Kalisat | suhu (C) | 3 | 73% | 1.26 | 90% | 1.88 |
| Kalisat | rh (%) | 3 | 71% | 9.33 | 90% | 15.08 |
| Kalisat | angin (km/h) | 3 | 82% | 5.96 | 91% | 7.69 |
| Kalisat | suhu (C) | 7 | 72% | 1.53 | 89% | 2.28 |
| Kalisat | rh (%) | 7 | 74% | 10.70 | 90% | 18.30 |
| Kalisat | angin (km/h) | 7 | 80% | 6.48 | 91% | 8.55 |
| Surabaya | suhu (C) | 1 | 79% | 0.86 | 90% | 1.12 |
| Surabaya | rh (%) | 1 | 79% | 5.37 | 90% | 7.67 |
| Surabaya | angin (km/h) | 1 | 81% | 3.29 | 90% | 4.32 |
| Surabaya | suhu (C) | 3 | 78% | 1.16 | 89% | 1.66 |
| Surabaya | rh (%) | 3 | 76% | 7.61 | 89% | 11.58 |
| Surabaya | angin (km/h) | 3 | 79% | 4.13 | 91% | 6.12 |
| Surabaya | suhu (C) | 7 | 74% | 1.53 | 91% | 2.64 |
| Surabaya | rh (%) | 7 | 74% | 9.52 | 90% | 15.42 |
| Surabaya | angin (km/h) | 7 | 77% | 5.09 | 91% | 7.64 |

N-BEATS-lite lebih baik dari Ridge walk-forward di 6 dari 18 sel (MAE); yang bermakna (p DM < 0,05 dan MAE lebih kecil): 0.
