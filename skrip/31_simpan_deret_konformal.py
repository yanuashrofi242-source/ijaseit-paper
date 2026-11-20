"""Menyimpan deret Ridge walk-forward penuh (dari 2025-03-01, termasuk periode kalibrasi) untuk gambar konformal agar memakai prosedur yang sama dengan tabel.
Pakai: python 31_simpan_deret_konformal.py <data_bersih> <hasil>"""
import sys, pickle, warnings, numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
dd, out = sys.argv[1], sys.argv[2]
SITES = {"Kalisat": ("nwp_arsip_ecmwf_ifs025_kalisat.csv", "om_harian_kalisat_2005_sekarang.csv"), "Surabaya": ("nwp_arsip_ecmwf_ifs025_sensor.csv", "om_harian_sensor_2005_sekarang.csv")}
V = {"suhu": ("temperature_2m", "temperature_2m_mean", "C"), "rh": ("relative_humidity_2m", "relative_humidity_2m_mean", "%"),
     "angin": ("wind_speed_10m", "wind_speed_10m_mean", "km/h"), "hujan": ("precipitation", "precipitation_sum", "mm")}
LEADS = (1, 3, 7); T_FIX_TR, T_WF0, T_TE = "2025-02-28", "2025-03-01", "2025-07-01"; WIN, STEP = 540, 30
def daily_nwp(f):
    h = pd.read_csv(f, parse_dates=["time"]); h["d"] = h.time.dt.floor("D"); o = {}
    for k, (b, _, _) in V.items():
        for L in LEADS:
            a = h.groupby("d")[f"{b}_previous_day{L}"]
            o[f"{k}_n{L}"] = a.sum(min_count=24) if k == "hujan" else a.mean().where(a.count() >= 24)
    return pd.DataFrame(o)
OUT = {}
for site, (fn, ft) in SITES.items():
    tr_ = pd.read_csv(f"{dd}/{ft}", parse_dates=["time"]).set_index("time").sort_index(); nw = daily_nwp(f"{dd}/{fn}")
    D = nw.join(tr_[[c for _, c, _ in V.values()]], how="inner"); doys = D.index.dayofyear
    for k, (b, c, u) in V.items():
        if k == "hujan": continue
        y_all = D[c]
        for L in LEADS:
            F = pd.DataFrame(index=D.index); F["nwp"] = D[f"{k}_n{L}"]
            for kk, (_, cc, _) in V.items():
                F[f"{kk}_obs"] = D[cc].shift(L); F[f"{kk}_obs7"] = D[cc].rolling(7).mean().shift(L); F[f"{kk}_nwp"] = D[f"{kk}_n{L}"]
            F["doy_s"] = np.sin(2 * np.pi * doys / 365.25); F["doy_c"] = np.cos(2 * np.pi * doys / 365.25)
            F["bias30"] = (F.nwp - y_all).rolling(30, min_periods=15).mean().shift(L)
            ok = F.notna().all(axis=1) & y_all.notna(); clipf = lambda a: a
            ridge_wf = pd.Series(np.nan, index=F.index)
            for s0 in pd.date_range(T_WF0, D.index.max(), freq=f"{STEP}D"):
                blk = ok & (D.index >= s0) & (D.index < s0 + pd.Timedelta(days=STEP)); cut = s0 - pd.Timedelta(days=L)
                trw = ok & (D.index <= cut) & (D.index > cut - pd.Timedelta(days=WIN))
                if blk.sum() == 0 or trw.sum() < 120: continue
                ridge_wf[blk] = make_pipeline(StandardScaler(), Ridge(10.0)).fit(F[trw], y_all[trw]).predict(F[blk])
            allm = ok & ridge_wf.notna()
            OUT[(site, k, L)] = (D.index[allm], y_all[allm].values, ridge_wf[allm].values)
            if (site, k, L) == ("Kalisat", "suhu", 1):
                print("kolom Ridge:", list(F.columns), len(F.columns), "kolom kembar nwp==suhu_nwp:", bool((F.nwp.fillna(0) == F.suhu_nwp.fillna(0)).all()))
pickle.dump(OUT, open(f"{out}/_konformal_deret.pkl", "wb")); print("selesai", len(OUT))
