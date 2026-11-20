# Indeks agro-meteorologi harian vs riwayat serangan

Indeks per desa x bulan dari cuaca harian Open-Meteo (28 kolom: hari hujan, hari deras >= 20 mm, hari kering beruntun, derajat-hari basis 10, jam RH > 90, VPD, jendela 14 hari terakhir, lag 1-2 bulan).
Anomali indeks = nilai dikurangi rata-rata bulan kalender dari data latih. Selisih AUC memakai bootstrap berpasangan terhadap 'riwayat + musim' (model yang sama).

## Target SSJ > 0 bulan berikutnya, rolling

| Fitur | Model | AUC | CI 95% | selisih vs riwayat+musim (CI 95%) | PR-AUC |
| --- | --- | --- | --- | --- | --- |
| riwayat + musim | Logistik | 0.747 | 0.67-0.82 | +0.000 (+0.00 s.d. +0.00) | 0.428 |
| riwayat + musim | Random Forest | 0.754 | 0.68-0.82 | +0.000 (+0.00 s.d. +0.00) | 0.371 |
| riwayat + musim | LightGBM | 0.779 | 0.72-0.84 | +0.000 (+0.00 s.d. +0.00) | 0.413 |
| cuaca bulanan + musim | Logistik | 0.683 | 0.62-0.75 | -0.064 (-0.12 s.d. -0.01) | 0.287 |
| cuaca bulanan + musim | Random Forest | 0.643 | 0.57-0.71 | -0.111 (-0.19 s.d. -0.03) | 0.265 |
| cuaca bulanan + musim | LightGBM | 0.630 | 0.55-0.70 | -0.149 (-0.23 s.d. -0.07) | 0.269 |
| indeks harian + musim | Logistik | 0.653 | 0.59-0.71 | -0.093 (-0.17 s.d. -0.03) | 0.237 |
| indeks harian + musim | Random Forest | 0.635 | 0.56-0.71 | -0.119 (-0.21 s.d. -0.03) | 0.246 |
| indeks harian + musim | LightGBM | 0.651 | 0.59-0.72 | -0.129 (-0.21 s.d. -0.04) | 0.259 |
| riwayat + cuaca bulanan + musim | Logistik | 0.744 | 0.67-0.81 | -0.003 (-0.04 s.d. +0.04) | 0.406 |
| riwayat + cuaca bulanan + musim | Random Forest | 0.762 | 0.70-0.83 | +0.008 (-0.03 s.d. +0.06) | 0.409 |
| riwayat + cuaca bulanan + musim | LightGBM | 0.761 | 0.69-0.83 | -0.018 (-0.06 s.d. +0.02) | 0.438 |
| riwayat + indeks harian + musim | Logistik | 0.697 | 0.63-0.76 | -0.050 (-0.12 s.d. +0.01) | 0.318 |
| riwayat + indeks harian + musim | Random Forest | 0.776 | 0.71-0.83 | +0.022 (-0.03 s.d. +0.08) | 0.380 |
| riwayat + indeks harian + musim | LightGBM | 0.767 | 0.70-0.82 | -0.013 (-0.06 s.d. +0.05) | 0.360 |

## Target SSJ > 0 bulan berikutnya, leave-village-out

| Fitur | Model | AUC | CI 95% | selisih vs riwayat+musim (CI 95%) | PR-AUC |
| --- | --- | --- | --- | --- | --- |
| riwayat + musim | Logistik | 0.769 | 0.71-0.82 | +0.000 (+0.00 s.d. +0.00) | 0.463 |
| riwayat + musim | Random Forest | 0.762 | 0.71-0.81 | +0.000 (+0.00 s.d. +0.00) | 0.412 |
| riwayat + musim | LightGBM | 0.774 | 0.72-0.82 | +0.000 (+0.00 s.d. +0.00) | 0.423 |
| cuaca bulanan + musim | Logistik | 0.635 | 0.58-0.69 | -0.134 (-0.19 s.d. -0.08) | 0.246 |
| cuaca bulanan + musim | Random Forest | 0.625 | 0.56-0.69 | -0.137 (-0.21 s.d. -0.06) | 0.261 |
| cuaca bulanan + musim | LightGBM | 0.639 | 0.58-0.70 | -0.135 (-0.21 s.d. -0.07) | 0.265 |
| indeks harian + musim | Logistik | 0.654 | 0.60-0.71 | -0.115 (-0.18 s.d. -0.05) | 0.262 |
| indeks harian + musim | Random Forest | 0.644 | 0.58-0.70 | -0.118 (-0.19 s.d. -0.05) | 0.287 |
| indeks harian + musim | LightGBM | 0.656 | 0.60-0.71 | -0.118 (-0.19 s.d. -0.05) | 0.282 |
| riwayat + cuaca bulanan + musim | Logistik | 0.764 | 0.71-0.81 | -0.004 (-0.03 s.d. +0.03) | 0.439 |
| riwayat + cuaca bulanan + musim | Random Forest | 0.765 | 0.71-0.81 | +0.003 (-0.03 s.d. +0.04) | 0.388 |
| riwayat + cuaca bulanan + musim | LightGBM | 0.780 | 0.73-0.83 | +0.006 (-0.03 s.d. +0.04) | 0.465 |
| riwayat + indeks harian + musim | Logistik | 0.761 | 0.71-0.81 | -0.008 (-0.05 s.d. +0.03) | 0.416 |
| riwayat + indeks harian + musim | Random Forest | 0.784 | 0.73-0.83 | +0.021 (-0.02 s.d. +0.06) | 0.403 |
| riwayat + indeks harian + musim | LightGBM | 0.793 | 0.75-0.84 | +0.019 (-0.02 s.d. +0.06) | 0.431 |

## Ringkasan

Kombinasi 'riwayat + cuaca/indeks' yang selisih AUC-nya di atas 0 dengan CI 95% (di atas riwayat + musim saja): **0** dari 12.

