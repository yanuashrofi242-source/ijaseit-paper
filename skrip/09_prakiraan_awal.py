"""Baseline prakiraan harian dari Open-Meteo per jam (hujan dikecualikan karena kolomnya tidak valid).
Pakai: python 09_prakiraan_awal.py <folder kerja>. Latih 2022-2023, uji 2024 (kronologis)."""
import sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import lightgbm as lgb
root = sys.argv[1]
h = pd.read_csv(f"{root}/data_bersih/openmeteo_jam_bersih.csv", parse_dates=["time", "time_wib_dugaan"])
h["tgl"] = h.time_wib_dugaan.dt.floor("D")
d = h.groupby("tgl").agg(suhu=("temperature_2m (°C)", "mean"), rh=("relative_humidity_2m (%)", "mean"), angin=("wind_speed_10m (km/h)", "mean"),
                         uv=("uv_index ()", "max"), suhu80=("temperature_80m (°C)", "mean")).iloc[1:-1]
d["doy_sin"] = np.sin(2 * np.pi * d.index.dayofyear / 365.25); d["doy_cos"] = np.cos(2 * np.pi * d.index.dayofyear / 365.25)
V = ["suhu", "rh", "angin"]; LAGS = range(0, 7)
X = pd.DataFrame(index=d.index)
for v in V + ["uv", "suhu80"]:
    for k in LAGS: X[f"{v}_l{k}"] = d[v].shift(k)
    X[f"{v}_m7"] = d[v].rolling(7).mean()
X["doy_sin"], X["doy_cos"] = d.doy_sin, d.doy_cos
L = ["# Baseline prakiraan harian (Studi A, tahap awal)", "",
     "Sumber: openmeteo_jam_bersih.csv (lokasi tidak tercatat; diduga dataran rendah seperti Surabaya karena suhu rata-rata 28,4 C), waktu digeser +7 jam (dugaan UTC ke WIB). Hujan dikecualikan.",
     "Latih 2022-2023, uji 2024. Ini menguji prakiraan terhadap Open-Meteo sendiri, bukan terhadap sensor; fungsinya sebagai pra-latih dan pembanding.", ""]
rows = []
for H in (1, 7):
    for v in V:
        y = d[v].shift(-H); ok = X.notna().all(axis=1) & y.notna()
        tr = ok & (d.index < "2024-01-01"); te = ok & (d.index >= "2024-01-01")
        yt = y[te]
        pers = d.loc[te, v] if True else None
        # seasonal naive: nilai tanggal sasaran tahun lalu
        tgt_dates = d.index[te] + pd.Timedelta(days=H); prev = d[v].reindex(tgt_dates - pd.Timedelta(days=364)).values
        clim = d[v][d.index < "2024-01-01"].groupby(d[d.index < "2024-01-01"].index.dayofyear).mean()
        clim_pred = np.array([clim.get(t.dayofyear, np.nan) for t in tgt_dates])
        res = {"Persistensi": pers.values, "Klimatologi (rata-rata hari-dalam-tahun 2022-2023)": clim_pred,
               "Ridge (lag 0-6 + musim)": make_pipeline(StandardScaler(), Ridge(1.0)).fit(X[tr], y[tr]).predict(X[te]),
               "LightGBM (lag 0-6 + musim)": lgb.LGBMRegressor(n_estimators=300, learning_rate=0.03, num_leaves=15, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, verbose=-1, random_state=0).fit(X[tr], y[tr]).predict(X[te])}
        mae_p = np.nanmean(np.abs(yt.values - res["Persistensi"]))
        for nm, p in res.items():
            m = np.isfinite(p)
            mae = np.mean(np.abs(yt.values[m] - p[m])); rmse = np.sqrt(np.mean((yt.values[m] - p[m]) ** 2))
            rows.append((H, v, nm, mae, rmse, 1 - mae / mae_p))
L += ["| Horizon | Variabel | Model | MAE | RMSE | Skill vs persistensi (MAE) |", "| --- | --- | --- | --- | --- | --- |"]
unit = {"suhu": "C", "rh": "%", "angin": "km/j"}
for H, v, nm, mae, rmse, sk in rows:
    L.append(f"| {H} hari | {v} ({unit[v]}) | {nm} | {mae:.2f} | {rmse:.2f} | {sk:+.0%} |")
L += ["", "Skill positif berarti lebih baik daripada persistensi. Prakiraan 7 hari terhadap reanalisis memperlihatkan bahwa model lag sederhana sudah kuat; pembeda sebenarnya baru muncul saat target adalah sensor lokal."]
open(f"{root}/hasil/prakiraan_awal.md", "w", encoding="utf8").write("\n".join(L) + "\n"); print("\n".join(L))
