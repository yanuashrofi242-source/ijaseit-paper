"""Langkah 2: audit dan bersihkan data. Jalankan: python 01_audit_bersihkan.py <folder kerja>
Hanya membaca dari raw/, menulis ke data_bersih/ dan hasil/. File asli tidak diubah."""
import sys, os
import numpy as np, pandas as pd

root = sys.argv[1]
raw, out, res = f"{root}/raw", f"{root}/data_bersih", f"{root}/hasil"
log = []
def say(s=""):
    print(s); log.append(s)

# ---------- 1. Data OPT Kalisat ----------
o = pd.read_csv(f"{raw}/data-opt_kecamatan-kalisat_2021-2026.csv", parse_dates=["Date"])
o = o.sort_values(["Desa", "Date"]).reset_index(drop=True)
say("## Data OPT Kalisat")
say(f"- Baris: {len(o)}, desa: {o.Desa.nunique()}, bulan: {o.Date.nunique()} ({o.Date.min():%Y-%m} s.d. {o.Date.max():%Y-%m})")
say(f"- Kunci (Desa, Date) unik: {not o.duplicated(['Desa','Date']).any()}")
wcols = ["temp", "humidity", "precip", "windspeed", "vpd", "lwd"]
chg = o.groupby("Desa")[wcols].diff().abs().sum(axis=1) > 0
o["cuaca_berubah"] = chg.astype(int)
first = o.groupby("Desa").cumcount() == 0
o.loc[first, "cuaca_berubah"] = 1
q = o.groupby("Desa").agg(suhu_unik=("temp", "nunique"), hujan_unik=("precip", "nunique"),
                           bulan_cuaca_berubah=("cuaca_berubah", "sum"), n=("Date", "size"))
q["persen_cuaca_berubah"] = (100 * q.bulan_cuaca_berubah / q.n).round(0)
say("- **Kualitas cuaca per desa** (cuaca asli seharusnya berubah hampir tiap bulan):")
say("")
say(q.to_markdown() if hasattr(q, "to_markdown") else q.to_string())
say("")
say(f"- Bulan dengan cuaca berubah dibanding bulan sebelumnya: {int(o.cuaca_berubah.sum())} dari {len(o)} "
    f"({100*o.cuaca_berubah.mean():.0f}%). Sisanya diduga terisi ulang (forward-fill) atau gagal unduh.")
# Tingkat keparahan: pakai definisi dari csv (konsisten dengan LKSJ), buang kolom turunan LKSJ dari fitur
kep_map = {"Stabil": 0, "Agak Stabil": 1, "Sedang": 2, "Parah": 3}
o["keparahan"] = o["Tingkat_Keparahan"].map(kep_map)
say(f"- Keparahan (csv) menurut LKSJ rata-rata: " + o.groupby("Tingkat_Keparahan").LKSJ.mean().round(2).to_dict().__str__())
const = [c for c in o.columns if o[c].dtype != object and c not in ("Date",) and o[c].nunique() <= 1]
say(f"- Kolom konstan (dibuang): {const}")
drop = const + ["Tingkat_Keparahan", "Aktif_OPT", "anomaly_score", "Kecamatan", "coord_status"]
o_clean = o.drop(columns=[c for c in drop if c in o.columns])
o_clean.to_csv(f"{out}/kalisat_bersih.csv", index=False)
say(f"- Disimpan: data_bersih/kalisat_bersih.csv ({o_clean.shape[0]} x {o_clean.shape[1]})")
vil = o.groupby("Desa")[["Latitude", "Longitude", "latitude_fixed", "longitude_fixed"]].first().reset_index()
vil.to_csv(f"{out}/desa_koordinat.csv", index=False)
say("- Koordinat per desa disimpan di data_bersih/desa_koordinat.csv (dua pasang kolom; kolom *_fixed perlu Anda cocokkan dengan peta sebelum dipakai untuk unduhan cuaca)")

# ---------- 2. data_terlabel (BMKG) ----------
d = pd.read_csv(f"{raw}/data_terlabel.csv")
say("\n## data_terlabel.csv (BMKG harian)")
n0 = len(d)
r = "Curah Hujan (mm)"
say(f"- Baris awal {n0}; duplikat persis: {int(d.duplicated().sum())}")
say(f"- Hujan >= 900 mm (kode sentinel): {int((d[r] >= 900).sum())}; hujan > 100 mm/hari: {int((d[r] > 100).sum())}")
say(f"- Baris yang kelembapannya persis rata-rata (diduga imputasi): {int((d.Kelembaban == d.Kelembaban.mean()).sum())}; "
    f"kecepatan angin persis rata-rata: {int((d['Kecepatan Angin rata-rata (m/s)'] == d['Kecepatan Angin rata-rata (m/s)'].mean()).sum())}")
d["curiga_imputasi"] = ((d.Kelembaban == d.Kelembaban.mean()) | (d["Kecepatan Angin rata-rata (m/s)"] == d["Kecepatan Angin rata-rata (m/s)"].mean())).astype(int)
d.loc[d[r] >= 900, r] = np.nan
d = d.drop_duplicates()
say(f"- Kelas Mongso dengan penanda curiga: " + d.groupby("Mongso").curiga_imputasi.mean().round(2).sort_values(ascending=False).head(3).to_dict().__str__())
d.to_csv(f"{out}/data_terlabel_bersih.csv", index=False)
say(f"- Disimpan: data_bersih/data_terlabel_bersih.csv ({len(d)} baris). Kolom tanggal tidak ada: cari di arsip BMKG asli.")

# ---------- 3. Open-Meteo per jam ----------
h = pd.read_excel(f"{raw}/dataset_cuaca_hama_final_v2 (1).xlsx")
say("\n## dataset_cuaca_hama_final_v2 (Open-Meteo per jam)")
ann = h.groupby(h.time.dt.year)["rain (mm)"].sum().round(0).to_dict()
say(f"- Hujan tahunan (mm): {ann}. Normal Jawa Timur: > 1.000 mm. Kolom hujan perlu diunduh ulang.")
uv_peak = h.groupby(h.time.dt.hour)["uv_index ()"].mean().idxmax()
say(f"- Jam puncak UV rata-rata: {uv_peak:02d}:00 pada kolom waktu. Puncak UV lokal normalnya ~ 11:00-13:00 WIB, jadi kolom waktu diduga UTC.")
h["time_wib_dugaan"] = h.time + pd.Timedelta(hours=7)
h = h.rename(columns={"risk_score": "label_risk_score", "risk_level": "label_risk_level", "pest_type": "label_pest_type", "risk_numeric": "label_risk_numeric"})
h.to_csv(f"{out}/openmeteo_jam_bersih.csv", index=False)
say("- Kolom label_* ditandai karena bisa direkonstruksi dari cuaca; jangan dipakai sebagai kebenaran lapang. Disimpan: data_bersih/openmeteo_jam_bersih.csv")

# ---------- 4. Sensor cuacaPintar ----------
c = pd.read_excel(f"{raw}/dataset hasil cuacaPintar.xlsx")
say("\n## dataset hasil cuacaPintar (sensor)")
c["t"] = pd.to_datetime(c.captured_at)
c = c.sort_values("t")
gap = c.t.diff().dt.total_seconds().div(3600)
say(f"- Baris: {len(c)}, rentang {c.t.min()} s.d. {c.t.max()}; celah > 1 jam: {int((gap > 1).sum())}, celah terpanjang {gap.max():.1f} jam")
say(f"- Kolom pred_* kosong semua: {bool(c[['pred_temp','pred_humid','pred_wind_speed']].isna().all().all())}; hujan total {c.rain_total.max()} mm; UV maks {c.uv.max()} (bukan skala indeks UV 0-11)")
c.drop(columns=["t"]).to_csv(f"{out}/sensor_bersih.csv", index=False)

open(f"{res}/audit_log.md", "w", encoding="utf8").write("# Audit data\n\n" + "\n".join(log) + "\n")
print("\nSelesai. Log: hasil/audit_log.md")
