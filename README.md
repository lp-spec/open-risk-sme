# OpenRiskSME

Turn messy small business financial data into lender-ready risk reports in seconds.

## Why This Exists

Small businesses struggle to access capital because:
- Financial data is inconsistent
- Risk is hard to interpret
- Documentation is not lender-aligned

This project fixes that.

## Features

- Normalize raw SME financials
- Generate risk indicators (DSCR, volatility)
- Produce lender-ready summaries
- API + CLI support

## Quick Start (30 seconds)

pip install -r requirements.txt

python main.py

OR

openrisk examples/sample_input.csv

## Example Output

{
  "risk_score": 70,
  "risk_level": "Moderate",
  "explanations": ["Low DSCR"]
}

## Architecture

See docs/architecture.md

## Roadmap

- Industry-specific models
- Benchmark datasets
- Credit decision simulation

## Contributing

PRs welcome. See CONTRIBUTING.md
