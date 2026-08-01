import csv
import math
from pathlib import Path

REQUIRED = {"units", "period_start", "period_end", "economic_scope", "value_status"}
STATUSES = {"observed", "derived", "assumed", "unavailable"}


class ValidationError(ValueError):
    pass


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        missing = [field for field in REQUIRED if not row.get(field)]
        if missing:
            raise ValidationError(f"{row.get('metric_id')}: missing {', '.join(missing)}")
        status = row["value_status"]
        if status not in STATUSES:
            raise ValidationError(f"{row['metric_id']}: invalid value_status {status}")
        if status == "assumed" and not row.get("notes"):
            raise ValidationError(f"{row['metric_id']}: assumed values need notes")
        if status == "derived" and not row.get("transformation"):
            raise ValidationError(f"{row['metric_id']}: derived values need a transformation")
        if status != "unavailable":
            try:
                value = float(row["value"])
            except ValueError as exc:
                raise ValidationError(f"{row['metric_id']}: numeric value required") from exc
            if not math.isfinite(value):
                raise ValidationError(f"{row['metric_id']}: finite value required")
    return rows


def compatible(numerator: dict[str, str], denominator: dict[str, str]) -> None:
    if numerator["currency"] != denominator["currency"]:
        raise ValidationError("currency mismatch; conversion metadata is required")
    if numerator["economic_scope"] != denominator["economic_scope"]:
        raise ValidationError("incompatible numerator and denominator scopes")
    if numerator["accounting_basis"] != denominator["accounting_basis"]:
        raise ValidationError("incompatible accounting bases")
