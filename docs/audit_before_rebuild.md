# Audit before rebuild

The pre-rebuild branch was inspected at commit `c969433` plus its uncommitted working tree. `python3 -m src.run` executed the calculations but failed while saving a chart because the environment could not write to `outputs`; `pytest -q` reported 42 passing tests. The following findings drove the rebuild.

| Issue | Current behavior and problem | Interpretation changed? | Correction |
|---|---|---|---|
| Klarna “NCO” | Allocated 80% of company provision to Fair Financing. This was an analyst assumption, not realized NCO. | Yes | Removed as NCO; provision remains an accounting input. |
| Provision | Treated provision as charge-offs despite CECL/IFRS expected-loss and growth effects. | Yes | Labelled provision throughout; direct loss disclosures separated. |
| Klarna distribution | Used twice Affirm's CV. It was neither Klarna history nor a probability estimate. | Yes | Removed simulation and Beta fitting. |
| Affirm history | Inferred NCO from allowance change. The filing directly gives charge-offs and recoveries. | Yes | Reconciled direct quarterly NCO for the comparable quarter. |
| Scope | Company income/provision was divided by retained or Fair Financing exposure. | Yes | Main layer uses company operating income, company provision, and company consumer receivables. |
| Accounting basis | Affirm GAAP was compared to Klarna adjusted operating profit. | Yes | Main comparison uses reported operating income/profit; adjusted Klarna is only documented as a sensitivity candidate. |
| Denominator | Ending balance was used. | Yes | Uses disclosed average LHI for Affirm and beginning/ending average consumer receivables for Klarna. |
| Periods | Affirm Q3 and Klarna Q4 were mixed. | Yes | Uses March 31, 2026 for both. |
| “Roll rate” | Annual loss rates were called roll rates without delinquency transitions. | Yes | Removed `rollrate.py` and all transition claims. |
| Product mix | Claimed causality without a product-level P&L decomposition. | Yes | Retained only as context; no causal claim. |
| Cross-subsidy | README denied cross-subsidy while using company profit as a buffer. | Yes | Company-level earnings explicitly can absorb company-level losses. |
| Precision | 1.2pp and 4.3x headlines rested on allocation and mixed scope. | Yes | Replaced with scenario-based capacity ranges. |
| Public materials | CLAUDE/STATUS and development narration were public. | No, but professionalism changed | Removed them and internal planning artifacts. |
