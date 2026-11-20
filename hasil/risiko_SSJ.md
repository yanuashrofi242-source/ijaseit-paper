# Model risiko OPT bulan berikutnya (hasil awal)

Sumber cuaca: **Open-Meteo unduhan ulang**.

Target: ada/tidak serangan (SSJ > 0) pada bulan berikutnya (serangan baru). AUC dan PR-AUC dihitung dari prediksi gabungan seluruh fold uji; CI 95% bootstrap baris (cenderung terlalu sempit karena baris satu desa berkorelasi).
Prevalensi positif: 0.179. Untuk leave-village-out, anomali cuaca memakai rata-rata desa sendiri (sedikit bocor, tercatat sebagai batasan).

## rolling

| Fitur | Model | AUC | CI 95% | PR-AUC | Brier |
| --- | --- | --- | --- | --- | --- |
| - | persistensi (bulan ini ada serangan) | 0.611 | - | 0.232 | 0.220 |
| - | prevalensi latih | 0.500 | - | 0.166 | 0.140 |
| riwayat + musim | Logistik | 0.754 | 0.68-0.82 | 0.433 | 0.193 |
| riwayat + musim | SVM rbf (draft) | 0.738 | 0.67-0.80 | 0.400 | 0.125 |
| riwayat + musim | Random Forest | 0.754 | 0.68-0.82 | 0.371 | 0.157 |
| riwayat + musim | LightGBM | 0.779 | 0.72-0.84 | 0.413 | 0.172 |
| riwayat + musim | CatBoost | 0.730 | 0.66-0.80 | 0.394 | 0.170 |
| cuaca anomali + musim | Logistik | 0.560 | 0.49-0.65 | 0.223 | 0.357 |
| cuaca anomali + musim | SVM rbf (draft) | 0.624 | 0.55-0.70 | 0.235 | 0.140 |
| cuaca anomali + musim | Random Forest | 0.634 | 0.56-0.71 | 0.269 | 0.170 |
| cuaca anomali + musim | LightGBM | 0.627 | 0.55-0.70 | 0.251 | 0.212 |
| cuaca anomali + musim | CatBoost | 0.613 | 0.54-0.69 | 0.263 | 0.198 |
| riwayat + cuaca anomali + musim | Logistik | 0.703 | 0.62-0.78 | 0.357 | 0.251 |
| riwayat + cuaca anomali + musim | SVM rbf (draft) | 0.672 | 0.60-0.74 | 0.267 | 0.139 |
| riwayat + cuaca anomali + musim | Random Forest | 0.777 | 0.71-0.83 | 0.395 | 0.132 |
| riwayat + cuaca anomali + musim | LightGBM | 0.783 | 0.72-0.84 | 0.447 | 0.148 |
| riwayat + cuaca anomali + musim | CatBoost | 0.760 | 0.69-0.81 | 0.399 | 0.154 |

## leave-village-out

| Fitur | Model | AUC | CI 95% | PR-AUC | Brier |
| --- | --- | --- | --- | --- | --- |
| - | persistensi (bulan ini ada serangan) | 0.643 | - | 0.274 | 0.213 |
| - | prevalensi latih | 0.257 | - | 0.127 | 0.152 |
| riwayat + musim | Logistik | 0.779 | 0.73-0.83 | 0.476 | 0.181 |
| riwayat + musim | SVM rbf (draft) | 0.682 | 0.62-0.74 | 0.338 | 0.138 |
| riwayat + musim | Random Forest | 0.762 | 0.71-0.82 | 0.412 | 0.146 |
| riwayat + musim | LightGBM | 0.774 | 0.72-0.83 | 0.423 | 0.158 |
| riwayat + musim | CatBoost | 0.665 | 0.60-0.72 | 0.358 | 0.168 |
| cuaca anomali + musim | Logistik | 0.628 | 0.57-0.68 | 0.252 | 0.228 |
| cuaca anomali + musim | SVM rbf (draft) | 0.555 | 0.49-0.61 | 0.192 | 0.149 |
| cuaca anomali + musim | Random Forest | 0.577 | 0.52-0.63 | 0.197 | 0.160 |
| cuaca anomali + musim | LightGBM | 0.572 | 0.51-0.63 | 0.199 | 0.190 |
| cuaca anomali + musim | CatBoost | 0.524 | 0.47-0.58 | 0.198 | 0.193 |
| riwayat + cuaca anomali + musim | Logistik | 0.786 | 0.74-0.83 | 0.449 | 0.178 |
| riwayat + cuaca anomali + musim | SVM rbf (draft) | 0.619 | 0.55-0.68 | 0.292 | 0.143 |
| riwayat + cuaca anomali + musim | Random Forest | 0.767 | 0.72-0.81 | 0.371 | 0.131 |
| riwayat + cuaca anomali + musim | LightGBM | 0.765 | 0.71-0.81 | 0.384 | 0.144 |
| riwayat + cuaca anomali + musim | CatBoost | 0.734 | 0.68-0.79 | 0.353 | 0.144 |

## Fitur terpenting (SHAP rata-rata mutlak, LightGBM, uji 2025+)

| Fitur | |SHAP| |
| --- | --- |
| LKSJ | 0.653 |
| LT | 0.474 |
| om_lwd_jam_per_hari_l3_an | 0.384 |
| om_windspeed_l1_an | 0.219 |
| om_lwd_jam_per_hari_l2_an | 0.210 |
| om_humidity_an | 0.183 |
| om_precip_total_l2_an | 0.178 |
| om_temp_l2_an | 0.141 |
| om_humidity_l1_an | 0.114 |
| om_windspeed_an | 0.101 |
| om_windspeed_l3_an | 0.100 |
| om_precip_total_l1_an | 0.086 |

Catatan: bila sumber cuaca masih 'bawaan', fitur cuaca bisa hanya menandai waktu atau desa, bukan cuaca sebenarnya.
