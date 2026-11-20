"""Profil dan validasi log sensor JSONL (stasiun Surabaya) terhadap arsip NWP ECMWF IFS 0.25 (Open-Meteo Previous Runs).
Pakai: python 21_log_sensor_besar.py <log.jsonl> <csv nwp sensor> <folder keluaran>"""
import sys, json, numpy as np, pandas as pd
src, nwp, out = sys.argv[1:4]
R = []; bad = 0
for l in open(src, encoding="utf8"):
    try: j = json.loads(l)
    except Exception: bad += 1; continue
    e, w, r, g = j.get("env", {}), j.get("wind", {}), j.get("rain", {}), j.get("gps", {})
    R.append(dict(time=j["time"], T=e.get("temp"), RH=e.get("humid"), P=e.get("press"), uv=e.get("uv"), W=w.get("speed"), R1h=r.get("mm1h"), lat=g.get("lat"), lon=g.get("lon"), alt=g.get("alt"),
                  pred=("pred_temp" in j) or ("pred" in j), pred_echo=(j.get("pred_temp") == e.get("temp")) if "pred_temp" in j else None))
d = pd.DataFrame(R); d["t"] = pd.to_datetime(d.time); d["site"] = np.where(d.lat > -7.31, "A", "B")
fail = (d["T"] == 0) | (d.RH == 0) | (d.P == 0)
ok = d[~fail].drop_duplicates("t").copy(); ok["hr"] = ok.t.dt.floor("h")
h = ok.groupby(["site", "hr"]).agg(n=("t", "size"), T=("T", "mean"), RH=("RH", "mean"), W=("W", "mean")).reset_index()
N = pd.read_csv(nwp, parse_dates=["time"]); m = h.merge(N, left_on="hr", right_on="time"); m = m[m.n >= 20].copy()
def st(a, b): e = a - b; return f"n={len(e)}, bias {e.mean():+.2f}, MAE {e.abs().mean():.2f}, r {np.corrcoef(a, b)[0,1]:.2f}"
L = ["# Log sensor besar: profil dan validasi", "",
     f"Baris terbaca: {len(d)} (baris rusak: {bad}); timestamp unik: {d.t.nunique()}; baris gagal (suhu/RH/tekanan = 0): {int(fail.sum())}; detik valid unik: {len(ok)}.",
     f"Hari rekaman: {d.t.dt.date.nunique()}; jam-kalender valid: {len(h)}; jam dengan >=20 bacaan berpasangan dengan NWP: {len(m)}.",
     f"Baris dengan kolom prediksi: {int(d.pred.sum())}; di antaranya prediksi == bacaan: {int((d.pred_echo == True).sum())}.", "",
     "| Lokasi | Variabel | Statistik (sensor - NWP) |", "| --- | --- | --- |"]
for s, gp in [("semua", m)] + list(m.groupby("site")):
    L.append(f"| {s} | suhu (C) | {st(gp['T'], gp.temperature_2m)} |"); L.append(f"| {s} | RH (%) | {st(gp.RH, gp.relative_humidity_2m)} |")
L.append(f"| semua | angin (m/s x 3.6 vs km/h) | {st(m.W * 3.6, m.wind_speed_10m)} |")
m["siang"] = m.hr.dt.hour.between(9, 17)
L += ["", "Bias suhu menurut waktu: " + "; ".join(f"{'siang 09-17' if k else 'malam'} n={len(g)} {(g['T']-g.temperature_2m).mean():+.2f} C" for k, g in m.groupby("siang"))]
m.round(2).to_csv(f"{out}/studiA_log_sensor_besar_pasangan.csv", index=False)
open(f"{out}/studiA_log_sensor_besar.md", "w", encoding="utf8").write("\n".join(L) + "\n"); print("\n".join(L))
