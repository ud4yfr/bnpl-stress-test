from dataclasses import dataclass


@dataclass(frozen=True)
class CompanyInputs:
    company: str
    operating_income: float
    provision: float
    average_exposure: float
    currency: str
    accounting_basis: str
    scope: str


@dataclass(frozen=True)
class Scenario:
    name: str
    revenue_stress: float
    funding_cost_shock: float
    operating_expense_stress: float
