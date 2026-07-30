# LOOP 4 — SCIENTIFIC BRANCH DETERMINATION: **BRANCH B**
All numbers from outputs/deployable_v1/. Old artifacts untouched.

## Cohort identity (I3) — PASS
270/270 cells match on satellite, staleness, screen, candidate/accepted/rejected
pair counts, reject rate, train/val/test split sizes, status — AND on every SGP4
baseline metric (val_sgp4_mae_hz, test_sgp4_mae_hz, p95, p99, outage,
block_bootstrap_days). Only model-derived values differ. Exactly as required.

## Headline counts: primary result PRESERVED
                        OLD              NEW (deployable)
primary cells            54               54
gate open (primary)      0/54             0/54     <-- preserved
screening cells          270              270
gate open (screening)    1/270            1/270

model selection counts:
  OLD  stale_age_ridge 158 | linear_bias_rate 97 | ridge 15
  NEW  age_ridge      220 | linear_age       26 | deployable_ridge 24

## THE HERO EFFECT DOES NOT SURVIVE
IRIDIUM-181 @ 8 h, 1500 Hz screen, n=633 pairs (identical pair set):

                       OLD (non-deployable)   NEW (deployable)
selected m*            stale_age_ridge        age_ridge
val improvement        +1.369 %               -0.818 %
held-out improvement   +1.944 %               -0.702 %
held-out MAE           0.16414 Hz             0.16857 Hz   (SGP4 = 0.16740)
pair win rate          0.618                  0.450
Holm-adjusted p        0.000                  1.000
sign-test p            0.000                  0.0137
bootstrap CI           [-4.1, -2.4] mHz       [+0.79, +1.58] mHz

The CI does not merely widen to include zero: it moves to the WRONG SIDE. The
deployable corrector is significantly WORSE than SGP4 here. Per-candidate
validation MAE at this cell (new run):
  zero 0.194536 | median_bias 0.194163 | mean_bias 0.194894
  linear_age 0.196241 | age_ridge 0.196127 | deployable_ridge 0.310816
Every learned candidate loses to the SGP4 zero predictor, and even the constant
median-bias reference beats all three.

CONCLUSION: the entire +1.94 % / 3.26 mHz effect was carried by t_gap_s, a
quantity the endpoint cannot observe. It was a deployment-causality artifact.

## Deployable-only landscape (54 primary cells)
val improvement > 0            : 11/54
val improvement >= +5 % (gate) :  0/54
held-out improvement > 0       :  2/54  (BK-1 @72 h +0.048 %, FLOCK-1 @168 h +0.025 %)
    both Holm p = 1.00, both block-bootstrap CI includes zero -> not detectable
median val improvement   : -0.825 %
median held-out          : -0.863 %

## The single 1/270 opening SURVIVES and is now DEPLOYABLE
IRIDIUM-177 @ 168 h, 150 Hz screen, m* = deployable_ridge:
  val +18.390 %, held-out +5.119 %, n=522, win 0.556
  Holm-adjusted p = 1.00, block-bootstrap CI INCLUDES zero
  screen discards 40.3 % of candidate pairs
  neighbours contradict it: none -2.004 %, 500 Hz -13.923 %,
                            1500 Hz -0.433 %, 3000 Hz -0.487 %
Still isolated and non-robust -- but no longer dismissible as "a non-deployable
model", which makes the screening-sensitivity argument cleaner than before.

## gamma frontier, re-derived from new per-candidate metrics
gamma  1.00  0.99  0.98  0.975  0.95  0.90
open     11     3     2      2     0     0
improve   2     0     0      0     -     -
worsen    9     3     2      2     -     -
At gamma=1.00 (any improvement admits) 11 open and 9 of them harm held-out data.
The pre-specified gamma=0.95 admits none. The margin's protective role is
sharper than in the old run.

## BRANCH B rationale
No robust deployable-only residual signal survives. Therefore:
- the old IRIDIUM value MUST NOT be reused as the hero result;
- the primary framing becomes: deployable low-capacity corrections fail BOTH
  admission AND stable learnability in this regime;
- the old fuller-feature result may appear ONLY as a clearly-marked
  retrospective attainability diagnostic -- and now has a second, stronger role:
  it is a worked example of apparent learnability produced by a feature the
  endpoint cannot have.
