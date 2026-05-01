# Quick Start Guide

## Step 1: Add Your API Key

Edit `.env` and add your Anthropic API key:

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
```

Get your key from: https://console.anthropic.com/

## Step 2: Test with Sample Data

```bash
cd code/
python main.py --sample
```

Expected output:
- Console: progress bar + summary stats
- File: `../support_tickets/output.csv` with results

## Step 3: Run on Full Dataset

```bash
cd code/
python main.py
```

This processes `../support_tickets/support_tickets.csv` and creates `../support_tickets/output.csv`

## Troubleshooting

**"ANTHROPIC_API_KEY not set"**
→ Add your key to .env file

**"ModuleNotFoundError: No module named 'anthropic'"**
→ Run: `pip install -r requirements.txt`

**"No relevant documentation found"**
→ This is expected for truly out-of-scope issues (escalates automatically)

## Output Format

CSV columns:
- `Status`: `replied` or `escalated`
- `Product Area`: category (e.g., "api", "billing")  
- `Response`: full user-facing answer
- `Justification`: why this decision was made
- `Request Type`: `product_issue`, `feature_request`, `bug`, `invalid`

## Performance

- First run: ~5-10 seconds (builds FAISS index)
- Per ticket: ~2-3 seconds
- 100 tickets: ~4-5 minutes total
