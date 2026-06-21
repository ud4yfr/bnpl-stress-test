# Affirm vs Klarna: How Much Can Delinquency Rise Before the Model Breaks?

47% of BNPL users said they paid late in the past year. Affirm's 30+ day delinquency rate is flat at 2.8% YoY. Those two numbers don't obviously reconcile, and figuring out why — and whether either company is actually close to a cliff — is what this project is about.

The short answer: Affirm has a ~5.4 percentage point buffer before its model flips to a loss. Klarna has about 1.2. Same delinquency pressure, very different exposure, and the reason comes down to product mix.

---

## What's actually being measured

Both companies originate BNPL loans, but they make money very differently. Affirm's book is 71% interest-bearing installment loans — meaning when a borrower pays late, Affirm has finance-charge revenue sitting on top of the loan that absorbs some of the hit. Klarna runs mostly Pay Later products with no interest income cushion. If a Klarna loan goes bad, the only thing covering it is the merchant fee that was collected at origination.

This model stresses both companies' retained, on-balance-sheet exposure (not total GMV — Affirm sells a meaningful chunk of loans to capital partners and doesn't hold that credit risk) and finds the net charge-off rate at which each one goes from profitable to not.

---

## Pre-flight findings

Before touching the model, I pulled the actual filings to confirm every input number.

**Affirm (FQ3 FY2026, quarter ended March 31, 2026):** Revenue $1,038.8M, GMV $11.6B, operating income $88.4M, 30+ DPD 2.8%, allowance $512.3M at 6.0% of loans held for investment — all confirmed against the 10-Q.

**Klarna correction:** The product mix I originally had was wrong. "Pay Later" (the 79% of GMV figure) is an umbrella covering three short-term products. Pay-in-4 alone is ~26% of GMV. More importantly, only ~12% of Klarna's GMV is Fair Financing — the interest-bearing, balance-sheet-retained piece that actually carries credit risk. The other 88% gets merchant fees and the receivables are sold after origination.

**Scope:** The model stresses Affirm's $8.6B loans held for investment and Klarna's $15.2B Fair Financing outstanding. Stressing total GMV for either company would conflate origination volume with retained credit risk, which are very different things.

**Klarna data caveat:** Klarna IPO'd September 2025. There's one estimated NCO data point for the Fair Financing book. The Beta distribution for Klarna uses Affirm's historical coefficient of variation as a documented proxy, with 2× wider spread to reflect data uncertainty. Klarna's results show direction, not precise magnitude.

---

## Method

Starting from each company's GAAP operating income and provision for credit losses, I compute *pre-provision income per $100 of on-balance-sheet exposure* — the income available to absorb credit losses before the company tips into a loss. I fit a Beta distribution to historical quarterly net charge-off rates (7 quarters for Affirm, derived from allowance roll-forwards; proxy for Klarna). 10,000 Monte Carlo draws per company simulate the distribution of quarterly outcomes. The breakeven NCO rate is derived analytically as the point where pre-provision income equals credit losses.

---

## Results

| | Affirm | Klarna |
|---|---|---|
| On-balance-sheet exposure | $8.6B (LHI) | $15.2B (Fair Financing) |
| Current annual NCO rate (est.) | 7.93% | 5.26% (estimated) |
| Breakeven annual NCO rate | ~13.3% | ~6.5% |
| Buffer before loss | ~5.4 pp | ~1.2 pp |
| Fragility ratio | — | ~4.3× more fragile |

![Stress test chart](outputs/bnpl_stress_test.png)

---

## So what?

Affirm needs its annual NCO rate to rise from ~7.9% to ~13.3% — a 67% increase — before it's in trouble. Its interest-bearing product mix generates $532M/quarter in finance-charge revenue that acts as a buffer. The 47% "paying late" industry statistic has not, so far, translated into the NCO trajectory that would threaten that buffer.

Klarna's situation is structurally thinner. Its Fair Financing book needs only a ~1.2 percentage-point increase in NCO rate to consume all of Klarna's adjusted operating profit. The rest of its business generates merchant fees without retained credit risk, but those fees don't cross-subsidize Fair Financing losses. The same shock hits a much smaller income base.

Both companies are currently profitable. Neither is on the immediate edge. But Klarna's margin of safety is roughly 4× smaller, and a moderate credit cycle deterioration — not a tail scenario — could flip Fair Financing into a loss. Affirm would need something more sustained.

---

## What this model doesn't capture

- **Funding cost shocks:** Klarna funds the Fair Financing book via consumer deposits (~$13B). Rising rates or deposit outflows would increase funding costs independently of NCO rates.
- **Recession tail:** The Monte Carlo reflects historical NCO variance. A macro shock could push NCOs discontinuously above anything in the historical distribution.
- **Regulatory changes:** CFPB proposals to apply credit-bureau reporting to BNPL could change borrower behavior in ways not captured by historical roll rates.
- **Growth dilution:** Rapid new originations dilute the delinquency ratio in the short term. Sustained growth can mask rising credit costs.
- **Correlation:** A macro shock would hit both companies simultaneously — the comparison assumes independent credit curves.

---

## Running it

```bash
pip install -r requirements.txt
python src/run.py
```

## Data sources

- Affirm FQ3 FY2026 8-K shareholder letter (filed May 7, 2026)
- Affirm FQ3 FY2026 10-Q (Accession 0001628280-26-032294)
- StockAnalysis.com quarterly financials (provision, LHI — cross-checked vs 10-Q)
- Klarna Q4 2025 earnings release (February 19, 2026)
- Klarna 20-F FY2025 (SEC EDGAR)
- Klarna F-1 prospectus (SEC EDGAR, March 2025)
