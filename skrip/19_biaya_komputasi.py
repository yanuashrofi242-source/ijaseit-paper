"""Biaya komputasi model koreksi Studi A: parameter, GFLOPs analitik (2 x MAC / 1e9) per prakiraan, latensi CPU satu jendela.
Pakai: python 19_biaya_komputasi.py <folder keluaran>   (jalankan saat CPU senggang; torch 1 thread)"""
import sys, time, importlib.util, numpy as np, pandas as pd, torch, torch.nn as nn
torch.set_num_threads(1)
out = sys.argv[1]
def load(path, name):
    src = open(path, encoding="utf8").read().split("PRED = pickle.load")[0].replace("dd, out = sys.argv[1], sys.argv[2]", "dd, out = '', ''")
    ns = {}; exec(compile(src, name, "exec"), ns); return ns
g = load("16_nn_pembanding.py", "gru"); n = load("17_nbeats_pembanding.py", "nb")
NIN, NSTAT, T = 7, 6, 14
def params(m): return sum(p.numel() for p in m.parameters())
def macs_linear(m, rep=1): return sum(l.in_features * l.out_features * rep for l in m.modules() if isinstance(l, nn.Linear))
gru = g["Net"](NIN, NSTAT); nb = n["Net"](NIN, NSTAT)
H = 16
mac_gru = 2 * T * 3 * H * (NIN + H)                       # GRU dua arah, 3 gerbang
mac_att = T * (2 * H) * H + T * H                          # atensi aditif
mac_head = (2 * H + NSTAT) * 32 + 32 * 9
MAC = {"BiGRU-attention (3 var x 3 kuantil)": mac_gru + mac_att + mac_head, "N-BEATS-lite": macs_linear(nb)}
F = 16
rows = [["Rolling bias 30 days", 1, 1, 0.0], ["Ridge (per target)", F + 1, F, 0.0]]
rows = [dict(model=r[0], params=r[1], gflops=2 * r[2] / 1e9) for r in rows]
rows += [dict(model="BiGRU-attention (3 targets)", params=params(gru), gflops=2 * MAC["BiGRU-attention (3 var x 3 kuantil)"] / 1e9),
         dict(model="N-BEATS-lite (3 targets)", params=params(nb), gflops=2 * MAC["N-BEATS-lite"] / 1e9)]
def lat(fn, reps=300, rounds=5):
    best = 1e9
    for _ in range(rounds):
        t = time.perf_counter()
        for _ in range(reps): fn()
        best = min(best, (time.perf_counter() - t) / reps)
    return best * 1e3
x = torch.randn(1, T, NIN); z = torch.randn(1, NSTAT)
gru.eval(); nb.eval()
w = np.random.randn(F + 1); v = np.random.randn(F)
with torch.no_grad():
    L = {"Rolling bias 30 days": lat(lambda: float(np.mean(v))), "Ridge (per target)": lat(lambda: float(v @ w[:F] + w[F])),
         "BiGRU-attention (3 targets)": lat(lambda: gru(x, z)), "N-BEATS-lite (3 targets)": lat(lambda: nb(x, z))}
import lightgbm as lgb
Xr = np.random.randn(600, F); yr = np.random.randn(600)
gb = lgb.LGBMRegressor(n_estimators=200, num_leaves=8, learning_rate=0.03, verbose=-1, n_jobs=1).fit(Xr, yr)
L["LightGBM residual (per target)"] = lat(lambda: gb.predict(Xr[:1]), reps=100, rounds=3)
rows.append(dict(model="LightGBM residual (per target)", params=int(sum(t.tree_.node_count for t in []) or 200 * (2 * 8 - 1)), gflops=float("nan")))
for r in rows: r["latency_ms"] = L[r["model"]]
R = pd.DataFrame(rows); R.to_csv(f"{out}/studiA_biaya_komputasi.csv", index=False)
print(R.to_string())
