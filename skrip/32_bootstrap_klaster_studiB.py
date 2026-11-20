"""Studi B: bootstrap berklaster (desa, bulan) dan kalibrasi ulang probabilitas. Turunan 10_model_indeks.py.
Pakai: python 32_bootstrap_klaster_studiB.py <folder kerja>
Langkah 4 (lanjutan): indeks agro-meteorologi HARIAN -> fitur desa x bulan, lalu uji apakah menambah prediksi OPT.
Pakai:  python 10_model_indeks.py <folder kerja>
Masukan : data_bersih/weather_desa_harian.csv (02), data_bersih/fitur_kalisat.csv (03)
Keluaran: data_bersih/indeks_harian_bulanan.csv, hasil/risiko_indeks.md
Anomali indeks dihitung dari data LATIH saja (rata-rata per bulan kalender, semua desa)."""
import sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
import lightgbm as lgb

root = sys.argv[1]
h = pd.read_csv(f"{root}/data_bersih/weather_desa_harian.csv", parse_dates=["date"]).sort_values(["Desa", "date"])
h["Date"] = h.date.dt.to_period("M").dt.to_timestamp()
h["hujan"] = (h.p_sum >= 1).astype(int)
h["deras"] = (h.p_sum >= 20).astype(int)
h["kering"] = (h.p_sum < 1).astype(int)
h["gdd10"] = (h.t_mean - 10).clip(lower=0)
h["trange"] = h.t_max - h.t_min

def run_max(s):
    best = cur = 0
    for v in s:
        cur = cur + 1 if v else 0; best = max(best, cur)
    return best

rows = []
for (desa, bln), g in h.groupby(["Desa", "Date"]):
    l14 = g.tail(14)
    rows.append(dict(Desa=desa, Date=bln,
        ix_hari_hujan=g.hujan.sum(), ix_hari_deras=g.deras.sum(), ix_hujan_total=g.p_sum.sum(), ix_hujan_maks=g.p_sum.max(),
        ix_kering_beruntun=run_max(g.kering.values), ix_gdd10=g.gdd10.sum(), ix_trange=g.trange.mean(),
        ix_rh90_jam=g.rh90_jam.sum(), ix_rh=g.rh_mean.mean(), ix_vpd=g.vpd_mean.mean(), ix_angin=g.w_mean.mean(),
        ix14_hujan=l14.p_sum.sum(), ix14_rh=l14.rh_mean.mean(), ix14_t=l14.t_mean.mean(), ix14_rh90=l14.rh90_jam.sum(), ix14_hari_hujan=l14.hujan.sum()))
ix = pd.DataFrame(rows).sort_values(["Desa", "Date"])
base_cols = [c for c in ix.columns if c.startswith("ix")]
for c in ["ix_hujan_total", "ix_hari_hujan", "ix_rh90_jam", "ix_vpd", "ix_gdd10", "ix14_rh90"]:
    for k in (1, 2):
        ix[f"{c}_l{k}"] = ix.groupby("Desa")[c].shift(k)
ix.to_csv(f"{root}/data_bersih/indeks_harian_bulanan.csv", index=False)

d = pd.read_csv(f"{root}/data_bersih/fitur_kalisat.csv", parse_dates=["Date", "target_date"]).merge(ix, on=["Desa", "Date"], how="left")
IX = [c for c in ix.columns if c.startswith("ix")]
season = ["bulan_sin", "bulan_cos", "mangsa_idx"]
WM = ["om_temp", "om_humidity", "om_precip_total", "om_hari_hujan", "om_windspeed", "om_vpd", "om_lwd_jam_per_hari"]
d["bln"] = d.Date.dt.month

def add_anom(tr, te, cols):
    mu = tr.groupby("bln")[cols].mean()
    out = []
    for part in (tr.copy(), te.copy()):
        a = part[cols].values - mu.reindex(part.bln).values
        part[[c + "_an" for c in cols]] = a
        out.append(part)
    return out

def models():
    return {"Logistik": make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=3000, class_weight="balanced")),
            "Random Forest": RandomForestClassifier(300, min_samples_leaf=3, class_weight="balanced", random_state=0, n_jobs=-1),
            "LightGBM": lgb.LGBMClassifier(n_estimators=200, learning_rate=0.03, num_leaves=8, min_child_samples=10, subsample=0.8, subsample_freq=1,
                                           colsample_bytree=0.8, reg_lambda=2, class_weight="balanced", random_state=0, verbose=-1)}

folds = {"rolling": [(d.target_date < "2023-01-01", (d.target_date >= "2023-01-01") & (d.target_date < "2024-01-01")),
                     (d.target_date < "2024-01-01", (d.target_date >= "2024-01-01") & (d.target_date < "2025-01-01")),
                     (d.target_date < "2025-01-01", d.target_date >= "2025-01-01")],
         "leave-village-out": [(d.Desa != v, d.Desa == v) for v in sorted(d.Desa.unique())]}
rng = np.random.default_rng(0)


def auc_safe(y, p):
    return roc_auc_score(y, p) if y.min() != y.max() else np.nan
def cluster_boot(y, p1, p0, grp, n=1000):
    """Bootstrap berklaster: sampel ulang klaster (desa atau bulan) dengan pengembalian; semua baris klaster ikut."""
    u = np.unique(grp); idx = {g: np.flatnonzero(grp == g) for g in u}; a, dl = [], []
    for _ in range(n):
        s = np.concatenate([idx[g] for g in rng.choice(u, len(u))])
        if y[s].min() == y[s].max(): continue
        x1 = roc_auc_score(y[s], p1[s]); a.append(x1); dl.append(x1 - roc_auc_score(y[s], p0[s]))
    return np.percentile(a, [2.5, 97.5]), np.percentile(dl, [2.5, 97.5])
def row_boot(y, p1, p0, n=1000):
    a, dl = [], []
    for _ in range(n):
        s = rng.integers(0, len(y), len(y))
        if y[s].min() == y[s].max(): continue
        x1 = roc_auc_score(y[s], p1[s]); a.append(x1); dl.append(x1 - roc_auc_score(y[s], p0[s]))
    return np.percentile(a, [2.5, 97.5]), np.percentile(dl, [2.5, 97.5])
rows = []; CAL = []
ycol = "y_next_SSJ"; hist = ["SSJ", "SSJ_l1", "SSJ_l2", "LKSJ", "LT"]
sets = {"history + season": (hist + season, []), "monthly weather + season": (season, WM), "daily indices + season": (season, IX),
        "history + monthly weather + season": (hist + season, WM), "history + daily indices + season": (hist + season, IX)}
for scheme, fl in folds.items():
    P, Y, GV, GM, PRI = {}, None, None, None, None
    for sname, (fixed, an) in sets.items():
        for mname in models():
            ys, ps, gv, gm, pri = [], [], [], [], []
            for tri, tei in fl:
                tr, te = d[tri], d[tei]; cols = fixed
                if an: tr, te = add_anom(tr, te, an); cols = fixed + [c + "_an" for c in an]
                m = models()[mname]; med = tr[cols].median(); m.fit(tr[cols].fillna(med), tr[ycol])
                ps.append(m.predict_proba(te[cols].fillna(med))[:, 1]); ys.append(te[ycol].values); gv.append(te.Desa.values); gm.append(te.target_date.values.astype("datetime64[M]").astype(str)); pri.append(np.full(len(te), tr[ycol].mean()))
            P[(sname, mname)] = np.concatenate(ps); Y = np.concatenate(ys); GV = np.concatenate(gv); GM = np.concatenate(gm); PRI = np.concatenate(pri)
    for (sname, mname), p in P.items():
        p0 = P[("history + season", mname)]
        ci_r, dci_r = row_boot(Y, p, p0); ci_v, dci_v = cluster_boot(Y, p, p0, GV); ci_m, dci_m = cluster_boot(Y, p, p0, GM)
        rows.append(dict(scheme=scheme, features=sname, model=mname, n=len(Y), pos=int(Y.sum()), auc=roc_auc_score(Y, p), auc_diff=roc_auc_score(Y, p) - roc_auc_score(Y, p0),
                         ci_row_lo=ci_r[0], ci_row_hi=ci_r[1], ci_village_lo=ci_v[0], ci_village_hi=ci_v[1], ci_month_lo=ci_m[0], ci_month_hi=ci_m[1],
                         d_row_lo=dci_r[0], d_row_hi=dci_r[1], d_village_lo=dci_v[0], d_village_hi=dci_v[1], d_month_lo=dci_m[0], d_month_hi=dci_m[1]))
        if sname == "history + season":   # kalibrasi ulang: koreksi pergeseran prior dari bobot kelas seimbang
            lg = np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6))) + np.log(PRI / (1 - PRI)); pc = 1 / (1 + np.exp(-lg))
            q = np.quantile(pc, [0, .25, .5, .75, 1]); bins = np.digitize(pc, np.unique(np.quantile(pc, [.2, .4, .6, .8])))
            rel = [(float(pc[bins == b].mean()), float(Y[bins == b].mean()), int((bins == b).sum())) for b in np.unique(bins)]
            CAL.append(dict(scheme=scheme, model=mname, brier_raw=brier_score_loss(Y, p), brier_corrected=brier_score_loss(Y, pc), brier_prevalence=brier_score_loss(Y, PRI),
                            mean_pred_raw=p.mean(), mean_pred_corrected=pc.mean(), observed=Y.mean(), auc_unchanged=roc_auc_score(Y, pc), reliability=rel))
    print(scheme, "selesai", flush=True)
R = pd.DataFrame(rows); R.to_csv(f"{root}/hasil/studiB_bootstrap_klaster.csv", index=False)
C = pd.DataFrame(CAL); C.to_csv(f"{root}/hasil/studiB_kalibrasi_ulang.csv", index=False)
pd.set_option("display.width", 250)
print(R[["scheme", "features", "model", "auc", "auc_diff", "ci_row_lo", "ci_row_hi", "ci_village_lo", "ci_village_hi", "ci_month_lo", "ci_month_hi"]].round(3).to_string())
print(R[["scheme", "features", "model", "auc_diff", "d_row_lo", "d_row_hi", "d_village_lo", "d_village_hi", "d_month_lo", "d_month_hi"]].round(3).to_string())
print(C.drop(columns="reliability").round(3).to_string())
