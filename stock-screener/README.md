# yfinance-screener — Alpaca Auto-Trade Integration

This branch adds an optional Alpaca paper trading integration that will:
- Read the screener "Stocks" scan CSV (default: stock-screener/stocks_scan.csv)
- Select the top pick (by score/rank or first row)
- Place a market buy bracket order on Alpaca with:
  - Take-profit: +5%
  - Stop-loss: -2%
- Position sizing: 10% of capital (default capital $5,000)

IMPORTANT: This is configured to use Alpaca PAPER trading by default. Do not commit secrets.

Setup

1. Install dependencies (recommended in a virtualenv):

   pip install -r stock-screener/requirements.txt

2. Configure Alpaca API keys as repository secrets (preferred) or environment variables:

   - APCA_API_KEY_ID  (Alpaca API Key ID)
   - APCA_API_SECRET_KEY  (Alpaca API Secret)
   - APCA_API_BASE_URL  (optional, default: https://paper-api.alpaca.markets)

3. Ensure your screener writes a CSV of the Stocks scan to stock-screener/stocks_scan.csv. The CSV must contain a symbol column named `symbol` or `ticker`.

Usage

- Dry run (default, does not submit orders):

  python stock-screener/trade.py --scan stock-screener/stocks_scan.csv --dry-run

- Execute a paper trade (ensure secrets/env vars are set):

  python stock-screener/trade.py --scan stock-screener/stocks_scan.csv --no-dry-run

Scheduling (GitHub Actions)

This branch adds a GitHub Actions workflow to run the trade automatically at 9:30 AM Eastern Time, Monday–Friday. Because GitHub cron uses UTC and US daylight saving time changes, the workflow schedules two UTC crons to cover both EST and EDT. See `.github/workflows/schedule-trade.yml`.

Be sure to set the repository secrets `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY` before enabling the workflow. The workflow will run the screener (if it can) and then the trading script.

Notes & Safety

- Always test using Alpaca paper trading before considering live trading.
- The default capital is $5,000; you can override via the `PAPER_CAPITAL` environment variable or the `--capital` CLI option.
- Never commit your API keys. Use repo secrets or a local `.env` excluded from git.
