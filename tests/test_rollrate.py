"""Tests for Beta distribution fitting and sampling."""

import numpy as np
import pytest
from scipy.stats import beta as scipy_beta

from src.rollrate import (
    fit_beta_mle,
    fit_beta_moments,
    fit_beta_klarna,
    sample_nco_rates,
)
from src.sourcing import AFFIRM, KLARNA


def test_fit_beta_mle_returns_tuple():
    a, b = fit_beta_mle(AFFIRM.nco_rate_history)
    assert isinstance(a, float)
    assert isinstance(b, float)


def test_fit_beta_mle_alpha_positive():
    a, b = fit_beta_mle(AFFIRM.nco_rate_history)
    assert a > 0
    assert b > 0


def test_fit_beta_mle_mean_matches_data():
    """Fitted Beta mean should be close to sample mean of input data."""
    a, b = fit_beta_mle(AFFIRM.nco_rate_history)
    fitted_mean = a / (a + b)
    sample_mean = float(np.mean(AFFIRM.nco_rate_history))
    assert abs(fitted_mean - sample_mean) < 0.002  # within 0.2 percentage points


def test_fit_beta_moments_recovers_inputs():
    """Method-of-moments should produce a distribution with the given mean/std."""
    mean, std = 0.0793, 0.00357
    a, b = fit_beta_moments(mean, std)
    assert abs(a / (a + b) - mean) < 1e-6
    fitted_std = (a * b / ((a + b) ** 2 * (a + b + 1))) ** 0.5
    assert abs(fitted_std - std) < 1e-4


def test_fit_beta_moments_rejects_invalid():
    """std² must be < mean*(1-mean) for Beta to be valid."""
    with pytest.raises(ValueError, match="variance"):
        fit_beta_moments(mean=0.5, std=0.6)  # variance > mean*(1-mean)


def test_klarna_proxy_mean_preserved():
    """Klarna proxy Beta should be centered at Klarna's mean NCO rate."""
    a_afrm, b_afrm = fit_beta_mle(AFFIRM.nco_rate_history)
    a_klar, b_klar = fit_beta_klarna(a_afrm, b_afrm, KLARNA.baseline_nco_rate_annual)
    fitted_mean = a_klar / (a_klar + b_klar)
    assert abs(fitted_mean - KLARNA.baseline_nco_rate_annual) < 0.001


def test_klarna_proxy_wider_than_affirm():
    """Klarna proxy should have higher uncertainty (wider relative std) than Affirm's
    empirical fit, because we only have one data point."""
    a_afrm, b_afrm = fit_beta_mle(AFFIRM.nco_rate_history)
    a_klar, b_klar = fit_beta_klarna(a_afrm, b_afrm, KLARNA.baseline_nco_rate_annual)

    affirm_cv = (a_afrm * b_afrm / ((a_afrm + b_afrm) ** 2 * (a_afrm + b_afrm + 1))) ** 0.5
    affirm_cv /= (a_afrm / (a_afrm + b_afrm))

    klarna_cv = (a_klar * b_klar / ((a_klar + b_klar) ** 2 * (a_klar + b_klar + 1))) ** 0.5
    klarna_cv /= (a_klar / (a_klar + b_klar))

    assert klarna_cv >= affirm_cv


def test_sample_nco_rates_shape():
    a, b = fit_beta_mle(AFFIRM.nco_rate_history)
    samples = sample_nco_rates(a, b, n=1000, seed=42)
    assert samples.shape == (1000,)


def test_sample_nco_rates_in_unit_interval():
    a, b = fit_beta_mle(AFFIRM.nco_rate_history)
    samples = sample_nco_rates(a, b, n=10_000, seed=42)
    assert samples.min() >= 0
    assert samples.max() <= 1


def test_sample_nco_rates_mean_close_to_fitted():
    a, b = fit_beta_mle(AFFIRM.nco_rate_history)
    samples = sample_nco_rates(a, b, n=100_000, seed=42)
    fitted_mean = a / (a + b)
    assert abs(samples.mean() - fitted_mean) < 0.001


def test_sample_reproducible_with_seed():
    a, b = fit_beta_mle(AFFIRM.nco_rate_history)
    s1 = sample_nco_rates(a, b, n=100, seed=99)
    s2 = sample_nco_rates(a, b, n=100, seed=99)
    np.testing.assert_array_equal(s1, s2)
