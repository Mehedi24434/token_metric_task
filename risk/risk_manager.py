def max_trades_reached(state, asset, max_trades):
    return state[asset]["trades"] >= max_trades

def drawdown_exceeded(state, starting_capital, max_dd_pct):
    total_pnl = sum(v["pnl"] for v in state.values())
    return total_pnl < -starting_capital * max_dd_pct / 100
