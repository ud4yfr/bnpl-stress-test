# CLAUDE.md

## What this project is

A comparative Monte Carlo stress test on the unit economics of Affirm Holdings (NASDAQ: AFRM) and Klarna Group (NYSE: KLAR), built on each company's actual disclosed financials, not assumed numbers. The question being answered: as BNPL "pay late" rates climb, at what point does each company's profitability actually break, and which one is more fragile.

This is a portfolio project built to signal credit-risk and quantitative modeling ability to economic consulting firms (Cornerstone Research, Analysis Group, NERA) and fintech/risk roles. It also doubles as quant-prep reps for Two Sigma style interviews, since roll-rate analysis and Monte Carlo stress testing are real risk-desk techniques, not toy modeling.

## The real-world hook (why this isn't a generic toy model)

There is an active, unresolved analyst debate right now: roughly 47% of BNPL users paid late in the past year, but Affirm's own 30-plus day delinquency rate has stayed flat at 2.8% year over year. The open question is whether "paying late" is converting into real charge-offs, or whether it's noise that never hits the bottom line. This project takes a quantified position on that debate using each company's own numbers, instead of restating the headline stat.

## Locked baseline facts, verify before using, do not silently override

These are the figures I have already verified from public reporting. Use them as the starting point, but the pre-flight step below requires you to confirm them against the actual primary source before they go into the model. If a number in the primary source differs from what's listed here, the primary source wins, flag the discrepancy to me.

**Affirm Holdings (AFRM), fiscal Q3 2026, quarter ended March 31, 2026:**
- Revenue: $1.04 billion, up 33% year over year
- Gross merchandise volume (GMV): $11.6 billion, up 35% year over year
- GAAP operating profit, EPS $0.30
- 30-plus day delinquency rate: 2.8%, flat year over year
- Allowance for credit losses: $512 million, or 6.0% of loans held for investment
- Product mix (FY2025): 72% of GMV was monthly interest-bearing installment loans, not 0%-interest Pay-in-4
- Affirm's fiscal year ends June 30, quarters do not align with calendar quarters, watch for this when comparing to Klarna

**Klarna Group (KLAR):**
- IPO'd on NYSE September 10, 2025 at $40, opened at $52, has since traded back below the $40 IPO price
- Pure-play BNPL originator, less diversified than Affirm
- Product mix (2025): 75 to 79% of GMV is Pay-in-4 (typically zero-interest, no finance-charge revenue cushion)
- Roughly one-third of Klarna's revenue comes from the US market, vs Affirm which is predominantly US
- Total GMV roughly $112 billion (trailing twelve months to June 30, 2025), much larger scale than Affirm by GMV, but thinner per-unit margin given the Pay-in-4 mix

**Why the product mix difference matters and must be modeled, not glossed over:** Affirm's interest-bearing loans generate finance-charge revenue that can absorb rising credit losses. Klarna's Pay-in-4 mix mostly cannot, since there's no interest income cushion, Klarna's buffer against delinquency is closer to merchant fees alone. This is the actual analytical payoff of doing this comparative instead of single-company: same headline delinquency pressure can hit two business models very differently. Build the model so this shows up as a result, not as a stated assumption.

## Pre-flight checks, required before building the model

Do these first and report back before touching the Monte Carlo. Do not assume, verify against primary sources.

### 1. Confirm the baseline numbers
Pull Affirm's actual FQ3 FY2026 shareholder letter and 10-Q, and Klarna's most recent 10-Q or equivalent SEC disclosure. Confirm every locked figure above against the primary source. Flag any discrepancy.

### 2. Source the inputs the model actually needs
For both companies, locate and cite, with the specific filing and line item:
- Revenue breakdown by stream (merchant/network fees, interest income, card network revenue, etc.)
- Funding cost or cost of capital, however each company discloses it
- Operating expense relevant to loan servicing
- Credit loss data: allowance for credit losses, and delinquency by stage (30, 60, 90 day) over time if disclosed

### 3. Check Klarna's disclosure history
Klarna only IPO'd in September 2025, so it has far fewer quarters of public delinquency-by-stage data than Affirm. Document explicitly how many quarters of real data exist for Klarna. If there isn't enough to fit an empirical roll-rate distribution independently, say so plainly, do not quietly substitute Affirm's distribution without flagging it as a proxy assumption.

### 4. Resolve the on-balance-sheet question
A meaningful share of Affirm's originated GMV is sold to capital partners rather than held on Affirm's own balance sheet, meaning Affirm doesn't carry all the credit risk on every loan it originates. Determine and document whether this model is stressing Affirm's retained/on-balance-sheet exposure (loans held for investment) or its total platform GMV, and do the same check for Klarna's funding model. State the choice explicitly in the writeup, this single decision changes what "breakeven" even means.

## The golden rule for the assistant

Build the whole thing, and teach me as you go. Concretely:

- Narrate the reasoning at every decision point. Before each major step, tell me what you're about to do, why, and what the alternative was.
- When a choice is debatable (which revenue lines to include, how to calibrate the roll-rate distribution, on-balance-sheet vs total GMV scope), explain the tradeoff, make a call, and state clearly which call you made.
- Never hide a statistical step behind a library call without explaining the formula underneath.
- Treat me like someone taking Econometrics this summer who has not done credit-risk modeling before. Define terms the first time they come up: roll rate, charge-off, delinquency stage, allowance for credit losses, Monte Carlo, breakeven.
- If data is missing or thin (especially for Klarna), say so directly instead of filling the gap silently.

The goal is that by the end I can explain every modeling choice cold, even though you wrote the code.

## How to teach me (the protocol)

Work in stages, not one dump:
1. Say what the stage is and why it exists in this kind of stress test.
2. Show the code.
3. Run it, show the output.
4. Explain what the output means and what would make it misleading.
5. Pause point: tell me what I should be able to explain before we move to the next stage.

## Tech stack

- Python 3.11+
- pandas, numpy
- scipy.stats (for fitting the roll-rate distribution and running the Monte Carlo)
- matplotlib (breakeven and distribution plots, side by side for both companies)

Keep dependencies minimal. No ML libraries, this is a financial/credit-risk model, not a prediction model.

## Methodology (the spine, run once per company, then compare)

### 1. Build the unit-economics baseline
From the sourced inputs, construct a per-loan or per-$100-of-GMV profitability equation for each company:

```
Profit = Merchant fee revenue + Finance charge revenue
         - Funding cost - Opex
         - (Roll rate x Loss given default x Exposure)
```

State explicitly which revenue and cost lines exist for each company and which don't (for example, Klarna's Pay-in-4 mix means finance charge revenue is much smaller relative to GMV than Affirm's).

### 2. Derive the roll-rate distribution empirically, not from a guessed range
Using each company's historical 30/60/90-day delinquency-stage data, estimate the empirical relationship between a loan going 30+ days late and it eventually charging off (the roll rate). Fit a distribution to this (for example a Beta distribution bounded on [0,1], parameterized off the historical mean and variance) rather than picking an arbitrary uniform range. For Klarna, if there isn't enough independent history, explicitly use Affirm's distribution shape as a documented proxy and flag it as a limitation, do not present it as Klarna's own empirical result.

### 3. Run the Monte Carlo
For each company, draw many samples from its roll-rate distribution, compute resulting profitability per draw, and build the distribution of outcomes. Explain in plain English what a single simulation draw represents.

### 4. Find the breakeven roll rate
For each company, find the roll rate at which profitability crosses zero. This is the headline number, the threshold at which "late payments converting to real losses" actually breaks the business model.

### 5. Compare
Plot both companies' profitability distributions and breakeven points on the same chart. State which company is more fragile to the same delinquency shock, and connect that explicitly back to the product-mix difference (interest-bearing buffer vs Pay-in-4 reliance on fees).

### 6. Position against the real-world trend
Take the actual current numbers (47% pay-late industry rate, Affirm's flat 2.8% 30-plus day rate) and show where each company currently sits relative to its own breakeven. Answer directly: based on this model, is either company close to the edge, or is the current headline overstating the risk.

## What I must be able to answer by the end

1. Why an empirically derived roll-rate distribution instead of an arbitrary assumed range.
2. Why Monte Carlo instead of a simple scenario table.
3. Why the same headline delinquency pressure could hit Affirm and Klarna differently, tied to product mix.
4. What this model does not capture (funding cost shocks, a recession scenario, regulatory changes to credit-bureau reporting, growth diluting the delinquency ratio).
5. Where each company sits relative to its breakeven today, and what would have to change for that to flip.

Quiz me on these five at the end and correct me where I'm wrong.

## Project structure

```
bnpl-stress-test/
  CLAUDE.md
  README.md          # event hook, method, results for both companies, the "so what"
  requirements.txt
  data/               # sourced filing data, cited by document and line item
  src/
    sourcing.py        # pulls and structures the inputs from filings, with citations
    rollrate.py         # fits the empirical roll-rate distribution per company
    model.py            # unit economics + Monte Carlo + breakeven, runs per company
    plot.py              # comparative distribution and breakeven plots
    run.py               # orchestrates the full analysis end to end
  notebooks/           # scratch / pre-flight verification notes
```

## Writeup requirements (README.md)

- The real-world hook and why it's an open question worth modeling.
- The pre-flight findings: confirmed baseline numbers, data limitations (especially Klarna's shorter history), and the on-balance-sheet scoping decision.
- The method in plain English, four or five sentences.
- Both companies' breakeven roll rates, side by side, with the comparative plot.
- The "so what": which company is more fragile and why, and where each sits relative to breakeven given current real delinquency trends.

## Coding conventions

- Clear names over short names.
- Comment the WHY on every nontrivial choice.
- Cite the specific filing and line item next to every hardcoded input number.
- No silent fallbacks. If a number can't be sourced, raise and say so, don't substitute a guess without flagging it.
- Pin all inputs at the top of run.py so the whole thing reruns from one place.

## What not to do

- Do not invent input numbers. Every dollar figure traces back to a cited filing.
- Do not quietly use Affirm's data to fill a Klarna gap without labeling it as a proxy.
- Do not add ML models, this is a financial stress test, not a prediction model.
- Do not skip the teaching, or the pre-flight checks, they're part of the analysis, not housekeeping.
