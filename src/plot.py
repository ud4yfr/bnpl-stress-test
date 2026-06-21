"""
Comparative visualization: Affirm vs Klarna profit distributions and breakeven.

Figure layout (two columns):
  Left:  Affirm profit distribution histogram + breakeven + current position
  Right: Klarna profit distribution histogram + breakeven + current position

Each panel also shows the Beta distribution of NCO rates in a secondary subplot.
"""

import matplotlib.pyplot as plt
import numpy as np

from src.model import MonteCarloResult, unit_economics
from src.sourcing import AFFIRM, KLARNA


_AFFIRM_COLOR = "#1a6faf"   # blue
_KLARNA_COLOR = "#e63946"   # red (Klarna brand)
_BREAKEVEN_COLOR = "#333333"
_CURRENT_COLOR = "#f4a261"


def build_comparison_figure(
    affirm_result: MonteCarloResult,
    klarna_result: MonteCarloResult,
) -> plt.Figure:
    """
    Build 2×2 figure comparing Affirm and Klarna.

    Top row: profit distribution histograms (quarterly profit per $100 LHI)
    Bottom row: Beta distribution of NCO rates used in the simulation
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "BNPL Credit Stress Test: Affirm vs Klarna\n"
        "Monte Carlo — Quarterly Profit per $100 On-Balance-Sheet Exposure",
        fontsize=13,
        y=0.98,
    )

    _plot_profit_distribution(axes[0, 0], affirm_result, _AFFIRM_COLOR)
    _plot_profit_distribution(axes[0, 1], klarna_result, _KLARNA_COLOR)
    _plot_nco_distribution(axes[1, 0], affirm_result, _AFFIRM_COLOR)
    _plot_nco_distribution(axes[1, 1], klarna_result, _KLARNA_COLOR)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


def _plot_profit_distribution(
    ax: plt.Axes,
    result: MonteCarloResult,
    color: str,
) -> None:
    """Histogram of simulated quarterly profits per $100, with breakeven and current markers."""
    ax.hist(result.profits, bins=80, color=color, alpha=0.7, edgecolor="none")

    # Breakeven line
    ax.axvline(0, color=_BREAKEVEN_COLOR, linewidth=1.5, linestyle="--", label="Breakeven (profit=0)")

    # Current (baseline NCO rate) profit
    _COMPANY_MAP = {"Affirm": AFFIRM, "Klarna": KLARNA}
    if result.company_name not in _COMPANY_MAP:
        raise ValueError(
            f"Unknown company '{result.company_name}'; expected one of {list(_COMPANY_MAP)}"
        )
    company = _COMPANY_MAP[result.company_name]
    current_profit = unit_economics(company, result.current_nco)
    ax.axvline(current_profit, color=_CURRENT_COLOR, linewidth=1.5, linestyle="-",
               label=f"Current NCO ({result.current_nco*100:.2f}%)")

    ax.set_title(
        f"{result.company_name} — Profit Distribution\n"
        f"Breakeven NCO: {result.breakeven_nco*100:.2f}% | "
        f"Buffer: {result.buffer_pp:.2f}pp | "
        f"P(loss): {result.prob_loss*100:.1f}%",
        fontsize=10,
    )
    ax.set_xlabel("Quarterly profit per $100 LHI ($)")
    ax.set_ylabel("Frequency (out of 10,000 simulations)")

    ax.legend(fontsize=8)

    if not result.is_empirical:
        ax.text(
            0.02, 0.97, "⚠ PROXY: limited data\ntreat as illustrative",
            transform=ax.transAxes, fontsize=7, color="#c44",
            verticalalignment="top",
        )


def _plot_nco_distribution(
    ax: plt.Axes,
    result: MonteCarloResult,
    color: str,
) -> None:
    """Plot the Beta density function for the NCO rate distribution used."""
    from scipy.stats import beta as scipy_beta

    x = np.linspace(0, 0.30, 1000)
    pdf = scipy_beta.pdf(x, result.alpha, result.beta_param)

    ax.plot(x * 100, pdf / 100, color=color, linewidth=2)
    ax.fill_between(x * 100, pdf / 100, alpha=0.2, color=color)

    ax.axvline(result.current_nco * 100, color=_CURRENT_COLOR, linewidth=1.5,
               linestyle="-", label=f"Current: {result.current_nco*100:.2f}%")
    ax.axvline(result.breakeven_nco * 100, color=_BREAKEVEN_COLOR, linewidth=1.5,
               linestyle="--", label=f"Breakeven: {result.breakeven_nco*100:.2f}%")

    ax.set_title(
        f"{result.company_name} — NCO Rate Distribution\n"
        f"Beta(α={result.alpha:.0f}, β={result.beta_param:.0f})",
        fontsize=10,
    )
    ax.set_xlabel("Annual NCO rate (%)")
    ax.set_ylabel("Probability density")
    ax.legend(fontsize=8)

    if not result.is_empirical:
        ax.text(
            0.02, 0.97, "⚠ PROXY distribution",
            transform=ax.transAxes, fontsize=7, color="#c44",
            verticalalignment="top",
        )


def save_figure(fig: plt.Figure, path: str) -> None:
    """Save figure to path (PNG at 150 DPI)."""
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Chart saved → {path}")
