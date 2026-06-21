# Affirm NCO History — Derived from Allowance Roll-Forward

**Method:** Net Charge-Offs ≈ Beginning Allowance + Provision − Ending Allowance

**Limitations:**
1. Does not isolate recoveries (understates NCO slightly)
2. Does not adjust for ABS/forward-flow de-recognition effects
3. ABS consolidation may cause allowance jumps unrelated to NCO
4. The 30+ DPD metric (2.8%) covers monthly installment loans only;
   NCO covers the full LHI book (including Pay-in-X short-term loans)

**Source for provision:** StockAnalysis.com quarterly income statement, backed by Affirm 10-Q filings
**Source for LHI:** StockAnalysis.com quarterly balance sheet (Gross = loans before allowance, Net = after)
**Primary filing for FQ3 2026:** Affirm 10-Q, quarter ended March 31, 2026 (Accession: 0001628280-26-032294)

| Quarter | Gross LHI ($M) | Provision ($M) | Implied NCO ($M) | Annual NCO Rate |
|---------|---------------|----------------|-----------------|-----------------|
| FQ1 2025 (Sep '24) | 6,311 → prev: 5,670 | 159.82 | 117.82 | 7.87% |
| FQ2 2025 (Dec '24) | 6,796 → prev: 6,311 | 152.98 | 139.98 | 8.55% |
| FQ3 2025 (Mar '25) | 6,630 → prev: 6,796 | 147.25 | 136.25 | 8.11% |
| FQ4 2025 (Jun '25) | 7,026 → prev: 6,630 | 156.63 | 134.63 | 7.89% |
| FQ1 2026 (Sep '25) | 7,235 → prev: 7,026 | 162.75 | 133.75 | 7.51% |
| FQ2 2026 (Dec '25) | 8,774 → prev: 7,235 | 214.15 | 161.15 | 8.05% |
| FQ3 2026 (Mar '26) | 8,573 → prev: 8,774 | 196.54 | 163.54 | 7.54% |

Annual NCO rates: [0.0787, 0.0855, 0.0811, 0.0789, 0.0751, 0.0805, 0.0754]
Mean: 7.93% | Std: 0.357%
Beta(α=454, β=5274) fitted via method of moments
