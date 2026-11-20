import os
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from style import *
import pickle, numpy as np, pandas as pd
O=HASIL
P=pickle.load(open(O+"_pred.pkl","rb"))
NM={"NWP mentah":"raw","Bias bergulir 30 hari":"bias","Ridge walk-forward":"ridge","LightGBM residu walk-forward":"lgbm"}
LAB={"raw":"Raw NWP","bias":"Rolling bias","ridge":"Ridge (WF)","lgbm":"LightGBM"}
# ---- Fig ts: Kalisat temperature lead 1
d,y,M=P[("Kalisat","suhu",1)]; d=pd.DatetimeIndex(d)
fig,ax=plt.subplots(2,1,figsize=(3.45,3.3),sharex=True,gridspec_kw={"height_ratios":[1.15,1]})
ax[0].plot(d,y,color="k",lw=0.7,label="Reanalysis (target)"); ax[0].plot(d,M["NWP mentah"],color=C["raw"],lw=0.7,label="Raw NWP"); ax[0].plot(d,M["Ridge walk-forward"],color=C["ridge"],lw=0.7,label="Ridge (WF)")
ax[0].set_ylabel("Temperature (°C)"); ax[0].legend(ncol=3,frameon=False,loc="upper center",bbox_to_anchor=(0.5,1.22),handlelength=1.4,columnspacing=0.8)
for k in ("raw","bias","ridge","lgbm"):
    key=[a for a,b in NM.items() if b==k][0]; e=pd.Series(np.abs(y-M[key]),index=d).rolling(30,min_periods=20).mean()
    ax[1].plot(d,e,color=C[k],label=LAB[k],lw=1.0)
ax[1].set_ylabel("30-day MAE (°C)"); ax[1].legend(ncol=2,frameon=False,loc="upper right",handlelength=1.4); ax[1].set_xlabel("Date (2025–2026)")
for a in ax: a.grid(lw=0.3,color="#DDD"); a.set_axisbelow(True)
plt.setp(ax[1].get_xticklabels(),rotation=0); ax[1].xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=3)); ax[1].xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b\n%y"))
plt.tight_layout(pad=0.4); plt.savefig(GAMBAR+"/fig_ts.png",dpi=400); plt.close()
# ---- Fig resid: signed error boxplots, Kalisat, three variables, three leads
fig,axs=plt.subplots(3,1,figsize=(3.45,4.6))
for ax,(v,ttl,u) in zip(axs,[("suhu","Temperature","°C"),("rh","Relative humidity","%"),("angin","Wind speed","km/h")]):
    pos=0; ticks=[]; labs=[]
    for L in (1,3,7):
        d,y,M=P[("Kalisat",v,L)]
        for k in ("raw","bias","ridge","lgbm"):
            key=[a for a,b in NM.items() if b==k][0]; e=y-M[key]; e=e[~np.isnan(e)]
            bp=ax.boxplot([e],positions=[pos],widths=0.7,showfliers=False,patch_artist=True,medianprops=dict(color="k",lw=0.8),whiskerprops=dict(lw=0.5),capprops=dict(lw=0.5),boxprops=dict(lw=0.5))
            bp["boxes"][0].set_facecolor(C[k]); bp["boxes"][0].set_alpha(0.85); pos+=1
        ticks.append(pos-2.5); labs.append(f"{L} d"); pos+=1
    ax.axhline(0,color="k",lw=0.5,ls=":"); ax.set_xticks(ticks); ax.set_xticklabels(labs); ax.set_title(f"{ttl}, Kalisat"); ax.set_ylabel(f"Error ({u})")
    if ax is axs[-1]: ax.set_xlabel("Lead time"); ax.grid(axis="y",lw=0.3,color="#DDD")
h=[plt.Rectangle((0,0),1,1,fc=C[k],alpha=0.85) for k in ("raw","bias","ridge","lgbm")]
fig.legend(h,[LAB[k] for k in ("raw","bias","ridge","lgbm")],ncol=4,frameon=False,loc="lower center",fontsize=6.5)
plt.tight_layout(pad=0.4,rect=(0,0.045,1,1)); plt.savefig(GAMBAR+"/fig_resid.png",dpi=400); plt.close()
# ---- Fig cov: rolling coverage static vs adaptive; Kalisat RH lead 3 and Surabaya RH lead 3
def aci(y,p,alpha=0.1,gamma=0.02,win=120,L=1):
    n=len(y); a=alpha; lo=np.full(n,np.nan); hi=np.full(n,np.nan); err=np.full(n,np.nan); ae=np.abs(y-p)
    for t in range(n):
        kn=ae[max(0,t-L-win+1):t-L+1] if t-L>=0 else np.array([])
        if len(kn)<30: continue
        q=np.quantile(kn,float(np.clip(1-a,0.5,0.999))); lo[t],hi[t]=p[t]-q,p[t]+q; err[t]=float(not(lo[t]<=y[t]<=hi[t]))
        if t-L>=0 and not np.isnan(err[t-L]): a=a+gamma*(alpha-err[t-L])
    return lo,hi
CONF=pickle.load(open(HASIL+"/_konformal_deret.pkl","rb"))   # dari 31_simpan_deret_konformal.py: Ridge walk-forward sejak 2025-03-01
T_WF0,T_TE="2025-03-01","2025-07-01"
fig,axs=plt.subplots(4,1,figsize=(3.45,5.0),sharex=True)
NAME={"suhu":("temperature","°C"),"angin":("wind","km/h"),"rh":("humidity","%")}
for j,(site,v,L) in enumerate([("Kalisat","suhu",3),("Surabaya","angin",3)]):   # cells where the static interval covered least at each site
    idx,y,p=CONF[(site,v,L)]; idx=pd.DatetimeIndex(idx)
    cal=(idx<T_TE)&(idx>=pd.Timestamp(T_WF0)+pd.Timedelta(days=L))
    qs=np.quantile(np.abs(y[cal]-p[cal]),0.9*(1+1/cal.sum()))      # static: one quantile from March-June 2025 (same as the tables)
    ls,hs=aci(y,p,L=L); te=idx>=T_TE
    cs=((y>=p-qs)&(y<=p+qs)).astype(float); ca=((y>=ls)&(y<=hs)).astype(float); ca[np.isnan(ls)]=np.nan
    d=idx[te]; st=pd.Series(cs[te],index=d).rolling(60,min_periods=40).mean(); ad=pd.Series(ca[te],index=d).rolling(60,min_periods=40).mean()
    print(site,v,L,"PICP static",round(cs[te].mean(),3),"PICP ACI",round(np.nanmean(ca[te]),3),"width ACI",round(np.nanmean((hs-ls)[te]),2),"static",round(2*qs,2))
    ax=axs[2*j]; ax.plot(d,st*100,color=C["raw"],label="Static"); ax.plot(d,ad*100,color=C["ridge"],label="Adaptive (ACI)"); ax.axhline(90,color="#B03A2E",lw=0.7,ls="--"); ax.set_ylim(40,102)
    ax.set_title(f"{site}, {NAME[v][0]}, lead {L} d"); ax.set_ylabel("60-day coverage (%)"); ax.grid(lw=0.3,color="#DDD")
    if j==0: ax.legend(frameon=False,loc="lower left",handlelength=1.4,ncol=2)
    ax=axs[2*j+1]; ax.plot(d,(hs-ls)[te],color=C["ridge"],label="Adaptive width"); ax.axhline(2*qs,color=C["raw"],ls="-",label="Static width"); ax.set_ylabel(f"Interval width ({NAME[v][1]})"); ax.grid(lw=0.3,color="#DDD")
    if j==0: ax.legend(frameon=False,loc="upper left",handlelength=1.4,ncol=2)
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=3)); ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %y"))
plt.tight_layout(pad=0.4); plt.savefig(GAMBAR+"/fig_cov.png",dpi=400); plt.close()
print("ok")
