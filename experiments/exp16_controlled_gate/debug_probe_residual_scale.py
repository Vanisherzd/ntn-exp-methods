"""Self-contained probe: does pre-registered Delta_n clear the residual scale floor?
DEBUG territory. NOT the production simulator. No tuning permitted on the result."""
import math, json
import numpy as np
from sgp4.api import Satrec, WGS72

CFG=json.load(open("/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/experiments/exp16_controlled_gate/physical_config.json"))
MU=398600.4418; WGS84_A=6378137.0; WGS84_E2=0.006694379990141317
OMEGA=7.292115e-5; C=299792458.0
DN=CFG["injected_od_error_Delta"]["nominal_magnitudes"]["delta_n_rev_per_day"]
DB=CFG["injected_od_error_Delta"]["nominal_magnitudes"]["delta_bstar_frac"]
DMA=CFG["injected_od_error_Delta"]["nominal_magnitudes"]["delta_mean_anomaly_deg"]
OFFS=CFG["fixed_config"]["transmission_offsets"]
GS=(24.0,121.0,100.0); FC=868e6; MASK=10.0

def mk(n_rev_day,incl,ecc,bstar,ma_deg,epoch_jd,raan=40.0,argp=30.0):
    s=Satrec()
    s.sgp4init(WGS72,'i',99999,epoch_jd-2433281.5,bstar,0.0,0.0,
               ecc,math.radians(argp),math.radians(incl),
               math.radians(ma_deg%360.0),n_rev_day*2*math.pi/1440.0,math.radians(raan))
    return s

def geom(sat,unix):
    jt=unix/86400.0+2440587.5; jd=np.floor(jt-0.5)+0.5; fr=jt-jd
    err,r,v=sat.sgp4_array(jd,fr)
    lat,lon=math.radians(GS[0]),math.radians(GS[1])
    n=WGS84_A/math.sqrt(1-WGS84_E2*math.sin(lat)**2)
    re=np.array([(n+GS[2])*math.cos(lat)*math.cos(lon),(n+GS[2])*math.cos(lat)*math.sin(lon),
                 (n*(1-WGS84_E2)+GS[2])*math.sin(lat)])
    d=(jd+fr)-2451545.0; th=np.radians((280.46061837+360.98564736629*d)%360.0)
    ct,st=np.cos(th),np.sin(th)
    x=(ct*re[0]-st*re[1])*1e-3; y=(st*re[0]+ct*re[1])*1e-3; z=np.full_like(x,re[2]*1e-3)
    gr=np.stack([x,y,z],1); gv=np.stack([-OMEGA*y,OMEGA*x,np.zeros_like(x)],1)
    dr=r-gr; rm=np.linalg.norm(dr,axis=1); ok=(err==0)&(rm>1)&np.isfinite(rm)
    rh=dr/np.where(ok,rm,1.0)[:,None]
    # geodetic up (the repaired vertical)
    up=np.stack([np.cos(lat)*np.cos(th+lon-th),np.zeros_like(x),np.zeros_like(x)],1)
    up=gr/(np.linalg.norm(gr,axis=1)[:,None]+1e-9)   # probe: geocentric is fine for scale
    el=np.degrees(np.arcsin(np.clip(np.einsum("ij,ij->i",rh,up),-1,1)))
    rr=np.einsum("ij,ij->i",v-gv,rh)
    return el,rm,-FC*rr*1e3/C,ok

def passes(sat,t0,t1,thr=MASK,step=60.0):
    g=t0+np.arange(int((t1-t0)/step)+1)*step
    el,_,_,ok=geom(sat,g); f=np.where(ok,el-thr,-1e3)
    up=np.flatnonzero((f[:-1]<0)&(f[1:]>=0)); dn=np.flatnonzero((f[:-1]>=0)&(f[1:]<0))
    def ref(tb,ta):
        lo,hi=tb,ta
        for _ in range(30):
            if abs(hi-lo)<=1.0: break
            m=0.5*(lo+hi)
            if geom(sat,np.array([m]))[0][0]-thr>=0: hi=m
            else: lo=m
        return hi
    out=[]
    for i in up:
        later=dn[dn>i]
        if later.size==0: continue
        j=int(later[0])
        a=ref(float(g[i]),float(g[i+1])); b=ref(float(g[j+1]),float(g[j]))
        if b-a>=60.0: out.append((a,b))
    return out

print(f"pre-registered: delta_n={DN:.2e} rev/day  delta_bstar={DB}  delta_MA={DMA} deg")
print(f"offsets={OFFS}  floor = 0.1% of median|D_physics|\n")
print(f"{'regime':16s} {'age_h':>6s} {'n_tx':>5s} {'med|D_phys|':>12s} {'med|r|':>9s} {'ratio%':>8s} {'floor':>6s}")
for nm,rg in CFG["regimes"].items():
    for sl,age in CFG["staleness_levels_h"].items():
        # CORRECT construction: ONE element set at epoch ep0. Truth is its SGP4
        # propagation (SGP4 is self-consistent). The held element is the SAME set
        # with the injected OD error Delta. Both are evaluated at t = ep0 + age, so
        # the residual arises PURELY from Delta propagated over `age`.
        ep=2460000.5
        true=mk(rg["n_rev_day"],rg["incl_deg"],rg["ecc"],rg["bstar"],10.0,ep)
        held=mk(rg["n_rev_day"]+DN,rg["incl_deg"],rg["ecc"],rg["bstar"]*(1+DB),
                10.0+DMA,ep)
        t0=(ep-2440587.5)*86400.0+age*3600.0
        iv=passes(true,t0,t0+2*86400.0)
        D=[];RR=[]
        for (a,b) in iv:
            for f in OFFS:
                t=a+f*(b-a)
                e1,_,d1,o1=geom(true,np.array([t])); e2,_,d2,o2=geom(held,np.array([t]))
                if o1[0] and o2[0]: D.append(abs(d2[0])); RR.append(abs(d1[0]-d2[0]))
        if not D: print(f"{nm:16s} {age:6.0f}  no visible passes"); continue
        md=float(np.median(D)); mr=float(np.median(RR)); ra=100*mr/md
        print(f"{nm:16s} {age:6.0f} {len(D):5d} {md:12.1f} {mr:9.3f} {ra:8.3f} "
              f"{'PASS' if ra>=0.1 else 'FAIL':>6s}")
print("\nSystematic term only (no OU noise). Residual arises purely from Delta")
print("propagated over `age`; both trajectories share the same element epoch.")
# analytic cross-check
import math as _m
for nm,rg in CFG["regimes"].items():
    a=(MU/((rg["n_rev_day"]*2*_m.pi/86400.0)**2))**(1/3)
    for sl,age in CFG["staleness_levels_h"].items():
        ds=2*_m.pi*a*DN*(age/24.0)
        v=_m.sqrt(MU/a); dt=ds/v
        print(f"  analytic {nm:14s} age={age:5.0f}h  along-track drift={ds:7.3f} km  dt={dt:6.3f} s")
    break
