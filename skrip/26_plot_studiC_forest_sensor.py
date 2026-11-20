import os
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from style import *
import numpy as np, pandas as pd
O=HASIL
# ---- forest plot, Study C
Dl=pd.read_csv(O+"studiC_bootstrap_blok.csv")   # from 33_bootstrap_blok_studiC.py: moving-block bootstrap, 9-block length
order=["Persistence","Pranata Mangsa (phase mode)","Logistic (weather only)","Logistic (with calendar)","LightGBM (with calendar)"]
lab={"Persistence":"Persistence","Pranata Mangsa (phase mode)":"Pranata Mangsa","Logistic (weather only)":"Logistic, weather only","Logistic (with calendar)":"Logistic + calendar","LightGBM (with calendar)":"LightGBM + calendar"}
lc={10:"#9DB4D3",20:"#5F86B8",30:"#2D5A96",60:"#0E2A52"}
fig,axs=plt.subplots(2,1,figsize=(3.45,4.2),sharex=True)
for ax,site in zip(axs,["Kalisat","Surabaya"]):
    for i,m in enumerate(order):
        for j,Ld in enumerate((10,20,30,60)):
            r=Dl[(Dl.site==site)&(Dl.model==m)&(Dl.lead==Ld)].iloc[0]; y=i+(j-1.5)*0.16
            ax.plot([r.lo_block,r.hi_block],[y,y],color=lc[Ld],lw=1.0); ax.scatter(r.dF1,y,s=9,color=lc[Ld],zorder=3,label=f"{Ld} d" if i==0 else None)
    ax.axvline(0,color="k",lw=0.6); ax.set_yticks(range(len(order))); ax.set_yticklabels([lab[m] for m in order]); ax.invert_yaxis()
    ax.set_title(site)
    if ax is axs[-1]: ax.set_xlabel("Δ macro-F1 vs climatology (95% block-bootstrap CI)")
    ax.grid(axis="x",lw=0.3,color="#DDD"); ax.set_xlim(-0.30,0.17)
axs[0].legend(frameon=False,loc="lower left",ncol=2,title="Lead",title_fontsize=6,handletextpad=0.2,columnspacing=0.8)
plt.tight_layout(pad=0.4); plt.savefig(GAMBAR+"/fig_forest.png",dpi=400,bbox_inches="tight",pad_inches=0.03); plt.close()
# ---- rainfall per mangsa
H=pd.read_csv(O+"studiC_hujan_per_mangsa.csv",index_col=0)
fig,ax=plt.subplots(figsize=(3.45,2.1)); x=np.arange(len(H)); w=0.38
ax.bar(x-w/2,H.Kalisat,w,color="#14284A",label="Kalisat"); ax.bar(x+w/2,H.Surabaya,w,color="#8A5A00",label="Surabaya")
ax.set_xticks(x); ax.set_xticklabels(H.index,rotation=55,ha="right",fontsize=6); ax.set_ylabel("Mean rainfall (mm per 30 d)"); ax.legend(frameon=False,loc="upper left"); ax.grid(axis="y",lw=0.3,color="#DDD"); ax.set_axisbelow(True)
ax.set_xlabel("Pranata Mangsa phase (Kasa starts about 22 June)")
plt.tight_layout(pad=0.4); plt.savefig(GAMBAR+"/fig_mangsa.png",dpi=400,bbox_inches="tight",pad_inches=0.03); plt.close()
# ---- sensor vs NWP
m=pd.read_csv(O+"studiA_log_sensor_besar_pasangan.csv",parse_dates=["hr"])
fig,axs=plt.subplots(2,2,figsize=(3.45,3.7)); axs=axs.ravel(); sc={"A":"#C0392B","B":"#14284A"}
for ax,(a,b,t,u) in zip(axs[:2],[("T","temperature_2m","Temperature","°C"),("RH","relative_humidity_2m","Relative humidity","%")]):
    for s,g in m.groupby("site"): ax.scatter(g[b],g[a],s=12,color=sc[s],label=f"Site {s} (n={len(g)})",alpha=0.85,edgecolor="white",lw=0.3)
    lo,hi=min(m[a].min(),m[b].min())-1,max(m[a].max(),m[b].max())+1; ax.plot([lo,hi],[lo,hi],color="#999",lw=0.6,ls="--"); ax.set_xlim(lo,hi); ax.set_ylim(lo,hi)
    ax.set_xlabel(f"ECMWF archive ({u})"); ax.set_ylabel(f"Sensor ({u})"); ax.set_title(t); ax.grid(lw=0.3,color="#DDD")
axs[0].legend(frameon=False,loc="upper left",handletextpad=0.2)
m["h"]=m.hr.dt.hour
for ax,(a,b,t,u) in zip(axs[2:],[("T","temperature_2m","Temperature error","°C"),("RH","relative_humidity_2m","Humidity error","%")]):
    m["e"]=m[a]-m[b]
    for s_,g in m.groupby("site"): ax.scatter(g.h,g.e,s=12,color=sc[s_],alpha=0.85,edgecolor="white",lw=0.3)
    ax.axhline(0,color="k",lw=0.6); ax.set_xlabel("Hour of day (WIB)"); ax.set_ylabel(f"Sensor − NWP ({u})"); ax.set_title(t); ax.grid(lw=0.3,color="#DDD")
plt.tight_layout(pad=0.4); plt.savefig(GAMBAR+"/fig_sensor.png",dpi=400,bbox_inches="tight",pad_inches=0.03); plt.close(); print("ok")
