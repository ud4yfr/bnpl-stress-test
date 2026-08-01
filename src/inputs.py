from pathlib import Path

from .schema import CompanyInputs
from .validation import ValidationError, compatible, read_manifest


def load_inputs(manifest_path: Path) -> tuple[dict[str, CompanyInputs], list[dict[str, str]]]:
    rows = read_manifest(manifest_path)
    by_company: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        by_company.setdefault(row["company"], {})[row["metric_id"]] = row
    inputs = {}
    for company, metrics in by_company.items():
        needed = ("operating_income", "provision", "average_exposure")
        if any(metric not in metrics for metric in needed):
            raise ValidationError(f"{company}: missing required company-level inputs")
        income, provision, exposure = (metrics[key] for key in needed)
        compatible(income, exposure)
        compatible(provision, exposure)
        if float(exposure["value"]) <= 0:
            raise ValidationError(f"{company}: exposure must be positive")
        inputs[company] = CompanyInputs(
            company, float(income["value"]), float(provision["value"]),
            float(exposure["value"]), income["currency"], income["accounting_basis"],
            income["economic_scope"],
        )
    return inputs, rows
