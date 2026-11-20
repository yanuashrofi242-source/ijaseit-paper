"""Unduhan tambahan untuk blok prakiraan cuaca. JALANKAN DI KOMPUTER ANDA (butuh internet).
Pakai:  python 07_unduh_open_meteo_ekstra.py <folder kerja>
Keluaran di data_bersih/:
  om_harian_kalisat_2005_sekarang.csv    harian, titik tengah desa-desa Kalisat (untuk pra-latih prakiraan)
  om_harian_sensor_2005_sekarang.csv     harian, titik sensor cuacaPintar (Surabaya)
  om_jam_sensor_21_27okt2026.csv         per jam di titik sensor, untuk membandingkan sensor dengan Open-Meteo"""
import sys, time, json, urllib.request, urllib.parse
import pandas as pd

root = sys.argv[1]
vil = pd.read_csv(f"{root}/data_bersih/desa_koordinat.csv")
kal = (round(vil.Latitude.mean(), 4), round(vil.Longitude.mean(), 4))
sen = pd.read_csv(f"{root}/data_bersih/sensor_bersih.csv")
sen_pt = (round(sen.gps_lat.median(), 4), round(sen.gps_lon.median(), 4))
print("Titik Kalisat:", kal, "Titik sensor:", sen_pt)
DAILY = "temperature_2m_mean,temperature_2m_max,temperature_2m_min,relative_humidity_2m_mean,precipitation_sum,wind_speed_10m_mean,wind_direction_10m_dominant,shortwave_radiation_sum"
HOURLY = "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m,surface_pressure"
end = (pd.Timestamp.today().normalize() - pd.Timedelta(days=7)).strftime("%Y-%m-%d")

def get(params):
    url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)
    for k in range(5):
        try:
            with urllib.request.urlopen(url, timeout=180) as r: return json.load(r)
        except Exception as e:
            print("  ulangi", k + 1, e); time.sleep(6 * (k + 1))
    raise SystemExit("Gagal: " + url)

for nm, (la, lo) in (("kalisat", kal), ("sensor", sen_pt)):
    j = get(dict(latitude=la, longitude=lo, start_date="2005-01-01", end_date=end, daily=DAILY, timezone="Asia/Jakarta"))["daily"]
    pd.DataFrame(j).to_csv(f"{root}/data_bersih/om_harian_{nm}_2005_sekarang.csv", index=False); print("tulis", nm); time.sleep(2)
j = get(dict(latitude=sen_pt[0], longitude=sen_pt[1], start_date="2026-10-21", end_date="2026-10-27", hourly=HOURLY, timezone="Asia/Jakarta"))["hourly"]
pd.DataFrame(j).to_csv(f"{root}/data_bersih/om_jam_sensor_21_27okt2026.csv", index=False)
print("Selesai.")
