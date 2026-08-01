from .schema import CompanyInputs, Scenario


def pre_credit_loss_operating_income(company: CompanyInputs) -> float:
    """Accounting capacity: reported operating income plus recognized provision."""
    return company.operating_income + company.provision


def annualized_capacity(company: CompanyInputs, scenario: Scenario) -> float:
    income = pre_credit_loss_operating_income(company)
    stressed_income = income * (1 - scenario.revenue_stress - scenario.operating_expense_stress)
    stressed_income -= company.average_exposure * scenario.funding_cost_shock / 4
    return 4 * stressed_income / company.average_exposure


def operating_result(company: CompanyInputs, scenario: Scenario, annual_loss_rate: float) -> float:
    """Quarterly operating result in the manifest's monetary unit."""
    capacity = annualized_capacity(company, scenario) * company.average_exposure / 4
    return capacity - annual_loss_rate * company.average_exposure / 4
