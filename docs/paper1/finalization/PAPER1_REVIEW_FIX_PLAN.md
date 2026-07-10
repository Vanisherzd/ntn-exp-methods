# Paper 1 Review-Driven Fix Plan

Date: 2026-07-10

Scope constraints: no experiments, no hardware, no firmware flashing, no USRP
capture, no OTA, no numerical-result changes, no new claims, and hard 6 pages
including references.

## Review Files Read

- `REVIEW_A_COMMUNICATIONS.md`
- `REVIEW_B_ORBIT_ML.md`
- `REVIEW_C_HARDWARE_EMBEDDED.md`
- `REVIEW_D_META_WORKSHOP.md`
- `PAPER1_REVIEW_MODE_SUMMARY.md`

## A. Must-Fix Before Advisor/Submission

| Source | Exact concern | Proposed fix | Target file/section | Page overflow risk |
|---|---|---|---|---|
| Review D; Summary | Placeholder author/affiliation fields remain in submission-mode PDF. | Replace `Author 1 / Example University` block with clearly anonymous placeholder because target anonymity is not decided; keep finalization TODO for real authors if non-anonymous. | `paper/icc_main.tex` author block; `PAPER1_FINALIZATION_STATUS.md` blockers | Low; likely shorter. |
| Review A; Summary | `F_{\mathrm{tol}}=500` Hz is plausible but insufficiently justified and could read as receiver threshold. | Add one concise sentence: representative sub-kHz hop-bin/control tolerance proxy, not a standard receiver threshold. | `paper/icc_main.tex`, Control Proxies and Table III parameter row | Low; one sentence/phrase. |
| Review B; Summary | Gate uses MAE while operational story uses tail/outage proxies. | Add compact rationale that MAE is the gate loss because it is stable on small chronological windows; tail/outage proxies are reported after gating and do not override the deploy decision. | `paper/icc_main.tex`, Evidence Gate | Low; one sentence. |
| Review A; Review B; Review D; Summary | Synthetic/PGRL gains can read as real BLACK KITE improvement. | Ensure abstract, Fig. 2/Fig. 3 captions, synthetic subsection, endpoint proxy text all say controlled/synthetic and that real gate closes. | `paper/icc_main.tex`, Abstract, Fig. captions, Sec. Evaluation | Low; mostly word substitutions. |
| Review C; Summary | Conducted hardware check may look like validation of Doppler correction, evidence gate, packet/link/OTA behavior. | Add one compact boundary sentence that the 923.2 MHz conducted run does not exercise Doppler correction, evidence gate, packet decode, or OTA behavior. Keep Table IV compact. | `paper/icc_main.tex`, Conducted-IQ Evidence and Table IV | Low; one sentence, no table growth beyond wording. |
| Review C; Summary | 868 MHz software carrier vs 923.2 MHz hardware carrier must be repeated near hardware claim. | Repeat in hardware section that 923.2 MHz was local AS923 conducted measurement-path evidence, separate from 868 MHz software metrics. | `paper/icc_main.tex`, Conducted-IQ Evidence | Low. |
| Review B; Review C; Summary | PGRL/MCU footprint looks too strong for estimate-only evidence and 326 KB Flash is large. | Keep offline training, endpoint inference only, Cortex-M4F estimate, no M0 claim; add "Flash-feasible on mid-range MCU-class devices, not ultra-minimal nodes." | `paper/icc_main.tex`, Endpoint-Control Proxies | Low; one clause. |
| Review A; Review C; Review D; Summary | Abstract density and proximity of hardware result to proxy gains can imply packet/link validation. | Compress abstract by one sentence and keep boundaries in the same sentence as synthetic/proxy/hardware claims. | `paper/icc_main.tex`, Abstract | Low; net neutral or shorter. |
| Review A; Summary | Fig. 3 orange/PGRL bar may read as real-data performance. | Caption already says gate-open synthetic; tighten if needed to "controlled gate-open synthetic." | `paper/icc_main.tex`, Fig. `fig:proxies` caption | Low. |
| Review A; Review B; Review D; Summary | Central contribution should be negative real-data gate closure plus synthetic sanity check, not demonstrated learned LR-FHSS gain. | Preserve title, but make abstract/conclusion say real-data gate closes and synthetic is a sanity/stress check only. | `paper/icc_main.tex`, Abstract, Conclusion | Low; replacement text only. |

## B. Nice-To-Fix If Space Allows

- Review A: add threshold sensitivity at 100 Hz, 1 kHz, and 2 kHz. Not applied
  unless already available because it would change/add numerical evidence.
- Review B: report validation window sizes next to gate decisions. Not applied
  unless already present in artifacts because it may require new table space.
- Review B: define PGRL in the abstract or remove acronym. Current abstract avoids
  expanding the acronym; no edit unless space remains.
- Review B: add a compact feature list. Already present in Sec. II-B.
- Review C: clarify whether `-17 dBm` is configured output power or calibrated at
  measurement point. Apply only if wording can be done without adding evidence.
- Review D: reduce acronym density. Only opportunistic wording changes; no broad
  rewrite.
- Review D: citation/reference typography polish. Build log scan only; no optional
  references.
- Summary: figure readability adjustments. Captions only; no figure redesign.

## C. Rebuttal/Defense Only

- Review A: independence assumptions in Eq. (12) and Gaussian residual model are
  not validated against packet traces. Defend as explicitly labeled coverage
  proxies; no new experiment or claim.
- Review B: synthetic regime is too clean to establish usefulness. Defend as a
  gate sanity/stress check after tightening language.
- Review B: real-data result is negative across all staleness values. This is the
  central contribution, not a defect to hide.
- Review C: conducted-IQ evidence is thin for hardware credibility. Defend as
  deliberately bounded measurement-path sanity evidence.
- Review D: workshop outcome depends on tolerance for negative/proxy evidence.
  Address by focusing the pitch; no new evidence added.

## D. Ignore / Already Addressed

- No packet, PER/PDR/CRC, gateway ACK, OTA, live-satellite, or link-layer claim:
  already explicit in abstract, Table IV, and limitations; scan after edits.
- Keep `[7]` arXiv unless published ToSN metadata is fully verified: no reference
  metadata change planned.
- Do not reintroduce hardware figure: already removed from main paper.
- Keep Table IV as conducted-IQ sanity evidence: no removal planned.
- Do not redesign figures unless consensus says major problem: no consensus;
  captions only.
