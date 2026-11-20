"""Langkah 3: tabel fitur Kalisat (desa x bulan) + baseline awal bebas kebocoran.
Pakai:  python 03_bangun_fitur.py <folder kerja>
Memakai data_bersih/weather_desa_bulanan.csv bila ada (hasil 02_unduh_open_meteo.py), jika tidak memakai kolom cuaca bawaan
yang kualitasnya diragukan (lihat hasil/audit_log.md)."""
import sys, os
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score

root = sys.argv[1]
o = pd.read_csv(f"{root}/data_bersih/kalisat_bersih.csv", parse_dates=["Date"]).sort_values(["Desa", "Date"]).reset_index(drop=True)
src = "bawaan (diragukan)"
wp = f"{root}/data_bersih/weather_desa_bulanan.csv"
if os.path.exists(wp):
    om = pd.read_csv(wp, parse_dates=["Date"])
    o = o.merge(om, on=["Desa", "Date"], how="left")
    W = ["om_temp", "om_humidity", "om_precip_total", "om_hari_hujan", "om_windspeed", "om_vpd", "om_lwd_jam_per_hari"]
    src = "Open-Meteo unduhan ulang"
else:
    W = ["temp", "humidity", "precip", "windspeed", "vpd", "lwd"]
print("Sumber cuaca:", src)

# --- Pranata Mangsa dari tanggal (versi umum Surakarta; cocokkan dengan rujukan Anda) ---
MANGSA = [("Kasa", 6, 22), ("Karo", 8, 2), ("Katelu", 8, 25), ("Kapat", 9, 18), ("Kalima", 10, 13), ("Kanem", 11, 9),
          ("Kapitu", 12, 22), ("Kawolu", 2, 3), ("Kasanga", 3, 1), ("Kasadasa", 3, 26), ("Dhesta", 4, 19), ("Sadha", 5, 12)]
def mangsa_idx(ts):
    md = (ts.month, ts.day)
    best = None
    for i, (_, m, d) in enumerate(MANGSA):
        if md >= (m, d) and (best is None or (m, d) >= (MANGSA[best][1], MANGSA[best][2])):
            best = i
    # tanggal sebelum 3 Feb dan setelah 22 Des = Kapitu; Jan -> Kapitu
    if ts.month == 1 or (ts.month == 2 and ts.day < 3): return 6
    return best
mid = o.Date + pd.Timedelta(days=14)          # tanggal tengah bulan
o["mangsa_idx"] = mid.map(mangsa_idx)
o["mangsa"] = o.mangsa_idx.map(lambda i: MANGSA[i][0])
o["bulan_sin"] = np.sin(2 * np.pi * o.Date.dt.month / 12); o["bulan_cos"] = np.cos(2 * np.pi * o.Date.dt.month / 12)

g = o.groupby("Desa")
for c in W:
    for k in (1, 2, 3):
        o[f"{c}_l{k}"] = g[c].shift(k)
o["cuaca_asli"] = o.cuaca_berubah if "cuaca_berubah" in o else 1
for k in (1, 2):
    o[f"LKSJ_l{k}"] = g.LKSJ.shift(k)
for sp in ("Hdb", "Pbp", "Wbc", "Blas"):
    o[f"LKSJ_{sp}_l1"] = g[f"LKSJ_{sp}"].shift(1)
o["LKSJ_riwayat3"] = g.LKSJ.transform(lambda s: s.rolling(3, min_periods=1).sum())
for k in (1, 2):
    o[f"SSJ_l{k}"] = g.SSJ.shift(k)

# --- target bulan berikutnya ---
o["y_next"] = (g.LKSJ.shift(-1) > 0).astype(float).where(g.LKSJ.shift(-1).notna())
o["LKSJ_next"] = g.LKSJ.shift(-1)
o["y_next_SSJ"] = (g.SSJ.shift(-1) > 0).astype(float).where(g.SSJ.shift(-1).notna())   # kejadian serangan BARU bulan depan
for sp in ("Hdb", "Pbp", "Wbc", "Blas"):
    o[f"y_next_{sp}"] = (g[f"LKSJ_{sp}"].shift(-1) > 0).astype(float).where(g[f"LKSJ_{sp}"].shift(-1).notna())
o["target_date"] = o.Date + pd.offsets.MonthBegin(1)
d = o.dropna(subset=["y_next"] + [f"{W[0]}_l3"]).copy()
d["split"] = np.where(d.target_date >= "2025-01-01", "uji", "latih")
d.to_csv(f"{root}/data_bersih/fitur_kalisat.csv", index=False)
print("Tabel fitur:", d.shape, d.split.value_counts().to_dict(), "positif latih/uji:",
      d[d.split == 'latih'].y_next.mean().round(3), d[d.split == 'uji'].y_next.mean().round(3))

# --- baseline awal: split kronologis, anomali cuaca dihitung dari data latih saja ---
tr, te = d[d.split == "latih"].copy(), d[d.split == "uji"].copy()
base = tr.groupby("Desa")[W].mean()
for part in (tr, te):
    for c in W:
        part[c + "_anom"] = part[c] - part.Desa.map(base[c])
        for k in (1, 2, 3):
            part[f"{c}_l{k}_anom"] = part[f"{c}_l{k}"] - part.Desa.map(base[c])
anom = [c for c in tr.columns if c.endswith("_anom")]
raw_w = W + [f"{c}_l{k}" for c in W for k in (1, 2, 3)]
season = ["bulan_sin", "bulan_cos", "mangsa_idx"]
hist = ["LKSJ", "LKSJ_l1", "LKSJ_l2", "LKSJ_riwayat3", "LT"]
sets = {"musim saja": season,
        "riwayat serangan saja": hist,
        "cuaca mentah + musim": raw_w + season,
        "cuaca anomali + musim": anom + season,
        "riwayat + musim": hist + season,
        "riwayat + cuaca anomali + musim": hist + anom + season}
rng = np.random.default_rng(0)
def boot_auc(y, p, n=1000):
    y = np.asarray(y); p = np.asarray(p); idx = np.arange(len(y)); vals = []
    for _ in range(n):
        s = rng.choice(idx, len(idx))
        if y[s].min() != y[s].max(): vals.append(roc_auc_score(y[s], p[s]))
    return np.percentile(vals, [2.5, 97.5])
lines = ["# Baseline awal risiko OPT (bulan berikutnya)", "",
         f"Sumber cuaca: {src}. Latih: target sebelum 2025 (n={len(tr)}), uji: 2025 ke atas (n={len(te)}, positif {int(te.y_next.sum())}).",
         "Random Forest 500 pohon, 5 seed dirata-rata, tanpa penyetelan. Anomali cuaca = nilai dikurangi rata-rata desa dari data latih.", "",
         "| Set fitur | AUC | CI 95% | PR-AUC |", "| --- | --- | --- | --- |"]
for name, f in sets.items():
    ps = []
    for seed in range(5):
        m = RandomForestClassifier(500, min_samples_leaf=3, class_weight="balanced", random_state=seed, n_jobs=-1)
        m.fit(tr[f].fillna(tr[f].median()), tr.y_next); ps.append(m.predict_proba(te[f].fillna(tr[f].median()))[:, 1])
    p = np.mean(ps, axis=0); lo, hi = boot_auc(te.y_next, p)
    lines.append(f"| {name} | {roc_auc_score(te.y_next, p):.3f} | {lo:.2f}-{hi:.2f} | {average_precision_score(te.y_next, p):.3f} |")
lines += ["", "Catatan: uji kecil; selisih antar baris sering lebih kecil dari lebar interval kepercayaan."]
open(f"{root}/hasil/baseline_awal.md", "w", encoding="utf8").write("\n".join(lines) + "\n")
print("\n".join(lines))
