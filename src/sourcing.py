"""
Verified financial inputs for the BNPL Monte Carlo stress test.

Every hardcoded number is cited inline. Two data quality labels used:
  # SOURCE: [filing] [line item]
  # ESTIMATED: [methodology] — not from a primary disclosure; labeled clearly
  # PROXY: [what was substituted and why]

Do not change any number without updating the citation.
"""

from dataclasses import dataclass


@dataclass
class CompanyInputs:
    """
    All inputs to the unit economics model for one company.

    Monetary fields in millions of dollars (mm).
    Rate fields as decimals (0.08 = 8%).
    """
    name: str

    # On-balance-sheet gross loans (the stress-test exposure denominator)
    lhi_gross_mm: float

    # Most recent quarter GAAP operating income
    operating_income_quarterly_mm: float

    # Most recent quarter provision for credit losses (income statement line)
    provision_quarterly_mm: float

    # 30+ day past-due rate on the on-balance-sheet book (decimal)
    dq_rate_30plus: float

    # Historical mean annual NCO rate (decimal, weighted mean of history)
    baseline_nco_rate_annual: float

    # Time series of annual NCO rate observations used to fit the Beta.
    # For Affirm: 7 quarters derived from allowance roll-forward.
    # For Klarna: 1 estimated point. See data/affirm_nco_history.md.
    nco_rate_history: list

    # Human-readable description of what lhi_gross_mm represents
    exposure_label: str

    # Whether nco_rate_history is empirical (True) or a proxy (False)
    nco_history_is_empirical: bool = True

    # Free-text note explaining any proxy or estimation choices
    data_quality_note: str = ""


# ---------------------------------------------------------------------------
# Affirm Holdings (AFRM) — FQ3 FY2026, quarter ended March 31, 2026
# ---------------------------------------------------------------------------
AFFIRM = CompanyInputs(
    name="Affirm",

    # SOURCE: Affirm 10-Q FQ3 FY2026 (Accession 0001628280-26-032294), balance sheet.
    # StockAnalysis.com cross-check: Gross LHI $8,573M, Net LHI $8,061M,
    # implied allowance $512M = 6.00% of gross (matches 8-K shareholder letter).
    lhi_gross_mm=8_573.0,

    # SOURCE: Affirm 8-K shareholder letter FQ3 FY2026, filed May 7, 2026.
    # GAAP operating income = $88.4M; diluted EPS $0.30.
    operating_income_quarterly_mm=88.4,

    # SOURCE: StockAnalysis.com quarterly income statement, backed by Affirm 10-Q.
    # Provision for credit losses, quarter ended March 31, 2026: $196.54M.
    provision_quarterly_mm=196.54,

    # SOURCE: Affirm 8-K shareholder letter FQ3 FY2026.
    # "30+ day delinquency rate: 2.8%, flat year-over-year."
    # SCOPE: Monthly installment loans excluding Peloton — NOT the full LHI book.
    dq_rate_30plus=0.028,

    # DERIVED: Mean of nco_rate_history below. See data/affirm_nco_history.md.
    baseline_nco_rate_annual=0.0793,

    # DERIVED from allowance roll-forward (see data/affirm_nco_history.md).
    # NCO_approx = Prior_Allowance + Provision - Current_Allowance.
    # Annualized: (NCO_approx / Avg_Gross_LHI) * 4.
    # Source for provisions and LHI: StockAnalysis.com / Affirm 10-Q filings.
    nco_rate_history=[
        0.0787,  # FQ1 2025 (Sep 30, 2024)
        0.0855,  # FQ2 2025 (Dec 31, 2024)
        0.0811,  # FQ3 2025 (Mar 31, 2025)
        0.0789,  # FQ4 2025 (Jun 30, 2025)
        0.0751,  # FQ1 2026 (Sep 30, 2025)
        0.0805,  # FQ2 2026 (Dec 31, 2025) — LHI grew +21% QoQ, likely ABS consolidation; NCO proxy may overstate credit losses
        0.0754,  # FQ3 2026 (Mar 31, 2026)
    ],

    exposure_label="Gross Loans Held for Investment (on-balance-sheet)",
    nco_history_is_empirical=True,

    data_quality_note=(
        "NCO rates derived from allowance roll-forward, not directly disclosed. "
        "Understates NCO slightly (recoveries not separated). "
        "30+ DPD scoped to monthly installment loans only; NCO covers full LHI book."
    ),
)


# ---------------------------------------------------------------------------
# Klarna Group (KLAR) — Q4 2025, quarter ended December 31, 2025
# ---------------------------------------------------------------------------
# IMPORTANT: Klarna's public reporting is blended across Pay Later (off-balance-sheet
# after receivable sale) and Fair Financing (on-balance-sheet installment loans).
# This model stresses the FAIR FINANCING book only — the portion Klarna retains.
# All dollar attributions below are ESTIMATED by applying reasonable fractions to
# total company figures. None are directly disclosed by product type.
#
# Key product mix (Klarna F-1 + Q4'25 earnings):
#   Pay Later (fee-only, receivable sold): ~79% GMV, NO retained credit risk
#   Pay Now / Pay in Full: ~9% GMV, no loan extended
#   Fair Financing (installment, ≤48mo): ~12% GMV, HELD ON BALANCE SHEET
#
# Source: Klarna Q4 2025 earnings release (February 19, 2026)
#         Klarna 20-F FY2025 (SEC EDGAR)
#         Klarna F-1 prospectus (SEC EDGAR, March 2025)

KLARNA = CompanyInputs(
    name="Klarna",

    # SOURCE: Klarna 20-F FY2025, consumer credit exposure outstanding Dec 31, 2025.
    # Represents the retained Fair Financing installment book (interest-bearing,
    # funded by ~$13B consumer deposits).
    lhi_gross_mm=15_200.0,

    # SOURCE: Klarna Q4 2025 earnings release — adjusted operating profit = $47M.
    # This is total company profit; it INCLUDES Pay Later merchant fees alongside
    # Fair Financing income — Fair Financing standalone income is not separately disclosed.
    # The model uses total company profit as the income buffer against Fair Financing
    # credit losses. This is conservative: it means Fair Financing losses consume the
    # entire company P&L buffer, with no credit to Pay Later margin offsetting them.
    operating_income_quarterly_mm=47.0,

    # ESTIMATED: Total company provision = $250M (SOURCE: Klarna Q4 2025 earnings).
    # 80% attributed to Fair Financing (retained book bears the credit loss).
    # Pay Later provisions are also included in total but are recouped at sale.
    # This 80% factor is a modeling assumption, not a Klarna disclosure.
    provision_quarterly_mm=200.0,

    # SOURCE: Klarna Q4 2025 earnings release — aggregate delinquency disclosure.
    # Fair Financing 30+ DPD: 2.18% (Q2 2025; latest available aggregate point).
    # Only two data points exist: Q2 2024 (2.20%) and Q2 2025 (2.18%).
    dq_rate_30plus=0.0218,

    # ESTIMATED: Annual NCO on Fair Financing outstanding.
    # Method: (Provision_attributed_quarterly × 4) / Fair_Financing_outstanding
    # = ($200M × 4) / $15,200M = 5.26%
    # Single point estimate; no multi-quarter NCO series available.
    baseline_nco_rate_annual=0.0526,

    # PROXY: Single estimated point — cannot fit independent distribution.
    # See rollrate.py fit_beta_klarna() for the proxy methodology.
    nco_rate_history=[0.0526],

    exposure_label="Fair Financing outstanding (retained on-balance-sheet installment book)",
    nco_history_is_empirical=False,

    data_quality_note=(
        "Klarna IPO'd Sep 2025 — limited public quarterly data. "
        "NCO rate is a single estimated point from provision attribution. "
        "Beta distribution uses Affirm's coefficient of variation as proxy. "
        "All Fair Financing attributions (provision split, DPD) are estimated from "
        "blended company disclosures. Treat all Klarna outputs as illustrative. "
        "NCO estimate is provision-derived, not actual charge-off data; provision overstates NCO during book growth (CECL reserve builds). Actual charge-off rate likely lower — Klarna's true buffer may be slightly wider than modeled. "
    ),
)
