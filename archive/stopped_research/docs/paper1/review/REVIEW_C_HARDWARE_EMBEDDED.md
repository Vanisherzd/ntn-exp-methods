# Review C - Hardware / Embedded Reviewer

## Recommendation

Score: 2.5/5, reject to weak reject. The conducted-IQ section is appropriately bounded, but it is too thin to carry hardware credibility beyond "the measurement path can see deterministic LR1121 transmissions." For a workshop this can remain as a sanity check, but it must not be framed as hardware validation of the proposed controller.

## Major Concerns

1. Table IV wording is mostly careful: it says conducted IQ only and explicitly excludes packet decode, PER/PDR/CRC, gateway ACK, OTA, and link validation. That is the right boundary. The concern is that the abstract mentions this result alongside the control contribution, which may make the hardware sound more supportive than it is.

2. The 923.2 MHz firmware reflashing is well disclosed, but it is disconnected from the 868 MHz software carrier used for Doppler/control metrics. The paper says residuals scale linearly with carrier frequency; still, the hardware check does not exercise Doppler pre-compensation, gate selection, frequency correction, or LR-FHSS receiver behavior.

3. The conducted setup verifies TX-ON/TX-OFF separation through 50 dB attenuation into a USRP, not packet-level operation. A strict embedded reviewer will ask what was actually modulated, whether bursts are standards-compliant, whether hop behavior is visible, and whether a reference LR-FHSS receiver could decode anything.

4. The MCU footprint statement is estimate-based. Parameters, MACs, Flash, RAM, latency, and energy are useful, but without implementation details, compiler target, quantization method, and measured current, "MCU-class" remains plausible rather than demonstrated.

5. The PGRL bar in Fig. 3 creates a credibility problem: it implies a final embedded controller yielding 90% proxy success and 11.2 mJ/success, but the real gate closes and no embedded closed-loop run is shown.

## Minor Fixes

- Rename "Preliminary Conducted-IQ Evidence" to "Conducted-IQ Measurement-Path Sanity Check" if space allows.
- In Table IV, change "near hop-grid proxy bin" to a more concrete observation or remove it; "proxy bin" is not a hardware result.
- Add the USRP sample rate, attenuation, and TX power in one compact row, already mostly present.
- State whether `-17 dBm` is configured output power or calibrated conducted power at the measurement point.
- If retaining the MCU estimate, state "estimated on Cortex-M4F-class core, not measured on this board."

## Must Fix Before Submission

- Keep Table IV, but make the hardware section a clearly bounded sanity check, not a validation pillar.
- Add one sentence in the abstract or introduction: "The conducted run does not exercise the evidence gate or Doppler correction."
- Clarify the 868 MHz vs 923.2 MHz convention in the hardware section itself, not only Sec. IV-A.
- Remove or soften any wording that implies packet, link-layer, gateway, OTA, or Doppler measurement validation.

## Overreach Check

The PDF explicitly says no packet decode, PER/PDR/CRC, gateway ACK, OTA, or link validation. That is strong. The remaining issue is proximity: placing a conducted TX visibility result next to learned-control proxy gains can make the hardware seem to validate more than it does.
