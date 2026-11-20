"""Unduh prakiraan ARSIP Open-Meteo (Previous Runs API): prakiraan yang dibuat 1-7 hari sebelumnya, untuk Kalisat dan titik sensor Surabaya.
JALANKAN DI KOMPUTER ANDA (butuh internet).  Pakai:  python 13_unduh_prakiraan_arsip.py <folder kerja> [model]   contoh model: ecmwf_ifs025 (satu model tetap, arsip homogen)
Keluaran di data_bersih/: nwp_arsip_kalisat.csv, nwp_arsip_sensor.csv  (per jam, 2024-01-01 sampai 7 hari lalu, zona waktu Asia/Jakarta)
Catatan: arsip ini tersedia sejak Januari 2024 untuk sebagian besar model; skrip ini BELUM diuji dari sisi Claude (jaringan tidak terjangkau),
jika muncul galat HTTP 400 kirim pesannya apa adanya."""
import sys, time, json, urllib.request, urllib.parse
import pandas as pd
root = sys.argv[1]
MODEL = sys.argv[2] if len(sys.argv) > 2 else None
SUF = f"_{MODEL}" if MODEL else ""
vil = pd.read_csv(f"{root}/data_bersih/desa_koordinat.csv")
sen = pd.read_csv(f"{root}/data_bersih/sensor_bersih.csv")
PTS = {"kalisat": (round(vil.Latitude.mean(), 4), round(vil.Longitude.mean(), 4)), "sensor": (round(sen.gps_lat.median(), 4), round(sen.gps_lon.median(), 4))}
BASE = ["temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m"]
HOURLY = ",".join(b if k == 0 else f"{b}_previous_day{k}" for b in BASE for k in range(0, 8))
end = pd.Timestamp.today().normalize() - pd.Timedelta(days=7)

def get(params):
    url = "https://previous-runs-api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
    for k in range(6):
        try:
            with urllib.request.urlopen(url, timeout=180) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf8", "ignore")[:300]
            print("  HTTP", e.code, msg)
            if e.code == 400: raise SystemExit("Parameter ditolak: " + url)
            time.sleep(10 * (k + 1))
        except Exception as e:
            print("  ulangi", k + 1, e); time.sleep(6 * (k + 1))
    raise SystemExit("Gagal: " + url)

for nm, (la, lo) in PTS.items():
    parts = []
    for s in pd.date_range("2024-01-01", end, freq="90D"):
        e = min(s + pd.Timedelta(days=89), end)
        j = get(dict(latitude=la, longitude=lo, start_date=s.strftime("%Y-%m-%d"), end_date=e.strftime("%Y-%m-%d"), hourly=HOURLY, timezone="Asia/Jakarta", **({"models": MODEL} if MODEL else {})))["hourly"]
        j = {k.replace(f"_{MODEL}", "") if MODEL else k: v for k, v in j.items()}
        parts.append(pd.DataFrame(j)); print(nm, s.date(), "ok", flush=True); time.sleep(2)
    out = pd.concat(parts).drop_duplicates("time")
    out.to_csv(f"{root}/data_bersih/nwp_arsip{SUF}_{nm}.csv", index=False); print("tulis", nm, out.shape)
print("Selesai.")
