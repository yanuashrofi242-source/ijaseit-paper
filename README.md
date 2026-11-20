# Baseline-first, leakage-aware evaluation of weather post-processing, pest-risk ranking and seasonal-state prediction (East Java)

Code, processed data and result tables for the manuscript submitted to IJASEIT. Three studies share one evaluation rule: every learned model is compared with a simple baseline under chronological validation.

| Study | Task | Main scripts |
| --- | --- | --- |
| A | Post-processing of archived ECMWF IFS 0.25° forecasts at Kalisat and Surabaya, leads 1/3/7 d (rolling bias, Ridge, LightGBM, BiGRU+attention, N-BEATS-lite, adaptive conformal intervals, cost) | 13, 15, 16s, 17, 19, 31, 35–37 |
| B | Next-month reported rice-pest attack occurrence in nine villages of Kalisat (history vs weather vs Pranata Mangsa) | 01–03, 06, 08, 10, 32, 34, 38, 39 |
| C | Seasonal dry/transition/wet state at 10–60 d leads | 18, 18b, 33 |
| Audit | Label audit of two earlier datasets | 05 |

Script names are in Indonesian (`skrip` = scripts, `hasil` = results, `gambar` = figures, `data_bersih` = cleaned data).

## Layout

```
skrip/        numbered scripts, in the order they were written and run
data_bersih/  processed inputs (Open-Meteo downloads, cleaned pest tables, features)
hasil/        result tables (CSV/markdown) cited in the manuscript
gambar/       manuscript figures (PNG)
```

## Environment

Python 3.13; see `requirements.txt` (numpy 2.5, pandas 3.0, scipy 1.18, scikit-learn 1.9, lightgbm 4.7, torch 2.15 CPU, matplotlib 3.11). All models use fixed seeds (BiGRU: seeds 0–4; N-BEATS-lite: seeds 0–1). Neural-network runs were done on CPU with 1–2 threads; small numerical differences across CPUs and library versions are possible.

## Data

* **Weather**: Open-Meteo (CC BY 4.0). `data_bersih/om_harian_*` is the Historical Weather API daily series in its default best-match configuration (the verification target of Study A and the input of Study C); `data_bersih/nwp_arsip_ecmwf_ifs025_*` is the hourly Previous Runs API archive for `ecmwf_ifs025`; `weather_desa_*` are village-level series for Study B. All were downloaded on 13 November 2026 by scripts 02, 07 and 13. Because the best-match series can change when Open-Meteo updates its sources, re-downloading may give slightly different values; the files provided are the ones used in the manuscript.
* **Pest records** (Study B, audit): provided by the Jember Regency government. The cleaned tables in `data_bersih/` (`kalisat_bersih.csv`, `fitur_kalisat.csv`, `data_terlabel_bersih.csv`, `desa_koordinat.csv`) are the inputs of Study B. The original raw files (`raw/`) and the 34 MB sensor log used for the sensor check are not included; scripts 00, 01, 20 and 21 read them and are provided for transparency only.
* The sensor check (scripts 20, 21) is a descriptive comparison, not a verification target (only 49 valid sensor hours on 18 days).

## Run order

All paths below are relative to the repository root (`<root>` = `.`). Scripts 22–29 read the root from the environment variable `KERJA` (default: one level above `skrip/`); script 37 must be started from the root.

```
# data (needs internet; skip to use the provided files)
python skrip/02_unduh_open_meteo.py .            # village weather, Study B
python skrip/07_unduh_open_meteo_ekstra.py .     # daily series for Kalisat and Surabaya
python skrip/13_unduh_prakiraan_arsip.py . ecmwf_ifs025

# Study A
python skrip/15_pembanding_adil.py data_bersih hasil     # baselines, Ridge, LightGBM, DM tests, conformal; writes hasil/_pred.pkl
python skrip/16s_nn_5seed.py data_bersih hasil           # BiGRU+attention, five seeds; writes hasil/studiA_nn5_hasil.csv and hasil/_pred_bigru.pkl
cp hasil/studiA_nn5_hasil.csv hasil/studiA_nn_hasil.csv  # scripts 28, 30 and 35 read this file name (16_nn_pembanding.py is the two-seed predecessor and would overwrite it)
python skrip/17_nbeats_pembanding.py data_bersih hasil                              # N-BEATS-lite, 64 units, weight decay 1e-3, 40 epochs (defaults); also writes hasil/_pred_nbeats.pkl
NB_HID=16 NB_WD=0.01 NB_EPOCHS=25 NB_TAG=_kecil python skrip/17_nbeats_pembanding.py data_bersih hasil   # 16 units, weight decay 0.01, 25 epochs (exploratory, chosen post hoc)
python skrip/35_sampel_bersama_holm.py data_bersih hasil # common-sample MAE and Holm tables used in the manuscript
python skrip/40_sensitivitas_dm.py data_bersih hasil     # sensitivity of the paired tests: HAC variance and block bootstrap (needs the three _pred_*.pkl files above)
python skrip/36_diagnosis_galat_dan_jendela.py data_bersih hasil
python skrip/37_menang_harian.py data_bersih hasil
python skrip/31_simpan_deret_konformal.py data_bersih hasil
python skrip/19_biaya_komputasi.py hasil                 # parameters, analytic GFLOPs (2 x MAC / 1e9), CPU latency

# Study B
python skrip/03_bangun_fitur.py .
python skrip/06_model_risiko.py .
python skrip/08_mangsa_vs_bulan.py .
python skrip/10_model_indeks.py .
python skrip/32_bootstrap_klaster_studiB.py .            # village/month/row bootstrap intervals
python skrip/34_sensitivitas_mangsa.py .
python skrip/38_riwayat_saja_tanpa_lksj.py .             # history-only and no-LKSJ variants
python skrip/39_sensitivitas_cuaca_tanpa_lksj.py .       # weather sensitivity without LKSJ, lagged weather
python skrip/41_auc_per_fold_studiB.py .                 # AUC per rolling-origin fold and score-pooling sensitivity
python skrip/42_auc_rata_lipatan_bootstrap_studiB.py .      # fold-mean AUC with village-cluster bootstrap (main Study B measure)

# Study C
python skrip/18b_keadaan_musim_simpan_detail.py data_bersih hasil   # also writes hasil/_detail.csv
python skrip/33_bootstrap_blok_studiC.py hasil

# audit of the earlier datasets (needs raw/)
python skrip/05_audit_label.py .

# figures
for s in 22 23 24 25 26 27 28 29; do python skrip/${s}_*.py; done
```

Notes:

* `30_holm_dm.py` is an earlier Holm script on the per-model samples; the Holm table in the manuscript comes from `35_sampel_bersama_holm.py` (`hasil/studiA_holm_ringkasan_bersama.csv`).
* Some usage lines in script docstrings were copied from parent scripts (for example 16s, 17, 18b, 32, 38, 39) and are out of date; the commands above are the ones to use.
* `hasil/_pred.pkl`, `hasil/_konformal_deret.pkl`, `hasil/_pred_bigru.pkl`, `hasil/_pred_nbeats.pkl` and `hasil/_pred_nbeats_kecil.pkl` are intermediate files regenerated by scripts 15, 31, 16s and 17.
* Number 04 was not used. Scripts 09, 11, 12 and 14 are early exploratory runs, superseded by 15 and later scripts.
* Spot checks: re-running `35_sampel_bersama_holm.py`, `33_bootstrap_blok_studiC.py` and the 16-unit N-BEATS-lite run (`17_nbeats_pembanding.py` with the settings above) from the files in this repository reproduced the common-sample MAE table, the Holm summary, the Study C block-bootstrap table and the N-BEATS-lite 16-unit results (mean skill 27.4%) identically. Scripts 16s and 17 (64 and 16 units) were re-run to store the daily forecasts used by script 40, and their error tables were identical to the ones in `hasil/`; script 41 reproduced the pooled AUCs of the manuscript. The other scripts were not re-run for this release.

## Main result files

| Manuscript item | File |
| --- | --- |
| Study A MAE and skill, common sample | `hasil/studiA_sampel_bersama_mae.csv` |
| Paired tests, Holm (Table XII) | `hasil/studiA_holm_ringkasan_bersama.csv`, `hasil/studiA_holm_sampel_bersama.csv` |
| BiGRU, N-BEATS-lite | `hasil/studiA_nn5_hasil.csv`, `hasil/studiA_nbeats_hasil.csv`, `hasil/studiA_nbeats_kecil_hasil.csv` |
| Cost | `hasil/studiA_biaya_komputasi.csv` |
| Study A sensitivity of the paired tests (HAC, block bootstrap) | `hasil/studiA_sensitivitas_dm.csv`, `hasil/studiA_sensitivitas_dm_ringkasan.csv` |
| Study B AUC per fold and score pooling | `hasil/studiB_auc_per_lipatan.csv`, `hasil/studiB_auc_penggabungan.csv` |
| Study B AUC and cluster bootstrap | `hasil/studiB_bootstrap_klaster.csv`, `hasil/studiB_riwayat_saja.csv`, `hasil/studiB_sensitivitas_cuaca.csv`, `hasil/studiB_sensitivitas_mangsa.csv` |
| Study C macro-F1 and bootstrap | `hasil/studiC_keadaan_musim.csv`, `hasil/studiC_selisih_klimatologi.csv`, `hasil/studiC_bootstrap_blok.csv` |

## Licence and citation

Code: MIT (see `LICENSE`). Processed Open-Meteo data: CC BY 4.0, attribution to Open-Meteo.com and to the underlying ECMWF IFS, ERA5 and ERA5-Land products. Pest records: see the statement in the manuscript. Please cite the manuscript when it is published (citation to be added).
