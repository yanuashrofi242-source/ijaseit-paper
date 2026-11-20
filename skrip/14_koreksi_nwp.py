"""Studi A tahap 3: koreksi prakiraan NWP arsip (Open-Meteo Previous Runs) terhadap reanalisis, lead 1/3/7 hari, dua lokasi.
Pakai: python 14_koreksi_nwp.py <folder kerja> [model]   Keluaran: hasil/koreksi_nwp{SUF}.md
Latih 2024-01..2025-02, kalibrasi konformal 2025-03..2025-06, uji 2025-07..2026-11 (kronologis).
Kebenaran = Open-Meteo arsip (reanalisis); BUKAN pengukuran stasiun. Untuk Surabaya, sensor hanya 15 jam sehingga belum dipakai."""
import sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, brier_score_loss
import lightgbm as lgb
root = sys.argv[1]
SUF = f"_{sys.argv[2]}" if len(sys.argv) > 2 else ""   # contoh: ecmwf_ifs025 (arsip satu model)
SITES = {"Kalisat": ("kalisat", "om_harian_kalisat_2005_sekarang.csv"), "Surabaya": ("sensor", "om_harian_sensor_2005_sekarang.csv")}
V = {"suhu": ("temperature_2m", "temperature_2m_mean", "C"), "rh": ("relative_humidity_2m", "relative_humidity_2m_mean", "%"),
     "angin": ("wind_speed_10m", "wind_speed_10m_mean", "km/h"), "hujan": ("precipitation", "precipitation_sum", "mm")}
LEADS = (1, 3, 7)
T_TR, T_CAL, T_TE = "2025-02-28", "2025-06-30", "2025-07-01"
rng = np.random.default_rng(0)
def daily_nwp(f):
    h = pd.read_csv(f, parse_dates=["time"]); h["d"] = h.time.dt.floor("D")
    out = {}
    for k, (b, _, _) in V.items():
        for L in LEADS:
            c = f"{b}_previous_day{L}"
            a = h.groupby("d")[c]
            out[f"{k}_n{L}"] = a.sum(min_count=24) if k == "hujan" else a.mean().where(a.count() >= 24)
    return pd.DataFrame(out)
def boot_skill(e_new, e_ref, n=1000):
    k = ~(np.isnan(e_new) | np.isnan(e_ref)); a, b = np.abs(e_new[k]), np.abs(e_ref[k]); v = []
    for _ in range(n):
        s = rng.integers(0, len(a), len(a)); v.append(1 - a[s].mean() / b[s].mean())
    return np.percentile(v, [2.5, 97.5])
def lg(): return lgb.LGBMRegressor(n_estimators=250, learning_rate=0.03, num_leaves=7, min_child_samples=15, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=3, verbose=-1, random_state=0)

L_out = ["# Koreksi prakiraan NWP arsip (Studi A, tahap 3)", "",
         f"Latih sampai {T_TR}, kalibrasi konformal sampai {T_CAL}, uji dari {T_TE}. Galat = prakiraan dikurangi reanalisis Open-Meteo (bukan stasiun). Skill = 1 - MAE/MAE pembanding.",
         "CI 95% dari bootstrap hari (hari berdekatan berkorelasi, sehingga CI cenderung sempit).", ""]
RAIN = []
for site, (nm, ftruth) in SITES.items():
    tr_ = pd.read_csv(f"{root}/data_bersih/{ftruth}", parse_dates=["time"]).set_index("time").sort_index()
    nw = daily_nwp(f"{root}/data_bersih/nwp_arsip{SUF}_{nm}.csv")
    D = nw.join(tr_[[c for _, c, _ in V.values()]], how="inner")
    clim_src = tr_[tr_.index < "2024-07-01"]
    L_out += [f"## {site}", "", "| Variabel | Lead | MAE NWP mentah | MAE persistensi | MAE bias-koreksi | MAE Ridge | MAE LightGBM residu | Skill LightGBM vs NWP mentah (CI) | PICP 90% | MPIW 90% |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k, (b, c, u) in V.items():
        y_all = D[c]
        for L in LEADS:
            F = pd.DataFrame(index=D.index)
            F["nwp"] = D[f"{k}_n{L}"]
            for kk, (_, cc, _) in V.items():
                F[f"{kk}_obs"] = D[cc].shift(L); F[f"{kk}_obs7"] = D[cc].rolling(7).mean().shift(L)
                F[f"{kk}_nwp"] = D[f"{kk}_n{L}"]
            F["doy_s"] = np.sin(2 * np.pi * D.index.dayofyear / 365.25); F["doy_c"] = np.cos(2 * np.pi * D.index.dayofyear / 365.25)
            ok = F.notna().all(axis=1) & y_all.notna()
            tr = ok & (D.index <= T_TR); ca = ok & (D.index > T_TR) & (D.index <= T_CAL); te = ok & (D.index >= T_TE)
            y = y_all.values
            raw = F.nwp
            bias = (y_all[tr] - raw[tr]).mean()
            pers = D[c].shift(L)
            rd = make_pipeline(StandardScaler(), Ridge(10.0)).fit(F[tr], y_all[tr])
            m = lg().fit(F[tr], (y_all - raw)[tr])
            def pred_lgb(idx): return raw[idx].values + m.predict(F[idx])
            if k == "hujan": clip = lambda a: np.clip(a, 0, None)
            else: clip = lambda a: a
            p_raw, p_bias, p_pers = raw[te].values, clip(raw[te].values + bias), pers[te].values
            p_rd, p_lg = clip(rd.predict(F[te])), clip(pred_lgb(te))
            yt = y_all[te].values
            mae = lambda p: np.mean(np.abs(yt - p))
            # konformal split: kuantil galat absolut kalibrasi (|y - p_lg|), 90%
            q = np.quantile(np.abs(y_all[ca].values - clip(pred_lgb(ca))), 0.9 * (1 + 1 / ca.sum()))
            cover = np.mean(np.abs(yt - p_lg) <= q)
            lo, hi = boot_skill(p_lg - yt, p_raw - yt)
            L_out.append(f"| {k} ({u}) | {L} | {mae(p_raw):.2f} | {mae(p_pers):.2f} | {mae(p_bias):.2f} | {mae(p_rd):.2f} | {mae(p_lg):.2f} | {1 - mae(p_lg)/mae(p_raw):+.0%} ({lo:+.0%} s.d. {hi:+.0%}) | {cover:.0%} | {2*q:.2f} |")
            if k == "hujan":
                obs = (yt >= 1).astype(int)
                tr_d = clim_src.precipitation_sum; cl = (tr_d >= 1).groupby(tr_d.index.dayofyear).mean()
                pc = np.array([cl.get(t.dayofyear, np.nan) for t in D.index[te]])
                Fc = F.copy(); Fc["nwp1mm"] = (F.nwp >= 1).astype(float)
                clf = lgb.LGBMClassifier(n_estimators=250, learning_rate=0.03, num_leaves=7, min_child_samples=15, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=3, verbose=-1, random_state=0)
                clf.fit(Fc[tr], (y_all[tr] >= 1).astype(int)); pp = clf.predict_proba(Fc[te])[:, 1]
                RAIN.append(dict(site=site, L=L, frek=obs.mean(), auc_nwp=roc_auc_score(obs, p_raw), auc_clim=roc_auc_score(obs, pc), auc_lgb=roc_auc_score(obs, pp),
                                 brier_clim=brier_score_loss(obs, pc), brier_lgb=brier_score_loss(obs, pp)))
    L_out.append("")
L_out += ["## Kejadian hujan (>= 1 mm)", "", "AUC NWP memakai jumlah hujan prakiraan sebagai skor.", "",
          "| Lokasi | Lead | Frekuensi hujan uji | AUC NWP mentah | AUC klimatologi | AUC LightGBM terkoreksi | Brier klimatologi | Brier LightGBM |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
L_out += [f"| {r.site} | {r.L} | {r.frek:.2f} | {r.auc_nwp:.3f} | {r.auc_clim:.3f} | {r.auc_lgb:.3f} | {r.brier_clim:.3f} | {r.brier_lgb:.3f} |" for r in pd.DataFrame(RAIN).itertuples()]
open(f"{root}/hasil/koreksi_nwp{SUF}.md", "w", encoding="utf8").write("\n".join(L_out) + "\n"); print("\n".join(L_out))
