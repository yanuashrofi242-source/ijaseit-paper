import os
import sys, warnings; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); warnings.filterwarnings("ignore")
from style import *
import numpy as np, pandas as pd, lightgbm as lgb
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve, average_precision_score
root=ROOT
ix=pd.read_csv(f"{root}/data_bersih/indeks_harian_bulanan.csv",parse_dates=["Date"])
d=pd.read_csv(f"{root}/data_bersih/fitur_kalisat.csv",parse_dates=["Date","target_date"]).merge(ix,on=["Desa","Date"],how="left")
IX=[c for c in ix.columns if c.startswith("ix")]; season=["bulan_sin","bulan_cos","mangsa_idx"]
WM=["om_temp","om_humidity","om_precip_total","om_hari_hujan","om_windspeed","om_vpd","om_lwd_jam_per_hari"]
d["bln"]=d.Date.dt.month; ycol="y_next_SSJ"; hist=["SSJ","SSJ_l1","SSJ_l2","LKSJ","LT"]
def add_anom(tr,te,cols):
    mu=tr.groupby("bln")[cols].mean(); out=[]
    for part in (tr.copy(),te.copy()):
        part[[c+"_an" for c in cols]]=part[cols].values-mu.reindex(part.bln).values; out.append(part)
    return out
mk=lambda:lgb.LGBMClassifier(n_estimators=200,learning_rate=0.03,num_leaves=8,min_child_samples=10,subsample=0.8,subsample_freq=1,colsample_bytree=0.8,reg_lambda=2,class_weight="balanced",random_state=0,verbose=-1)
folds=[(d.target_date<"2023-01-01",(d.target_date>="2023-01-01")&(d.target_date<"2024-01-01")),(d.target_date<"2024-01-01",(d.target_date>="2024-01-01")&(d.target_date<"2025-01-01")),(d.target_date<"2025-01-01",d.target_date>="2025-01-01")]
sets={"History + season":(hist+season,[]),"Monthly weather + season":(season,WM),"Daily indices + season":(season,IX),"History + monthly weather":(hist+season,WM)}
P={}; Y=None; imp=None; PRI=None
for nm,(fixed,an) in sets.items():
    ys,ps,pri=[],[],[]
    for tri,tei in folds:
        tr,te=d[tri],d[tei]; cols=fixed
        if an: tr,te=add_anom(tr,te,an); cols=fixed+[c+"_an" for c in an]
        med=tr[cols].median(); m=mk().fit(tr[cols].fillna(med),tr[ycol]); ps.append(m.predict_proba(te[cols].fillna(med))[:,1]); ys.append(te[ycol].values); pri.append(np.full(len(te),tr[ycol].mean()))
        if nm=="History + season" and tri is folds[-1][0]: imp=pd.Series(m.booster_.feature_importance("gain"),index=cols)
    P[nm]=np.concatenate(ps); Y=np.concatenate(ys)
    if nm=="History + season": PRI=np.concatenate(pri)
te_all=pd.concat([d[t] for _,t in folds]); pers=(te_all.SSJ.values>0).astype(float)+1e-6*np.random.default_rng(0).random(len(te_all))
P["Persistence (SSJ > 0 now)"]=pers
col={"History + season":C["ridge"],"Monthly weather + season":C["gru"],"Daily indices + season":C["nb64"],"History + monthly weather":C["bias"],"Persistence (SSJ > 0 now)":"#000000"}
print("n",len(Y),"prev",Y.mean().round(3)); 
for k,p in P.items(): print(k,"AUC %.3f PR %.3f"%(roc_auc_score(Y,p),average_precision_score(Y,p)))
fig,axs=plt.subplots(2,2,figsize=(3.45,3.9)); axs=axs.ravel()
for k,p in P.items():
    f,t,_=roc_curve(Y,p); axs[0].plot(f,t,color=col[k],lw=1.0,ls=":" if "Pers" in k else "-",label=f"{k} ({roc_auc_score(Y,p):.2f})")
    pr,rc,_=precision_recall_curve(Y,p); axs[1].plot(rc,pr,color=col[k],lw=1.0,ls=":" if "Pers" in k else "-")
axs[0].plot([0,1],[0,1],color="#999",lw=0.5,ls="--"); axs[0].set_xlabel("False positive rate"); axs[0].set_ylabel("True positive rate"); axs[0].set_title("ROC")
axs[1].axhline(Y.mean(),color="#999",lw=0.5,ls="--"); axs[1].set_xlabel("Recall"); axs[1].set_ylabel("Precision"); axs[1].set_title("Precision–recall")
# reliability for history+season
p=P["History + season"]; pc=1/(1+np.exp(-(np.log(np.clip(p,1e-6,1-1e-6)/(1-np.clip(p,1e-6,1-1e-6)))+np.log(PRI/(1-PRI)))))   # prior-shift correction of the class weights
axs[2].plot([0,1],[0,1],color="#999",lw=0.5,ls="--")
for q,c_,lb in ((p,C["raw"],"Class-weighted score"),(pc,C["ridge"],"Prior-corrected")):
    bins=np.quantile(q,np.linspace(0,1,7)); b=np.clip(np.digitize(q,bins[1:-1]),0,5)
    axs[2].plot([q[b==i].mean() for i in range(6)],[Y[b==i].mean() for i in range(6)],color=c_,marker="o",ms=3,label=lb)
from sklearn.metrics import brier_score_loss
print("Brier raw %.3f corrected %.3f prevalence %.3f"%(brier_score_loss(Y,p),brier_score_loss(Y,pc),brier_score_loss(Y,PRI)))
axs[2].legend(frameon=False,loc="upper left",fontsize=5.5,handlelength=1.2,handletextpad=0.3); axs[2].set_xlabel("Mean predicted probability"); axs[2].set_ylabel("Observed share"); axs[2].set_title("Reliability (history + season)")
im=imp.sort_values(ascending=True); lab={"SSJ":"SSJ (now)","SSJ_l1":"SSJ lag 1","SSJ_l2":"SSJ lag 2","LKSJ":"LKSJ","LT":"Rice area","bulan_sin":"sin(month)","bulan_cos":"cos(month)","mangsa_idx":"Mangsa index"}
axs[3].barh([lab.get(i,i) for i in im.index],im.values/im.sum()*100,color=C["ridge"],height=0.6); axs[3].set_xlabel("Gain share (%)"); axs[3].set_title("LightGBM importance")
for a in axs[:3]: a.grid(lw=0.3,color="#DDD"); a.set_axisbelow(True)
h,l=axs[0].get_legend_handles_labels(); fig.legend(h,l,ncol=2,frameon=False,loc="lower center",fontsize=6,handlelength=1.6,columnspacing=1.0)
plt.tight_layout(pad=0.4,rect=(0,0.14,1,1)); plt.savefig(GAMBAR+"/fig_roc.png",dpi=400,bbox_inches="tight",pad_inches=0.03); plt.close()
