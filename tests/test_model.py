"""Tests for unit economics, breakeven, and Monte Carlo."""

import numpy as np
import pytest

from src.sourcing import AFFIRM, KLARNA, CompanyInputs
from src.rollrate import fit_beta_mle, fit_beta_klarna
from src.model import (
    pre_provision_income_per_100,
    unit_economics,
    find_breakeven_nco_rate,
    monte_carlo,
    MonteCarloResult,
)


# --- Unit economics ---

def test_pre_provision_income_positive_affirm():
    income = pre_provision_income_per_100(AFFIRM)
    assert income > 0


def test_pre_provision_income_positive_klarna():
    income = pre_provision_income_per_100(KLARNA)
    assert income > 0


def test_unit_economics_zero_nco_equals_pre_provision():
    """At NCO=0, all income is profit (no credit losses)."""
    income = pre_provision_income_per_100(AFFIRM)
    profit = unit_economics(AFFIRM, nco_rate_annual=0.0)
    assert abs(profit - income) < 1e-9


def test_unit_economics_at_breakeven_nco_is_zero():
    """Profit should be ~0 at the breakeven NCO rate."""
    breakeven = find_breakeven_nco_rate(AFFIRM)
    profit = unit_economics(AFFIRM, nco_rate_annual=breakeven)
    assert abs(profit) < 1e-9


def test_unit_economics_above_breakeven_negative():
    """Profit should go negative for NCO rates above breakeven."""
    breakeven = find_breakeven_nco_rate(AFFIRM)
    profit = unit_economics(AFFIRM, nco_rate_annual=breakeven + 0.01)
    assert profit < 0


def test_unit_economics_below_breakeven_positive():
    breakeven = find_breakeven_nco_rate(AFFIRM)
    profit = unit_economics(AFFIRM, nco_rate_annual=breakeven - 0.01)
    assert profit > 0


# --- Breakeven ---

def test_affirm_breakeven_above_current():
    """Affirm's breakeven should be above its current NCO rate (company is profitable)."""
    breakeven = find_breakeven_nco_rate(AFFIRM)
    assert breakeven > AFFIRM.baseline_nco_rate_annual


def test_klarna_breakeven_above_current():
    """Klarna's breakeven should also be above current (profitable at baseline)."""
    breakeven = find_breakeven_nco_rate(KLARNA)
    assert breakeven > KLARNA.baseline_nco_rate_annual


def test_klarna_buffer_smaller_than_affirm():
    """
    Klarna should have a smaller buffer to breakeven than Affirm.
    This is the core thesis: Klarna is more fragile.
    """
    affirm_buffer = find_breakeven_nco_rate(AFFIRM) - AFFIRM.baseline_nco_rate_annual
    klarna_buffer = find_breakeven_nco_rate(KLARNA) - KLARNA.baseline_nco_rate_annual
    assert klarna_buffer < affirm_buffer


# --- Monte Carlo ---

def test_monte_carlo_returns_result():
    a, b = fit_beta_mle(AFFIRM.nco_rate_history)
    result = monte_carlo(AFFIRM, a, b, n_sims=1000, seed=42)
    assert isinstance(result, MonteCarloResult)


def test_monte_carlo_profits_shape():
    a, b = fit_beta_mle(AFFIRM.nco_rate_history)
    result = monte_carlo(AFFIRM, a, b, n_sims=1000, seed=42)
    assert result.profits.shape == (1000,)


def test_monte_carlo_median_profit_positive_at_current():
    """Affirm at current NCO distribution should have mostly positive outcomes."""
    a, b = fit_beta_mle(AFFIRM.nco_rate_history)
    result = monte_carlo(AFFIRM, a, b, n_sims=10_000, seed=42)
    assert np.median(result.profits) > 0


def test_monte_carlo_prob_loss_affirm_very_low():
    """Affirm is far from breakeven — nearly zero probability of loss in historical range."""
    a, b = fit_beta_mle(AFFIRM.nco_rate_history)
    result = monte_carlo(AFFIRM, a, b, n_sims=10_000, seed=42)
    assert result.prob_loss < 0.05  # less than 5% chance of loss at historical rates


def test_monte_carlo_klarna_higher_prob_loss():
    """Klarna should show higher (though still low) probability of loss."""
    a_afrm, b_afrm = fit_beta_mle(AFFIRM.nco_rate_history)
    a_klar, b_klar = fit_beta_klarna(a_afrm, b_afrm, KLARNA.baseline_nco_rate_annual)
    result = monte_carlo(KLARNA, a_klar, b_klar, n_sims=10_000, seed=42)
    # Klarna's buffer is thinner, so prob_loss should exceed Affirm's
    a_afrm2, b_afrm2 = fit_beta_mle(AFFIRM.nco_rate_history)
    result_afrm = monte_carlo(AFFIRM, a_afrm2, b_afrm2, n_sims=10_000, seed=42)
    assert result.prob_loss >= result_afrm.prob_loss


def test_monte_carlo_reproducible():
    a, b = fit_beta_mle(AFFIRM.nco_rate_history)
    r1 = monte_carlo(AFFIRM, a, b, n_sims=100, seed=7)
    r2 = monte_carlo(AFFIRM, a, b, n_sims=100, seed=7)
    np.testing.assert_array_equal(r1.profits, r2.profits)
