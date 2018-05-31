from pywhaleclub import *
import sys
import csv

key = "841a7dae-67fa-4d31-963b-4b76ff0ccb41"

pw = Client(key)

print(pw.get_balance())
print(pw.get_price('BTC-USD'))

def run_experiment(num_trades, cum_pnl, mean_pnl, num_pnls, sd_pnl, t_stat, cbv, fast_ema_weight, slow_ema_weight):
    STARTING_BALANCE_USD = 10000
    MIN_POINTS_TO_PRIME_EMA = 1000


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
                num_trades+=1

            if sell_signal and (not buy_signal):
                balance_usd += balance_btc * n['low_price']
                balance_btc = 0
                #num_trades+=1

            # Buy signal if fast EMA crosses from blow to above slow EMA - vice versa for Sell signal
            buy_signal = (not buy_signal) and (fast_ema > slow_ema) and (prev_fast_ema <= prev_slow_ema)
            sell_signal = (not sell_signal) and (fast_ema < slow_ema) and (prev_fast_ema >= prev_slow_ema)

            '''
            # Update PnLs
            unrealized_balance_usd = balance_usd + balance_btc * n['weighted_price']
            prev_unrealized_pnl = unrealized_pnl
            unrealized_pnl = (unrealized_balance_usd - STARTING_BALANCE_USD) / STARTING_BALANCE_USD
            this_pnl = unrealized_pnl - prev_unrealized_pnl
            #pnls.push_back(this_pnl);

            cum_pnl = unrealized_pnl
            '''

    return (balance_usd, [slow_ema_weight, fast_ema_weight, num_trades])

def main():
    cbv = {}
    try:
        cbv = load(sys.argv[1])
    except IndexError:
        print("Usage: python3 trade.py <input-file>")
    except FileNotFoundError:
        print("No file named '{}'".format(sys.argv[1]))
    cum_pnl = 0
    mean_pnl = 0
    sd_pnl = 0
    t_stat = 0
    num_pnls = 0
    num_trades = 0


    slowest_ema_weight = 1.0 / (60.0*24.0*7.0) # Roughly 1 week at a data point per minute
    fastest_ema_weight = 1.0 # Ignore all history and just use the latest data point

    # Seed with a reasonable set of weights
    #double fast_ema_weight = 0.01;
    #double slow_ema_weight = 0.0001;
    #double fast_ema_weight = 0.008;
    #double slow_ema_weight = 0.003;
    fast_ema_weight = 0.00703268
    slow_ema_weight = 0.00443511


    results = run_experiment(num_trades, cum_pnl, mean_pnl, num_pnls, sd_pnl, t_stat, cbv, fast_ema_weight, slow_ema_weight);

    print('''
    End balance: {}
    fast_ema_weight: {}
    slow_ema_weight: {}
    num_trades = {}
    '''.format(results[0],results[1][1], results[1][0], results[1][2]))



def load(name):
    cbv = []
    with open(name, mode='r') as f:
        reader = csv.reader(f)
        for line in reader:
            linedict = {'timestamp': float(line[0]), 'open_price': float(line[1]), 'high_price': float(line[2]), 'low_price': float(line[3]), 'close_price': float(line[3]), 'volume_btc': float(line[4]), 'volume_usd': float(line[5]), 'weighted_price': float(line[6])}
            cbv.append(linedict)
    return cbv

main()
