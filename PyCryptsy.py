# coding=iso-8859-1

# PyCryptsy: a Python binding to the Cryptsy API
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

import time
import hmac
import hashlib
import urllib
import requests


class PyCryptsy:
    # constructor (Key: API public key, Secret: API private key)
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    # issue any supported query (method: string, req: dictionary with method parameters)
    def Query(self, method, req):
        req["method"] = method
        req["nonce"] = int(time.time())
        sign = hmac.new(self.secret, urllib.urlencode(req), hashlib.sha512).hexdigest()
        headers = {"Sign": sign, "Key": self.key}
        r = requests.post("https://api.cryptsy.com/api", data=req, params=req, headers=headers)
        r.raise_for_status()  # raise exception if any HTTP 4XX or 5XX
        return r.json()

    # get market ID (return None if not found)
    def get_market_id(self, src, dest):
        try:
            r = self.Query("getmarkets", {})
            mkt_id = None
            for i, market in enumerate(r["return"]):
                if market["primary_currency_code"].upper() == src.upper() and \
                        market["secondary_currency_code"].upper() == dest.upper():
                    mkt_id = market["marketid"]
            return mkt_id
        except:
            return None

    # get buy price for a currency pair
    def get_buy_price(self, src, dest):
        mktid = self.get_market_id(src, dest)
        if mktid is None:
            return 0
        try:
            r = self.Query("marketorders", {"marketid": mktid})
            return float(r["return"]["buyorders"][0]["buyprice"])
        except:
            return 0

    # get sell price for a currency pair
    def get_sell_price(self, src, dest):
        mktid = self.get_market_id(src, dest)
        if mktid is None:
            return 0
        try:
            r = self.Query("marketorders", {"marketid": mktid})
            return float(r["return"]["sellorders"][0]["sellprice"])
        except:
            return 0

    # get available balance for a currency
    def get_available_balance(self, curr):
        try:
            r = self.Query("getinfo", {})
            return float(r["return"]["balances_available"][curr.upper()])
        except:
            return 0

    def get_available_balances(self):
        try:
            r = self.Query("getinfo", {})
            return r
        except:
            return 0

    # create a sell order
    def create_sell_order(self, src, dest, qty, price):
        try:
            return self.Query("createorder",
                              {"marketid": self.get_market_id(src, dest), "ordertype": "Sell", "quantity": qty,
                               "price": price})
        except:
            return None

    # create a buy order
    def create_buy_order(self, src, dest, qty, price):
        try:
            return self.Query("createorder",
                              {"marketid": self.get_market_id(src, dest), "ordertype": "Buy", "quantity": qty,
                               "price": price})
        except:
            return None

    # get current open sell and buy orders for market listing
    def get_my_orders(self, src, dest):
        try:
            return self.Query("myorders", {"marketid": self.get_market_id(src, dest)})
        except:
            return None

    # cancel market orders for specified market listing
    def cancel_market_orders(self, src, dest):
        try:
            return self.Query("cancelmarketorders", {"marketid": self.get_market_id(src, dest)})
        except:
            return None

    # cancel specific order id
    def cancel_order(self, orderid):
        try:
            return self.Query("cancelmarketorders", {"orderid": orderid})
        except:
            return None

    # cancel all open orders
    def cancel_all_orders(self):
        try:
            return self.Query("cancelallorders")
        except:
            return None
