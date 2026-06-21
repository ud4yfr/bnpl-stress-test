"""
Roll-rate distribution fitting for the BNPL Monte Carlo stress test.

'Roll rate' in this model = annual net charge-off rate as a fraction of
outstanding loans. We fit a Beta(α, β) distribution because:
  1. NCO rates live on [0, 1] — Beta is the natural distribution for that domain
  2. It can represent skewed shapes (important for tail-risk modeling)
  3. Parameters α and β have intuitive interpretations:
       α = "pseudo-count of charged-off dollars"
       β = "pseudo-count of repaid dollars"

For Affirm: 7 quarterly observations derived from allowance roll-forward → MLE fit.
For Klarna: 1 estimated point → proxy using Affirm's coefficient of variation.
"""

import numpy as np
from scipy.stats import beta as scipy_beta


def fit_beta_mle(observations: list) -> tuple:
    """
    Fit Beta(α, β) to historical annual NCO rate observations via MLE.

    scipy.stats.beta.fit() with loc=0, scale=1 constrains the distribution
    to [0, 1] and finds α, β that maximize the log-likelihood of the data.

    Args:
        observations: list of annual NCO rate floats (e.g. [0.0787, 0.0855, ...])

    Returns:
        (alpha, beta_param): Beta distribution parameters
    """
    if len(observations) < 2:
        raise ValueError(
            f"Need at least 2 observations for MLE fit; got {len(observations)}. "
            "Use fit_beta_moments() for a single-point estimate."
        )
    data = np.array(observations, dtype=float)
    # floc=0, fscale=1 pins the support to exactly [0, 1]
    alpha, beta_param, _loc, _scale = scipy_beta.fit(data, floc=0, fscale=1)
    return float(alpha), float(beta_param)


def fit_beta_moments(mean: float, std: float) -> tuple:
    """
    Fit Beta(α, β) via method of moments given mean and standard deviation.

    Used when we have a point estimate of mean and an assumed std,
    rather than a full time series.

    Method of moments:
        α = mean × [ mean(1 − mean)/var − 1 ]
        β = α × (1 − mean)/mean

    Args:
        mean: target mean of the distribution
        std:  target standard deviation

    Returns:
        (alpha, beta_param)

    Raises:
        ValueError: if std² ≥ mean*(1−mean), which violates Beta constraints
    """
    var = std ** 2
    max_var = mean * (1 - mean)
    if var >= max_var:
        raise ValueError(
            f"variance ({var:.6f}) must be < mean*(1-mean) ({max_var:.6f}) "
            "for a valid Beta distribution. Reduce std."
        )
    alpha = mean * (mean * (1 - mean) / var - 1)
    beta_param = alpha * (1 - mean) / mean
    return float(alpha), float(beta_param)


def fit_beta_klarna(
    affirm_alpha: float,
    affirm_beta: float,
    klarna_mean: float,
) -> tuple:
    """
    PROXY: Construct Klarna's Beta using Affirm's coefficient of variation (CV).

    Klarna has only one point estimate of annual NCO rate — not enough to fit
    an independent distribution. This proxy preserves Affirm's relative
    variability (CV = std/mean) but scales it to Klarna's mean.

    Why 2× Affirm's CV: Klarna's estimate is itself uncertain (estimated from
    provision attribution, not directly disclosed). Doubling the CV makes the
    prior wider to reflect this second-order uncertainty.

    This is explicitly labeled as a proxy in all outputs.

    Args:
        affirm_alpha: Affirm's fitted Beta alpha
        affirm_beta:  Affirm's fitted Beta beta
        klarna_mean:  Klarna's estimated baseline NCO rate

    Returns:
        (alpha, beta_param) for Klarna proxy distribution
    """
    affirm_mean = affirm_alpha / (affirm_alpha + affirm_beta)
    affirm_var = (
        affirm_alpha * affirm_beta
        / ((affirm_alpha + affirm_beta) ** 2 * (affirm_alpha + affirm_beta + 1))
    )
    affirm_std = affirm_var ** 0.5
    affirm_cv = affirm_std / affirm_mean

    # Double the CV to reflect Klarna data uncertainty
    klarna_std = klarna_mean * affirm_cv * 2.0
    return fit_beta_moments(klarna_mean, klarna_std)


def sample_nco_rates(alpha: float, beta_param: float, n: int, seed: int) -> np.ndarray:
    """
    Draw n samples from Beta(alpha, beta_param) using a seeded RNG.

    Each sample represents one possible annual NCO rate outcome.
    In the Monte Carlo, we draw 10,000 samples and compute profitability
    for each — this gives us the distribution of profit outcomes.

    Args:
        alpha, beta_param: Beta distribution parameters
        n:    number of Monte Carlo draws
        seed: random seed for reproducibility

    Returns:
        numpy array of shape (n,) with values in [0, 1]
    """
    rng = np.random.default_rng(seed)
    return scipy_beta.rvs(alpha, beta_param, size=n, random_state=rng)
