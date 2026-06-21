"""Tests for sourced financial inputs. Validates ranges, not exact values —
the exact values are assertions against the filing (documented in sourcing.py comments)."""

import pytest
from src.sourcing import AFFIRM, KLARNA, CompanyInputs


def test_affirm_is_company_inputs():
    assert isinstance(AFFIRM, CompanyInputs)


def test_klarna_is_company_inputs():
    assert isinstance(KLARNA, CompanyInputs)


def test_affirm_lhi_plausible():
    # Affirm FQ3'26 gross LHI ~$8.6B confirmed vs 10-Q allowance cross-check
    assert 7_000 < AFFIRM.lhi_gross_mm < 10_000


def test_klarna_lhi_plausible():
    # Klarna Fair Financing outstanding ~$15.2B per 20-F Dec 31, 2025
    assert 10_000 < KLARNA.lhi_gross_mm < 20_000


def test_affirm_provision_quarterly_positive():
    assert AFFIRM.provision_quarterly_mm > 0


def test_klarna_provision_quarterly_positive():
    assert KLARNA.provision_quarterly_mm > 0


def test_affirm_nco_rate_in_range():
    # Historical Affirm annual NCO rate has ranged 7.51%–8.55%
    assert 0.05 < AFFIRM.baseline_nco_rate_annual < 0.15


def test_klarna_nco_rate_in_range():
    # Klarna Fair Financing NCO is estimated; should be below Affirm's
    assert 0.02 < KLARNA.baseline_nco_rate_annual < 0.12


def test_affirm_nco_history_has_observations():
    assert len(AFFIRM.nco_rate_history) >= 5


def test_klarna_nco_history_single_estimate():
    # Klarna does not have multi-quarter NCO series — only 1 point estimate
    assert len(KLARNA.nco_rate_history) == 1


def test_dq_rate_reasonable():
    assert 0.01 < AFFIRM.dq_rate_30plus < 0.20
    # Klarna Fair Financing 30+ DPD
    assert 0.01 < KLARNA.dq_rate_30plus < 0.20


def test_operating_income_positive():
    # Both companies are profitable at baseline
    assert AFFIRM.operating_income_quarterly_mm > 0
    assert KLARNA.operating_income_quarterly_mm > 0
