import csv
from datetime import datetime

def init_logger(path):
    f = open(path, "a", newline="")
    writer = csv.DictWriter(f, fieldnames = [
    "timestamp", "asset", "signal",
    "mid_price", "exec_price",
    "direction", "size",
    "pnl", "position",
    "exit_reason"])
    if f.tell() == 0:
        writer.writeheader()
    return f, writer

def log_trade(writer, asset, trade, position, signal):
    writer.writerow({
    "timestamp": datetime.utcnow().isoformat(),
    "asset": asset,
    "signal": signal,
    "mid_price": trade.get("mid_price"),
    "exec_price": trade.get("price"),
    "direction": trade["direction"],
    "size": trade["size"],
    "pnl": trade.get("realized_pnl", 0.0),
    "position": position,
    "exit_reason": trade.get("exit_reason", "")
})


