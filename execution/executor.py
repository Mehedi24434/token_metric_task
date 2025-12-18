def estimate_execution_price(orderbook, side, order_size):
    """
    Estimate VWAP execution price using Hyperliquid L2 order book.
    side: 'BUY' or 'SELL'
    order_size: base asset size
    """

    levels = orderbook.get("levels")
    if not levels or len(levels) != 2:
        return None

    bids, asks = levels

    # BUY → consume asks (lowest price first)
    # SELL → consume bids (highest price first)
    book = asks if side == "BUY" else bids

    remaining = order_size
    cost = 0.0
    filled = 0.0

    for lvl in book:
        px = float(lvl["px"])
        sz = float(lvl["sz"])

        take = min(sz, remaining)
        cost += take * px
        filled += take
        remaining -= take

        if remaining <= 0:
            break

    if filled == 0:
        return None

    return cost / filled



def execute_trade(asset, target_pos, mid_price, state, orderbook,
                  max_position_usd, tp_pct, sl_pct):

    size = max_position_usd / mid_price
    pos = state[asset]["position"]

    # ENTRY
    if pos == 0 and target_pos == 1:
        px = estimate_execution_price(orderbook, "BUY", size)
        if px is None:
            return None

        state[asset]["position"] = 1
        state[asset]["entry_price"] = px
        state[asset]["trades"] += 1

        return {
            "direction": "BUY",
            "price": px,
            "mid_price": mid_price,
            "size": size,
            "exit_reason": ""
        }

    # EXIT
    if pos == 1:
        entry = state[asset]["entry_price"]
        pnl_pct = (mid_price - entry) / entry

        if pnl_pct >= tp_pct:
            reason = "TAKE_PROFIT"
        elif pnl_pct <= -sl_pct:
            reason = "STOP_LOSS"
        elif target_pos == 0:
            reason = "TREND_EXIT"
        else:
            return None

        px = estimate_execution_price(orderbook, "SELL", size)
        if px is None:
            return None

        pnl = (px - entry) * size
        state[asset]["pnl"] += pnl
        state[asset]["position"] = 0
        state[asset]["entry_price"] = None
        state[asset]["trades"] += 1

        return {
            "direction": "SELL",
            "price": px,
            "mid_price": mid_price,
            "size": size,
            "realized_pnl": pnl,
            "exit_reason": reason
        }

    return None

