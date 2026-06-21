"""
Unit economics, Monte Carlo simulation, and breakeven analysis.

Core formula:
    profit_per_100_quarterly = pre_provision_income_per_100
                               - (nco_rate_annual / 4) * 100

Where:
    pre_provision_income_per_100 = (operating_income + provision) / lhi_gross * 100
    nco_rate_annual is drawn from Beta(α, β) in the Monte Carlo

Term definitions:
    pre_provision_income: operating income BEFORE deducting credit losses.
        We add provision back to reported GAAP operating income because GAAP
        already deducted it — we want to model credit losses ourselves.
    breakeven NCO rate: the annual NCO rate at which quarterly profit = 0.
        Computed analytically: breakeven = 4 * pre_provision_income_per_100 / 100
"""

from dataclasses import dataclass

import numpy as np

from src.rollrate import sample_nco_rates
from src.sourcing import CompanyInputs


@dataclass
class MonteCarloResult:
    """Output of a Monte Carlo run for one company."""
    company_name: str
    profits: np.ndarray       # quarterly profit per $100 exposure, one per simulation
    breakeven_nco: float      # annual NCO rate where profit = 0
    current_nco: float        # baseline (historical mean) annual NCO rate
    buffer_pp: float          # breakeven_nco - current_nco, in percentage points
    prob_loss: float          # fraction of simulations with negative profit
    alpha: float              # Beta distribution parameter used
    beta_param: float         # Beta distribution parameter used
    is_empirical: bool        # True if Beta fitted from primary data; False if proxy
    data_quality_note: str    # pass-through from CompanyInputs


def pre_provision_income_per_100(company: CompanyInputs) -> float:
    """
    Return quarterly pre-provision income per $100 of gross LHI.

    Pre-provision income = GAAP operating income + provision for credit losses.
    We add provision back because GAAP already subtracted it; we want to
    model the credit loss component ourselves via the Monte Carlo.

    Result is per $100 of LHI (not total dollars) so the unit economics
    equation is: profit = this_number - (nco_rate/4)*100

    Income scope: GAAP operating income includes off-balance-sheet revenue —
    gain on loan sales (~$127M/quarter) and servicing income (~$44M/quarter)
    from loans sold to capital partners. This model tests company-level
    profitability, not whether the LHI book is self-funding. The LHI-only
    breakeven (using only interest income attributable to retained loans)
    would be meaningfully lower. See README for scope decision rationale.
    """
    total_quarterly_mm = (
        company.operating_income_quarterly_mm + company.provision_quarterly_mm
    )
    return total_quarterly_mm / company.lhi_gross_mm * 100


def unit_economics(company: CompanyInputs, nco_rate_annual: float) -> float:
    """
    Return quarterly profit per $100 of gross LHI at a given annual NCO rate.

    Args:
        company:          company financial inputs
        nco_rate_annual:  annual net charge-off rate as a decimal (e.g. 0.08 = 8%)

    Returns:
        float: quarterly profit per $100 of LHI exposure
               positive = profitable, negative = loss-making

    Example:
        unit_economics(AFFIRM, 0.0793) ≈ $0.65 per $100 LHI per quarter
        (pre-provision income ~$3.32 minus quarterly NCO share ~$1.98)
    """
    income = pre_provision_income_per_100(company)
    # Quarterly credit loss per $100: annual rate / 4 seasons × $100 face value
    quarterly_credit_loss = (nco_rate_annual / 4) * 100
    return income - quarterly_credit_loss


def find_breakeven_nco_rate(company: CompanyInputs) -> float:
    """
    Return the annual NCO rate at which quarterly profit per $100 = 0.

    Derived analytically from the unit economics formula:
        0 = pre_provision_income_per_100 - (breakeven / 4) * 100
        => breakeven = 4 * pre_provision_income_per_100 / 100

    Returns:
        float: annual NCO rate (decimal) where profit = 0
    """
    income = pre_provision_income_per_100(company)
    return 4 * income / 100


def monte_carlo(
    company: CompanyInputs,
    alpha: float,
    beta_param: float,
    n_sims: int = 10_000,
    seed: int = 42,
) -> MonteCarloResult:
    """
    Run Monte Carlo simulation: draw NCO rates, compute profit distribution.

    Each draw represents one possible future annual NCO rate, sampled from
    Beta(alpha, beta_param). The resulting distribution of profits shows:
      - Where the company typically sits (median profit)
      - Tail risk (profit at 5th percentile)
      - Probability of loss (fraction of draws below zero)

    Args:
        company:    company financial inputs
        alpha:      Beta distribution parameter (fitted from history)
        beta_param: Beta distribution parameter
        n_sims:     number of Monte Carlo draws (default: 10,000)
        seed:       random seed for reproducibility

    Returns:
        MonteCarloResult with profits array and summary statistics
    """
    nco_draws = sample_nco_rates(alpha, beta_param, n=n_sims, seed=seed)
    profits = np.array([unit_economics(company, r) for r in nco_draws])

    breakeven = find_breakeven_nco_rate(company)
    prob_loss = float(np.mean(profits < 0))

    return MonteCarloResult(
        company_name=company.name,
        profits=profits,
        breakeven_nco=breakeven,
        current_nco=company.baseline_nco_rate_annual,
        buffer_pp=(breakeven - company.baseline_nco_rate_annual) * 100,
        prob_loss=prob_loss,
        alpha=alpha,
        beta_param=beta_param,
        is_empirical=company.nco_history_is_empirical,
        data_quality_note=company.data_quality_note,
    )
