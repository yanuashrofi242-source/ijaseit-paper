"""Apakah Pranata Mangsa memprediksi serangan OPT lebih baik daripada bulan kalender?
Pakai: python 08_mangsa_vs_bulan.py <folder kerja>. Butuh data_bersih/fitur_kalisat.csv (hasil 03)."""
import sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from scipy.stats import kruskal
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score
root = sys.argv[1]
d = pd.read_csv(f"{root}/data_bersih/fitur_kalisat.csv", parse_dates=["Date", "target_date"])
d["bulan"] = d.Date.dt.month
d["ada"] = (d.LKSJ > 0).astype(int)
L = ["# Pranata Mangsa vs bulan kalender (data Kalisat)", "",
     f"{len(d)} baris desa x bulan. Mangsa ditetapkan dari tanggal tengah bulan (versi umum Surakarta), jadi resolusi bulanan membatasi uji ini; ulangi dengan data harian bila ada.", ""]
g = d.groupby("mangsa").agg(n=("ada", "size"), persen_ada_serangan=("ada", lambda s: round(100 * s.mean())), rata_LKSJ_ha=("LKSJ", "mean")).round(2)
order = ["Kasa", "Karo", "Katelu", "Kapat", "Kalima", "Kanem", "Kapitu", "Kawolu", "Kasanga", "Kasadasa", "Dhesta", "Sadha"]
g = g.reindex([m for m in order if m in g.index])
L += ["## Serangan per mangsa (bulan berjalan)", "", "| Mangsa | n | % bulan ada serangan | Rata-rata LKSJ (ha) |", "| --- | --- | --- | --- |"]
L += [f"| {i} | {r.n} | {r.persen_ada_serangan} | {r.rata_LKSJ_ha} |" for i, r in g.iterrows()]
kw_m = kruskal(*[x.LKSJ.values for _, x in d.groupby("mangsa")]); kw_b = kruskal(*[x.LKSJ.values for _, x in d.groupby("bulan")])
L += ["", f"Uji Kruskal-Wallis LKSJ antar kelompok: mangsa p = {kw_m.pvalue:.3f}; bulan kalender p = {kw_b.pvalue:.3f}.", ""]
folds = [(d.target_date < "2023-01-01", (d.target_date >= "2023-01-01") & (d.target_date < "2024-01-01")),
         (d.target_date < "2024-01-01", (d.target_date >= "2024-01-01") & (d.target_date < "2025-01-01")),
         (d.target_date < "2025-01-01", d.target_date >= "2025-01-01")]
def auc(cols, hist=False):
    ys, ps = [], []
    for tri, tei in folds:
        X = pd.get_dummies(d[cols].astype(str)).astype(float)
        if hist: X = pd.concat([X, d[["LKSJ", "LKSJ_l1", "LKSJ_riwayat3"]]], axis=1)
        m = LogisticRegression(C=0.5, max_iter=3000).fit(X[tri], d.y_next[tri])
        ps.append(m.predict_proba(X[tei])[:, 1]); ys.append(d.y_next[tei].values)
    y, p = np.concatenate(ys), np.concatenate(ps)
    return roc_auc_score(y, p), average_precision_score(y, p)
L += ["## Prediksi serangan bulan berikutnya (logistik, rolling-origin 2023, 2024, 2025+)", "", "| Prediktor | AUC | PR-AUC |", "| --- | --- | --- |"]
for nm, cols, h in (("Pranata Mangsa saja (12 fase)", ["mangsa"], False), ("Bulan kalender saja (12 bulan)", ["bulan"], False),
                    ("Desa saja", ["Desa"], False), ("Riwayat serangan saja", ["Desa"][:0] or ["bulan"], None)):
    if h is None: continue
    a, ap = auc(cols, h); L.append(f"| {nm} | {a:.3f} | {ap:.3f} |")
y = np.concatenate([d.y_next[t].values for _, t in folds]); p = np.concatenate([(d.LKSJ[t] > 0).astype(float).values for _, t in folds])
L.append(f"| Persistensi (bulan ini ada serangan) | {roc_auc_score(y, p):.3f} | {average_precision_score(y, p):.3f} |")
for nm, cols in (("Mangsa + riwayat serangan", ["mangsa"]), ("Bulan + riwayat serangan", ["bulan"])):
    a, ap = auc(cols, True); L.append(f"| {nm} | {a:.3f} | {ap:.3f} |")
L += ["", "Catatan: nilai AUC dekat 0,5 berarti penanda musim tidak informatif untuk prediksi lintas tahun. Uji kecil; baca bersama interval kepercayaan dari `06_model_risiko.py`."]
open(f"{root}/hasil/mangsa_vs_bulan.md", "w", encoding="utf8").write("\n".join(L) + "\n"); print("\n".join(L))
