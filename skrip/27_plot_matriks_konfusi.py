import os
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from style import *
import numpy as np, pandas as pd
D=pd.read_csv(HASIL+"_detail.csv")
names=["Dry","Transition","Wet"]
panels=[(10,"Climatology (10-day slot)","Climatology, 10 d"),(10,"Logistic (with calendar)","Logistic + calendar, 10 d"),(30,"Climatology (10-day slot)","Climatology, 30 d"),(30,"Logistic (with calendar)","Logistic + calendar, 30 d")]
fig,axs=plt.subplots(2,2,figsize=(3.45,3.5)); axs=axs.ravel()
for ax,(L,m,t) in zip(axs,panels):
    g=D[(D.site=="Kalisat")&(D.lead==L)&(D.model==m)]; cm=np.bincount(g.y*3+g.p,minlength=9).reshape(3,3)
    f1=(2*np.diag(cm)/(cm.sum(0)+cm.sum(1))); rn=cm/cm.sum(1,keepdims=True)
    ax.imshow(rn,cmap="Blues",vmin=0,vmax=0.8)
    for i in range(3):
        for j in range(3): ax.text(j,i,f"{cm[i,j]}",ha="center",va="center",fontsize=7,color="white" if rn[i,j]>0.45 else "black")
    ax.set_xticks(range(3)); ax.set_yticks(range(3)); ax.set_xticklabels(["Dry","Trans.","Wet"]); ax.set_yticklabels(names)
    ax.set_xlabel("Predicted"); ax.set_title(f"{t}\nmacro-F1 = {f1.mean():.3f}",fontsize=7)
    ax.set_ylabel("Observed")
    for s in ax.spines.values(): s.set_visible(True); s.set_linewidth(0.5)
plt.tight_layout(pad=0.4); plt.savefig(GAMBAR+"/fig_conf.png",dpi=400,bbox_inches="tight",pad_inches=0.03); plt.close(); print("ok")
