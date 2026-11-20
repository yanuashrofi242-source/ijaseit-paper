"""N4: audit label dan kebocoran. Jalankan: python 05_audit_label.py <folder kerja>
Mereplikasi protokol draft IES lalu membandingkannya dengan protokol bersih."""
import sys, time
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, f1_score
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

root = sys.argv[1]
L = ["# Audit label dan kebocoran (N4)", ""]
def say(s=""): print(s, flush=True); L.append(s)

# ---------- A. data_terlabel (Mongso) ----------
d = pd.read_csv(f"{root}/raw/data_terlabel.csv")
F = ["Temperatur", "Kelembaban", "Curah Hujan (mm)", "Arah Angin (derajat)", "Kecepatan Angin rata-rata (m/s)"]
X, y = d[F].values, d["Mongso"].values
grid = {"C": [0.1, 1, 10], "gamma": [0.01, 0.1, 1], "kernel": ["rbf"]}
say("## A. data_terlabel.csv, label Mongso (12 kelas, 7.306 baris)")
say("Baris tidak berurutan waktu dan tidak punya kolom tanggal, jadi split kronologis tidak mungkin; semua split di bawah acak. Itu sendiri batasan data ini.")
say("")
rows = []
def svm_eval(Xtr, ytr, Xte, yte):
    sc = StandardScaler().fit(Xtr)
    g = GridSearchCV(SVC(), grid, cv=3, scoring="accuracy", n_jobs=-1).fit(sc.transform(Xtr), ytr)
    p = g.predict(sc.transform(Xte))
    return accuracy_score(yte, p), f1_score(yte, p, average="macro")

t0 = time.time()
# 1. Protokol draft: imputasi/scaler seluruh data, SMOTE sebelum split, split acak
Xs = StandardScaler().fit_transform(X)
Xb, yb = SMOTE(random_state=42).fit_resample(Xs, y)
Xtr, Xte, ytr, yte = train_test_split(Xb, yb, test_size=0.2, random_state=42)
g = GridSearchCV(SVC(), grid, cv=3, scoring="accuracy", n_jobs=-1).fit(Xtr, ytr)
p = g.predict(Xte)
rows.append(("Protokol draft IES: scaler pada semua data, SMOTE sebelum split, split acak", accuracy_score(yte, p), f1_score(yte, p, average="macro")))
# 2. Split acak tanpa SMOTE
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
a, f = svm_eval(Xtr, ytr, Xte, yte); rows.append(("Split acak, tanpa SMOTE, scaler dari data latih", a, f))
# 3. Split acak + SMOTE hanya di data latih
sc = StandardScaler().fit(Xtr); Xs_tr, ys_tr = SMOTE(random_state=42).fit_resample(sc.transform(Xtr), ytr)
g = GridSearchCV(SVC(), grid, cv=3, scoring="accuracy", n_jobs=-1).fit(Xs_tr, ys_tr)
p = g.predict(sc.transform(Xte)); rows.append(("Split acak, SMOTE hanya di data latih", accuracy_score(yte, p), f1_score(yte, p, average="macro")))
# 4. Tanpa duplikat
dd = d.drop_duplicates()
Xtr, Xte, ytr, yte = train_test_split(dd[F].values, dd["Mongso"].values, test_size=0.2, random_state=42, stratify=dd["Mongso"].values)
a, f = svm_eval(Xtr, ytr, Xte, yte); rows.append(("Duplikat dibuang (6.849 baris), tanpa SMOTE", a, f))
# 5. Tanpa kelas Kasadasa (dugaan sintesis/imputasi) 
dk = dd[dd.Mongso != "Kasadasa"]
Xtr, Xte, ytr, yte = train_test_split(dk[F].values, dk["Mongso"].values, test_size=0.2, random_state=42, stratify=dk["Mongso"].values)
a, f = svm_eval(Xtr, ytr, Xte, yte); rows.append(("Duplikat dan kelas Kasadasa dibuang, tanpa SMOTE", a, f))
say("| Skenario | Akurasi | Macro-F1 |"); say("| --- | --- | --- |")
for n, a, f in rows: say(f"| {n} | {a:.4f} | {f:.4f} |")
say("")
# Rekonstruksi aturan oleh pohon dangkal
Xtr, Xte, ytr, yte = train_test_split(dd[F].values, dd["Mongso"].values, test_size=0.2, random_state=42, stratify=dd["Mongso"].values)
say("Pohon keputusan tunggal pada split acak (tanpa SMOTE): jika akurasi tinggi pada kedalaman kecil, label adalah aturan atas fitur.")
say(""); say("| Kedalaman | Akurasi uji |"); say("| --- | --- |")
for dep in (2, 4, 6, 8, 12):
    t = DecisionTreeClassifier(max_depth=dep, random_state=0).fit(Xtr, ytr); say(f"| {dep} | {t.score(Xte, yte):.4f} |")
imp = pd.Series(DecisionTreeClassifier(max_depth=12, random_state=0).fit(Xtr, ytr).feature_importances_, index=F).sort_values(ascending=False).round(3)
say(""); say("Kepentingan fitur pohon: " + ", ".join(f"{k} {v}" for k, v in imp.items()))
say(f"\n(waktu bagian A: {time.time()-t0:.0f} dtk)\n")

# ---------- B. Open-Meteo per jam: risk_level, pest_type ----------
h = pd.read_excel(f"{root}/raw/dataset_cuaca_hama_final_v2 (1).xlsx")
FH = ["temperature_2m (°C)", "rain (mm)", "wind_speed_10m (km/h)", "temperature_80m (°C)", "uv_index ()", "relative_humidity_2m (%)", "wind_direction_10m (°)"]
say("## B. dataset_cuaca_hama_final_v2, label risk_level dan pest_type (26.304 jam, 2022-2024)")
say("")
lr = LinearRegression().fit(h[FH], h.risk_score)
say(f"- risk_score direkonstruksi regresi linear dari 7 fitur cuaca: R2 = {lr.score(h[FH], h.risk_score):.4f}")
say(f"- Pasangan pest_type dan risk_level: " + h.groupby("pest_type").risk_level.nunique().max().__str__() + " risk_level per pest_type (1 berarti satu jenis hama selalu satu level)")
tr, te = h[h.time < "2024-01-01"], h[h.time >= "2024-01-01"]
say(f"- Latih 2022-2023, uji 2024 (kronologis):")
say(""); say("| Target | Model | Akurasi uji |"); say("| --- | --- | --- |")
for tgt in ("risk_level", "pest_type"):
    for dep in (3, 6, 10):
        t = DecisionTreeClassifier(max_depth=dep, random_state=0).fit(tr[FH], tr[tgt]); say(f"| {tgt} | pohon kedalaman {dep} | {t.score(te[FH], te[tgt]):.4f} |")
h["jam"] = h.time.dt.hour
for tgt in ("risk_level", "pest_type"):
    t = DecisionTreeClassifier(max_depth=6, random_state=0).fit(tr.assign(jam=tr.time.dt.hour)[["jam"]], tr[tgt])
    say(f"| {tgt} | hanya jam dalam sehari (tanpa cuaca), kedalaman 6 | {t.score(te.assign(jam=te.time.dt.hour)[['jam']], te[tgt]):.4f} |")
say("")
say("- Rata-rata risk_numeric per jam pada kolom waktu: " + ", ".join(f"{k:02d}:{v:.1f}" for k, v in h.groupby('jam').risk_numeric.mean().items()))
say("\nKesimpulan: label di kedua dataset dapat direkonstruksi dari cuaca (atau dari jam saja), jadi akurasi tinggi tidak menunjukkan kemampuan memprediksi serangan hama.")
open(f"{root}/hasil/audit_label.md", "w", encoding="utf8").write("\n".join(L) + "\n")
