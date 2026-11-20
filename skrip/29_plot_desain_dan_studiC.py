import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import font_manager as fm
fam="DejaVu Serif"
for f in ["Times New Roman","Liberation Serif","Nimbus Roman"]:
    if any(f in x.name for x in fm.fontManager.ttflist): fam=f; break
plt.rcParams.update({"font.family":fam,"font.size":7,"axes.linewidth":0.6,"axes.spines.top":False,"axes.spines.right":False})
import os
HASIL=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","hasil"))+"/"
GAMBAR=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","gambar")); os.makedirs(GAMBAR,exist_ok=True)
O=HASIL
# ---- Fig. 1 design diagram (single column, vertical flow)
fig,ax=plt.subplots(figsize=(3.45,3.9)); ax.set_xlim(0,34.5); ax.set_ylim(0,39); ax.axis("off")
def box(x,y,w,h,title,body,fc,ec="#334155"):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.0,rounding_size=0.6",fc=fc,ec=ec,lw=0.7))
    ax.text(x+w/2,y+h-0.5,title,ha="center",va="top",fontsize=6.4,fontweight="bold")
    ax.text(x+w/2,y+h-2.3,body,ha="center",va="top",fontsize=5.4,linespacing=1.25)
def arr(x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=6,lw=0.7,color="#334155"))
# row 1: data
D=[("Archived NWP","ECMWF IFS 0.25°\nleads 1, 3, 7 d"),("Verification","reanalysis, daily\n2005–2026, 2 sites"),("Pest records","9 villages, monthly\n2021–2026"),("Sensor (pilot)","49 paired hours")]
w=8.0
for i,(t,bd) in enumerate(D): box(0.2+i*8.6,32.0,w,6.6,t,bd,"#E6EFFB")
# row 2: studies
S=[("Study A: forecast correction","Raw, persistence, rolling bias, Ridge, LightGBM, BiGRU,\nN-BEATS-lite; static vs adaptive conformal; cost","#E4F3EA"),
   ("Study B: pest risk","Next-month attack: history, season, monthly weather,\ndaily indices; Mangsa vs calendar month","#FBF0DC"),
   ("Study C: seasonal state","Dry / transition / wet at 10–60 d: persistence, climatology,\nPranata Mangsa, logistic, LightGBM","#EDE8F8")]
ys=[24.0,16.8,9.6]
for (t,bd,c),y in zip(S,ys): box(0.2,y,34.1,5.6,t,bd,c)
for x in (4.2,12.8,21.4,30.0): arr(x,32.0,x if x>0 else 4.2,29.7)
box(0.2,0.2,16.6,7.6,"Chronological tests","Walk-forward, rolling origin,\nleave-one-village-out, DM test,\npaired bootstrap, PICP/MPIW","#E9ECEF")
box(17.7,0.2,16.6,7.6,"Outputs","MAE and skill, intervals, macro-F1,\nAUC, GFLOPs and latency,\nlabel audit","#FBE3DE")
arr(8.5,9.6,8.5,7.9); arr(26.0,9.6,26.0,7.9)
plt.savefig(GAMBAR+"/fig_design.png",dpi=400,bbox_inches="tight",pad_inches=0.03); plt.close()
# ---- Fig. 4 seasonal-state skill
R=pd.read_csv(O+"studiC_keadaan_musim.csv")
fig,axs=plt.subplots(1,2,figsize=(3.45,2.5),sharey=True)
styles={"Persistence":("#000000",":","o"),"Climatology (10-day slot)":("#7A8794","--","s"),"Pranata Mangsa (phase mode)":("#8A5A00","-","^"),"Logistic (with calendar)":("#14284A","-","o"),"Logistic (weather only)":("#6FA3DE","-","v")}
lab={"Climatology (10-day slot)":"Climatology","Pranata Mangsa (phase mode)":"Pranata Mangsa","Logistic (with calendar)":"Logistic + calendar","Logistic (weather only)":"Logistic, weather only"}
for ax,site in zip(axs,["Kalisat","Surabaya"]):
    for m,(c,ls,mk) in styles.items():
        d=R[(R.site==site)&(R.model==m)].sort_values("lead")
        ax.plot(d.lead,d.macroF1,color=c,ls=ls,marker=mk,ms=3,lw=1,label=lab.get(m,m))
    ax.set_title(site,fontsize=7.5); ax.set_xticks([10,20,30,60]); ax.set_xlabel("Lead time (days)"); ax.grid(lw=0.3,color="#DDD"); ax.set_axisbelow(True)
axs[0].set_ylabel("Macro-F1, season state"); h,l=axs[0].get_legend_handles_labels(); fig.legend(h,l,fontsize=5.5,frameon=False,loc="lower center",ncol=3,handlelength=2.2,columnspacing=1.0)
plt.tight_layout(pad=0.4,rect=(0,0.15,1,1)); plt.savefig(GAMBAR+"/fig4.png",dpi=400); plt.close()
print("ok")
