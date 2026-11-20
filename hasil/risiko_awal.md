# Model risiko OPT bulan berikutnya (hasil awal)

Sumber cuaca: **Open-Meteo unduhan ulang**.

Target: ada/tidak serangan (LKSJ > 0) pada bulan berikutnya (keadaan serangan, memuat sisa bulan lalu). AUC dan PR-AUC dihitung dari prediksi gabungan seluruh fold uji; CI 95% bootstrap baris (cenderung terlalu sempit karena baris satu desa berkorelasi).
Prevalensi positif: 0.284. Untuk leave-village-out, anomali cuaca memakai rata-rata desa sendiri (sedikit bocor, tercatat sebagai batasan).

## rolling

| Fitur | Model | AUC | CI 95% | PR-AUC | Brier |
| --- | --- | --- | --- | --- | --- |
| - | persistensi (bulan ini ada serangan) | 0.701 | - | 0.459 | 0.249 |
| - | prevalensi latih | 0.454 | - | 0.278 | 0.210 |
| riwayat + musim | Logistik | 0.705 | 0.64-0.76 | 0.585 | 0.210 |
| riwayat + musim | SVM rbf (draft) | 0.713 | 0.66-0.77 | 0.522 | 0.183 |
| riwayat + musim | Random Forest | 0.739 | 0.69-0.80 | 0.576 | 0.186 |
| riwayat + musim | LightGBM | 0.758 | 0.71-0.81 | 0.601 | 0.187 |
| riwayat + musim | CatBoost | 0.732 | 0.67-0.79 | 0.558 | 0.197 |
| cuaca anomali + musim | Logistik | 0.503 | 0.43-0.57 | 0.323 | 0.339 |
| cuaca anomali + musim | SVM rbf (draft) | 0.601 | 0.53-0.66 | 0.369 | 0.205 |
| cuaca anomali + musim | Random Forest | 0.582 | 0.52-0.65 | 0.378 | 0.225 |
| cuaca anomali + musim | LightGBM | 0.591 | 0.52-0.66 | 0.428 | 0.261 |
| cuaca anomali + musim | CatBoost | 0.590 | 0.52-0.66 | 0.412 | 0.254 |
| riwayat + cuaca anomali + musim | Logistik | 0.637 | 0.58-0.70 | 0.503 | 0.261 |
| riwayat + cuaca anomali + musim | SVM rbf (draft) | 0.654 | 0.59-0.71 | 0.422 | 0.199 |
| riwayat + cuaca anomali + musim | Random Forest | 0.731 | 0.67-0.79 | 0.569 | 0.180 |
| riwayat + cuaca anomali + musim | LightGBM | 0.722 | 0.66-0.78 | 0.565 | 0.193 |
| riwayat + cuaca anomali + musim | CatBoost | 0.695 | 0.63-0.75 | 0.530 | 0.195 |

## leave-village-out

| Fitur | Model | AUC | CI 95% | PR-AUC | Brier |
| --- | --- | --- | --- | --- | --- |
| - | persistensi (bulan ini ada serangan) | 0.706 | - | 0.454 | 0.240 |
| - | prevalensi latih | 0.231 | - | 0.200 | 0.215 |
| riwayat + musim | Logistik | 0.741 | 0.70-0.78 | 0.564 | 0.199 |
| riwayat + musim | SVM rbf (draft) | 0.702 | 0.65-0.75 | 0.464 | 0.190 |
| riwayat + musim | Random Forest | 0.707 | 0.66-0.76 | 0.487 | 0.190 |
| riwayat + musim | LightGBM | 0.719 | 0.67-0.77 | 0.495 | 0.193 |
| riwayat + musim | CatBoost | 0.666 | 0.62-0.71 | 0.464 | 0.202 |
| cuaca anomali + musim | Logistik | 0.558 | 0.50-0.61 | 0.334 | 0.249 |
| cuaca anomali + musim | SVM rbf (draft) | 0.542 | 0.49-0.59 | 0.299 | 0.209 |
| cuaca anomali + musim | Random Forest | 0.566 | 0.51-0.61 | 0.314 | 0.214 |
| cuaca anomali + musim | LightGBM | 0.548 | 0.50-0.60 | 0.309 | 0.251 |
| cuaca anomali + musim | CatBoost | 0.569 | 0.52-0.62 | 0.318 | 0.243 |
| riwayat + cuaca anomali + musim | Logistik | 0.724 | 0.68-0.77 | 0.544 | 0.201 |
| riwayat + cuaca anomali + musim | SVM rbf (draft) | 0.610 | 0.56-0.66 | 0.387 | 0.201 |
| riwayat + cuaca anomali + musim | Random Forest | 0.720 | 0.67-0.77 | 0.472 | 0.182 |
| riwayat + cuaca anomali + musim | LightGBM | 0.706 | 0.66-0.75 | 0.452 | 0.198 |
| riwayat + cuaca anomali + musim | CatBoost | 0.677 | 0.63-0.73 | 0.431 | 0.207 |

## Fitur terpenting (SHAP rata-rata mutlak, LightGBM, uji 2025+)

| Fitur | |SHAP| |
| --- | --- |
| LKSJ_riwayat3 | 0.391 |
| om_lwd_jam_per_hari_l2_an | 0.371 |
| LT | 0.306 |
| om_windspeed_an | 0.244 |
| om_windspeed_l1_an | 0.238 |
| om_windspeed_l3_an | 0.208 |
| LKSJ | 0.208 |
| bulan_cos | 0.132 |
| om_lwd_jam_per_hari_l3_an | 0.116 |
| om_lwd_jam_per_hari_an | 0.105 |
| om_temp_l3_an | 0.086 |
| om_lwd_jam_per_hari_l1_an | 0.082 |

Catatan: bila sumber cuaca masih 'bawaan', fitur cuaca bisa hanya menandai waktu atau desa, bukan cuaca sebenarnya.
