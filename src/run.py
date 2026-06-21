"""
BNPL Monte Carlo Stress Test — full pipeline orchestrator.

Run with: python src/run.py

Stages:
  1. Load inputs (sourcing.py)
  2. Fit Beta distributions (rollrate.py)
  3. Run Monte Carlo + find breakeven (model.py)
  4. Print results with teaching narration
  5. Save chart (plot.py)

All numeric inputs are pinned in sourcing.py — change them there to rerun.
"""

import os
import sys

# When run as `python src/run.py` from the project root, Python does NOT add the
# project root to sys.path automatically (only the src/ directory is added).
# Insert the project root so that `from src.xxx import ...` works correctly.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import matplotlib
matplotlib.use("Agg")  # non-interactive backend (saves to file, no window needed)

from src.sourcing import AFFIRM, KLARNA
from src.rollrate import fit_beta_mle, fit_beta_klarna
from src.model import monte_carlo, unit_economics, find_breakeven_nco_rate
from src.plot import build_comparison_figure, save_figure

N_SIMS = 10_000
RANDOM_SEED = 42
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "bnpl_stress_test.png")


def _header(text: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def _section(text: str) -> None:
    print(f"\n--- {text} ---")


def run() -> None:

    # -----------------------------------------------------------------------
    # STAGE 1: Inputs
    # -----------------------------------------------------------------------
    _header("STAGE 1: INPUTS")
    print("""
What this is: We start with hardcoded, filing-verified financials for both
companies. The key inputs are: (1) how much money each company makes before
credit losses, and (2) how much they've been losing historically to defaults.

Key concept — Gross LHI (Loans Held for Investment):
  The on-balance-sheet loan book each company actually carries credit risk on.
  Affirm: $8.6B. Klarna: $15.2B Fair Financing book.
  We stress these books — not total GMV, which includes loans sold off.
""")

    for company in [AFFIRM, KLARNA]:
        _section(company.name)
        pre_prov = (company.operating_income_quarterly_mm + company.provision_quarterly_mm) \
                   / company.lhi_gross_mm * 100
        print(f"  Exposure (gross LHI): ${company.lhi_gross_mm:,.0f}M — {company.exposure_label}")
        print(f"  Quarterly operating income: ${company.operating_income_quarterly_mm:.1f}M")
        print(f"  Quarterly provision: ${company.provision_quarterly_mm:.1f}M")
        print(f"  → Pre-provision income: ${company.operating_income_quarterly_mm + company.provision_quarterly_mm:.1f}M/quarter")
        print(f"  → Pre-provision income per $100 LHI: ${pre_prov:.3f}/quarter")
        print(f"  Baseline annual NCO rate: {company.baseline_nco_rate_annual*100:.2f}%")
        print(f"  30+ DPD rate: {company.dq_rate_30plus*100:.2f}%")
        if not company.nco_history_is_empirical:
            print(f"  ⚠ DATA NOTE: {company.data_quality_note}")

    # -----------------------------------------------------------------------
    # STAGE 2: Roll-rate distribution
    # -----------------------------------------------------------------------
    _header("STAGE 2: FITTING THE ROLL-RATE DISTRIBUTION")
    print("""
What is a roll rate? In credit modeling, the roll rate describes how loans
"roll" from current to delinquent to charged-off. In this model, we use
a simplified version: the annual net charge-off rate as a fraction of the
total loan book. This is a number between 0 and 1.

Why Beta distribution? Beta is the natural distribution for quantities on
[0, 1] like probabilities and rates. Its two parameters α and β let it
represent a wide range of shapes. When α is large, the distribution is
tight — reflecting consistent historical NCO rates. When α is small, the
distribution is wide — reflecting high uncertainty.

Why fit empirically instead of picking an arbitrary range? If we just said
"let's try NCO rates from 1% to 20%", we'd be inventing the uncertainty
range. By fitting to actual historical data, the distribution reflects
how much Affirm's NCO rate has actually varied quarter-to-quarter.
""")

    print("Affirm: fitting Beta via MLE to 7 quarters of derived NCO observations")
    a_afrm, b_afrm = fit_beta_mle(AFFIRM.nco_rate_history)
    affirm_fitted_mean = a_afrm / (a_afrm + b_afrm)
    affirm_fitted_std = (a_afrm * b_afrm / ((a_afrm+b_afrm)**2*(a_afrm+b_afrm+1)))**0.5
    print(f"  Beta(α={a_afrm:.0f}, β={b_afrm:.0f})")
    print(f"  Fitted mean: {affirm_fitted_mean*100:.2f}%  |  Fitted std: {affirm_fitted_std*100:.3f}%")
    print(f"  Historical observations: {[f'{x*100:.2f}%' for x in AFFIRM.nco_rate_history]}")

    print("\nKlarna: PROXY — using Affirm's coefficient of variation × 2 at Klarna's mean")
    print("  Reason: only 1 estimated NCO point; no independent time series available")
    a_klar, b_klar = fit_beta_klarna(a_afrm, b_afrm, KLARNA.baseline_nco_rate_annual)
    klarna_fitted_mean = a_klar / (a_klar + b_klar)
    klarna_fitted_std = (a_klar * b_klar / ((a_klar+b_klar)**2*(a_klar+b_klar+1)))**0.5
    print(f"  Beta(α={a_klar:.0f}, β={b_klar:.0f})")
    print(f"  Proxy mean: {klarna_fitted_mean*100:.2f}%  |  Proxy std: {klarna_fitted_std*100:.3f}%")
    print("  ⚠ This distribution reflects Klarna data uncertainty, not empirical history")

    # -----------------------------------------------------------------------
    # STAGE 3: Monte Carlo
    # -----------------------------------------------------------------------
    _header("STAGE 3: MONTE CARLO SIMULATION")
    print(f"""
What a single simulation draw represents:
  One draw = one possible future annual NCO rate, sampled from the Beta distribution.
  For that NCO rate, we compute: profit = pre_provision_income - (nco/4)*$100.
  10,000 draws give us the full distribution of possible profitability outcomes.

Why quarterly profit per $100 LHI? This normalizes for each company's balance
sheet size, so the profit axis is directly comparable between Affirm and Klarna.

Running {N_SIMS:,} simulations per company...
""")

    result_afrm = monte_carlo(AFFIRM, a_afrm, b_afrm, n_sims=N_SIMS, seed=RANDOM_SEED)
    result_klar = monte_carlo(KLARNA, a_klar, b_klar, n_sims=N_SIMS, seed=RANDOM_SEED)

    # -----------------------------------------------------------------------
    # STAGE 4: Results
    # -----------------------------------------------------------------------
    _header("STAGE 4: RESULTS")

    print("""
Key concept — breakeven NCO rate:
  The annual NCO rate at which quarterly profit per $100 LHI = 0.
  Derived analytically: breakeven = 4 × (pre_provision_income_per_100) / 100
  This is the threshold at which delinquency converts to actual P&L damage.

Buffer = breakeven NCO rate − current NCO rate (in percentage points).
  A larger buffer means the company can absorb more credit deterioration.
""")

    print(f"\n{'Metric':<40} {'Affirm':>12} {'Klarna':>12}")
    print("-" * 66)
    print(f"{'Pre-provision income / $100 LHI / qtr':<40} "
          f"{'$'+f'{result_afrm.profits.mean() + (result_afrm.current_nco/4)*100:.2f}':>12} "
          f"{'$'+f'{result_klar.profits.mean() + (result_klar.current_nco/4)*100:.2f}':>12}")
    print(f"{'Current (baseline) NCO rate (annual)':<40} "
          f"{result_afrm.current_nco*100:>11.2f}% "
          f"{result_klar.current_nco*100:>11.2f}%")
    print(f"{'Breakeven NCO rate (annual)':<40} "
          f"{result_afrm.breakeven_nco*100:>11.2f}% "
          f"{result_klar.breakeven_nco*100:>11.2f}%")
    print(f"{'Buffer (pp before loss)':<40} "
          f"{result_afrm.buffer_pp:>11.2f}pp "
          f"{result_klar.buffer_pp:>11.2f}pp")
    print(f"{'Fragility ratio (Affirm/Klarna buffer)':<40} "
          f"{'—':>12} "
          f"{f'{result_afrm.buffer_pp/result_klar.buffer_pp:.1f}× more resilient':>12}")
    print(f"{'P(loss) at historical NCO distribution':<40} "
          f"{result_afrm.prob_loss*100:>11.1f}% "
          f"{result_klar.prob_loss*100:>11.1f}%")

    print("""
So what does this mean?
  Affirm needs its annual NCO rate to increase by ~{:.1f}pp from current levels
  before it reports a loss — a large buffer given its 7-year history of NCO
  rates in the 7.5–8.6% range.

  Klarna, by contrast, needs only ~{:.1f}pp of NCO deterioration on its Fair
  Financing book to go from profitable to loss-making.

Why the difference? Product mix.
  Affirm: 71% interest-bearing installment loans → generates $532M/quarter in
  finance-charge revenue that can absorb rising credit losses.

  Klarna: 88% of GMV is fee-only (Pay Later receivable sold off) → the retained
  Fair Financing book has interest income, but the total company P&L buffer is
  thin ($47M/quarter). Same delinquency shock, much less revenue cushion.

Where does current industry data put us?
  The 47% self-reported "paying late" statistic is NOT the NCO rate.
  Affirm's current 30+ DPD: {:.1f}% (flat YoY) — far from converting to a
  9% NCO rate jump that would stress Affirm.
  Klarna's Fair Financing 30+ DPD: {:.1f}% — the buffer from current to
  breakeven is thin, but current data does not show it being breached.
""".format(
        result_afrm.buffer_pp,
        result_klar.buffer_pp,
        AFFIRM.dq_rate_30plus * 100,
        KLARNA.dq_rate_30plus * 100,
    ))

    print("⚠ Klarna caveat: all Klarna outputs use estimated attribution and a proxy distribution.")
    print("  Treat Klarna numbers as illustrative of direction, not precise magnitude.")

    # -----------------------------------------------------------------------
    # STAGE 5: Chart
    # -----------------------------------------------------------------------
    _header("STAGE 5: SAVING CHART")
    fig = build_comparison_figure(result_afrm, result_klar)
    save_figure(fig, OUTPUT_PATH)

    # -----------------------------------------------------------------------
    # STAGE 6: Quiz prompts
    # -----------------------------------------------------------------------
    _header("PAUSE — FIVE THINGS YOU SHOULD BE ABLE TO EXPLAIN")
    print("""
1. Why empirically derived roll-rate distribution instead of arbitrary range?
   ANSWER: Fitting to actual historical data (7 quarters of Affirm NCO) means
   the distribution reflects how much variability actually occurred. Picking a
   "1–20% range" arbitrarily gives equal weight to events that have never
   happened. The Beta MLE fit weights the distribution where the data lives.

2. Why Monte Carlo instead of a simple scenario table?
   ANSWER: A scenario table gives you 3 outcomes you pre-choose. Monte Carlo
   gives you the full probability distribution — including tail probabilities.
   "There's a 5% chance NCO exceeds X%" is a more useful risk statement than
   "in our bad scenario, NCO = 12%."

3. Why could the same headline delinquency pressure hit Affirm and Klarna
   differently, tied to product mix?
   ANSWER: Affirm earns $532M/quarter in finance-charge revenue (71% interest-
   bearing book). Klarna's Fair Financing is only 12% of GMV — most revenue
   is Pay Later merchant fees that have no credit-loss buffer. Same NCO rate
   increase hits a much thinner income base for Klarna.

4. What does this model NOT capture?
   - Funding cost shocks: if credit spreads widen, Klarna's deposit cost rises
   - Recession scenario: NCO rates could jump discontinuously, not gradually
   - Regulatory changes: CFPB rulings on BNPL credit reporting
   - Growth diluting the ratio: rapid origination growth can mask rising NCO
   - Correlation: a macro shock would hit both companies simultaneously

5. Where does each company sit relative to breakeven today, and what would
   flip it?
   ANSWER: Affirm is ~{:.1f}pp below its breakeven — would need NCO to roughly
   double from current levels to report a loss. Klarna is ~{:.1f}pp below
   breakeven — a moderate deterioration in Fair Financing credit quality
   (not unprecedented in consumer installment lending) could flip it.
   Neither is at the edge today, but Klarna's margin is thin.
""".format(result_afrm.buffer_pp, result_klar.buffer_pp))


if __name__ == "__main__":
    run()
