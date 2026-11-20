"""Studi A tahap 5: BiGRU-Attention kuantil (model usulan jaringan saraf) vs Ridge walk-forward dan bias bergulir.
Pakai: python 16_nn_pembanding.py <folder data> <folder keluaran>   (folder keluaran harus berisi _pred.pkl dari 15_pembanding_adil.py)
Target: residual (kebenaran - NWP) untuk suhu, kelembapan, angin pada lead 1, 3, 7. Keluaran kuantil 5%, 50%, 95%.
Walk-forward: refit tiap 30 hari, jendela latih 540 hari yang sudah terverifikasi, 3 seed dirata-ratakan."""
import sys, pickle, warnings, time
import numpy as np, pandas as pd
from scipy import stats
warnings.filterwarnings("ignore")
import os, torch, torch.nn as nn
torch.set_num_threads(2)
dd, out = sys.argv[1], sys.argv[2]
SITES = {"Kalisat": ("nwp_arsip_ecmwf_ifs025_kalisat.csv", "om_harian_kalisat_2005_sekarang.csv"),
         "Surabaya": ("nwp_arsip_ecmwf_ifs025_sensor.csv", "om_harian_sensor_2005_sekarang.csv")}
V = {"suhu": ("temperature_2m", "temperature_2m_mean", "C"), "rh": ("relative_humidity_2m", "relative_humidity_2m_mean", "%"),
     "angin": ("wind_speed_10m", "wind_speed_10m_mean", "km/h"), "hujan": ("precipitation", "precipitation_sum", "mm")}
TV = ["suhu", "rh", "angin"]; LEADS = (1, 3, 7); WIN_DAYS = 14; T_WF0, T_TE = "2025-03-01", "2025-07-01"; WIN, STEP = 540, 30
TAUS = torch.tensor([0.05, 0.5, 0.95]); SEEDS = (0, 1); EPOCHS = int(os.environ.get('NB_EPOCHS', 40))

def daily_nwp(f):
    h = pd.read_csv(f, parse_dates=["time"]); h["d"] = h.time.dt.floor("D"); o = {}
    for k, (b, _, _) in V.items():
        for L in LEADS:
            a = h.groupby("d")[f"{b}_previous_day{L}"]
            o[f"{k}_n{L}"] = a.sum(min_count=24) if k == "hujan" else a.mean().where(a.count() >= 24)
    return pd.DataFrame(o)

class Net(nn.Module):
    """N-BEATS-lite: tiga blok fully-connected dengan backcast/forecast residual pada vektor (jendela 14 hari diratakan + statis)."""
    def __init__(s, nin, nstat, hid=int(os.environ.get('NB_HID', 64)), blocks=3, T=14):
        super().__init__()
        s.dim = nin * T + nstat
        s.blocks = nn.ModuleList([nn.Sequential(nn.Linear(s.dim, hid), nn.ReLU(), nn.Linear(hid, hid), nn.ReLU()) for _ in range(blocks)])
        s.back = nn.ModuleList([nn.Linear(hid, s.dim) for _ in range(blocks)])
        s.fore = nn.ModuleList([nn.Linear(hid, 9) for _ in range(blocks)])
    def forward(s, x, z):
        r = torch.cat([x.flatten(1), z], 1); o = 0
        for blk, bk, fc in zip(s.blocks, s.back, s.fore):
            h = blk(r); r = r - bk(h); o = o + fc(h)
        o = o.view(-1, 3, 3)
        med = o[:, :, 1]; lo = med - nn.functional.softplus(o[:, :, 0]); hi = med + nn.functional.softplus(o[:, :, 2])
        return torch.stack([lo, med, hi], dim=2)

def pinball(pred, y):
    e = y.unsqueeze(-1) - pred
    return torch.maximum(TAUS * e, (TAUS - 1) * e).mean()

def fit_predict(Xs, Z, Y, Xs_te, Z_te, seed):
    torch.manual_seed(seed); np.random.seed(seed)
    m = Net(Xs.shape[2], Z.shape[1]); opt = torch.optim.Adam(m.parameters(), lr=3e-3, weight_decay=float(os.environ.get('NB_WD', 1e-3)))
    Xt, Zt, Yt = map(lambda a: torch.tensor(a, dtype=torch.float32), (Xs, Z, Y))
    n = len(Xt)
    for ep in range(EPOCHS):
        m.train(); perm = torch.randperm(n)
        for i in range(0, n, 64):
            b = perm[i:i + 64]; opt.zero_grad(); loss = pinball(m(Xt[b], Zt[b]), Yt[b]); loss.backward(); opt.step()
    m.eval()
    with torch.no_grad(): return m(torch.tensor(Xs_te, dtype=torch.float32), torch.tensor(Z_te, dtype=torch.float32)).numpy()

def dm_test(e1, e2, h):
    d = np.abs(e1) - np.abs(e2); n = len(d); dm = d - d.mean(); s = (dm ** 2).mean()
    for k in range(1, max(h, 1)): s += 2 * (1 - k / max(h, 1)) * (dm[k:] * dm[:-k]).mean()
    stat = d.mean() / np.sqrt(max(s, 1e-12) / n) * np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    return 2 * (1 - stats.t.cdf(abs(stat), df=n - 1))

def aci(y, p, alpha=0.1, gamma=0.02, win=120, L=1):
    n = len(y); a_t = alpha; lo = np.full(n, np.nan); hi = np.full(n, np.nan); err = np.full(n, np.nan); ae = np.abs(y - p)
    for t in range(n):
        known = ae[max(0, t - L - win + 1): t - L + 1] if t - L >= 0 else np.array([])
        if len(known) < 30: continue
        q = np.quantile(known, float(np.clip(1 - a_t, 0.5, 0.999))); lo[t], hi[t] = p[t] - q, p[t] + q; err[t] = float(not (lo[t] <= y[t] <= hi[t]))
        if t - L >= 0 and not np.isnan(err[t - L]): a_t = a_t + gamma * (alpha - err[t - L])
    return lo, hi

PRED = pickle.load(open(f"{out}/_pred.pkl", "rb"))
ROWS, DMS = [], []; DUMP = {}
t0 = time.time()
for site, (fn, ft) in SITES.items():
    tr_ = pd.read_csv(f"{dd}/{ft}", parse_dates=["time"]).set_index("time").sort_index()
    nw = daily_nwp(f"{dd}/{fn}"); D = nw.join(tr_[[c for _, c, _ in V.values()]], how="inner")
    for L in LEADS:
        T = pd.DataFrame({k: D[V[k][1]] for k in V}); N = pd.DataFrame({k: D[f"{k}_n{L}"] for k in V}); R = (T - N)[TV]
        feat = pd.concat([T[TV], np.log1p(T[["hujan"]].clip(lower=0)), R.add_suffix("_res")], axis=1)   # fitur deret harian
        idx = D.index; N_ = len(idx)
        Xs_all = np.full((N_, WIN_DAYS, feat.shape[1]), np.nan); Z_all = np.full((N_, 6), np.nan); Y_all = np.full((N_, 3), np.nan)
        fv = feat.values
        for i in range(N_):
            e = i - L   # hari terbit
            if e - WIN_DAYS + 1 < 0: continue
            Xs_all[i] = fv[e - WIN_DAYS + 1: e + 1]
            Z_all[i] = [N.suhu.iloc[i], N.rh.iloc[i], N.angin.iloc[i], np.log1p(max(N.hujan.iloc[i], 0)) if not np.isnan(N.hujan.iloc[i]) else np.nan,
                        np.sin(2 * np.pi * idx[i].dayofyear / 365.25), np.cos(2 * np.pi * idx[i].dayofyear / 365.25)]
            Y_all[i] = R.iloc[i].values
        ok = ~(np.isnan(Xs_all).any((1, 2)) | np.isnan(Z_all).any(1) | np.isnan(Y_all).any(1))
        base = np.stack([N[k].values for k in TV], 1)
        med = np.full((N_, 3), np.nan); qlo = med.copy(); qhi = med.copy()
        for s0 in pd.date_range(T_WF0, idx.max(), freq=f"{STEP}D"):
            blk = ok & (idx >= s0) & (idx < s0 + pd.Timedelta(days=STEP))
            cut = s0 - pd.Timedelta(days=L); trw = ok & (idx <= cut) & (idx > cut - pd.Timedelta(days=WIN))
            if blk.sum() == 0 or trw.sum() < 120: continue
            mu_x, sd_x = Xs_all[trw].mean((0, 1)), Xs_all[trw].std((0, 1)) + 1e-6
            mu_z, sd_z = Z_all[trw].mean(0), Z_all[trw].std(0) + 1e-6; sd_y = Y_all[trw].std(0) + 1e-6
            f = lambda a, m, s: (a - m) / s
            P = np.mean([fit_predict(f(Xs_all[trw], mu_x, sd_x), f(Z_all[trw], mu_z, sd_z), Y_all[trw] / sd_y, f(Xs_all[blk], mu_x, sd_x), f(Z_all[blk], mu_z, sd_z), s) for s in SEEDS], 0)
            P = P * sd_y[None, :, None]
            qlo[blk], med[blk], qhi[blk] = P[:, :, 0], P[:, :, 1], P[:, :, 2]
        print(site, "lead", L, f"selesai ({time.time()-t0:.0f} s)", flush=True)
        for j, k in enumerate(TV):
            key = (site, k, L)
            if key not in PRED: continue
            dates, yt, M = PRED[key]
            pos = idx.get_indexer(dates); ok2 = ~np.isnan(med[pos, j]); pos, yt = pos[ok2], yt[ok2]
            clip = (lambda a: np.clip(a, 0, 100)) if k == "rh" else ((lambda a: np.clip(a, 0, None)) if k == "angin" else (lambda a: a))
            pn = clip(base[pos, j] + med[pos, j]); lo_ = clip(base[pos, j] + qlo[pos, j]); hi_ = clip(base[pos, j] + qhi[pos, j])
            sel = np.flatnonzero(ok2)
            DUMP[key] = (np.asarray(dates)[ok2], pn)   # daily median forecasts, used by 40_sensitivitas_dm.py
            cmp = {"NWP mentah": M["NWP mentah"][sel], "Bias bergulir 30 hari": M["Bias bergulir 30 hari"][sel], "Ridge walk-forward": M["Ridge walk-forward"][sel], "N-BEATS-lite kuantil (median)": pn}
            mae = {n: np.mean(np.abs(yt - p)) for n, p in cmp.items()}
            # ACI pada median NN dengan seluruh deret walk-forward (kalibrasi dari galat terverifikasi)
            ya = T[k].values; allm = ~np.isnan(med[:, j]) & ~np.isnan(ya); ii = np.flatnonzero(allm)
            pa = clip(base[ii, j] + med[ii, j]); lo_a, hi_a = aci(ya[ii], pa, L=L)
            mt = (idx[ii] >= T_TE) & ~np.isnan(lo_a)
            picp_aci = np.mean((ya[ii][mt] >= lo_a[mt]) & (ya[ii][mt] <= hi_a[mt])); mpiw_aci = np.mean(hi_a[mt] - lo_a[mt])
            ROWS.append(dict(site=site, var=k, unit=V[k][2], L=L, n=len(yt), **{f"mae {n}": v for n, v in mae.items()},
                             picp_q=np.mean((yt >= lo_) & (yt <= hi_)), mpiw_q=np.mean(hi_ - lo_), picp_aci=picp_aci, mpiw_aci=mpiw_aci,
                             p_dm_vs_ridge=dm_test(yt - pn, yt - cmp["Ridge walk-forward"], L), p_dm_vs_bias=dm_test(yt - pn, yt - cmp["Bias bergulir 30 hari"], L)))
R_ = pd.DataFrame(ROWS); R_.to_csv(f"{out}/studiA_nbeats{os.environ.get('NB_TAG', '')}_hasil.csv", index=False)
pickle.dump(DUMP, open(f"{out}/_pred_nbeats{os.environ.get('NB_TAG', '')}.pkl", "wb"))
Lr = ["# Studi A, tahap 6: N-BEATS-lite kuantil vs pembanding sederhana", "",
      "Residual NWP (ECMWF, arsip Open-Meteo) terhadap reanalisis; N-BEATS-lite (3 blok FC 64 unit, backcast/forecast), jendela 14 hari, keluaran kuantil 5/50/95%, rata-rata 2 seed, refit tiap 30 hari dengan jendela 540 hari. Uji sama dengan tahap 4 (mulai 2025-07-01, hari yang sama untuk semua metode di tiap sel).", "",
      "| Lokasi | Variabel | Lead | n | NWP mentah | Bias bergulir | Ridge walk-forward | N-BEATS-lite median | p DM vs Ridge | p DM vs bias bergulir |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for r in R_.itertuples(index=False):
    d = r._asdict() if hasattr(r, "_asdict") else {}
    vals = {c: getattr(r, c) for c in R_.columns.map(lambda s: s.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")) if hasattr(r, c)}
for _, r in R_.iterrows():
    b = min(r["mae NWP mentah"], r["mae Bias bergulir 30 hari"], r["mae Ridge walk-forward"], r["mae N-BEATS-lite kuantil (median)"])
    fm = lambda v: f"**{v:.2f}**" if abs(v - b) < 1e-9 else f"{v:.2f}"
    Lr.append(f"| {r.site} | {r['var']} ({r.unit}) | {r.L} | {r.n} | {fm(r['mae NWP mentah'])} | {fm(r['mae Bias bergulir 30 hari'])} | {fm(r['mae Ridge walk-forward'])} | {fm(r['mae N-BEATS-lite kuantil (median)'])} | {r.p_dm_vs_ridge:.3f} | {r.p_dm_vs_bias:.3f} |")
Lr += ["", "## Interval 90% dari N-BEATS-lite", "", "Kuantil langsung = kuantil 5% dan 95% keluaran jaringan. Adaptif = konformal adaptif (sama seperti tahap 4) pada median jaringan.", "",
       "| Lokasi | Variabel | Lead | PICP kuantil langsung | MPIW kuantil langsung | PICP adaptif | MPIW adaptif |", "| --- | --- | --- | --- | --- | --- | --- |"]
Lr += [f"| {r.site} | {r['var']} ({r.unit}) | {r.L} | {r.picp_q:.0%} | {r.mpiw_q:.2f} | {r.picp_aci:.0%} | {r.mpiw_aci:.2f} |" for _, r in R_.iterrows()]
nb = int((R_["mae N-BEATS-lite kuantil (median)"] < R_["mae Ridge walk-forward"]).sum())
Lr += ["", f"N-BEATS-lite lebih baik dari Ridge walk-forward di {nb} dari {len(R_)} sel (MAE); yang bermakna (p DM < 0,05 dan MAE lebih kecil): {int(((R_.p_dm_vs_ridge < 0.05) & (R_['mae N-BEATS-lite kuantil (median)'] < R_['mae Ridge walk-forward'])).sum())}."]
open(f"{out}/studiA_nbeats{os.environ.get('NB_TAG', '')}_pembanding.md", "w", encoding="utf8").write("\n".join(Lr) + "\n"); print("\n".join(Lr))
