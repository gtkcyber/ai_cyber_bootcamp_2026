---
name: ds-domain-finance
description: "Domain overlay for finance tasks (return/price forecasting and strategy backtesting, credit-risk/default modeling, financial-statement/fundamentals analysis, market/portfolio risk estimation): states only the finance-specific deltas on non-stationarity severity, backtest overfitting, survivorship and look-ahead bias…"
---

# ds-domain-finance

## Subfields

- **Return/price forecasting and strategy backtesting** — trigger:
  "backtest this strategy," "forecast returns," time-ordered market/price
  data.
- **Credit risk / default modeling** — trigger: "probability of default,"
  "credit scoring," loan- or firm-level data with an origination-to-outcome
  window.
- **Financial statement / fundamentals analysis** — trigger: XBRL-tagged
  filings, restated financials, "financial ratios," fundamentals-based
  screens.
- **Market/portfolio risk estimation** — trigger: "VaR," "expected
  shortfall," "worst-case loss," tail risk on a return series.

## Deltas

- **Non-stationarity severity** — general treatment: the *degree* of
  non-stationarity, not just its presence, governs which methods stay
  valid") · domain delta: financial series (returns, spreads, volatility)
  shift regime characteristics — volatility clustering, mean/variance level
  — across market regimes (pre/post crisis, rate-cycle turns) faster and
  more severely than most series the general treatment generalizes over
  (regime-switching formalized in Hamilton 1989, "A New Approach to the
  Economic Analysis of Nonstationary Time Series and the Business Cycle,"
  Econometrica 57(2):357-384 — discrete shifts in a series' growth-rate
  parameters modeled as a recurrent, estimable feature, not noise; confirmed
  via IDEAS/RePEc bibliographic record, 4410+ citing works). State the
  regime-boundary dates and the severity (mild drift vs. a regime break)
  explicitly; a model tolerant of macro-series-level drift can silently fail
  on equity-volatility-series-level regime breaks.
- **Backtest overfitting** — general treatment: repeatedly tuning method or
  hyperparameters against the same rolling-origin windows inflates the
  reported metric via multiple testing over a fixed set of origins") ·
  domain delta: strategy backtests are especially exposed because the same
  finite historical market history is reused across every candidate
  strategy/parameter set an entire research effort tests, not just one
  analyst's iterations — the effective trial count is organizational, not
  per-model (Bailey, Borwein, López de Prado & Zhu 2014, "Pseudo-
  Mathematics and Financial Charlatanism: The Effects of Backtest
  Overfitting on Out-of-Sample Performance," Notices of the AMS
  61(5):458-471 — fetched from the journal's own hosted PDF; author-
  affiliated links embedded in the file corroborate authorship, full prose
  not cleanly extracted in this pass, re-verify a specific figure before
  citing it). Report the number of configurations evaluated against this
  history alongside the backtest metric; a performance number with no stated
  trial count is unverifiable.
- **Fat tails** — general treatment: peaks-over-threshold/generalized Pareto
  tail/extreme-value estimation, with threshold choice stated as a
  bias-variance tradeoff · domain delta: financial returns carry heavier
  tails than a Gaussian assumption predicts — large moves cluster and occur
  far more often than a normal-distribution model implies (Cont 2001,
  "Empirical properties of asset returns: stylized facts and statistical
  issues," Quantitative Finance 1(2):223-236 — confirmed via IDEAS/RePEc
  bibliographic record, DOI 10.1080/713665670, abstract covers
  distributional and tail properties, extreme fluctuations, and
  linear/nonlinear dependence across a wide variety of markets). A risk
  figure (VaR, expected shortfall, worst-case loss) built on a Gaussian or
  thin-tailed assumption systematically understates extreme-loss
  probability; use the owner's tail-estimation machinery rather than a
  symmetric-interval assumption, and state the chosen threshold's tradeoff
  per that subfield's own edge.
- A point-in-time-correct universe reconstructs index membership and
  delisting status as they stood on each historical date, never as they
  stand today (Brown, Goetzmann, Ibbotson & Ross 1992, "Survivorship Bias in
  Performance Studies," The Review of Financial Studies 5(4):553-580 —
  confirmed via IDEAS/RePEc bibliographic record, handle
  RePEc:oup:rfinst:v:5:y:1992:i:4:p:553-80; abstract identifies
  survivorship-truncated samples as the mechanism generating spurious return
  predictability, the seminal result behind this delta). Separately, a
  factor computed on point-in-time-incorrect fundamentals — today's
  post-restatement earnings joined to a historical price — is look-ahead
  bias, the specific finance failure mode `ds-pipelines`' point-in-time
  reconstruction subfield (below) exists to prevent.
- **Vendor restatement cadence** — general treatment: source data revises or
  arrives after initial load, handled via date-range validity rather than a
  current-record flag; as-of joins retrieve the latest value at-or-before
  the event timestamp") · domain delta: financial data vendors restate
  fundamentals (earnings, revenue) on a cadence driven by filing amendments
  and vendor reprocessing, not a fixed schedule — a quarter's reported
  figures can change months after the original filing. The as-of join must
  pin to the vendor's as-reported-at-the-time snapshot, never the vendor's
  current (restated) value, or point-in-time reconstruction silently
  reintroduces look-ahead bias through a "corrected" data feed.

## Standards catalog

Seeds for `ds-data-models` Research, not ceilings — confirm producer
version/dialect against the actual feed before relying on any entry.

- **FIX** (Financial Information eXchange) — real-time electronic trading
  messaging protocol; governs order/execution messages. Producer: FIX
  Trading Community, fixtrading.org. Version/dialect varies heavily by
  venue and counterparty (4.2/4.4/5.0 SP2/FIXT plus custom tags) — confirm
  the actual version against the counterparty's rules of engagement, never
  assume a default dialect.
- **ISO 20022** — single standardization methodology, process, and message
  repository for financial-industry data exchange (payments, securities,
  FX); SWIFT is the Registration Authority. Producer: iso20022.org, a
  nine-part current message scheme. The producer site returned a
  persistent live-fetch error when this catalog was compiled; confirmed
  instead via a Wayback Machine snapshot — re-verify against the live site
  with a non-automated fetch before pinning a version.
- **XBRL** (eXtensible Business Reporting Language) — open standard for
  tagging business/financial-report data for machine extraction. Producer:
  XBRL International, xbrl.org. Reporting-specific taxonomies (dictionaries)
  are versioned separately by each standards-setter on top of the shared
  grammar — confirm which taxonomy version a given filing was tagged
  against; never assume the current taxonomy applies to a historical
  filing.

### Equity-returns forecasting backtest with restatement-aware reconstruction

1. `ds-scoping` — task card, including `split_design`: this overlay's
   non-stationarity delta makes the initial split design load-bearing — a
   random split leaks future regimes into training and papers over the
   regime breaks a temporally-ordered split would expose.
2. `ds-data-models` — Attest register on vendor fundamentals fields,
   distinguishing as-reported-at-the-time values from restated values;
   fingerprints fields against the FIX/XBRL catalog above,
   `data-models.semantic_dictionary`.
3. `ds-gather` — join gate across price and fundamentals feeds;
   `sampling_bias_note` names the survivorship exposure in the equity
   universe under this overlay's survivorship delta, `gather.data_contract`.
4. `ds-pipelines` — point-in-time reconstruction of vendor fundamentals
   pinned to the as-reported-at-the-time snapshot, under this overlay's
   restatement-cadence delta.
5. `ds-causal` — identification statement addressing the survivorship
   selection mechanism's consequences for the return estimate (cross-family
   schema).
6. `ds-timeseries` — rolling-origin backtest protocol; framing note flags
   this overlay's non-stationarity-severity and backtest-overfitting
   pitfalls explicitly, `timeseries.pitfall_checklist` (family-skill
   schema).
7. `ds-uncertainty` — tail/extreme-value estimation on the backtest return
   distribution under this overlay's fat-tails delta (cross-family schema).
8. `ds-evaluate` — scorecard reporting the backtest metric as a distribution
   across origins, with the trial count from step 6 stated alongside it.

### Survivorship-corrected credit-risk universe

Quick-answer tier.

1. `ds-gather` — `sampling_bias_note` names the survivorship exposure: a
   borrower/firm universe drawn from currently-active accounts silently
   excludes defaulted, charged-off, and paid-off-and-exited accounts,
   biasing the retained universe toward better credit quality under this
   overlay's survivorship delta.
2. `ds-data-models` — Attest register on the borrower financial-statement
   fields, disaggregating as-reported-at-origination values from
   current/restated values per record-type discriminator, under this
   overlay's restatement-cadence delta.
3. `ds-communicate` — reports the default-rate figure against the
   survivorship-corrected population statement
   (`data-models.population_statement`), never against the
   survivorship-biased retained-account universe.

## Gates

- No delta bullet restates owner content beyond naming it — re-deriving
  owner content fails overlay scope.

## Edges

Covered: the five deltas above and the two worked compositions.
