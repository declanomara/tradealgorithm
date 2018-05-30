from pywhaleclub import *

key = "841a7dae-67fa-4d31-963b-4b76ff0ccb41"

pw = Client(key)

print(pw.get_balance())
print(pw.get_price('BTC-USD'))

def run_experiment(num_trades, cum_pnl, mean_pnl, num_pnls, sd_pnl, t_stat, cbv, fast_ema_weight, slow_ema_weight):
    # Declare the EMAs and define their weights based on parameters that were provided
    prev_fast_ema = 0
    fast_ema = 0
    fast_ema_history_weight = 1 - fast_ema_weight
    prev_slow_ema = 0
    slow_ema = 0
    slow_ema_history_weight = 1 - slow_ema_weight

    # Reset number of trades
    num_trades = 0

    # Ensure we use at least a minimum number of data points to prime the EMAs
    num_primers = 0
    ema_primed = False

    # Starting balance
    balance_usd = STARTING_BALANCE_USD
    balance_btc = 0

    # No signals yet
    buy_signal = False
    sell_signal = False

    pnls = []

    prev_unrealized_pnl = 0
    unrealized_pnl = 0
    this_pnl = 0

    # Iterate and print values of vector
    for n in cbv:
        prev_slow_ema = slow_ema
        prev_fast_ema = fast_ema
        slow_ema = slow_ema_history_weight * slow_ema + slow_ema_weight * n['weighted_price']
        fast_ema = fast_ema_history_weight * fast_ema + fast_ema_weight * n['weighted_price']

        if not ema_primed:
            num_primers += 1
            ema_primed = num_primers > MIN_POINTS_TO_PRIME_EMA

        if ema_primed:
            # If there was a buy signal, and holding USD, then move to BTC or vice versa for sell signal
            # always use the worst price for this time period

            if buy_signal and (not sell_signal):
                balance_btc += balance_usd / n['high_price']
                balance_usd = 0

            if sell_signal and (not buy_signal):
                balance_usd += balance_btc * n['low_price']
                balance_btc = 0

            # Buy signal if fast EMA crosses from blow to above slow EMA - vice versa for Sell signal
                buy_signal = (not buy_signal) and (fast_ema > slow_ema) and (prev_fast_ema <= prev_slow_ema)
                sell_signal = (not sell_signal) and (fast_ema < slow_ema) and (prev_fast_ema >= prev_slow_ema)
