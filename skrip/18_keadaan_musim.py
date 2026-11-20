"""Studi C: prediksi keadaan musim (kering / peralihan / basah) per blok 10 harian pada lead 10, 20, 30, 60 hari.
Pakai: python 18_keadaan_musim.py <folder data> <folder keluaran>
Data  : om_harian_{kalisat,sensor}_2005_sekarang.csv (reanalisis Open-Meteo harian, 2005 sampai sekarang)
Keadaan: tertil curah hujan blok 10 harian dari data latih (kering, peralihan, basah).
Uji    : rolling-origin tahunan, tahun uji 2015 sampai 2025; latih = semua blok yang targetnya selesai sebelum 1 Januari tahun uji."""
import sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import f1_score, accuracy_score
import lightgbm as lgb
dd, out = sys.argv[1], sys.argv[2]
SITES = {"Kalisat": "om_harian_kalisat_2005_sekarang.csv", "Surabaya": "om_harian_sensor_2005_sekarang.csv"}
MANGSA = [("Kasa", 6, 22), ("Karo", 8, 2), ("Katelu", 8, 25), ("Kapat", 9, 18), ("Kalima", 10, 13), ("Kanem", 11, 9),
          ("Kapitu", 12, 22), ("Kawolu", 2, 3), ("Kasanga", 3, 1), ("Kasadasa", 3, 26), ("Dhesta", 4, 19), ("Sadha", 5, 12)]
def mangsa_idx(ts):
    md = (ts.month, ts.day)
    if ts.month == 1 or (ts.month == 2 and ts.day < 3): return 6
    best = None
    for i, (_, m, d) in enumerate(MANGSA):
        if md >= (m, d) and (best is None or (m, d) >= (MANGSA[best][1], MANGSA[best][2])): best = i
    return best
LEADS = {10: 1, 20: 2, 30: 3, 60: 6}; TEST_YEARS = list(range(2015, 2026)); NHIST = 6
rng = np.random.default_rng(0)

def blocks(f):
    d = pd.read_csv(f"{dd}/{f}", parse_dates=["time"]).set_index("time").sort_index()
    spd = d.wind_speed_10m_mean; ang = np.deg2rad(d.wind_direction_10m_dominant)
    d["u"] = -spd * np.sin(ang)
    part = np.where(d.index.day <= 10, 1, np.where(d.index.day <= 20, 2, 3))
    key = pd.MultiIndex.from_arrays([d.index.year, d.index.month, part], names=["y", "m", "p"])
    g = d.groupby(key)
    b = pd.DataFrame({"rain": g.precipitation_sum.sum(), "T": g.temperature_2m_mean.mean(), "RH": g.relative_humidity_2m_mean.mean(), "u": g.u.mean(), "n": g.size(), "start": g.apply(lambda x: x.index.min()), "end": g.apply(lambda x: x.index.max())})
    b = b[(b.n >= 8)].reset_index(drop=True)
    b["mid"] = b.start + (b.end - b.start) / 2
    b["slot"] = (b.mid.dt.month - 1) * 3 + (b.mid.dt.day.map(lambda x: 0 if x <= 10 else (1 if x <= 20 else 2)))
    b["mangsa"] = b.mid.map(mangsa_idx)
    b["sin"] = np.sin(2 * np.pi * b.mid.dt.dayofyear / 365.25); b["cos"] = np.cos(2 * np.pi * b.mid.dt.dayofyear / 365.25)
    return b

def mf1(y, p):
    cm = np.bincount(y * 3 + p, minlength=9).reshape(3, 3); tp = np.diag(cm); pr = cm.sum(0); re = cm.sum(1)
    f = np.where(pr + re > 0, 2 * tp / np.maximum(pr + re, 1), 0.0); return f.mean()

def mode_map(keys, y):
    m = pd.DataFrame({"k": keys, "y": y}).groupby("k").y.agg(lambda s: s.value_counts().idxmax())
    return m

rows = []; detail = []
for site, f in SITES.items():
    b = blocks(f); N = len(b)
    for L, h in LEADS.items():
        # indeks blok target i, origin i-h; butuh blok kontigu: periksa selisih tanggal
        idx = np.arange(NHIST - 1 + h, N)
        feat = ["rain", "T", "RH", "u"]
        recs = []
        for i in idx:
            o = i - h
            span = (b.mid.iloc[i] - b.mid.iloc[o - NHIST + 1]).days
            if span > 10.5 * (NHIST - 1 + h) + 12 or span < 10 * (NHIST - 1 + h) - 12: continue   # lewati celah
            x = b.loc[o - NHIST + 1:o, feat].values.ravel()
            recs.append((i, o, x))
        I = np.array([r[0] for r in recs]); Xw = np.array([r[2] for r in recs])
        cal = b.loc[I, ["sin", "cos"]].values
        yr = b.mid.iloc[I].dt.year.values
        for Y in TEST_YEARS:
            tr_blocks_cut = pd.Timestamp(f"{Y}-01-01")
            trm = b.end.iloc[I].values < np.datetime64(tr_blocks_cut)
            tem = yr == Y
            if tem.sum() == 0 or trm.sum() < 200: continue
            # tertil curah hujan dari seluruh blok latih (tanpa kebocoran)
            train_rain = b.rain[b.end < tr_blocks_cut]
            q1, q2 = np.quantile(train_rain, [1 / 3, 2 / 3])
            lab = lambda r: np.where(r < q1, 0, np.where(r < q2, 1, 2))
            ytrue = lab(b.rain.iloc[I].values)
            ycur = lab(b.rain.iloc[I - h].values)
            # baselines
            clim = mode_map(b.slot.iloc[I][trm].values, ytrue[trm]); mg = mode_map(b.mangsa.iloc[I][trm].values, ytrue[trm])
            p_clim = pd.Series(b.slot.iloc[I][tem].values).map(clim).fillna(1).astype(int).values
            p_man = pd.Series(b.mangsa.iloc[I][tem].values).map(mg).fillna(1).astype(int).values
            P = {"Persistence": ycur[tem], "Climatology (10-day slot)": p_clim, "Pranata Mangsa (phase mode)": p_man}
            for nm, X in (("with calendar", np.hstack([Xw, cal])), ("weather only", Xw)):
                lr = make_pipeline(StandardScaler(), LogisticRegression(C=0.3, max_iter=2000)).fit(X[trm], ytrue[trm])
                P[f"Logistic ({nm})"] = lr.predict(X[tem])
                gb = lgb.LGBMClassifier(n_estimators=150, learning_rate=0.05, num_leaves=6, min_child_samples=15, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=2, random_state=0, verbose=-1).fit(X[trm], ytrue[trm])
                P[f"LightGBM ({nm})"] = gb.predict(X[tem])
            for k, p in P.items():
                detail.append(pd.DataFrame({"site": site, "lead": L, "year": Y, "model": k, "y": ytrue[tem], "p": p}))
D = pd.concat(detail); D["y"] = D.y.astype(int); D["p"] = D.p.astype(int)
def boot_f1(y, p, B=500):
    n = len(y); v = []
    for _ in range(B):
        s = rng.integers(0, n, n); v.append(mf1(y[s], p[s]))
    return np.percentile(v, [2.5, 97.5])
res = []
for (site, L, m), g in D.groupby(["site", "lead", "model"]):
    y = g.y.values; p = g.p.values
    ci = boot_f1(y, p)
    res.append(dict(site=site, lead=L, model=m, n=len(g), macroF1=mf1(y, p), lo=ci[0], hi=ci[1], acc=accuracy_score(y, p)))
R = pd.DataFrame(res); R.to_csv(f"{out}/studiC_keadaan_musim.csv", index=False)
# selisih vs klimatologi (bootstrap berpasangan)
dl = []
for (site, L), g in D.groupby(["site", "lead"]):
    base = g[g.model == "Climatology (10-day slot)"].reset_index(drop=True)
    for m, gm in g.groupby("model"):
        if m == "Climatology (10-day slot)": continue
        gm = gm.reset_index(drop=True); n = len(gm); d0 = mf1(gm.y.values, gm.p.values) - mf1(base.y.values, base.p.values); v = []
        for _ in range(500):
            s = rng.integers(0, n, n); v.append(mf1(gm.y.values[s], gm.p.values[s]) - mf1(base.y.values[s], base.p.values[s]))
        lo, hi = np.percentile(v, [2.5, 97.5]); dl.append(dict(site=site, lead=L, model=m, dF1=d0, lo=lo, hi=hi))
Dl = pd.DataFrame(dl); Dl.to_csv(f"{out}/studiC_selisih_klimatologi.csv", index=False)
# deskripsi: curah hujan rata-rata per fase mangsa (Kalisat, 2005 sampai 2025)
desc = []
for site, f in SITES.items():
    b = blocks(f); b = b[b.mid.dt.year <= 2025]
    dm = b.groupby("mangsa").rain.mean() * 3.0   # mm per 30 hari setara
    desc.append(dm.rename(site))
desc = pd.concat(desc, axis=1); desc.index = [MANGSA[i][0] for i in desc.index]; desc.to_csv(f"{out}/studiC_hujan_per_mangsa.csv")
L = ["# Studi C: keadaan musim per blok 10 harian", "", "Keadaan = tertil curah hujan blok (batas dari data latih tiap tahun uji). Uji rolling-origin 2015-2025. CI 95% bootstrap baris (cenderung sempit).", ""]
for site in SITES:
    L += [f"## {site}", "", "| Model | " + " | ".join(f"{k} d" for k in LEADS) + " |", "| --- | " + " | ".join("---" for _ in LEADS) + " |"]
    for m in R.model.unique():
        cells = []
        for k in LEADS:
            r = R[(R.site == site) & (R.lead == k) & (R.model == m)].iloc[0]; cells.append(f"{r.macroF1:.3f} ({r.lo:.2f}-{r.hi:.2f})")
        L.append(f"| {m} | " + " | ".join(cells) + " |")
    L.append("")
L += ["## Selisih macro-F1 terhadap klimatologi (CI 95% bootstrap berpasangan)", "", "| Lokasi | Model | " + " | ".join(f"{k} d" for k in LEADS) + " |", "| --- | --- | " + " | ".join("---" for _ in LEADS) + " |"]
for site in SITES:
    for m in Dl.model.unique():
        cells = []
        for k in LEADS:
            r = Dl[(Dl.site == site) & (Dl.lead == k) & (Dl.model == m)].iloc[0]; cells.append(f"{r.dF1:+.3f} ({r.lo:+.2f},{r.hi:+.2f})")
        L.append(f"| {site} | {m} | " + " | ".join(cells) + " |")
L += ["", "## Curah hujan rata-rata per fase mangsa (mm per 30 hari setara, 2005-2025)", "", desc.round(0).to_markdown()]
open(f"{out}/studiC_keadaan_musim.md", "w", encoding="utf8").write("\n".join(L) + "\n"); print("\n".join(L))
