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

Relays.app deployment

You can deploy this integration to relays.app as a scheduled job or as a triggered job. Two deployment options are common:

A) GitHub integration (recommended)
- Connect your GitHub repository in relays.app and point the job to the repository root or the `stock-screener/` subfolder.
- Set the entrypoint to the Python handler `stock-screener.relays_entry.handler` if relays.app supports module handlers. Otherwise, use the Docker deployment below.
- Configure environment variables in the relays.app UI (APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_API_BASE_URL, RUN_REAL, PAPER_CAPITAL, POSITION_PCT, SCAN_PATH).
- Set the schedule to run at 9:30 AM America/New_York if relays supports timezones, or use two UTC cron entries to cover DST:
  - EDT (approx Mar–Nov) 9:30 AM ET = 13:30 UTC
  - EST (approx Nov–Mar) 9:30 AM ET = 14:30 UTC
  Example (two cron entries):
    - 30 13 * 3-11 1-5  # 13:30 UTC Mon-Fri during DST months
    - 30 14 * 11,12,1,2 1-5  # 14:30 UTC Mon-Fri during standard time months

B) Docker upload
- Build and push the Docker image using the provided `stock-screener/Dockerfile`, or upload the image/zip in relays.app.
- Set the container command to run `/app/stock-screener/relays_entry.py` or the handler as appropriate.

Relays environment variables (set these in the relays UI)
- APCA_API_KEY_ID (required to enable real paper orders)
- APCA_API_SECRET_KEY (required)
- APCA_API_BASE_URL (optional, default https://paper-api.alpaca.markets)
- RUN_REAL (set "true" to actually place orders; default "false" for dry-run)
- PAPER_CAPITAL (optional; default 5000)
- POSITION_PCT (optional; default 0.10)
- SCAN_PATH (optional; default stock-screener/stocks_scan.csv)

Testing locally before deployment

- Run the handler locally to simulate relays.app:

  python -c "from stock_screener.relays_entry import handler; print(handler())"

  Or simply:

  python stock-screener/relays_entry.py

- Run the trade script in dry-run:

  python stock-screener/trade.py --scan stock-screener/stocks_scan.csv --dry-run

Notes & Safety

- Always test with dry-run and paper trading before enabling RUN_REAL.
- Do NOT commit API keys. Use relays.app environment variables/secret management.
- If you prefer a direct import (no subprocess), I can refactor trade.py to expose a run_trade(...) function so relays_entry can import and call it directly.
