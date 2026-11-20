"""Validasi sensor cuacaPintar (Surabaya) terhadap arsip NWP ECMWF IFS 0.25 (Open-Meteo Previous Runs), per jam.
Pakai: python 20_validasi_sensor.py <xlsx sensor> <csv nwp sensor> <folder keluaran>"""
import sys, numpy as np, pandas as pd
x, nwp, out = sys.argv[1:4]
d = pd.read_excel(x); d["t"] = pd.to_datetime(d.time_wib); n_rows = len(d)
u = d.drop_duplicates("t").copy(); u["hr"] = u.t.dt.floor("h")
h = u.groupby("hr").agg(n=("t", "size"), T=("temperature", "mean"), RH=("humidity", "mean"), Wr=("wind_rt", "mean"), rain=("rain_1h", "max")).reset_index()
N = pd.read_csv(nwp, parse_dates=["time"])
m = h.merge(N, left_on="hr", right_on="time"); m["W"] = m.Wr * 3.6
L = [f"# Validasi sensor vs NWP ECMWF IFS (arsip)", "", f"Baris: {n_rows}; timestamp unik: {len(u)}; duplikat persis: {n_rows-len(u)}; jam unik berpasangan: {len(m)}.", "",
     "| Variabel | Lead | n | Bias (sensor - NWP) | MAE | r |", "| --- | --- | --- | --- | --- | --- |"]
def row(nm, a, b, lead):
    e = a - b; L.append(f"| {nm} | {lead} | {len(e)} | {e.mean():+.2f} | {e.abs().mean():.2f} | {np.corrcoef(a, b)[0,1]:.2f} |")
for k, suf in (("0 (terbaru)", ""), ("1 hari", "_previous_day1"), ("3 hari", "_previous_day3"), ("7 hari", "_previous_day7")):
    row("suhu (C)", m["T"], m["temperature_2m" + suf], k); row("RH (%)", m.RH, m["relative_humidity_2m" + suf], k)
row("angin (km/h, m/s x 3.6 vs NWP)", m.W, m.wind_speed_10m, "0 (terbaru)")
m["siang"] = m.hr.dt.hour.between(9, 17)
L += ["", "Bias suhu menurut waktu: " + "; ".join(f"{'siang 09-17' if k else 'malam'} n={len(g)} {(g['T']-g.temperature_2m).mean():+.2f} C" for k, g in m.groupby("siang"))]
L += ["", "Catatan kualitas: kolom pred_* kosong; kolom uv bernilai ~21 saat tengah malam (bukan indeks UV); satuan angin tidak terdokumentasi."]
m.round(2).to_csv(f"{out}/studiA_validasi_sensor_pasangan.csv", index=False)
open(f"{out}/studiA_validasi_sensor.md", "w", encoding="utf8").write("\n".join(L) + "\n"); print("\n".join(L))
