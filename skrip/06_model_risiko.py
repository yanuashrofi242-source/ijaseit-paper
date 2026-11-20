"""Langkah 5-7: model risiko OPT bulan berikutnya. Jalankan: python 06_model_risiko.py <folder kerja>
Skema: rolling-origin (uji 2023, 2024, 2025+) dan leave-one-village-out. Anomali cuaca dihitung dari data latih saja."""
import sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
import lightgbm as lgb
from catboost import CatBoostClassifier

root = sys.argv[1]
TGT = sys.argv[2] if len(sys.argv) > 2 else "LKSJ"   # LKSJ = keadaan serangan; SSJ = serangan baru
DESK = "keadaan serangan, memuat sisa bulan lalu" if TGT == "LKSJ" else "serangan baru"
ycol = "y_next" if TGT == "LKSJ" else "y_next_SSJ"; pcol = TGT
d = pd.read_csv(f"{root}/data_bersih/fitur_kalisat.csv", parse_dates=["Date", "target_date"])
om = "om_temp" in d.columns
W = (["om_temp", "om_humidity", "om_precip_total", "om_hari_hujan", "om_windspeed", "om_vpd", "om_lwd_jam_per_hari"] if om
     else ["temp", "humidity", "precip", "windspeed", "vpd", "lwd"])
src = "Open-Meteo unduhan ulang" if om else "cuaca bawaan (sebagian besar TIDAK asli; hasil belum bisa dipercaya)"
season = ["bulan_sin", "bulan_cos", "mangsa_idx"]
hist = ["LKSJ", "LKSJ_l1", "LKSJ_l2", "LKSJ_riwayat3", "LT"] if TGT == "LKSJ" else ["SSJ", "SSJ_l1", "SSJ_l2", "LKSJ", "LT"]
wl = [f"{c}_l{k}" for c in W for k in (1, 2, 3)]

def add_anom(tr, te):
    base = tr.groupby("Desa")[W].mean()
    out = []
    for part in (tr.copy(), te.copy()):
        for c in W + wl:
            b = c.rsplit("_l", 1)[0] if c in wl else c
            part[c + "_an"] = part[c] - part.Desa.map(base[b]).fillna(tr[b].mean())
        out.append(part)
    return out
an = [c + "_an" for c in W + wl]
SETS = {"riwayat + musim": hist + season, "cuaca anomali + musim": an + season, "riwayat + cuaca anomali + musim": hist + an + season}

def models():
    return {
        "Logistik": make_pipeline(StandardScaler(), LogisticRegression(C=0.3, max_iter=2000, class_weight="balanced")),
        "SVM rbf (draft)": make_pipeline(StandardScaler(), SVC(C=1, gamma="scale", probability=True, class_weight="balanced", random_state=0)),
        "Random Forest": RandomForestClassifier(300, min_samples_leaf=3, class_weight="balanced", random_state=0, n_jobs=-1),
        "LightGBM": lgb.LGBMClassifier(n_estimators=200, learning_rate=0.03, num_leaves=8, min_child_samples=10, subsample=0.8, subsample_freq=1,
                                       colsample_bytree=0.8, reg_lambda=2, class_weight="balanced", random_state=0, verbose=-1),
        "CatBoost": CatBoostClassifier(iterations=300, depth=4, learning_rate=0.05, auto_class_weights="Balanced", random_seed=0, verbose=0),
    }
folds = {"rolling": [(d.target_date < "2023-01-01", (d.target_date >= "2023-01-01") & (d.target_date < "2024-01-01")),
                     (d.target_date < "2024-01-01", (d.target_date >= "2024-01-01") & (d.target_date < "2025-01-01")),
                     (d.target_date < "2025-01-01", d.target_date >= "2025-01-01")],
         "leave-village-out": [(d.Desa != v, d.Desa == v) for v in sorted(d.Desa.unique())]}
rng = np.random.default_rng(0)
def ci(y, p, n=500):
    v = []
    for _ in range(n):
        s = rng.integers(0, len(y), len(y))
        if y[s].min() != y[s].max(): v.append(roc_auc_score(y[s], p[s]))
    return np.percentile(v, [2.5, 97.5])

L = ["# Model risiko OPT bulan berikutnya (hasil awal)", "", f"Sumber cuaca: **{src}**.", "",
     f"Target: ada/tidak serangan ({TGT} > 0) pada bulan berikutnya ({DESK}). AUC dan PR-AUC dihitung dari prediksi gabungan seluruh fold uji; CI 95% bootstrap baris (cenderung terlalu sempit karena baris satu desa berkorelasi).",
     f"Prevalensi positif: {d[ycol].mean():.3f}. Untuk leave-village-out, anomali cuaca memakai rata-rata desa sendiri (sedikit bocor, tercatat sebagai batasan).", ""]
for scheme, fl in folds.items():
    L += [f"## {scheme}", "", "| Fitur | Model | AUC | CI 95% | PR-AUC | Brier |", "| --- | --- | --- | --- | --- | --- |"]
    # pembanding tanpa model
    ys, ps_per, pp = [], [], []
    for tri, tei in fl:
        te = d[tei]; ys.append(te[ycol].values); ps_per.append((te[pcol] > 0).astype(float).values); pp.append(np.full(len(te), d[tri][ycol].mean()))
    y = np.concatenate(ys)
    for nm, p in (("persistensi (bulan ini ada serangan)", np.concatenate(ps_per)), ("prevalensi latih", np.concatenate(pp))):
        L.append(f"| - | {nm} | {roc_auc_score(y, p):.3f} | - | {average_precision_score(y, p):.3f} | {brier_score_loss(y, np.clip(p, 0, 1)):.3f} |")
    res = {}
    for sname, feats in SETS.items():
        for mname in models():
            ys, ps = [], []
            for tri, tei in fl:
                tr, te = add_anom(d[tri], d[tei])
                m = models()[mname]; med = tr[feats].median()
                m.fit(tr[feats].fillna(med), tr[ycol]); ps.append(m.predict_proba(te[feats].fillna(med))[:, 1]); ys.append(te[ycol].values)
            y, p = np.concatenate(ys), np.concatenate(ps); lo, hi = ci(y, p)
            res[(sname, mname)] = (roc_auc_score(y, p), lo, hi, average_precision_score(y, p), brier_score_loss(y, p))
    for (sname, mname), (a, lo, hi, ap, br) in res.items():
        L.append(f"| {sname} | {mname} | {a:.3f} | {lo:.2f}-{hi:.2f} | {ap:.3f} | {br:.3f} |")
    L.append("")
    print(scheme, "selesai", flush=True)

# SHAP LightGBM pada latih <2025, set lengkap
import shap
tr, te = add_anom(d[d.target_date < "2025-01-01"], d[d.target_date >= "2025-01-01"])
feats = SETS["riwayat + cuaca anomali + musim"]
m = models()["LightGBM"]; med = tr[feats].median(); m.fit(tr[feats].fillna(med), tr[ycol])
sv = shap.TreeExplainer(m).shap_values(te[feats].fillna(med))
sv = sv[1] if isinstance(sv, list) else sv
imp = pd.Series(np.abs(sv).mean(0), index=feats).sort_values(ascending=False).head(12)
L += ["## Fitur terpenting (SHAP rata-rata mutlak, LightGBM, uji 2025+)", "", "| Fitur | |SHAP| |", "| --- | --- |"] + [f"| {k} | {v:.3f} |" for k, v in imp.items()]
L += ["", "Catatan: bila sumber cuaca masih 'bawaan', fitur cuaca bisa hanya menandai waktu atau desa, bukan cuaca sebenarnya."]
open(f"{root}/hasil/risiko_awal.md" if TGT == "LKSJ" else f"{root}/hasil/risiko_SSJ.md", "w", encoding="utf8").write("\n".join(L) + "\n")
print("\n".join(L))
