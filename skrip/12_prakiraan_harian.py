"""Studi A tahap 2: prakiraan cuaca harian dari Open-Meteo 2005-2026, dua lokasi (Kalisat utama, Surabaya titik sensor).
Pakai: python 12_prakiraan_harian.py <folder kerja>   Keluaran: hasil/prakiraan_harian.md
Latih: 2005-2021, uji: 2023-2026 (kronologis, 2022 dilewatkan sebagai jeda). Klimatologi dihitung dari data latih saja.
Catatan: data Open-Meteo arsip adalah produk reanalisis, bukan pengukuran stasiun."""
import sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, brier_score_loss
import lightgbm as lgb
root = sys.argv[1]
SITES = {"Kalisat": "om_harian_kalisat_2005_sekarang.csv", "Surabaya": "om_harian_sensor_2005_sekarang.csv"}
VARS = {"suhu": "temperature_2m_mean", "rh": "relative_humidity_2m_mean", "angin": "wind_speed_10m_mean", "hujan": "precipitation_sum"}
SAT = {"suhu": "C", "rh": "%", "angin": "km/h", "hujan": "mm"}
HZ = (1, 3, 7)
TR_END, TE_START = "2021-12-31", "2023-01-01"

def load(f):
    d = pd.read_csv(f"{root}/data_bersih/{f}", parse_dates=["time"]).set_index("time").sort_index()
    return d.asfreq("D")
def feats(d):
    X = pd.DataFrame(index=d.index)
    cols = {"suhu": "temperature_2m_mean", "tmax": "temperature_2m_max", "tmin": "temperature_2m_min", "rh": "relative_humidity_2m_mean",
            "angin": "wind_speed_10m_mean", "hujan": "precipitation_sum", "rad": "shortwave_radiation_sum"}
    for k, c in cols.items():
        for l in range(0, 7): X[f"{k}_l{l}"] = d[c].shift(l)
        X[f"{k}_m7"] = d[c].rolling(7).mean(); X[f"{k}_m30"] = d[c].rolling(30).mean()
    X["doy_sin"] = np.sin(2 * np.pi * d.index.dayofyear / 365.25); X["doy_cos"] = np.cos(2 * np.pi * d.index.dayofyear / 365.25)
    return X
def lgbm(): return lgb.LGBMRegressor(n_estimators=300, learning_rate=0.03, num_leaves=15, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, verbose=-1, random_state=0)

D = {s: load(f) for s, f in SITES.items()}; XF = {s: feats(d) for s, d in D.items()}
rows, rain = [], []
def clim_fn(d, v, tgt_dates):
    tr = d[VARS[v]][d.index <= TR_END]; c = tr.groupby(tr.index.dayofyear).mean()
    return np.array([c.get(t.dayofyear, np.nan) for t in tgt_dates])
def mae(a, b): k = ~(np.isnan(a) | np.isnan(b)); return np.mean(np.abs(a[k] - b[k]))

for site, d in D.items():
    X = XF[site]
    for H in HZ:
        for v in VARS:
            y = d[VARS[v]].shift(-H)
            ok = X.notna().all(axis=1) & y.notna()
            tr = ok & (d.index <= TR_END); te = ok & (d.index >= TE_START)
            yt = y[te].values; tgt = d.index[te] + pd.Timedelta(days=H)
            res = {"Persistensi": d[VARS[v]][te].values, "Klimatologi": clim_fn(d, v, tgt)}
            tf = (lambda a: np.log1p(a)) if v == "hujan" else (lambda a: a); inv = (lambda a: np.clip(np.expm1(a), 0, None)) if v == "hujan" else (lambda a: a)
            res["Ridge"] = inv(make_pipeline(StandardScaler(), Ridge(10.0)).fit(X[tr], tf(y[tr])).predict(X[te]))
            m = lgbm().fit(X[tr], tf(y[tr])); res["LightGBM"] = inv(m.predict(X[te]))
            if site == "Surabaya" and "Kalisat" in D:   # transfer: model dilatih di Kalisat saja
                Xk = XF["Kalisat"]; yk = D["Kalisat"][VARS[v]].shift(-H); okk = Xk.notna().all(axis=1) & yk.notna() & (D["Kalisat"].index <= TR_END)
                res["LightGBM transfer (latih Kalisat)"] = inv(lgbm().fit(Xk[okk], tf(yk[okk])).predict(X[te]))
            mp = mae(yt, res["Persistensi"])
            for nm, p in res.items():
                rows.append(dict(site=site, H=H, var=v, model=nm, mae=mae(yt, p), skill_pers=1 - mae(yt, p) / mp, rmse=np.sqrt(np.nanmean((yt - p) ** 2))))
        # kejadian hujan >= 1 mm
        yb = (d.hujan if False else d.precipitation_sum).shift(-H) >= 1
        ok = X.notna().all(axis=1) & d.precipitation_sum.shift(-H).notna()
        tr = ok & (d.index <= TR_END); te = ok & (d.index >= TE_START)
        clf = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.03, num_leaves=15, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, verbose=-1, random_state=0).fit(X[tr], yb[tr].astype(int))
        p = clf.predict_proba(X[te])[:, 1]; yy = yb[te].astype(int).values
        tr_d = d.precipitation_sum[d.index <= TR_END]; cl = (tr_d >= 1).groupby(tr_d.index.dayofyear).mean()
        pc = np.array([cl.get(t.dayofyear, np.nan) for t in d.index[te] + pd.Timedelta(days=H)])
        pp = (d.precipitation_sum[te] >= 1).astype(float).values
        rain.append(dict(site=site, H=H, auc=roc_auc_score(yy, p), brier=brier_score_loss(yy, p), brier_clim=brier_score_loss(yy, pc), brier_pers=brier_score_loss(yy, pp),
                         auc_clim=roc_auc_score(yy, pc), frek=yy.mean()))
R = pd.DataFrame(rows); RN = pd.DataFrame(rain)
L = ["# Prakiraan harian Open-Meteo, dua lokasi (Studi A, tahap 2)", "",
     f"Latih 2005-2021, uji {TE_START[:4]}-2026 (n uji sekitar {int((D['Kalisat'].index>=TE_START).sum())-7} hari per lokasi). Tanpa penyetelan hiperparameter. Skill = 1 - MAE/MAE persistensi (positif berarti lebih baik dari persistensi).",
     "Data Open-Meteo arsip = reanalisis, bukan pengukuran stasiun; hasil ini mengukur prakiraan terhadap produk reanalisis.", ""]
for site in SITES:
    L += [f"## {site}", "", "| Variabel | Horizon (hari) | Model | MAE | RMSE | Skill vs persistensi |", "| --- | --- | --- | --- | --- | --- |"]
    for _, r in R[R.site == site].iterrows():
        L.append(f"| {r['var']} ({SAT[r['var']]}) | {r.H} | {r.model} | {r.mae:.2f} | {r.rmse:.2f} | {r.skill_pers:+.0%} |")
    L.append("")
L += ["## Kejadian hujan (>= 1 mm) pada hari sasaran", "", "| Lokasi | Horizon | Frekuensi hujan uji | AUC LightGBM | AUC klimatologi | Brier LightGBM | Brier klimatologi | Brier persistensi |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for _, r in RN.iterrows():
    L.append(f"| {r.site} | {r.H} | {r.frek:.2f} | {r.auc:.3f} | {r.auc_clim:.3f} | {r.brier:.3f} | {r.brier_clim:.3f} | {r.brier_pers:.3f} |")
open(f"{root}/hasil/prakiraan_harian.md", "w", encoding="utf8").write("\n".join(L) + "\n"); print("\n".join(L))
