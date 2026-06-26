# Commit Plan — Conducted IQ Evidence Campaign

**Do not auto-commit.** This is a plan; run the commands when ready.
Prior commit `11d6725` already landed the initial bring-up tooling, recovered firmware,
deterministic patch, and board inventory. The commits below cover the work added since.

Never stage: raw IQ `*.npy`, `*.fc32`, `*.cfile`, board flash-dump `*.bin`, `build/`,
`tmp/`, `output/`. (All are gitignored; the `git add` directory forms below exclude them
automatically — verified: 28 `.npy` ignored.)

---

## Commit A — hardware bring-up tooling + report updates
```bash
git add \
  HARDWARE_BRINGUP_MASTER_REPORT.md \
  VALIDATION_STATUS_FOR_SLIDES.md \
  scripts/analyze_conducted_iq_artifact_masked.py \
  scripts/extract_conducted_iq_peaks.py \
  hardware_conducted_iq/board_inventory/board_B_flash_9232_20260626_002829/
git commit -m "hardware: artifact-masking + hop-peak tooling and Board B flash/serial verification logs"
```

## Commit B — deterministic 923.2 MHz conducted IQ evidence
```bash
# success runs (post-reflash, TX-ON visible) — raw .npy auto-excluded by .gitignore
git add \
  hardware_conducted_iq/20260626_003643_gain20_50db/ \
  hardware_conducted_iq/20260626_010100_gain20_50db/ \
  hardware_conducted_iq/20260626_011318_gain20_50db/ \
  hardware_conducted_iq/20260626_012205_gain20_50db/ \
  hardware_conducted_iq/20260626_013014_gain20_50db/ \
  hardware_conducted_iq/repeatability_summary.md hardware_conducted_iq/repeatability_summary.csv \
  hardware_conducted_iq/overflow_sanity_summary.md \
  hardware_conducted_iq/before_after_reflash_summary.md hardware_conducted_iq/before_after_reflash_summary.csv \
  hardware_conducted_iq/latest_summary.md \
  hardware_conducted_iq/MANIFEST.md hardware_conducted_iq/CAMPAIGN_SUMMARY.md
# pre-reflash negative-control runs (868 MHz; figures/json/md only, .npy excluded)
git add \
  hardware_conducted_iq/20260625_221658_gain0_60db/ hardware_conducted_iq/20260625_221658_gain10_60db/ \
  hardware_conducted_iq/20260625_221658_gain20_60db/ \
  hardware_conducted_iq/20260625_223023_gain0_50db/ hardware_conducted_iq/20260625_223023_gain10_50db/ \
  hardware_conducted_iq/20260625_223023_gain20_50db/ \
  hardware_conducted_iq/20260625_224417_debug_scan_50db/ hardware_conducted_iq/20260625_205839/
git commit -m "hardware: conducted IQ-level TX-ON evidence at 923.2MHz (repeatability, sanity, artifact-masked, before/after control)"
```

## Commit C — paper / slides figure + text updates
```bash
git add \
  hardware_conducted_iq/figures/ \
  PAPER_HARDWARE_EVIDENCE_TEXT.md \
  COMMIT_PLAN.md
git commit -m "paper: conducted IQ-level hardware evidence figures and paste-ready text"
```

## NOT part of this campaign (operator's separate decision)
The following are pre-existing untracked items unrelated to the conducted-IQ campaign;
review and commit separately if desired:
`paper/slides_overview.*`, `paper/slide_figures/`, `paper/assets_external/`,
`paper/figures/*.pdf`, `paper/figures/generate_slide_evidence_figures.py`,
`paper/nthu_logo.png`. (`output/`, `tmp/` stay untracked.)

## Verification done
- `python -m py_compile scripts/*.py` → all OK.
- `--help` on `analyze_conducted_iq_artifact_masked.py` and `extract_conducted_iq_peaks.py` → OK (hardware-safe; argparse exits before any device/IO).
- `git check-ignore` → all `*.npy` and the flash `*.bin` ignored.
