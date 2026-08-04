#!/usr/bin/env python3
"""
trade.py
Alpaca integration for yfinance-screener:
- Reads a screener CSV (default: stocks_scan.csv)
- Chooses top pick (first row)
- Buys with an Alpaca paper account using a bracket order:
    - take_profit: +5%
    - stop_loss: -2%
- Default sizing: 10% of capital (default capital $5,000)
- Dry-run mode available (no orders sent)

Usage examples:
- Dry run (default): python stock-screener/trade.py --scan stock-screener/stocks_scan.csv --dry-run
- Live (paper) run: set APCA_API_KEY_ID and APCA_API_SECRET_KEY in repo secrets or env, then run:
    python stock-screener/trade.py --scan stock-screener/stocks_scan.csv --no-dry-run
"""
import os
import math
import argparse
import logging
from decimal import Decimal, ROUND_DOWN

import pandas as pd

try:
    from alpaca_trade_api.rest import REST
except Exception:
    REST = None  # Will check at runtime

# Configuration defaults
DEFAULT_CAPITAL = float(os.getenv("PAPER_CAPITAL", "5000"))
POSITION_PCT = float(os.getenv("POSITION_PCT", "0.10"))  # 10% of capital
TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", "0.05"))  # +5%
STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", "0.02"))  # -2%

# Alpaca env vars
APCA_KEY = os.getenv("APCA_API_KEY_ID")
APCA_SECRET = os.getenv("APCA_API_SECRET_KEY")
APCA_BASE = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def round_price(x):
    # Round to 2 decimal places in a safe way
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_DOWN))


def load_scan(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Screener CSV not found: {csv_path}")
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError("Screener CSV is empty")
    return df


def select_top_pick(df):
    # Prefer an explicit 'score' or 'rank' or otherwise take the first row
    for col in ("score", "Score", "rank", "Rank"):
        if col in df.columns:
            if "rank" in col.lower():
                df_sorted = df.sort_values(col, ascending=True)  # rank 1 best
            else:
                df_sorted = df.sort_values(col, ascending=False)
            top = df_sorted.iloc[0]
            return top
    # Fallback: take first row
    return df.iloc[0]


def get_last_price_yf(symbol):
    try:
        import yfinance as yf
    except Exception:
        raise RuntimeError("yfinance required to fetch last price; install yfinance")
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d", interval="1m")
    if data.empty:
        data = ticker.history(period="2d", interval="1d")
        if data.empty:
            raise RuntimeError(f"No price data for {symbol}")
    return float(data["Close"].iloc[-1])


def compute_shares_from_cash(cash_to_use, last_price):
    if last_price <= 0:
        raise ValueError("Invalid last price")
    shares = int(math.floor(cash_to_use / last_price))
    return max(shares, 0)


def create_alpaca_client():
    if not REST:
        raise RuntimeError("alpaca-trade-api is not installed (pip install alpaca-trade-api)")
    if not APCA_KEY or not APCA_SECRET:
        raise RuntimeError("APCA_API_KEY_ID and APCA_API_SECRET_KEY must be set in environment")
    api = REST(APCA_KEY, APCA_SECRET, APCA_BASE, api_version="v2")
    return api


def get_account_cash(api, fallback=DEFAULT_CAPITAL):
    try:
        acct = api.get_account()
        cash = float(acct.cash)
        logging.info(f"Alpaca account cash: {cash}")
        return cash
    except Exception as e:
        logging.warning(f"Could not fetch account cash from Alpaca, using fallback {fallback}: {e}")
        return fallback


def place_bracket_buy(api, symbol, qty, take_profit_price, stop_price):
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side="buy",
            type="market",
            time_in_force="gtc",
            order_class="bracket",
            take_profit={"limit_price": str(take_profit_price)},
            stop_loss={"stop_price": str(stop_price)},
        )
        logging.info(f"Submitted order: id={getattr(order, 'id', None)} status={getattr(order, 'status', None)}")
        return order
    except Exception as e:
        logging.exception("Failed to submit order")
        raise


def main():
    parser = argparse.ArgumentParser(description="Alpaca auto-trader for yfinance-screener top pick")
    parser.add_argument("--scan", default="stock-screener/stocks_scan.csv", help="Path to screener CSV (default: stock-screener/stocks_scan.csv)")
    parser.add_argument("--dry-run", action="store_true", default=True, help="If set, do not submit orders")
    parser.add_argument("--no-dry-run", dest="dry_run", action="store_false", help="Submit orders to Alpaca")
    parser.add_argument("--capital", type=float, default=DEFAULT_CAPITAL, help="Base capital if Alpaca account unavailable")
    parser.add_argument("--position-pct", type=float, default=POSITION_PCT, help="Fraction of capital to risk per trade")
    parser.add_argument("--take-profit-pct", type=float, default=TAKE_PROFIT_PCT, help="Take profit pct (decimal)")
    parser.add_argument("--stop-loss-pct", type=float, default=STOP_LOSS_PCT, help="Stop loss pct (decimal)")
    args = parser.parse_args()

    logging.info("Loading screener results from %s", args.scan)
    df = load_scan(args.scan)
    top = select_top_pick(df)

    # Ensure there is a symbol column
    symbol_col = None
    for c in ("symbol", "ticker", "Symbol", "Ticker"):
        if c in df.columns:
            symbol_col = c
            break
    if not symbol_col:
        raise ValueError("No symbol column found in screener CSV (expected 'symbol' or 'ticker')")

    symbol = str(top[symbol_col]).strip().upper()
    logging.info("Top pick symbol: %s", symbol)

    # Get a last price (prefer Alpaca market data if connected, otherwise yfinance)
    last_price = None
    if not args.dry_run and APCA_KEY and APCA_SECRET:
        try:
            api = create_alpaca_client()
            try:
                bar = api.get_latest_trade(symbol)
                if hasattr(bar, "price"):
                    last_price = float(bar.price)
            except Exception:
                last_price = None
        except Exception:
            last_price = None

    if last_price is None:
        last_price = get_last_price_yf(symbol)
    last_price = round_price(last_price)
    logging.info("Last price for %s: %s", symbol, last_price)

    # Determine capital to use
    account_cash = args.capital
    if not args.dry_run and APCA_KEY and APCA_SECRET:
        api = create_alpaca_client()
        account_cash = get_account_cash(api, fallback=args.capital)
    logging.info("Using account cash: %s", account_cash)

    cash_to_use = account_cash * args.position_pct
    logging.info("Position cash (%.1f%%): %s", args.position_pct * 100, cash_to_use)

    shares = compute_shares_from_cash(cash_to_use, last_price)
    if shares <= 0:
        raise RuntimeError("Computed 0 shares for position; aborting")

    take_price = round_price(last_price * (1 + args.take_profit_pct))
    stop_price = round_price(last_price * (1 - args.stop_loss_pct))

    logging.info("Preparing bracket buy: symbol=%s shares=%s entry~%s take=%s stop=%s",
                 symbol, shares, last_price, take_price, stop_price)

    if args.dry_run:
        logging.info("Dry-run enabled — no order will be submitted.")
        logging.info("DRY RUN: would submit bracket market buy for %s qty=%s take=%s stop=%s", symbol, shares, take_price, stop_price)
        return

    # Submit order
    if APCA_KEY and APCA_SECRET:
        api = create_alpaca_client()
        order = place_bracket_buy(api, symbol, shares, take_price, stop_price)
        logging.info("Order submitted: %s", order)
    else:
        raise RuntimeError("APCA API keys not configured in environment")


if __name__ == "__main__":
    main()
