set -e
cd /Users/laizhendong/Desktop/LEO-Hybrid-PGRL/experiments/exp14_multisat_generalization_matrix
OUT=outputs/deployable_v1
mkdir -p $OUT
echo "### qualification (cohort identity check)"
uv run qualify_dataset.py --out-dir $OUT > $OUT/qualify.log 2>&1
echo "### phase0 BLACK KITE"
uv run run_phase0_black_kite.py --out-dir $OUT/phase0 > $OUT/phase0.log 2>&1
echo "### phase2 screening sweep (270 = 54 primary at 1500 Hz + 4 other screens)"
uv run run_phase2_reject_sensitivity.py --qualification $OUT/dataset_qualification.json \
    --out-dir $OUT/phase2 > $OUT/phase2.log 2>&1
echo "### phase3 endpoint + gamma frontier"
uv run run_phase3_endpoint_value.py --out-dir $OUT/phase3 > $OUT/phase3.log 2>&1
echo L3_RERUN_DONE
