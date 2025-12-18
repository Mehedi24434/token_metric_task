import time
import yaml
import signal
import sys
from collections import deque

from data.hyperliquid import (
    fetch_mids,
    fetch_orderbook
)

from strategy.trend_volatility import (
    compute_ema,
    compute_volatility,
    compute_rsi,
    generate_signal
)

from execution.executor import execute_trade
from risk.risk_manager import max_trades_reached, drawdown_exceeded
from logger.trade_logger import init_logger, log_trade

from datetime import datetime

import time
START_TIME = time.time()
MAX_RUNTIME_SECONDS = 7 * 60 * 60  # 7 hours

# =========================
# LOAD CONFIG
# =========================


def status_print(
    asset,
    price,
    ema,
    vol_rsi,
    signal_pos,
    position,
    trade=None
):
    ts = datetime.utcnow().strftime("%H:%M:%S")

    ema_str = f"{ema:.2f}" if ema is not None else "NA"
    vol_rsi_str = f"{vol_rsi:.1f}" if vol_rsi is not None else "NA"


    msg = (
        f"[{ts}] {asset} | "
        f"Mid: {price:.2f} | "
        f"EMA: {ema_str} | "
        f"Vol_RSI: {vol_rsi_str} | "
        f"Signal: {'LONG' if signal_pos else 'FLAT'} | "
        f"Position: {position}"
    )

    if trade:
        exec_px = trade.get("price")
        slip = trade.get("slippage", 0.0)
        reason = trade.get("exit_reason", "ENTRY")

        msg += (
            f" | TRADE: {trade['direction']} "
            f"@ {exec_px:.2f} "
            f"(slip {slip:.2f}) [{reason}]"
        )

    print(msg)

with open("config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

ASSETS = cfg["assets"]
STRAT = cfg["strategy"]
EXEC = cfg["execution"]
RISK = cfg["risk"]
LOGGING = cfg["logging"]



# =========================
# STATE
# =========================

price_history = {
    a: deque(maxlen=STRAT["sma_window"]) for a in ASSETS
}
vol_history = {
    a: deque(maxlen=STRAT["vol_window"]) for a in ASSETS
}
state = {
    a: {"position": 0, "entry_price": None, "pnl": 0.0, "trades": 0}
    for a in ASSETS
}


# =========================
# LOGGER
# =========================

log_file, log_writer = init_logger(LOGGING["trade_log_path"])


# =========================
# GRACEFUL SHUTDOWN
# =========================

def shutdown_handler(sig, frame):
    print("\nGraceful shutdown triggered. Closing log file...")
    log_file.close()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)


# =========================
# MAIN LOOP
# =========================

print("Starting paper trading loop...")

while True:
    mids = fetch_mids()

    for asset, params in ASSETS.items():
        price = float(mids[asset])
        price_history[asset].append(price)

        vol = compute_volatility(list(price_history[asset]))
        if vol is not None:
            vol_history[asset].append(vol)


        ema = compute_ema(list(price_history[asset]), STRAT["ema_window"])
        vol_rsi = compute_rsi(list(vol_history[asset]), STRAT["vol_rsi_window"])

        signal_pos = generate_signal(price, ema, vol_rsi)

        # Risk: max trades per asset
        if max_trades_reached(state, asset, RISK["max_trades_per_asset"]):
            continue

        orderbook = fetch_orderbook(asset)

        trade = execute_trade(
            asset=asset,
            target_pos=signal_pos,
            mid_price=price,
            state=state,
            orderbook=orderbook,
            max_position_usd=params["max_position_usd"],
            tp_pct=EXEC["take_profit_pct"],
            sl_pct=EXEC["stop_loss_pct"]
        )
        
        status_print(
            asset=asset,
            price=price,
            ema=ema,
            vol_rsi=vol_rsi,
            signal_pos=signal_pos,
            position=state[asset]["position"],
            trade=trade
        )


        if trade:
            log_trade(
                writer=log_writer,
                asset=asset,
                trade=trade,
                position=state[asset]["position"],
                signal=signal_pos,
            )

        # Portfolio-level drawdown stop
    if drawdown_exceeded(
        state,
        RISK["starting_capital"],
        RISK["max_drawdown_pct"]
    ):
        print("Drawdown limit hit. Stopping.")
        break

    # Max runtime stop
    if time.time() - START_TIME > MAX_RUNTIME_SECONDS:
        print("Max runtime reached. Stopping.")
        break

    time.sleep(EXEC["loop_interval_seconds"])


# Final flush
log_file.close()
print("Trading session ended cleanly.")
