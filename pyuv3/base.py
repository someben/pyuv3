#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

'''
Stateless functions that are used throughout the Uniswap V3 pool and position
classes.
'''

def calc_tick_price(tick):
    '''
    Price a certain, signed-integer tick index represents.
    '''
    return 1.0001 ** int(tick)


def calc_tick_adj_price(tick, decimals0, decimals1):
    '''
    Human readable, adjusted price at a certain signed-integer tick. This
    accounts for the decimal powers of two towens in a pool.
    '''
    price = calc_tick_price(tick)
    return price * (10 ** (int(decimals0) - int(decimals1)))


def calc_tick_inv_adj_price(tick, decimals0, decimals1):
    '''
    Human readable, adjusted inverse seprice at a certain signed-integer tick.
    This accounts for the decimal powers of two towens in a pool.
    '''
    return 1.0 / calc_tick_adj_price(tick, decimals0, decimals1)


def calc_price_tick(price):
    '''
    Tick index for a price, as a signed integer. To be called with "unadjusted"
    prices, which have not been scaled by the difference between the decimal
    powers of the two tokens in a pool.
    '''
    return int(np.floor(np.log(float(price)) / np.log(1.0001)))


def calc_adj_price_tick(adj_price, decimals0, decimals1):
    '''
    Tick index for an adjusted price, as a signed integer. This can be called
    with a human readable price and the decimal scaling of a pool.
    '''
    price = adj_price * (10 ** (int(decimals1) - int(decimals0)))
    return calc_price_tick(price)


def calc_inv_adj_price_tick(inv_adj_price, decimals0, decimals1):
    '''
    Tick index for the inverse of an an adjusted price, as a signed integer. This
    can be called with a human readable inverse price and the decimal scaling of
    a pool.
    '''
    return calc_adj_price_tick(1.0 / inv_adj_price, decimals0, decimals1)


def calc_fee_tier_tick_spacing(fee_tier):
    '''
    Calculate the spacing between activate-able ticks based upon the fee tier
    of a pool.
    '''
    return {
        500: 10,
        3000: 60,
        10000: 200,
    }[int(fee_tier)]

