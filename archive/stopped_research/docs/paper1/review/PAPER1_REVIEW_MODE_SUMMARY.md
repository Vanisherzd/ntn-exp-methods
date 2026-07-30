# Paper 1 Review Mode Summary

## Overall Assessment

Likely score: 3/5, borderline / weak reject under a strict ICC/GLOBECOM workshop review. The paper is coherent as a six-page workshop paper and unusually careful about limitations, but the main positive performance story is synthetic/proxy-only while the real BLACK KITE gate always closes.

## Cross-Reviewer Consensus

- Strongest contribution: chronological evidence gate showing that learned residual correction should not deploy on the tested real TLE history.
- Main weakness: the learned/PGRL controller is not validated on real data; real deployment equals SGP4 baseline.
- Main overclaim risk: abstract and Fig. 3 can be read as practical LR-FHSS improvement even though the 90% proxy success is synthetic and not packet/link/OTA evidence.
- Hardware wording: Table IV is appropriately bounded, but the conducted-IQ check is only measurement-path sanity.
- Carrier convention: 868 MHz software and 923.2 MHz hardware are disclosed, but this distinction should be repeated near every hardware claim.

## Must-Fix Before Submission

1. Reframe the abstract around the real-data negative result and safe gate closure.
2. Mark the synthetic gate-open/PGRL gains as synthetic in the abstract, Fig. 3 caption, and nearby text.
3. Add sensitivity or justification for `F_tol = 500 Hz`; ideally show decisions/proxies at a few thresholds.
4. Align the gate metric with operational risk, or explain why MAE is sufficient despite tail-risk proxy claims.
5. State explicitly that the conducted 923.2 MHz run does not exercise Doppler correction, the evidence gate, packet decode, or OTA behavior.
6. Soften PGRL footprint claims unless the model and measurement basis are specified.
7. Replace placeholder author/affiliation metadata before submission.

## Major Concerns by Topic

### Evidence Gate

The gate logic is defensible and causal, but because it closes on every real condition, the real-data controller is just the physics baseline. The paper should present this as the result, not as a caveat.

### Table IV Hardware Sanity

The table is useful and careful. It should remain a sanity check only. Do not let it support claims about link validation, receiver success, Doppler truth, or deployment.

### Carrier Convention

The 868 MHz vs 923.2 MHz distinction is clear in Sec. IV-A, but strict reviewers may still object. Repeat the distinction in Sec. V and in any hardware-related abstract wording.

### Proxy Assumptions and `F_tol`

The proxy chain depends heavily on a 500 Hz tolerance, Gaussian residual assumptions, independence in Eq. (12), and energy model parameters. A small threshold sensitivity result would remove a major reviewer objection.

### PGRL Footprint

The footprint is plausible for Cortex-M4F-class inference, but not fully credible as an embedded result without implementation/measurement details. Treat it as an estimate.

### Six-Page Coherence

The paper is coherent but overloaded. Prioritize the negative real-data gate result and demote synthetic/PGRL/hardware material to supporting sanity checks.

### Packet/Link/OTA Claims

The manuscript mostly avoids explicit overreach. The danger is implied overreach from performance numbers and hardware proximity. The current wording should be tightened, not expanded.

## Bottom Line

The paper is close to a defensible workshop submission if it embraces the negative result. It is risky if submitted as a learned-control performance paper.
