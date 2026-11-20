import re, pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"DejaVu Serif","font.size":7,"axes.linewidth":0.6,"axes.spines.top":False,"axes.spines.right":False,"xtick.major.width":0.6,"ytick.major.width":0.6})
for f in ["Times New Roman","Liberation Serif","Nimbus Roman"]:
    from matplotlib import font_manager as fm
    if any(f in x.name for x in fm.fontManager.ttflist): plt.rcParams["font.family"]=f; break
import os
HASIL=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","hasil"))+"/"
GAMBAR=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","gambar")); os.makedirs(GAMBAR,exist_ok=True)
O=HASIL
nn=pd.read_csv(O+"studiA_nn_hasil.csv")
C={"bias":"#B8C2CC","ridge":"#3B6FB6","gru":"#14284A"}
# Fig 1: skill vs raw NWP, mean over 3 variables
fig,axs=plt.subplots(1,2,figsize=(3.45,2.0),sharey=True)
for ax,site in zip(axs,["Kalisat","Surabaya"]):
    d=nn[nn.site==site]; x=np.arange(3); w=0.26
    for i,(k,col,lab) in enumerate([("mae Bias bergulir 30 hari","bias","Rolling bias"),("mae Ridge walk-forward","ridge","Ridge WF"),("mae BiGRU-Attention kuantil (median)","gru","BiGRU")]):
        v=[100*(1-(d[d.L==L][k]/d[d.L==L]["mae NWP mentah"]).mean()) for L in (1,3,7)]
        ax.bar(x+(i-1)*w,v,w*0.92,color=C[col],label=lab)
    ax.set_xticks(x); ax.set_xticklabels(["1 d","3 d","7 d"]); ax.set_title(site,fontsize=7.5)
    ax.set_xlabel("Lead time"); ax.set_ylim(0,50); ax.grid(axis="y",lw=0.3,color="#DDD"); ax.set_axisbelow(True)
axs[0].set_ylabel("Mean skill vs raw NWP (%)"); axs[0].legend(frameon=False,fontsize=6,loc="upper right",ncol=1)
plt.tight_layout(pad=0.4); plt.savefig(GAMBAR+"/fig1.png",dpi=400); plt.close()
# Fig 2: coverage
t=open(O+"studiA_pembanding_adil.md",encoding="utf8").read()
sec=t[t.index("## Interval 90%"):t.index("## Kejadian hujan")]
rows=[r for r in sec.splitlines() if r.startswith("| Kalisat") or r.startswith("| Surabaya")]
st=[];ad=[]
for r in rows:
    c=[x.strip() for x in r.strip("|").split("|")]; st.append(float(c[3].rstrip("%"))); ad.append(float(c[5].rstrip("%")))
series=[("Static\n(Ridge)",st,"#B8C2CC"),("Adaptive\n(Ridge)",ad,"#3B6FB6"),("BiGRU\nquantiles",list(100*nn.picp_q),"#8A5A00"),("BiGRU +\nadaptive",list(100*nn.picp_aci),"#14284A")]
fig,ax=plt.subplots(figsize=(3.45,2.0)); rng=np.random.default_rng(1)
for i,(n,v,c) in enumerate(series):
    xs=i+rng.uniform(-0.15,0.15,len(v)); ax.scatter(xs,v,s=11,color=c,edgecolor="white",linewidth=0.4,zorder=3)
    ax.hlines(np.mean(v),i-0.3,i+0.3,color="black",lw=1)
ax.axhline(90,color="#C2492F",lw=0.8,ls="--"); ax.text(-0.45,90.5,"nominal 90%",color="#C2492F",fontsize=6,ha="left")
ax.set_xticks(range(4)); ax.set_xticklabels([s[0] for s in series]); ax.set_ylabel("Empirical coverage, 18 cells (%)"); ax.set_ylim(75,98); ax.set_xlim(-0.5,3.5)
ax.grid(axis="y",lw=0.3,color="#DDD"); ax.set_axisbelow(True)
plt.tight_layout(pad=0.4); plt.savefig(GAMBAR+"/fig2.png",dpi=400); plt.close()
# Fig 3: Study B AUC
items=[("Persistence (attack this month)",0.611,None),("Monthly weather + season",0.630,(0.55,0.70)),("Daily indices + season",0.651,(0.59,0.72)),("History + monthly weather",0.761,(0.69,0.83)),("History + daily indices",0.767,(0.70,0.82)),("History + season",0.779,(0.72,0.84))]
fig,ax=plt.subplots(figsize=(3.45,2.0))
for i,(n,a,ci) in enumerate(items):
    col="#14284A" if "History" in n else "#7A8794"
    if ci: ax.hlines(i,ci[0],ci[1],color=col,lw=1.2)
    ax.scatter([a],[i],s=18,color=col,zorder=3,edgecolor="white",linewidth=0.4)
    ax.text(0.452,i,f"{a:.2f}",va="center",fontsize=6.5)
ax.set_yticks(range(len(items))); ax.set_yticklabels([i[0] for i in items],fontsize=6.5); ax.axvline(0.5,color="#999",lw=0.5,ls=":")
ax.set_xlim(0.44,0.90); ax.set_xlabel("AUC, next-month new attack (rolling origin, LightGBM)"); ax.grid(axis="x",lw=0.3,color="#DDD"); ax.set_axisbelow(True)
plt.tight_layout(pad=0.4); plt.savefig(GAMBAR+"/fig3.png",dpi=400); plt.close()
print(st[:3],ad[:3]); print(nn.groupby("site")[["picp_q","picp_aci"]].agg(["min","max"]))
