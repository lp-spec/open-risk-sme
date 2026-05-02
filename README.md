## Try it in 60 seconds

git clone https://github.com/lp-spec/open-risk-sme
cd open-risk-sme

pip install -r requirements.txt
python main.py

# OpenRiskSME

Turn messy small business financial data into lender-ready risk reports in seconds.

## Quick Start

Clone the repo and run:

python main.py

## Example Output

{
  "risk_level": "Moderate",
  "summary": "Risk Score: 70"
}
See: examples/output_example.json

## What This Does

- Normalizes SME financial data
- Computes risk metrics (DSCR, volatility)
- Generates lender-ready summaries

## Why It Matters

Small businesses are often rejected for funding due to poor financial presentation, not poor performance.

This tool bridges that gap.

## Roadmap

- More risk models
- Industry benchmarks
- API integrations

## Before vs After

### Input (raw SME data)
CSV with revenue, expenses, debt

### Output (this tool)
- Risk Score
- DSCR
- Risk explanations
- Lender-ready summary
