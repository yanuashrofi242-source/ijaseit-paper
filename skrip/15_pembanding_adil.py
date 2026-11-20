"""Studi A tahap 4: pembanding adil, konformal adaptif, dan uji Diebold-Mariano.
Pakai (Windows): python skrip\\15_pembanding_adil.py "D:\\JURNAL\\TOPIK 2\\kerja\\data_bersih" "D:\\JURNAL\\TOPIK 2\\kerja\\hasil"
Masukan (folder data_bersih): nwp_arsip_ecmwf_ifs025_kalisat.csv dan ..._sensor.csv (arsip ECMWF per jam), om_harian_kalisat_2005_sekarang.csv dan om_harian_sensor_2005_sekarang.csv (reanalisis harian).
Kebenaran = reanalisis Open-Meteo, bukan stasiun. Uji: 2025-07-01 sampai akhir data.
Metode: NWP mentah | persistensi | bias bergulir 30 hari | rata-rata (bias bergulir, persistensi) | Ridge tetap |
        Ridge walk-forward (refit tiap 30 hari, jendela 540 hari) | LightGBM residu walk-forward."""
import sys, warnings
import numpy as np, pandas as pd
from scipy import stats
warnings.filterwarnings("ignore")
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, brier_score_loss
import lightgbm as lgb

dd, out = sys.argv[1], sys.argv[2]
SITES = {"Kalisat": ("nwp_arsip_ecmwf_ifs025_kalisat.csv", "om_harian_kalisat_2005_sekarang.csv"),
         "Surabaya": ("nwp_arsip_ecmwf_ifs025_sensor.csv", "om_harian_sensor_2005_sekarang.csv")}   # nama berkas asli di data_bersih
V = {"suhu": ("temperature_2m", "temperature_2m_mean", "C"), "rh": ("relative_humidity_2m", "relative_humidity_2m_mean", "%"),
     "angin": ("wind_speed_10m", "wind_speed_10m_mean", "km/h"), "hujan": ("precipitation", "precipitation_sum", "mm")}
LEADS = (1, 3, 7)
T_FIX_TR, T_WF0, T_TE = "2025-02-28", "2025-03-01", "2025-07-01"   # Ridge tetap dilatih sampai T_FIX_TR; walk-forward mulai T_WF0 (untuk kalibrasi konformal)
WIN, STEP = 540, 30
rng = np.random.default_rng(0)

def daily_nwp(f):
    h = pd.read_csv(f, parse_dates=["time"]); h["d"] = h.time.dt.floor("D"); o = {}
    for k, (b, _, _) in V.items():
        for L in LEADS:
            a = h.groupby("d")[f"{b}_previous_day{L}"]
            o[f"{k}_n{L}"] = a.sum(min_count=24) if k == "hujan" else a.mean().where(a.count() >= 24)
    return pd.DataFrame(o)

def lgbr(): return lgb.LGBMRegressor(n_estimators=250, learning_rate=0.03, num_leaves=7, min_child_samples=15, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=3, verbose=-1, random_state=0)
def lgbc(): return lgb.LGBMClassifier(n_estimators=250, learning_rate=0.03, num_leaves=7, min_child_samples=15, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=3, verbose=-1, random_state=0)

def dm_test(e1, e2, h):
    """Diebold-Mariano (galat absolut), koreksi Harvey-Leybourne-Newbold; p dua sisi. d = |e1| - |e2|; negatif berarti model 1 lebih baik."""
    d = np.abs(e1) - np.abs(e2); n = len(d); dm = d - d.mean()
    g0 = (dm ** 2).mean(); s = g0
    for k in range(1, max(h, 1)):
        s += 2 * (1 - k / max(h, 1)) * (dm[k:] * dm[:-k]).mean()
    var = max(s, 1e-12) / n; stat = d.mean() / np.sqrt(var)
    hl = np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n); stat *= hl
    return d.mean(), 2 * (1 - stats.t.cdf(abs(stat), df=n - 1))

def boot_skill(e_new, e_ref, n=1000):
    a, b = np.abs(e_new), np.abs(e_ref); v = []
    for _ in range(n):
        s = rng.integers(0, len(a), len(a)); v.append(1 - a[s].mean() / b[s].mean())
    return np.percentile(v, [2.5, 97.5])

def aci(y, p, alpha=0.1, gamma=0.02, win=120, L=1):
    """Konformal adaptif (Gibbs-Candes) dengan kuantil jendela bergulir dari galat absolut yang SUDAH terverifikasi (tertunda L hari)."""
    n = len(y); a_t = alpha; lo = np.full(n, np.nan); hi = np.full(n, np.nan); err = np.full(n, np.nan)
    ae = np.abs(y - p)
    for t in range(n):
        known = ae[max(0, t - L - win + 1): t - L + 1] if t - L >= 0 else np.array([])
        if len(known) < 30: continue
        lvl = float(np.clip(1 - a_t, 0.5, 0.999)); q = np.quantile(known, lvl)
        lo[t], hi[t] = p[t] - q, p[t] + q; err[t] = float(not (lo[t] <= y[t] <= hi[t]))
        if t - L >= 0 and not np.isnan(err[t - L]): a_t = a_t + gamma * (alpha - err[t - L])
    return lo, hi

R, DMS, CONF, RAIN = [], [], [], []
PRED = {}
for site, (fn, ft) in SITES.items():
    tr_ = pd.read_csv(f"{dd}/{ft}", parse_dates=["time"]).set_index("time").sort_index()
    nw = daily_nwp(f"{dd}/{fn}")
    D = nw.join(tr_[[c for _, c, _ in V.values()]], how="inner")
    clim = tr_[tr_.index < "2024-07-01"]
    doys = D.index.dayofyear
    for k, (b, c, u) in V.items():
        y_all = D[c]
        for L in LEADS:
            F = pd.DataFrame(index=D.index); F["nwp"] = D[f"{k}_n{L}"]
            for kk, (_, cc, _) in V.items():
                F[f"{kk}_obs"] = D[cc].shift(L); F[f"{kk}_obs7"] = D[cc].rolling(7).mean().shift(L); F[f"{kk}_nwp"] = D[f"{kk}_n{L}"]
            F["doy_s"] = np.sin(2 * np.pi * doys / 365.25); F["doy_c"] = np.cos(2 * np.pi * doys / 365.25)
            res = (F.nwp - y_all)
            F["bias30"] = res.rolling(30, min_periods=15).shift(L).mean() if False else res.rolling(30, min_periods=15).mean().shift(L)
            ok = F.notna().all(axis=1) & y_all.notna()
            clipf = (lambda a: np.clip(a, 0, None)) if k == "hujan" else (lambda a: a)
            raw = F.nwp; pers = D[c].shift(L)
            adapt = clipf(raw - F.bias30)
            comb = 0.5 * adapt + 0.5 * pers
            # Ridge tetap
            tr = ok & (D.index <= T_FIX_TR)
            rd = make_pipeline(StandardScaler(), Ridge(10.0)).fit(F[tr], y_all[tr])
            ridge_fix = pd.Series(clipf(rd.predict(F.fillna(0))), index=F.index)
            # walk-forward
            ridge_wf = pd.Series(np.nan, index=F.index); lgb_wf = pd.Series(np.nan, index=F.index)
            starts = pd.date_range(T_WF0, D.index.max(), freq=f"{STEP}D")
            for s0 in starts:
                blk = ok & (D.index >= s0) & (D.index < s0 + pd.Timedelta(days=STEP))
                if blk.sum() == 0: continue
                cut = s0 - pd.Timedelta(days=L)
                trw = ok & (D.index <= cut) & (D.index > cut - pd.Timedelta(days=WIN))
                if trw.sum() < 120: continue
                ridge_wf[blk] = clipf(make_pipeline(StandardScaler(), Ridge(10.0)).fit(F[trw], y_all[trw]).predict(F[blk]))
                lgb_wf[blk] = clipf(F.nwp[blk].values + lgbr().fit(F[trw], (y_all - F.nwp)[trw]).predict(F[blk]))
            te = ok & (D.index >= T_TE) & ridge_wf.notna() & adapt.notna() & pers.notna()
            yt = y_all[te].values
            M = {"NWP mentah": raw[te].values, "Persistensi": pers[te].values, "Bias bergulir 30 hari": adapt[te].values,
                 "Rata-rata (bias bergulir, persistensi)": comb[te].values, "Ridge tetap": ridge_fix[te].values,
                 "Ridge walk-forward": ridge_wf[te].values, "LightGBM residu walk-forward": lgb_wf[te].values}
            mae = {n: np.mean(np.abs(yt - p)) for n, p in M.items()}
            for n, p in M.items():
                R.append(dict(site=site, var=k, unit=u, L=L, model=n, mae=mae[n], rmse=np.sqrt(np.mean((yt - p) ** 2)), skill_raw=1 - mae[n] / mae["NWP mentah"], n=len(yt)))
            best_nn = min([m for m in M if m not in ("NWP mentah", "Persistensi")], key=lambda m: mae[m])
            for ref in ("NWP mentah", "Persistensi", "Bias bergulir 30 hari"):
                if best_nn == ref: continue
                dmean, pv = dm_test(yt - M[best_nn], yt - M[ref], L)
                DMS.append(dict(site=site, var=k, L=L, best=best_nn, ref=ref, mae_best=mae[best_nn], mae_ref=mae[ref], p=pv))
            PRED[(site, k, L)] = (D.index[te], yt, M)
            # konformal adaptif untuk Ridge walk-forward (semua hari tersedia sejak T_WF0, kalibrasi dari galat terverifikasi)
            if k != "hujan":
                allm = ok & ridge_wf.notna()
                idx = D.index[allm]; ya = y_all[allm].values; pa = ridge_wf[allm].values
                lo, hi = aci(ya, pa, L=L)
                m_te = (idx >= T_TE) & ~np.isnan(lo)
                # konformal statis: kuantil 90% galat absolut pada kalibrasi T_WF0..T_TE
                cal = (idx < T_TE) & (idx >= pd.Timestamp(T_WF0) + pd.Timedelta(days=L))
                qs = np.quantile(np.abs(ya[cal] - pa[cal]), 0.9 * (1 + 1 / cal.sum()))
                yt2, pt2 = ya[idx >= T_TE], pa[idx >= T_TE]
                CONF.append(dict(site=site, var=k, unit=u, L=L, picp_aci=np.mean((ya[m_te] >= lo[m_te]) & (ya[m_te] <= hi[m_te])), mpiw_aci=np.mean(hi[m_te] - lo[m_te]),
                                 picp_static=np.mean(np.abs(yt2 - pt2) <= qs), mpiw_static=2 * qs))
            else:
                obs = (yt >= 1).astype(int)
                cl = (clim.precipitation_sum >= 1).groupby(clim.index.dayofyear).mean()
                pc = np.array([cl.get(t.dayofyear, np.nan) for t in D.index[te]])
                Fc = F.copy(); Fc["nwp1mm"] = (F.nwp >= 1).astype(float)
                pp = pd.Series(np.nan, index=F.index)
                for s0 in starts:
                    blk = ok & (D.index >= s0) & (D.index < s0 + pd.Timedelta(days=STEP))
                    cut = s0 - pd.Timedelta(days=L); trw = ok & (D.index <= cut) & (D.index > cut - pd.Timedelta(days=WIN))
                    if blk.sum() == 0 or trw.sum() < 120: continue
                    pp[blk] = lgbc().fit(Fc[trw], (y_all[trw] >= 1).astype(int)).predict_proba(Fc[blk])[:, 1]
                pt = pp[te].values; okp = ~np.isnan(pt)
                RAIN.append(dict(site=site, L=L, frek=obs.mean(), auc_nwp=roc_auc_score(obs, raw[te].values), auc_clim=roc_auc_score(obs, pc),
                                 auc_lgb=roc_auc_score(obs[okp], pt[okp]), brier_clim=brier_score_loss(obs, pc), brier_lgb=brier_score_loss(obs[okp], pt[okp])))

R = pd.DataFrame(R); R.to_csv(f"{out}/studiA_pembanding_hasil.csv", index=False)
DM = pd.DataFrame(DMS); CF = pd.DataFrame(CONF); RN = pd.DataFrame(RAIN)
Lr = ["# Studi A, tahap 4: pembanding adil, konformal adaptif, uji DM", "",
      f"Arsip NWP: ECMWF IFS 0,25 derajat (Open-Meteo Previous Runs), kebenaran = reanalisis Open-Meteo (bukan stasiun). Uji dari {T_TE} (n hari per sel: {int(R.n.min())}). MAE dalam satuan asli; skill = 1 - MAE/MAE NWP mentah.",
      f"Ridge walk-forward: refit tiap {STEP} hari dengan jendela {WIN} hari terakhir yang sudah terverifikasi pada saat prakiraan dibuat. Persistensi dan bias bergulir memakai informasi yang sama (tertunda L hari).", ""]
for site in SITES:
    Lr += [f"## {site}: MAE per metode", "", "| Variabel | Lead | " + " | ".join(R.model.unique()) + " |", "| --- | --- | " + " | ".join(["---"] * R.model.nunique()) + " |"]
    for (k, L), g in R[R.site == site].groupby(["var", "L"], sort=False):
        best = g.mae.min(); row = " | ".join((f"**{r.mae:.2f}**" if abs(r.mae - best) < 1e-9 else f"{r.mae:.2f}") for r in g.itertuples())
        Lr.append(f"| {k} ({g.unit.iloc[0]}) | {L} | {row} |")
    Lr.append("")
Lr += ["## Uji Diebold-Mariano (galat absolut, koreksi Harvey-Leybourne-Newbold)", "",
       "Model terbaik per sel (di antara metode terkoreksi) dibandingkan dengan tiga pembanding. p < 0,05 berarti selisih MAE bermakna secara statistik (satu sel uji, tanpa koreksi perbandingan ganda).", "",
       "| Lokasi | Variabel | Lead | Model terbaik | Pembanding | MAE terbaik | MAE pembanding | p |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
Lr += [f"| {r.site} | {r.var} | {r.L} | {r.best} | {r.ref} | {r.mae_best:.2f} | {r.mae_ref:.2f} | {r.p:.3f} |" for r in DM.itertuples()]
Lr += ["", "## Interval 90%: konformal adaptif vs statis (Ridge walk-forward)", "",
       "Statis = satu kuantil dari galat Mar-Jun 2025. Adaptif = kuantil jendela 120 hari yang bergulir dengan pembaruan level (Gibbs dan Candes, gamma 0,02), memakai hanya galat yang sudah terverifikasi.", "",
       "| Lokasi | Variabel | Lead | PICP statis | MPIW statis | PICP adaptif | MPIW adaptif |", "| --- | --- | --- | --- | --- | --- | --- |"]
Lr += [f"| {r.site} | {r.var} ({r.unit}) | {r.L} | {r.picp_static:.0%} | {r.mpiw_static:.2f} | {r.picp_aci:.0%} | {r.mpiw_aci:.2f} |" for r in CF.itertuples()]
Lr += ["", "## Kejadian hujan (>= 1 mm), LightGBM walk-forward", "", "| Lokasi | Lead | Frekuensi hujan uji | AUC NWP | AUC klimatologi | AUC LightGBM | Brier klimatologi | Brier LightGBM |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
Lr += [f"| {r.site} | {r.L} | {r.frek:.2f} | {r.auc_nwp:.3f} | {r.auc_clim:.3f} | {r.auc_lgb:.3f} | {r.brier_clim:.3f} | {r.brier_lgb:.3f} |" for r in RN.itertuples()]
open(f"{out}/studiA_pembanding_adil.md", "w", encoding="utf8").write("\n".join(Lr) + "\n")
import pickle; pickle.dump({k: (v[0], v[1], v[2]) for k, v in PRED.items()}, open(f"{out}/_pred.pkl", "wb"))
print("\n".join(Lr))
