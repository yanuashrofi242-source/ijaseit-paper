"""Studi A tahap 1: sensor cuacaPintar (Surabaya) vs Open-Meteo per jam, 21-27 Okt 2026.
Pakai: python 11_sensor_vs_om.py <folder kerja>   Keluaran: hasil/sensor_vs_om.md
Catatan: hanya ~6 hari sensor, jadi ini studi pendahuluan (bias dan kesesuaian), bukan bukti generalisasi."""
import sys
import numpy as np, pandas as pd
root = sys.argv[1]
s = pd.read_csv(f"{root}/data_bersih/sensor_bersih.csv", parse_dates=["time_wib"])
o = pd.read_csv(f"{root}/data_bersih/om_jam_sensor_21_27okt2026.csv", parse_dates=["time"])
n0 = len(s); s = s[s.sensor_valid == True].drop_duplicates(subset=["time_wib", "temperature", "humidity", "wind_avg", "rain_total"])
s["jam"] = s.time_wib.dt.floor("h")
g = s.groupby("jam").agg(t=("temperature", "mean"), rh=("humidity", "mean"), p=("pressure", "mean"), w=("wind_avg", "mean"), wmax=("wind_max", "mean"),
                         rain_tot=("rain_total", "max"), n=("temperature", "size"))
g["hujan_jam"] = g.rain_tot.diff().clip(lower=0)
m = g.join(o.set_index("time"), how="inner")
L = ["# Sensor cuacaPintar vs Open-Meteo (per jam, 21-27 Okt 2026)", "",
     f"Baris sensor mentah {n0}, valid dan unik {len(s)}; jam yang bisa dipasangkan: {len(m)} dari 168. Titik Open-Meteo = titik GPS sensor ({s.gps_lat.median():.4f}, {s.gps_lon.median():.4f}). Zona waktu keduanya WIB.", ""]
def row(nm, a, b, unit):
    k = a.notna() & b.notna(); a, b = a[k], b[k]; e = a - b
    return f"| {nm} | {unit} | {len(a)} | {e.mean():+.2f} | {e.abs().mean():.2f} | {np.sqrt((e**2).mean()):.2f} | {np.corrcoef(a, b)[0,1]:.2f} |"
L += ["Galat = sensor dikurangi Open-Meteo. Bias positif berarti sensor lebih tinggi.", "",
      "| Variabel | Satuan | n jam | Bias | MAE | RMSE | Korelasi |", "| --- | --- | --- | --- | --- | --- | --- |"]
L.append(row("Suhu", m.t, m["temperature_2m"], "C"))
L.append(row("Kelembapan", m.rh, m["relative_humidity_2m"], "%"))
L.append(row("Angin (sensor wind_avg diasumsikan m/s, dikali 3,6 ke km/h)", m.w * 3.6, m["wind_speed_10m"], "km/h"))
L.append(row("Angin (sensor wind_avg apa adanya, bila sudah km/h)", m.w, m["wind_speed_10m"], "km/h"))
L.append(row("Tekanan (sensor vs tekanan permukaan Open-Meteo)", m.p, m["surface_pressure"], "hPa"))
L += ["", "Pola harian suhu (rata-rata per jam, sensor vs Open-Meteo):", "", "| Jam | Sensor | Open-Meteo |", "| --- | --- | --- |"]
hh = m.groupby(m.index.hour).agg(a=("t", "mean"), b=("temperature_2m", "mean")).round(1)
L += [f"| {i:02d} | {r.a} | {r.b} |" for i, r in hh.iloc[::3].iterrows()]
tot_s = g.rain_tot.max() - g.rain_tot.min(); tot_o = m.precipitation.sum()
L += ["", f"Hujan 21-27 Okt: kenaikan rain_total sensor {tot_s:.1f}; jumlah Open-Meteo {tot_o:.1f} mm. Satuan rain_total sensor belum dipastikan (mm atau hitungan ember).",
      f"Jam hujan (Open-Meteo >= 0,2 mm): {(m.precipitation>=0.2).sum()}; jam sensor mencatat tambahan hujan: {(m.hujan_jam>0).sum()}; jam keduanya setuju: {((m.precipitation>=0.2)&(m.hujan_jam>0)).sum()}.", "",
      "Catatan: enam hari dalam satu cuaca musim tertentu tidak cukup untuk menyimpulkan sensor lebih baik atau lebih buruk dari Open-Meteo; hasil ini dipakai untuk menentukan koreksi bias awal dan satuan, bukan klaim N3."]
open(f"{root}/hasil/sensor_vs_om.md", "w", encoding="utf8").write("\n".join(L) + "\n"); print("\n".join(L))
