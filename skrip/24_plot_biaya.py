import os
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from style import *
pts=[("Rolling bias",2e-9,0.0022,25.6,"bias"),("Ridge",3.2e-8,0.0010,29.2,"ridge"),("LightGBM",None,0.37,27.3,"lgbm"),("BiGRU",7.96e-5,0.509,28.8,"gru"),("N-BEATS-lite 64",1.079e-4,0.138,17.9,"nb64"),("N-BEATS-lite 16",2.237e-5,0.129,27.4,"nb16")]
fig,axs=plt.subplots(2,1,figsize=(3.45,4.2))
off={"Rolling bias":(5,-2,"left"),"Ridge":(5,2,"left"),"BiGRU":(0,6,"center"),"N-BEATS-lite 64":(-6,-2,"right"),"N-BEATS-lite 16":(-6,-9,"right"),"LightGBM":(5,-9,"left")}
for ax,(xi,xl) in zip(axs,[(1,"Analytic GFLOPs per forecast (log scale)"),(2,"CPU latency per forecast (ms, log scale)")]):
    for nm,gf,lat,sk,c in pts:
        x=gf if xi==1 else lat
        if x is None: continue
        ax.scatter(x,sk,s=34,color=C[c],zorder=3,edgecolor="white",lw=0.6); dx,dy,ha=off[nm]; ax.annotate(nm,(x,sk),textcoords="offset points",xytext=(dx,dy),fontsize=6,ha=ha,va="center")
    ax.set_xscale("log"); ax.set_xlabel(xl); ax.set_ylabel("Mean skill (%)"); ax.set_ylim(14,32); ax.grid(lw=0.3,color="#DDD")
axs[0].set_xlim(5e-10,8e-4); axs[1].set_xlim(4e-4,2.5)
axs[0].set_title("Accuracy against operations"); axs[1].set_title("Accuracy against measured latency")
plt.tight_layout(pad=0.4); plt.savefig(GAMBAR+"/fig_cost.png",dpi=400,bbox_inches="tight",pad_inches=0.03); plt.close(); print("ok")
