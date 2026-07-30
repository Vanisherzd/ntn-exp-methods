# Review A - Communications / PHY Reviewer

## Recommendation

Score: 3/5, weak reject / borderline. The topic fits an ICC/GLOBECOM workshop on NTN IoT, LR-FHSS, and Doppler-aware endpoint control, but the communications evidence is mostly proxy-level and the positive result is synthetic. I would not accept without tightening the framing and making the real-data negative result the central contribution.

## Major Concerns

1. The evidence gate closes for every real BLACK KITE condition, so the actual deployed controller on real data is the SGP4 baseline. This is honest, but it weakens the communications contribution: the only regime with large improvement is synthetic, and the paper must not let Fig. 3(c,d) read as a demonstrated LR-FHSS gain.

2. The use of `F_tol = 500 Hz` is plausible as a hop-bin/control tolerance proxy, but it is not tied tightly enough to LR-FHSS receiver behavior, acquisition, oscillator error, or standard parameters. Since many headline proxy success values depend on this threshold, reviewers will ask why 500 Hz is the right tolerance and how the conclusion changes at 100 Hz, 1 kHz, and 2 kHz.

3. The paper repeatedly says the metrics are not packet, BER, PER/PDR, CRC, gateway ACK, or OTA results, which is good. However, the abstract still says proxy success moves from `<1%` to `~90%`; without the synthetic qualifier in the same sentence, that can sound like a communications-layer result.

4. The proxy chain mixes timing guard, hop-bin miss, and energy per successful burst into a clean story, but independence assumptions in Eq. (12) and the Gaussian residual model are not validated against LR-FHSS demodulation or packet traces. This is acceptable for a workshop if called a design sketch; it is not yet a PHY validation.

5. The 868 MHz software carrier vs 923.2 MHz conducted-IQ hardware carrier convention is stated clearly in Sec. IV-A. Still, this is reviewer-sensitive: the paper should emphasize that 923.2 MHz evidence verifies only local transmit observability and not the 868 MHz Doppler-control results.

## Minor Fixes

- Add a one-line sensitivity table or sentence for `F_tol` showing whether the gate decision and proxy conclusions change.
- In the abstract, change the proxy-success sentence so "synthetic gate-open regime" precedes the numerical improvement.
- Avoid "viable endpoint" wording unless immediately tied to proxy-only evidence.
- In Fig. 3 caption, make the orange PGRL bar impossible to read as real-data performance.
- State whether oscillator offset is included in the real-data proxy or only modeled in the system equation.

## Must Fix Before Submission

- Reframe the central contribution as "safe rejection of unsupported learning on real TLE data plus a synthetic sanity check that the gate can open," not as a demonstrated learned LR-FHSS improvement.
- Justify or sensitivity-test `F_tol = 500 Hz`.
- Put "no packet/link/OTA validation" near every high-gain proxy claim, including the abstract and Fig. 3.
- Ensure all claims involving energy/success say "proxy" and not measured energy or measured packet success.

## Overreach Check

The current PDF mostly avoids direct packet/link/OTA overclaiming, especially in Table IV and the conclusion. The remaining risk is implied overreach: the abstract and Fig. 3 can be read as a practical communications gain even though the real-data gate is always closed and the positive gain is synthetic.
