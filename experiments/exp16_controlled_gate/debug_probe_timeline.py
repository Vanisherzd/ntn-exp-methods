"""Does manoeuvre absorption destroy C2/C3? Absorption = first refresh q with
epoch(held) = t_q - S >= t_shift, i.e. t_q >= t_shift + S."""
import math
T=60.0; TR,VA,DE=0.60,0.20,0.20
t_tr_end=T*TR; t_va_end=T*(TR+VA); REFRESH=1.0   # 24 h in days
print(f"run={T}d  train[0,{t_tr_end})  validation[{t_tr_end},{t_va_end})  "
      f"freeze={t_va_end}  deployment[{t_va_end},{T})\n")
print("ABSORPTION ENABLED (v2 as written):")
print(f"{'cond':5s} {'S(h)':>5s} {'t_shift':>8s} {'t_absorb':>9s} {'dep_start':>10s} {'dep_end':>8s} {'verdict':>26s}")
for cond,t_shift in (("C2",t_tr_end+0.5*(t_va_end-t_tr_end)),("C3",t_va_end)):
    for S_h in (6.0,24.0,72.0):
        S=S_h/24.0
        t_abs=math.ceil((t_shift+S)/REFRESH)*REFRESH
        if t_abs<=t_va_end: v="FATAL: absorbed in validation"
        elif t_abs<T: v="FATAL: absorbed mid-deployment"
        else: v="ok"
        print(f"{cond:5s} {S_h:5.0f} {t_shift:8.2f} {t_abs:9.2f} {t_va_end:10.2f} {T:8.2f} {v:>26s}")
print("\n=> With absorption at the next refresh the mismatch VANISHES before or during")
print("   deployment in ALL SIX cases. C2 is not a valid protection experiment and C3")
print("   is not a valid boundary experiment. Confirmed structural conflict.\n")
print("ABSORPTION DISABLED (unreported manoeuvre -- the simplification):")
print(f"{'cond':5s} {'t_shift':>8s} {'t_absorb':>10s} {'required ordering':>44s}")
for cond,t_shift in (("C2",t_tr_end+0.5*(t_va_end-t_tr_end)),("C3",t_va_end)):
    ok = (t_tr_end < t_shift < t_va_end) if cond=="C2" else (t_va_end <= t_shift)
    print(f"{cond:5s} {t_shift:8.2f} {'never (inf)':>10s} "
          f"{'SATISFIED' if ok else 'VIOLATED':>44s}")
print(f"\nC2 validation exposure = {(t_va_end-(t_tr_end+0.5*(t_va_end-t_tr_end)))/(t_va_end-t_tr_end):.3f} (exactly 50%)")
print(f"C2 deployment exposure = 1.000    C3 deployment exposure = 1.000")
