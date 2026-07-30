# Paper 1 — Citation Support Audit (v2, with source support)

_Each row: the paper's claim (quoted/abridged), the citations, why the verified
source supports it (see `PAPER1_REFERENCE_AUDIT.md` for the evidence links), and
whether narrowing is needed._

| # | Paper claim (abridged quote) | Cites | Why the source supports it | Narrow? |
|---|---|---|---|---|
| 1 | "high relative velocity … induces Doppler shifts of tens of kHz—order 20 kHz at 868 MHz and roughly 50 kHz at S-band … Doppler-rate changes that stress the physical layer" | [1] | [1] is a dedicated study of LoRa-D2S Doppler limits (OJ-COMS 2024); it quantifies LEO Doppler magnitude/rate at LoRa carriers; S-band figure is carrier scaling of the same geometry (Eq. (1) in our paper), not attributed to [1] as a measurement | No — wording already "order/roughly" |
| 2 | "LR-FHSS, characterized in Semtech's AN1200.64 note, achieves robust uplink by distributing transmit energy across a grid of narrow frequency bins" | [2] | AN1200.64 is the defining vendor characterisation of LR-FHSS modulation, hopping grid, and system performance; sentence attributes the description to the note | No |
| 3 | "in practice a stale TLE propagated open-loop by SGP4/SDP4" | [3] | Vallado 4th ed. is the standard treatment of TLE/SGP4 propagation practice | No |
| 4 | "LR-FHSS link and energy analyses quantify uplink behaviour under LEO Doppler and large device populations" | [2],[4],[5],[1] | [4] = overview + performance analysis (Commun. Mag.); [5] = D2S capacity/packet-delivery simulation (WCL); [1] = Doppler-limit analysis; [2] = vendor system-performance note. All quantify uplink behaviour under the named conditions | Optional micro-nit: [2] is a vendor characterisation rather than an independent "analysis" — grouping is descriptive, no performance number attributed; left as-is for page budget |
| 5 | "transceiver / packet-trace studies improve reception \emph{after} a transmission exists" | [6],[7] | [6] designs a D2S LR-FHSS transceiver + detector (Commun. Lett. 2023); [7] builds a receiver and evaluates real LR-FHSS packet traces (arXiv 2312.13981). Both are receiver-side, matching the sentence's scoping | No |
| 6 | "ML orbit prediction anchors learned corrections on SGP4/SDP4, targeting trajectory accuracy" | [8],[9],[10],[11] | [8] defines the anchored propagator; [9] GP correction on orbit prediction (Acta Astr. 2019); [10] differentiable SGP4 closing gap to high-precision propagation (Acta Astr.); [11] survey states the trajectory-accuracy objective of the field | No |
| 7 | "NTN and D2S uplink-policy studies motivate terminal pre-compensation and choose when to transmit from pass geometry or link scores, assuming the prediction can be trusted" | [12],[13] | TR 38.821 specifies NTN UL timing/frequency pre-compensation solutions; [13] derives uplink transmission policies from satellite trajectory information. "Assuming the prediction can be trusted" is our gap framing (not attributed to them) | No — framing clause is ours, clearly positioned |
| 8 | System Model: "Propagating this stale TLE with SGP4 gives the deployable open-loop Doppler prediction" | [8] | Direct use of the SGP4 model definition (SPACETRACK Report No. 3) | No |

## Result

**PASS.** All 8 citation groups are supported by their verified sources; no
citation carries a performance claim its source does not contain; one cosmetic
grouping note (row 4) recorded, no change required.
