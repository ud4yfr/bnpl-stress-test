# Phase 0 Sourced Inputs

All figures verified against primary filings. Cite this file in code via comments.

---

## Affirm Holdings (AFRM)

**Filing:** 8-K shareholder letter, FQ3 FY2026, filed May 7, 2026 (SEC EDGAR)  
**Period:** Quarter ended March 31, 2026

### Income statement / revenue (quarterly)
| Line item | Value | As % of GMV |
|-----------|-------|-------------|
| GMV | $11,600M | 100% |
| Merchant network revenue | $268.0M | 2.31% |
| Card network revenue | $66.5M | 0.57% |
| Interest income | $532.4M | 4.59% |
| Gain on sales of loans | $127.2M | 1.10% |
| Servicing income | $44.6M | 0.38% |
| **Total revenue** | **$1,038.8M** | **8.95%** |
| Revenue Less Transaction Costs (RLTC) | $498.2M | 4.30% |

### Credit metrics
| Metric | Value | Note |
|--------|-------|------|
| 30+ day delinquency | 2.8% | Monthly installment loans ex-Peloton only |
| Allowance for credit losses | $512.3M | |
| Allowance as % of LHI | 6.0% | LHI = loans held for investment |
| Gross LHI | ~$8,600M | Back-calculated: $512.3M / 6.0% |

### Product mix
| Product | % of GMV |
|---------|----------|
| Interest-bearing installment (monthly) | 71% |
| 0%-APR (Pay-in-X, short-term) | 29% |

### Balance sheet (model scope)
- **On-balance-sheet exposure (model input): $8,600M gross LHI**
- Off-balance-sheet: loans sold via forward-flow agreements and revolving ABS
  - Gain on sales Q3 FY2026: $127.2M (+68% YoY); loan sale volume +40% YoY
  - Servicing income $44.6M covers serviced-but-not-owned population

### Gap: funding cost
Affirm's explicit interest expense on held loans not yet extracted. RLTC already nets it out.
Source location: Affirm FQ3 FY2026 10-Q, interest expense line on income statement.
SEC link: https://www.sec.gov/Archives/edgar/data/0001820953/000162828026032294/afrm-20260331.htm

---

## Klarna Group (KLAR)

**Filings used:**
- Q1 2025 earnings release (April–May 2025, user-provided images)
- Q4 2025 earnings release (February 19, 2026, user-provided images)
- Klarna F-1 prospectus (SEC EDGAR, filed March 2025)
- Klarna 20-F FY2025 (SEC EDGAR, year ended December 31, 2025)

### Product mix (F-1, end of 2024)
| Product | % of GMV | Interest-bearing? | Credit risk retained? |
|---------|----------|-------------------|-----------------------|
| Pay Later umbrella (Pay in 4 + Pay in 3 + Pay in 30) | 79% | No | No — receivable sold |
| Pay in Full / Pay Now | 16% | No | No — no loan extended |
| Fair Financing (installment, up to 48 months) | 5% (2024) → ~12% (Q4'25) | Yes | Yes — held on balance sheet |

**NOTE:** CLAUDE.md states "75–79% of GMV is Pay-in-4." CORRECTION: 79% is the Pay Later
umbrella across three short-term products. Pay-in-4 alone ≈ 26% of total GMV. The core
modeling distinction — fee-only vs. interest-bearing — still holds and is actually stronger:
88% of GMV generates no interest income for Klarna.

### Income statement — Q4 2025 (most recent quarter)
| Line item | Q4 2025 | Q1 2025 | Note |
|-----------|---------|---------|------|
| GMV | $38,700M | $25,300M | |
| Fair Financing GMV | $4,500M | — | 12% of Q4'25 GMV |
| Transaction & service revenue | $743M | $519M | Merchant fees + consumer fees + advertising |
| Gain on sale of consumer receivables | $73M | — | New line; Q4'25 Fair Financing forward-flow |
| Interest income | $267M | $182M | Primarily Fair Financing |
| **Total revenue** | **$1,082M** | **$701M** | |
| Revenue take rate | 2.80% | 2.77% | % of GMV |
| Processing and servicing | ($250M) | ($164M) | |
| Provision for credit losses | ($250M) | ($136M) | |
| Funding costs — interest on funding | ($132M) | ($113M) | |
| Funding costs — fair value adj loans sold | ($78M) | — | Loss on selling Pay Later below par |
| Funding costs total | ($210M) | ($130M) | |
| **Transaction margin dollars** | **$372M** | **$271M** | |
| Adjusted operating profit | $47M | $3M | |

### Provision for credit losses time series (% of GMV — 5 quarters)
| Q4'24 | Q1'25 | Q2'25 | Q3'25 | Q4'25 |
|-------|-------|-------|-------|-------|
| 0.53% | 0.54% | 0.56% | 0.72% | 0.65% |

### Delinquency data — what exists and what doesn't
| Data type | Status | Detail |
|-----------|--------|--------|
| Aggregate 30+ DPD quarterly series | NOT AVAILABLE | Only Q2'24 vs Q2'25 one-year comparison |
| BNPL 30+ DPD (two points) | Available | 1.03% Q2'24 → 0.88% Q2'25 |
| Fair Financing 30+ DPD (two points) | Available | 2.20% Q2'24 → 2.18% Q2'25 |
| US Fair Financing vintage 30+/60+ DPD charts | Available | 2023, 2024, 2025 cohorts by origination quarter |
| US Fair Financing cumulative charge-off by vintage | Available | Q1'24–Q1'25; plateau 3.0–3.7% at 24 months |
| 30/60/90 day staging by calendar quarter | NOT AVAILABLE | Cannot fit independent roll-rate |

**Roll-rate distribution plan (requires user confirmation):**
- Fair Financing: calibrate from US vintage charge-off curves (3–3.7% lifetime loss at 24 months)
- Pay Later: use Affirm's roll-rate distribution shape as documented proxy; label as such

### Balance sheet and funding (model scope)
| Item | Value | Source |
|------|-------|--------|
| Consumer credit exposure outstanding | $15.2B | 20-F, December 31, 2025 |
| Consumer deposits (primary funding) | ~$13B | 20-F FY2025 |
| Pay Later receivables | Sold off-balance-sheet | Q4'25 CFO letter explicit |
| Fair Financing receivables | Held on balance sheet | Forward-flow offloading growing |
| Q4'25 Fair Financing forward-flow sold | $1.6B | Q4'25 CFO letter |
| Q4'25 gain on sale | $73M | Q4'25 income statement |

**Model scope:** Retain Fair Financing as primary on-balance-sheet exposure.
The $15.2B outstanding is the right denominator for expressing Klarna's credit risk.

**Comparison normalization needed:**
The 0.65% provision/GMV rate includes provisions on Pay Later loans that are sold after provisioning.
To compare with Affirm's 6.0% allowance/LHI, convert both to: credit loss as % of outstanding exposure.
Klarna equivalent: annualized provision / $15.2B outstanding = to be calculated in model.py.
