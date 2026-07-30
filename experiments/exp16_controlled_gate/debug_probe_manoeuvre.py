"""Design the harm-producing shift HONESTLY: fixed physical manoeuvre direction,
seed-drawn OD-error sign. Harm must EMERGE, not be rigged."""
import numpy as np
MU=398600.4418; DN=5.0e-5
print("Setup: r ~ (n_held - n_true)*age. Pre-shift gap g0 = s*DN, s = +-1 drawn per seed.")
print("Manoeuvre changes n_true by dn_m (direction FIXED by physics, not by s).")
print("Post-shift gap g1 = g0 - dn_m.   k = g1/g0.   harm iff k < 0.5\n")
for nm,n_rev in (("R1_low_sso",15.21),("R2_mid_polar",14.43),("R3_upper_polar",13.11)):
    a=(MU/((n_rev*2*np.pi/86400.0)**2))**(1/3); v=np.sqrt(MU/a)
    print(f"{nm}  a={a:.1f} km  v={v:.4f} km/s")
    print(f"  {'dv(cm/s)':>9s} {'dir':>10s} {'dn_m(rev/d)':>12s} | {'s=+1: k':>9s} {'verdict':>7s} | {'s=-1: k':>9s} {'verdict':>7s}")
    for dv_cms,dirn in ((1.7,"prograde"),(1.7,"retrograde"),(3.4,"prograde")):
        sgn=1.0 if dirn=="prograde" else -1.0
        dv=sgn*dv_cms/1e5                     # km/s
        da=2*a*dv/v; dn_m=-1.5*n_rev*da/a     # rev/day
        row=f"  {dv_cms:9.2f} {dirn:>10s} {dn_m:12.3e} |"
        for s in (+1.0,-1.0):
            g0=s*DN; g1=g0-dn_m; k=g1/g0
            row+=f" {k:9.3f} {'HARM' if k<0.5 else 'helps':>7s} |"
        print(row)
    print()
print("KEY RESULT: with the manoeuvre direction FIXED by physics and the OD-error sign")
print("drawn per seed, harm occurs in exactly the seeds whose pre-existing error the")
print("manoeuvre OPPOSES -- about half. Harm EMERGES from the physics; it is not rigged,")
print("and it is not guaranteed. That is the honest benchmark.\n")
# what does the expected harmful-override rate look like?
rng=np.random.default_rng(11); r=rng.normal(0,1,50000)
for nm,n_rev in (("R1_low_sso",15.21),):
    a=(MU/((n_rev*2*np.pi/86400.0)**2))**(1/3); v=np.sqrt(MU/a)
    dv=1.7/1e5; da=2*a*dv/v; dn_m=-1.5*n_rev*da/a
    print(f"{'seed sign':>10s} {'k':>8s} {'MAE_A':>8s} {'MAE_B':>8s} {'B/A':>7s} {'verdict':>7s}")
    for s in (+1.0,-1.0):
        g0=s*DN; k=(g0-dn_m)/g0
        rd=k*r; A=np.mean(np.abs(rd)); B=np.mean(np.abs(rd-r))
        print(f"{int(s):+10d} {k:8.3f} {A:8.4f} {B:8.4f} {B/A:7.3f} {'HARM' if B/A>1 else 'helps':>7s}")
