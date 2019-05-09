# Algorithm
# Slow and fast moving exponential average, when fast crosses slow, indicates buy or sell depending on direction

import random
import sys
import time
import multiprocessing
import os
import pandas as pd


class Trader:
    def __init__(self, data):
        self.data = data

    def buy(self):
        pass

    def sell(self):
        pass


def buy(usd, price):
    # print('BOUGHT')
    btc = usd / price
    return (0, btc)


def sell(btc, price):
    # print('SOLD')
    usd = btc * price - 0.25
    # print(usd)
    return (usd, 0)


def value(btc, usd, price):
    if btc == 0:
        return usd

    else:
        return usd + (btc * price)


def run(fast, slow, file):
    data = load_data_pd_read_csv(file)
    data = data.itertuples()

    initial_price = next(data)[2]
    slow_ma = initial_price
    fast_ma = initial_price

    direction = ''

    usd = 10000
    btc = 0

    prev_value = value(btc, usd, initial_price)
    maxgain = 0
    maxloss = 0
    trades = 0

    for row in data:
        price = row[2]

        if trades >= 1000:
            return (value(btc, usd, price))

        if usd < 0:
            quit()

        if btc < 0:
            quit()


        fast_ma = price * fast + fast_ma * (1 - fast)
        slow_ma = price * slow + slow_ma * (1 - slow)

        if fast_ma > slow_ma:

            if direction != 'rising':
                trades += 1
                usd, btc_delta = buy(usd, price)
                btc += btc_delta

            direction = 'rising'

        else:

            if direction != 'falling':
                trades += 1
                usd_delta, btc = sell(btc, price)
                usd += usd_delta

            direction = 'falling'

        if value(btc, usd, price) != prev_value:
            delta = value(btc, usd, price) - prev_value
            if delta < maxloss:
                maxloss = delta
            if delta > maxgain:
                maxgain = delta

        '''
        if row[0] % 100 == 0:
            usd_delta, btc = sell(btc, price)
            usd += usd_delta

            dif = usd - 10000
            cashout += dif
            usd = 10000
        '''

        # print(f'fast_ma: {fast_ma} slow_ma: {slow_ma} price: {price} USD: {usd} BTC: {btc} Loss: {maxloss} Gain: {maxgain} Cashout: {cashout}')


def load_data_pd_read_csv(file):
    names = ['time', 'price', 'low', 'close', 'volumeBTC', 'volumeUSD', 'weightedPrice']
    return pd.read_csv(file, header=None, names=names, dtype={'time': float, 'price': float, 'low': float, 'close': float,
                                                              'volumeBTC': float, 'volumeUSD': float, 'weightedPrice': float},
                       skiprows=[0,1], delimiter=',')


if __name__ == '__main__':
    file_path = os.getcwd()
    files = ['oneyearofdata.csv']
    best = 0

    while True:
        big = random.uniform(0, .2)
        small = random.uniform(0, 1) * big

        total_profit = 0
        for file in files:
            file = os.path.join(file_path, file)
            results = run(big, small, file)
            total_profit += results - 10000
            print(f'FILE: {file} RETURNS: {results} ({round(((results / 10000) * 100) - 100, 4)}%)')

        print(f'TOTAL PROFIT: {total_profit}')

        print(f'FAST: {big} SLOW: {small}\n')
