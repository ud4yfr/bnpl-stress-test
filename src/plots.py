from pathlib import Path

import matplotlib.pyplot as plt


def save_plots(output_dir: Path, results: list[dict[str, object]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    companies = sorted({str(row["company"]) for row in results})
    base = [r for r in results if r["scenario"] == "base" and r["loss_rate"] == 0.03]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar([r["company"] for r in base], [100 * float(r["capacity_rate"]) for r in base])
    ax.set(ylabel="Static annualized credit-loss capacity (%)", title="Company-level accounting capacity")
    fig.tight_layout(); fig.savefig(output_dir / "credit_loss_capacity.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    for company in companies:
        rows = [r for r in results if r["company"] == company and r["scenario"] == "base"]
        ax.plot([100 * float(r["loss_rate"]) for r in rows], [float(r["operating_result"]) for r in rows], marker="o", label=company)
    ax.axhline(0, color="black", linewidth=0.8); ax.legend(); ax.set(xlabel="Assumed annualized loss rate (%)", ylabel="Quarterly operating result (USD millions)")
    fig.tight_layout(); fig.savefig(output_dir / "profitability_vs_loss_rate.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    scenarios = ["base", "downside", "severe"]
    for company in companies:
        values = [next(float(r["capacity_rate"]) * 100 for r in results if r["company"] == company and r["scenario"] == s) for s in scenarios]
        ax.plot(scenarios, values, marker="o", label=company)
    ax.legend(); ax.set(ylabel="Annualized capacity (%)", title="Sensitivity to combined assumptions")
    fig.tight_layout(); fig.savefig(output_dir / "sensitivity.png", dpi=160); plt.close(fig)
