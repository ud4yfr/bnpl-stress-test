import csv
from pathlib import Path

import pytest

from src.inputs import load_inputs
from src.model import annualized_capacity, operating_result, pre_credit_loss_operating_income
from src.run import run
from src.schema import CompanyInputs, Scenario
from src.validation import ValidationError, compatible, read_manifest

ROOT = Path(__file__).resolve().parents[1]


def company() -> CompanyInputs:
    return CompanyInputs("X", 20, 10, 1000, "USD", "GAAP", "consolidated company")


def test_breakeven_algebra_and_annualization():
    rate = annualized_capacity(company(), Scenario("base", 0, 0, 0))
    assert rate == pytest.approx(0.12)
    assert operating_result(company(), Scenario("base", 0, 0, 0), rate) == pytest.approx(0)


def test_profit_declines_with_loss_and_stresses_do_not_help():
    base = Scenario("base", 0, 0, 0)
    stressed = Scenario("stress", 0.1, 0.01, 0.05)
    assert operating_result(company(), base, 0.05) > operating_result(company(), base, 0.10)
    assert annualized_capacity(company(), stressed) < annualized_capacity(company(), base)


def test_average_exposure_and_manifest_compatibility():
    inputs, _ = load_inputs(ROOT / "data" / "source_manifest.csv")
    assert inputs["Klarna"].average_exposure == pytest.approx((10951 + 9614) / 2)
    with pytest.raises(ValidationError, match="currency"):
        compatible({"currency": "USD", "economic_scope": "x", "accounting_basis": "GAAP"}, {"currency": "EUR", "economic_scope": "x", "accounting_basis": "GAAP"})
    with pytest.raises(ValidationError, match="scope"):
        compatible({"currency": "USD", "economic_scope": "x", "accounting_basis": "GAAP"}, {"currency": "USD", "economic_scope": "y", "accounting_basis": "GAAP"})


def test_manifest_has_documented_derived_and_unavailable_values():
    rows = read_manifest(ROOT / "data" / "source_manifest.csv")
    assert any(r["metric_id"] == "net_chargeoffs" and r["transformation"] for r in rows)
    assert any(r["value_status"] == "unavailable" for r in rows)
    assert not any(r["metric_id"] == "net_chargeoffs" and r["company"] == "Klarna" for r in rows)


def test_adjusted_income_is_not_used_in_main_inputs():
    inputs, _ = load_inputs(ROOT / "data" / "source_manifest.csv")
    assert inputs["Klarna"].operating_income == 17
    assert pre_credit_loss_operating_income(inputs["Klarna"]) == 203


def test_manifest_rejects_nan_and_undocumented_assumptions(tmp_path):
    template = (ROOT / "data" / "source_manifest.csv").read_text()
    bad_nan = tmp_path / "nan.csv"
    bad_nan.write_text(template.replace("88.429", "nan", 1))
    with pytest.raises(ValidationError, match="finite"):
        read_manifest(bad_nan)
    bad_assumption = tmp_path / "assumed.csv"
    bad_assumption.write_text(
        template.replace(",observed,,high,Includes provision for credit losses.", ",assumed,,high,", 1)
    )
    with pytest.raises(ValidationError, match="assumed values need notes"):
        read_manifest(bad_assumption)


def test_clean_run_is_reproducible_and_complete(tmp_path):
    first = run(tmp_path / "one")
    second = run(tmp_path / "two")
    assert first == second
    assert {r["company"] for r in first} == {"Affirm", "Klarna"}
    assert {r["scenario"] for r in first} == {"base", "downside", "severe"}
    assert (tmp_path / "one" / "credit_loss_capacity.png").exists()
    with (tmp_path / "one" / "scenario_results.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 30
    summary = {row["company"]: float(row["capacity_rate"]) for row in first if row["scenario"] == "base" and row["loss_rate"] == 0.03}
    assert summary == pytest.approx({"Affirm": 0.1310216092, "Klarna": 0.0789691223})
