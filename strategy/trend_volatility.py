import numpy as np

def compute_ema(prices, window):
    if not prices:
        return None
    alpha = 2 / (window + 1)
    ema = prices[0]
    for p in prices[1:]:
        ema = alpha * p + (1 - alpha) * ema
    return ema

def compute_volatility(prices):
    if len(prices) < 2:
        return None
    returns = np.diff(prices) / prices[:-1]
    return np.std(returns)

def compute_rsi(series, window):
    if len(series) < window + 1:
        return None
    deltas = np.diff(series)
    gains = np.maximum(deltas, 0)
    losses = np.maximum(-deltas, 0)
    avg_gain = np.mean(gains[-window:])
    avg_loss = np.mean(losses[-window:])
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def generate_signal(price, ema, vol_rsi):
    """
    Entry logic:
    - Trend confirmation via EMA
    - Elevated volatility regime
    """
    trend_ok = ema is not None and price > ema
    volatility_ok = vol_rsi is not None and vol_rsi > 60

    return 1 if (trend_ok and volatility_ok) else 0
