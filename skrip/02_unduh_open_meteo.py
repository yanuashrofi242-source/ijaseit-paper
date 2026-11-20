"""Unduh cuaca Open-Meteo per desa Kalisat dan buat agregat bulanan.
JALANKAN DI KOMPUTER ANDA yang punya internet (sandbox kerja Claude tidak bisa mengakses Open-Meteo).
Pemakaian:  python 02_unduh_open_meteo.py <folder kerja> [original|fixed]
Butuh: pandas, numpy. Tanpa kunci API (Open-Meteo gratis untuk non-komersial).
Keluaran: data_bersih/weather_desa_harian.csv, data_bersih/weather_desa_bulanan.csv"""
import sys, time, json, urllib.request, urllib.parse
import numpy as np, pandas as pd

root = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "original"
vil = pd.read_csv(f"{root}/data_bersih/desa_koordinat.csv")
if mode == "fixed":
    vil["lat"], vil["lon"] = vil["latitude_fixed"], vil["longitude_fixed"]
else:
    vil["lat"], vil["lon"] = vil["Latitude"], vil["Longitude"]
START, END = "2021-01-01", "2026-05-31"
VARS = "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"

def fetch(lat, lon):
    q = dict(latitude=lat, longitude=lon, start_date=START, end_date=END, hourly=VARS, timezone="Asia/Jakarta")
    url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(q)
    for k in range(5):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return json.load(r)
        except Exception as e:
            print("  ulangi", k + 1, e); time.sleep(5 * (k + 1))
    raise SystemExit("Gagal mengunduh " + url)

rows = []
for _, v in vil.iterrows():
    print("Unduh", v.Desa, v.lat, v.lon)
    j = fetch(v.lat, v.lon)["hourly"]
    df = pd.DataFrame(j); df["time"] = pd.to_datetime(df["time"]); df["Desa"] = v.Desa
    rows.append(df); time.sleep(1.5)
h = pd.concat(rows, ignore_index=True).rename(columns={"temperature_2m": "t", "relative_humidity_2m": "rh",
                                                        "precipitation": "p", "wind_speed_10m": "w"})
es = 0.6108 * np.exp(17.27 * h.t / (h.t + 237.3))
h["vpd"] = es * (1 - h.rh / 100)
h["rh90"] = (h.rh >= 90).astype(int)
h["date"] = h.time.dt.floor("D")
d = h.groupby(["Desa", "date"]).agg(t_mean=("t", "mean"), t_max=("t", "max"), t_min=("t", "min"), rh_mean=("rh", "mean"),
                                    p_sum=("p", "sum"), w_mean=("w", "mean"), vpd_mean=("vpd", "mean"),
                                    rh90_jam=("rh90", "sum")).reset_index()
d.to_csv(f"{root}/data_bersih/weather_desa_harian.csv", index=False)
d["Date"] = d.date.dt.to_period("M").dt.to_timestamp()
d["hari_hujan"] = (d.p_sum >= 1).astype(int)
m = d.groupby(["Desa", "Date"]).agg(om_temp=("t_mean", "mean"), om_tmax=("t_max", "mean"), om_humidity=("rh_mean", "mean"),
                                    om_precip_total=("p_sum", "sum"), om_hari_hujan=("hari_hujan", "sum"),
                                    om_windspeed=("w_mean", "mean"), om_vpd=("vpd_mean", "mean"),
                                    om_lwd_jam_per_hari=("rh90_jam", "mean")).reset_index()
m.to_csv(f"{root}/data_bersih/weather_desa_bulanan.csv", index=False)
print("Selesai.", len(d), "baris harian,", len(m), "baris bulanan. Hujan tahunan rata-rata (mm):")
print(m.assign(th=m.Date.dt.year).groupby(["th"]).om_precip_total.sum().div(m.Desa.nunique()).round(0).to_dict())
