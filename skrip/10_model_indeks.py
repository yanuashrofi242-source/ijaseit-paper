"""Langkah 4 (lanjutan): indeks agro-meteorologi HARIAN -> fitur desa x bulan, lalu uji apakah menambah prediksi OPT.
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
from sklearn.metrics import roc_auc_score, average_precision_score
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

def boot(y, p1, p0, n=1000):
    """CI AUC p1 dan CI selisih AUC (p1 - p0), bootstrap baris berpasangan."""
    a, dl = [], []
    for _ in range(n):
        s = rng.integers(0, len(y), len(y))
        if y[s].min() == y[s].max(): continue
        x1 = roc_auc_score(y[s], p1[s]); a.append(x1); dl.append(x1 - roc_auc_score(y[s], p0[s]))
    return np.percentile(a, [2.5, 97.5]), np.percentile(dl, [2.5, 97.5])

L = ["# Indeks agro-meteorologi harian vs riwayat serangan", "",
     f"Indeks per desa x bulan dari cuaca harian Open-Meteo ({len(IX)} kolom: hari hujan, hari deras >= 20 mm, hari kering beruntun, derajat-hari basis 10, jam RH > 90, VPD, jendela 14 hari terakhir, lag 1-2 bulan).",
     "Anomali indeks = nilai dikurangi rata-rata bulan kalender dari data latih. Selisih AUC memakai bootstrap berpasangan terhadap 'riwayat + musim' (model yang sama).", ""]
summary = []
TARGETS = tuple(sys.argv[2:]) or ("SSJ", "LKSJ")   # contoh: python 10_model_indeks.py <folder> SSJ
for TGT in TARGETS:
    ycol = "y_next_SSJ" if TGT == "SSJ" else "y_next"
    hist = ["SSJ", "SSJ_l1", "SSJ_l2", "LKSJ", "LT"] if TGT == "SSJ" else ["LKSJ", "LKSJ_l1", "LKSJ_l2", "LKSJ_riwayat3", "LT"]
    sets = {"riwayat + musim": (hist + season, []),
            "cuaca bulanan + musim": (season, WM),
            "indeks harian + musim": (season, IX),
            "riwayat + cuaca bulanan + musim": (hist + season, WM),
            "riwayat + indeks harian + musim": (hist + season, IX)}
    for scheme, fl in folds.items():
        L += [f"## Target {TGT} > 0 bulan berikutnya, {scheme}", "", "| Fitur | Model | AUC | CI 95% | selisih vs riwayat+musim (CI 95%) | PR-AUC |", "| --- | --- | --- | --- | --- | --- |"]
        P, Y = {}, None
        for sname, (fixed, an) in sets.items():
            for mname in models():
                ys, ps = [], []
                for tri, tei in fl:
                    tr, te = d[tri], d[tei]
                    cols = fixed
                    if an:
                        tr, te = add_anom(tr, te, an); cols = fixed + [c + "_an" for c in an]
                    m = models()[mname]; med = tr[cols].median()
                    m.fit(tr[cols].fillna(med), tr[ycol]); ps.append(m.predict_proba(te[cols].fillna(med))[:, 1]); ys.append(te[ycol].values)
                P[(sname, mname)] = np.concatenate(ps); Y = np.concatenate(ys)
        for (sname, mname), p in P.items():
            p0 = P[("riwayat + musim", mname)]; ci, dci = boot(Y, p, p0)
            a = roc_auc_score(Y, p); da = a - roc_auc_score(Y, p0)
            L.append(f"| {sname} | {mname} | {a:.3f} | {ci[0]:.2f}-{ci[1]:.2f} | {da:+.3f} ({dci[0]:+.2f} s.d. {dci[1]:+.2f}) | {average_precision_score(Y, p):.3f} |")
            summary.append((TGT, scheme, sname, mname, a, da, dci[0], dci[1]))
        L.append("")
        print(TGT, scheme, "selesai", flush=True)
s = pd.DataFrame(summary, columns=["target", "skema", "fitur", "model", "auc", "selisih", "lo", "hi"])
sig = s[(s.fitur.str.contains("indeks|cuaca")) & (s.fitur.str.startswith("riwayat")) & (s.lo > 0)]
L += ["## Ringkasan", "", f"Kombinasi 'riwayat + cuaca/indeks' yang selisih AUC-nya di atas 0 dengan CI 95% (di atas riwayat + musim saja): **{len(sig)}** dari {len(s[(s.fitur.str.startswith('riwayat +')) & (~s.fitur.eq('riwayat + musim'))])}.", ""]
if len(sig): L += [f"- {r.target} {r.skema} {r.fitur} {r.model}: {r.selisih:+.3f} ({r.lo:+.2f} s.d. {r.hi:+.2f})" for r in sig.itertuples()]
open(f"{root}/hasil/risiko_indeks_{'_'.join(TARGETS)}.md", "w", encoding="utf8").write("\n".join(L) + "\n")
print("\n".join(L[-12:]))
