"""Koreksi perbandingan ganda (Holm) untuk uji Diebold-Mariano Studi A.
Pakai: python 30_holm_dm.py <folder hasil>   (butuh _pred.pkl dari 15, studiA_nn_hasil.csv, studiA_nbeats_hasil.csv, studiA_nbeats_kecil_hasil.csv)
Keluarga uji = 18 sel (2 lokasi x suhu, kelembapan, angin x lead 1, 3, 7) untuk satu jenis perbandingan."""
import sys, pickle, numpy as np, pandas as pd
from scipy import stats
out = sys.argv[1]
def dm(e1, e2, h):
    d = np.abs(e1) - np.abs(e2); n = len(d); dm_ = d - d.mean(); s = (dm_ ** 2).mean()
    for k in range(1, max(h, 1)): s += 2 * (1 - k / max(h, 1)) * (dm_[k:] * dm_[:-k]).mean()
    stat = d.mean() / np.sqrt(max(s, 1e-12) / n) * np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    return d.mean(), 2 * (1 - stats.t.cdf(abs(stat), df=n - 1))
def holm(p):
    p = np.asarray(p); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for r, i in enumerate(o):
        run = max(run, (m - r) * p[i]); adj[i] = min(1, run)
    return adj
P = pickle.load(open(f"{out}/_pred.pkl", "rb"))
rows = []
for (site, k, L), (dates, yt, M) in P.items():
    if k == "hujan": continue
    r = "Ridge walk-forward"; b = "Bias bergulir 30 hari"
    dmean, p = dm(yt - M[r], yt - M[b], L)
    rows.append(dict(family="Ridge vs rolling bias (n=487)", site=site, var=k, L=L, d=dmean, p=p))
    dmean, p = dm(yt - M[r], yt - M["NWP mentah"], L)
    rows.append(dict(family="Ridge vs raw NWP (n=487)", site=site, var=k, L=L, d=dmean, p=p))
    dmean, p = dm(yt - M[b], yt - M["NWP mentah"], L)
    rows.append(dict(family="Rolling bias vs raw NWP (n=487)", site=site, var=k, L=L, d=dmean, p=p))
    dmean, p = dm(yt - M["LightGBM residu walk-forward"], yt - M[b], L)
    rows.append(dict(family="LightGBM vs rolling bias (n=487)", site=site, var=k, L=L, d=dmean, p=p))
nn = pd.read_csv(f"{out}/studiA_nn_hasil.csv")
for _, r in nn.iterrows():
    rows.append(dict(family="BiGRU vs Ridge", site=r.site, var=r["var"], L=r.L, d=r["mae BiGRU-Attention kuantil (median)"] - r["mae Ridge walk-forward"], p=r.p_dm_vs_ridge))
    rows.append(dict(family="BiGRU vs rolling bias", site=r.site, var=r["var"], L=r.L, d=r["mae BiGRU-Attention kuantil (median)"] - r["mae Bias bergulir 30 hari"], p=r.p_dm_vs_bias))
for fn, nm in (("studiA_nbeats_hasil.csv", "N-BEATS-64"), ("studiA_nbeats_kecil_hasil.csv", "N-BEATS-16")):
    nb = pd.read_csv(f"{out}/{fn}"); mc = [c for c in nb.columns if c.startswith("mae") and "N-BEATS" in c or "NBEATS" in c.upper() and c.startswith("mae")]
    for _, r in nb.iterrows():
        rows.append(dict(family=f"{nm} vs Ridge", site=r.site, var=r["var"], L=r.L, d=r[mc[0]] - r["mae Ridge walk-forward"], p=r.p_dm_vs_ridge))
R = pd.DataFrame(rows); R["p_holm"] = np.nan
for f, g in R.groupby("family", sort=False): R.loc[g.index, "p_holm"] = holm(g.p.values)
R.to_csv(f"{out}/studiA_holm.csv", index=False)
S = []
for f, g in R.groupby("family", sort=False):
    S.append(dict(family=f, cells=len(g), better=int((g.d < 0).sum()), sig_raw=int((g.p < 0.05).sum()), sig_raw_better=int(((g.p < 0.05) & (g.d < 0)).sum()), sig_raw_worse=int(((g.p < 0.05) & (g.d > 0)).sum()),
                  sig_holm_better=int(((g.p_holm < 0.05) & (g.d < 0)).sum()), sig_holm_worse=int(((g.p_holm < 0.05) & (g.d > 0)).sum())))
S = pd.DataFrame(S); S.to_csv(f"{out}/studiA_holm_ringkasan.csv", index=False); print(S.to_string())
print(R[(R.p < 0.05)].sort_values(["family", "p"]).round(4).to_string())
