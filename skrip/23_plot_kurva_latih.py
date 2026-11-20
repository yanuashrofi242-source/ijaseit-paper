import sys, os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from style import *
import numpy as np, pandas as pd, torch, torch.nn as nn
torch.set_num_threads(2)
S=SKRIP+"/"
def load(path,hid=None):
    if hid: os.environ["NB_HID"]=str(hid)
    src=open(path,encoding="utf8").read().split("PRED = pickle.load")[0].replace("dd, out = sys.argv[1], sys.argv[2]","dd, out = '', ''")
    ns={"__name__":"x"}; exec(compile(src,path,"exec"),ns); return ns
g=load(S+"16_nn_pembanding.py"); n64=load(S+"17_nbeats_pembanding.py",64); n16=load(S+"17_nbeats_pembanding.py",16)
V,TV,WIN_DAYS=g["V"],g["TV"],g["WIN_DAYS"]; LEADS=g["LEADS"]
dd=DATA
site,L="Kalisat",1
tr_=pd.read_csv(f"{dd}/om_harian_kalisat_2005_sekarang.csv",parse_dates=["time"]).set_index("time").sort_index()
nw=g["daily_nwp"](f"{dd}/nwp_arsip_ecmwf_ifs025_kalisat.csv"); D=nw.join(tr_[[c for _,c,_ in V.values()]],how="inner")
T=pd.DataFrame({k:D[V[k][1]] for k in V}); N=pd.DataFrame({k:D[f"{k}_n{L}"] for k in V}); R=(T-N)[TV]
feat=pd.concat([T[TV],np.log1p(T[["hujan"]].clip(lower=0)),R.add_suffix("_res")],axis=1); idx=D.index; n=len(idx); fv=feat.values
Xs=np.full((n,WIN_DAYS,feat.shape[1]),np.nan); Z=np.full((n,6),np.nan); Y=np.full((n,3),np.nan)
for i in range(n):
    e=i-L
    if e-WIN_DAYS+1<0: continue
    Xs[i]=fv[e-WIN_DAYS+1:e+1]
    Z[i]=[N.suhu.iloc[i],N.rh.iloc[i],N.angin.iloc[i],np.log1p(max(N.hujan.iloc[i],0)) if not np.isnan(N.hujan.iloc[i]) else np.nan,np.sin(2*np.pi*idx[i].dayofyear/365.25),np.cos(2*np.pi*idx[i].dayofyear/365.25)]
    Y[i]=R.iloc[i].values
ok=~(np.isnan(Xs).any((1,2))|np.isnan(Z).any(1)|np.isnan(Y).any(1))
s0=pd.Timestamp("2025-07-01"); cut=s0-pd.Timedelta(days=L); trw=ok&(idx<=cut)&(idx>cut-pd.Timedelta(days=540)); blk=ok&(idx>=s0)&(idx<s0+pd.Timedelta(days=30))
ids=np.flatnonzero(trw); nv=int(0.2*len(ids)); itr,iva=ids[:-nv],ids[-nv:]       # validasi = 20% terakhir jendela latih (kronologis)
mu_x,sd_x=Xs[itr].mean((0,1)),Xs[itr].std((0,1))+1e-6; mu_z,sd_z=Z[itr].mean(0),Z[itr].std(0)+1e-6; sd_y=Y[itr].std(0)+1e-6
f=lambda a,m,s:torch.tensor((a-m)/s,dtype=torch.float32)
Xt,Zt,Yt=f(Xs[itr],mu_x,sd_x),f(Z[itr],mu_z,sd_z),torch.tensor(Y[itr]/sd_y,dtype=torch.float32)
Xv,Zv,Yv=f(Xs[iva],mu_x,sd_x),f(Z[iva],mu_z,sd_z),torch.tensor(Y[iva]/sd_y,dtype=torch.float32)
TAUS=g["TAUS"]
def pin(p,y): e=y.unsqueeze(-1)-p; return torch.maximum(TAUS*e,(TAUS-1)*e).mean()
def run(mk,epochs,wd,seed=0):
    torch.manual_seed(seed); m=mk(); opt=torch.optim.Adam(m.parameters(),lr=3e-3,weight_decay=wd); tl,vl=[],[]
    for ep in range(epochs):
        m.train(); perm=torch.randperm(len(Xt))
        for i in range(0,len(Xt),64):
            b=perm[i:i+64]; opt.zero_grad(); l=pin(m(Xt[b],Zt[b]),Yt[b]); l.backward(); opt.step()
        m.eval()
        with torch.no_grad(): tl.append(pin(m(Xt,Zt),Yt).item()); vl.append(pin(m(Xv,Zv),Yv).item())
    return tl,vl
nin,nst=Xt.shape[2],Zt.shape[1]
res={"BiGRU (4,489 par.)":run(lambda:g["Net"](nin,nst),40,1e-3),"N-BEATS-lite 64 (54,675 par.)":run(lambda:n64["Net"](nin,nst),40,1e-3),"N-BEATS-lite 16 (11,619 par.)":run(lambda:n16["Net"](nin,nst),25,0.01)}
cols=[C["gru"],C["nb64"],C["nb16"]]
fig,axs=plt.subplots(1,2,figsize=(3.45,2.1),sharey=True)
for (nm,(tl,vl)),c in zip(res.items(),cols):
    axs[0].plot(range(1,len(tl)+1),tl,color=c,label=nm); axs[1].plot(range(1,len(vl)+1),vl,color=c)
    print(nm,"train end %.3f val min %.3f at ep %d val end %.3f"%(tl[-1],min(vl),int(np.argmin(vl))+1,vl[-1]))
axs[0].set_title("Training"); axs[1].set_title("Validation (last 20% of window)"); 
for a in axs: a.set_xlabel("Epoch"); a.grid(lw=0.3,color="#DDD")
axs[0].set_ylabel("Pinball loss (scaled)")
h,l=axs[0].get_legend_handles_labels(); fig.legend(h,l,fontsize=5.4,frameon=False,loc="lower center",ncol=1,handlelength=1.8)
plt.tight_layout(pad=0.4,rect=(0,0.2,1,1)); plt.savefig(GAMBAR+"/fig_train.png",dpi=400); plt.close()
import json; json.dump({k:[v[0][-1],min(v[1]),int(np.argmin(v[1]))+1,v[1][-1],len(v[0])] for k,v in res.items()},open(GAMBAR+"/train_summary.json","w"))
