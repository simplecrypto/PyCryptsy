# coding=iso-8859-1

# PyCryptsy Example
#
# Copyright © 2013 Scott Alfter
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import time as t
import logging

from PyCryptsy import PyCryptsy

public_key = 'TODO'
private_key = 'TODO'

api = PyCryptsy(public_key, private_key)

# Don't trade these currencies
non_traded_currencies = ('BTC', 'LTC')

# currencies to trade

#src_currencies = ['NVC', 'MNC', 'WDC', 'DGC', 'LKY', 'ARG', 'PXC', 'NRB']
dest_currency = "BTC"

# trade multiplier (set to 1 to trade at lowest buy price)
multiplier = 1
percent_to_sell = 1.0


def setup_logging():
    global console
    logging.basicConfig(filename='trades.log.txt', level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)


def get_non_zero_currencies():
    balances = api.get_available_balances()

    if not balances.has_key("return") or not balances["return"].has_key("balances_available"):
        logging.info("balances object doesn't have return/balances_available: " + str(balances))
        return None

    balances_available = balances["return"]["balances_available"] #CUR -> amt
    non_zero_currencies = {cur: float(coin_amt) for (cur, coin_amt) in balances_available.iteritems() if
                           float(coin_amt) > 0 and cur not in non_traded_currencies}

    return non_zero_currencies


# src_currencies dict of CUR -> amt available
def do_trades(src_currencies):
    print src_currencies
    for (currency, coins_available) in src_currencies.iteritems():
        # get target price
        target = api.get_buy_price(currency, dest_currency) * multiplier

        logging.info("Target: %s, Avail: %s" % (target, coins_available))
        if coins_available > 0:
            units_to_sell = coins_available * percent_to_sell
            logging.info(
                "Creating sell order from %s to %s, units: %d, target price: %d" % (currency, dest_currency, units_to_sell, target))
            result = api.create_sell_order(currency, dest_currency, units_to_sell, target)
            # {u'orderid': u'532446', u'moreinfo': u'Your Sell order has been placed for<br><b>353.81173381 NRB @ 0.00016990 BTC</b> each.<br>Order ID: <b>532446</b>', u'success': u'1'}
            logging.info("Result: OrderId: %s, Info: %s, Success: %s" % (result['orderid'], result['moreinfo'], result['success']))

# start trading
setup_logging()
while True:
    non_zero_currencies = get_non_zero_currencies()

    if non_zero_currencies is None:
        logging.info("Unable to get available balances")
    elif len(non_zero_currencies) == 0:
        logging.info("All balances == 0, doing no trading")
    else:
        do_trades(non_zero_currencies)

    logging.info("Sleeping for 180 seconds ...")
    t.sleep(180) # Sleep for 3 minutes