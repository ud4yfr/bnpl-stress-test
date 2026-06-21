# BNPL Stress Test — Session Status

**Last updated:** 2026-06-21  
**Current phase:** Phase 0 complete, Phase 1 pending confirmation

---

## Phase 0: Pre-Flight — COMPLETE

All four checks done. Findings below. User to confirm before Phase 1 build starts.

### Check 1: Affirm baseline numbers — CONFIRMED

Source: Affirm FQ3 FY2026 8-K shareholder letter, filed May 7, 2026 (SEC EDGAR)

| Metric | CLAUDE.md | Verified | Match |
|--------|-----------|----------|-------|
| Revenue | $1.04B, +33% | $1,038.8M, +33% | ✓ |
| GMV | $11.6B, +35% | $11.6B, +35% | ✓ |
| GAAP operating profit / EPS | operating profit, $0.30 | $88.4M op. income, $0.30 EPS | ✓ |
| 30+ DPD | 2.8%, flat YoY | 2.8% (monthly installment ex-Peloton) | ✓ with caveat |
| Allowance | $512M, 6.0% of LHI | $512.3M, 6.0% of $8.6B gross LHI | ✓ |
| Product mix | 72% interest-bearing (FY2025) | 71% FQ3'26 (timing diff, not error) | ✓ |

**Caveat:** The 2.8% delinquency is measured on monthly installment loans only, excluding
Peloton loans and Pay-in-X (short-term 0%-APR) loans. This scoping must carry into the model.

**Revenue breakdown (FQ3 FY2026):**
- Merchant network revenue: $268.0M (2.31% of GMV)
- Card network revenue: $66.5M (0.57% of GMV)
- Interest income: $532.4M (4.59% of GMV)
- Gain on sales of loans: $127.2M (1.10% of GMV)
- Servicing income: $44.6M (0.38% of GMV)
- **Total RLTC: $498.2M**

**Balance sheet:** Gross loans held for investment = $8.6B

**Gap:** Affirm explicit funding cost (interest expense on held loans) not yet extracted.
RLTC is known. Will source from 10-Q at Phase 1 start.

---

### Check 2: Klarna model inputs — SOURCED

Sources: Klarna Q1 2025 earnings release; Klarna Q4 2025 earnings release (user-provided);
Klarna F-1 prospectus (SEC EDGAR); Klarna 20-F FY2025 (SEC EDGAR partial)

**Revenue breakdown (Q4 2025, most recent quarter):**
- Transaction and service revenue: $743M (69% of total)
- Gain on sale of consumer receivables: $73M (7%) — new forward-flow line
- Interest income: $267M (25%)
- **Total: $1,082M** | Revenue take rate: 2.80% of $38.7B GMV

**Transaction costs (Q4 2025):**
- Processing and servicing: $250M (0.65% of GMV)
- Provision for credit losses: $250M (0.65% of GMV)
- Funding costs: $210M total
  - Interest costs on funding: $132M (0.34% of GMV)
  - Fair value adj on loans sold: ($78M) loss (0.20% of GMV) — cost of selling Pay Later below par
- Transaction margin: $372M

**Provision for credit losses — 5-quarter time series (% of GMV):**

| Q4'24 | Q1'25 | Q2'25 | Q3'25 | Q4'25 |
|-------|-------|-------|-------|-------|
| 0.53% | 0.54% | 0.56% | 0.72% | 0.65% |

**Klarna product mix (F-1, end of 2024):**
- Pay Later (umbrella: Pay in 4 + Pay in 3 + Pay in 30): 79% of GMV
- Pay in Full / Pay Now: 16% of GMV
- Fair Financing (interest-bearing installment): 5% of GMV (2024), growing to ~12% by Q4 2025

**CORRECTION vs CLAUDE.md:** CLAUDE.md states "75–79% of GMV is Pay-in-4." This is wrong.
79% is the full Pay Later *umbrella* (three products). Pay-in-4 alone ≈ 26% of GMV.
For credit modeling purposes, the key distinction is: ~12% Fair Financing (interest-bearing,
Klarna bears credit risk) vs. ~88% Pay Later + Pay Now (fee-only products, receivable sold off).

**US revenue share:** $399M of $1,012M in Q1 2026 = ~39% of revenue (aligns with CLAUDE.md's
"roughly one-third" directionally; US GMV is only 21% of total GMV, but higher revenue/GMV ratio).

**Consumer credit exposure:** $15.2B outstanding as of December 31, 2025 (20-F)
**Consumer deposits:** $13B (primary funding source for on-balance-sheet book)

---

### Check 3: Klarna delinquency-stage data — DOCUMENTED

**Available:**
1. Aggregate delinquency (one year-over-year pair, Q2 2024 vs Q2 2025 only):
   - BNPL 30+ DPD: 1.03% → 0.88%
   - Fair Financing 30+ DPD: 2.20% → 2.18%
2. US Fair Financing vintage charts (Q4 2025 earnings, page 6):
   - 30+ DPD and 60+ DPD by cohort quarter (2023, 2024, 2025 vintages)
   - 30+ DPD peaks ~3.3–3.5% for 2023/2024 cohorts at Q2–Q3 of maturation
3. US Fair Financing cumulative charge-off by vintage (months since origination):
   - Cohorts: Q1'24, Q2'24, Q3'24, Q4'24, Q1'25
   - 2024 cohorts plateau at 3.0–3.7% cumulative at 24 months
   - Q1'25 cohort: ~1% at 8 months (still maturing)
4. Provision for credit losses % of GMV: 5 quarters (see table above)

**NOT available:**
- Multi-quarter aggregate 30/60/90-day delinquency time series
- Pay Later (BNPL) delinquency staging by bucket
- Global (non-US) Fair Financing staging

**Consequence:** Cannot independently fit an empirical roll-rate distribution for Klarna
from public data. Phase 1 plan:
- Fair Financing: use US vintage charge-off curves (3–3.7% at 24 months) to calibrate
- Pay Later: use Affirm's roll-rate distribution shape as explicit, labeled proxy
- Document limitation in model and README

---

### Check 4: On-balance-sheet scope — RESOLVED

**Affirm:**
- Model exposure = $8.6B gross LHI (retained on-balance-sheet)
- Loans sold via forward-flow and ABS (Gain on Sales $127.2M, loan volume +40% YoY)
- All delinquency and allowance metrics already on LHI basis → inputs align

**Klarna (MAJOR STRUCTURAL FINDING):**
- **Pay Later (79% of GMV):** Klarna SELLS the consumer receivable, retains merchant fee.
  → Pay Later credit risk is transferred off-balance-sheet. Klarna has minimal LHI exposure here.
- **Fair Financing (~12% of GMV):** Held on balance sheet (funded by deposits), with forward-flow
  offloading growing — $1.6B sold in Q4 2025 alone, recording $73M gain.
- Model exposure = retained Fair Financing, primary component of the $15.2B outstanding book
- The 0.65% provision/GMV rate is a blended number including provisions on Pay Later before sale;
  it overstates the credit cost on the retained book.

**Comparison problem (Phase 1 must solve):**
- Affirm: 2.8% 30+ DPD and 6.0% allowance both expressed as % of LHI stock
- Klarna: 0.65% provision as % of GMV flow — different denominator entirely
- Must convert to common basis (credit loss as % of outstanding exposure) before any comparison

---

## Phase 1: Pending User Confirmation

**Decision requested:** Confirm Phase 0 findings and approach before build starts.

**Phase 1 will cover:**
1. Source Affirm funding cost from 10-Q (one remaining data gap)
2. Write full task plan: sourcing.py → rollrate.py → model.py → plot.py → run.py
3. Build with TDD-style verification at each calculation step
4. Teaching checkpoints as per CLAUDE.md protocol

---

## Project Structure

```
/Users/uday/Desktop/BNPL/
  CLAUDE.md           — locked spec
  STATUS.md           — this file
  README.md           — not yet written (Phase 1+)
  requirements.txt    — not yet written (Phase 1)
  data/               — empty, Phase 1 will populate
  src/                — empty, Phase 1 will populate
  notebooks/          — empty, Phase 1 will populate
```
