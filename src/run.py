from __future__ import annotations

import argparse
import json
from pathlib import Path

from .inputs import load_inputs
from .model import annualized_capacity, operating_result, pre_credit_loss_operating_income
from .plots import save_plots
from .reporting import write_csv
from .schema import Scenario


def run(output_dir: Path, scenario_name: str | None = None) -> list[dict[str, object]]:
    root = Path(__file__).resolve().parents[1]
    companies, manifest = load_inputs(root / "data" / "source_manifest.csv")
    config = json.loads((root / "config" / "scenarios.json").read_text())
    scenario_items = config["scenarios"].items()
    if scenario_name:
        scenario_items = [(scenario_name, config["scenarios"][scenario_name])]
    rows: list[dict[str, object]] = []
    for name, definition in scenario_items:
        scenario = Scenario(name, **definition)
        for company in companies.values():
            capacity = annualized_capacity(company, scenario)
            for loss_rate in config["annual_loss_rates"]:
                rows.append({
                    "company": company.company, "scenario": name, "loss_rate": loss_rate,
                    "pre_credit_loss_operating_income": pre_credit_loss_operating_income(company),
                    "average_exposure": company.average_exposure, "capacity_rate": capacity,
                    "operating_result": operating_result(company, scenario, loss_rate),
                    "change_from_provision_proxy": loss_rate - 4 * company.provision / company.average_exposure,
                    "currency": company.currency, "accounting_basis": company.accounting_basis,
                })
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "scenario_results.csv", rows)
    summary = [r for r in rows if r["scenario"] == "base" and r["loss_rate"] == config["annual_loss_rates"][0]]
    write_csv(output_dir / "summary.csv", summary)
    write_csv(output_dir / "assumptions_used.csv", [{"name": k, "value": v} for k, v in config.items()])
    if not scenario_name:
        save_plots(output_dir, rows)
    unavailable = [r["metric_name"] for r in manifest if r["value_status"] == "unavailable"]
    print("Validated source manifest and wrote deterministic scenario outputs.")
    for row in summary:
        print(f"{row['company']}: base static annualized capacity {float(row['capacity_rate']):.1%}")
    print("Unavailable inputs: " + (", ".join(unavailable) or "none"))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic BNPL credit-loss capacity scenarios")
    parser.add_argument("--mode", choices=["deterministic"], default="deterministic")
    parser.add_argument("--scenario", choices=["base", "downside", "severe"])
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()
    run(Path(args.output_dir), args.scenario)


if __name__ == "__main__":
    main()
