# NON-NEGOTIABLE INVARIANTS (enforced mechanically where marked [T])

I1 DEPLOYMENT CAUSALITY  [T3,T4]
  A deployed feature may use only: the stale TLE held by the terminal; the
  current transmission UTC; fixed ground-station parameters; static config known
  before transmission; frozen model parameters and gate state.
  Forbidden: later/reference TLE; the publication epoch of a later TLE; held-out
  data; a future sample index anchored to the reference epoch; any RF/downlink
  observation not assumed by the method.

I2 RETROSPECTIVE TARGET SEPARATION  [T1,T2]
  The later/reference TLE may build ONLY the retrospective target r. It must
  never enter the deployed feature vector.

I3 SAME SCIENTIFIC COHORT  [cohort diff in L3]
  Except removal of the non-deployable feature: same canonical histories,
  qualification, satellites, staleness targets/bands, chronological boundaries,
  screening thresholds, pair definition, K=24, carrier, ground station, metrics,
  gamma frontier, statistical procedures. Anything else needs a DECISIONS.md entry.

I4 HELD-OUT IMMUTABILITY  [T5]
  Held-out data may not select features, model families, penalties, screens,
  gamma, figure cases, or narrative framing.

I5 NO RESULT-PRESERVATION PRESSURE
  The old 1.94%, 3.26 mHz, IRIDIUM-181 hero case and 1/270 opening are NOT
  acceptance criteria. They may change or disappear.

I6 CLAIM/ARTIFACT CONSISTENCY
  The words "deployable", "endpoint admission", "pre-transmission" and
  "available at transmission" may be used only where the result passes the
  deployment-causality manifest.
