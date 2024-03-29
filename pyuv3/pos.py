#!/usr/bin/env python
# -*- coding: utf-8 -*-

import contextlib
import numpy as np

import pyuv3
from pyuv3.flowint import UFlow
import pyuv3.thegraph as thegraph


class UniswapV3Position():
    '''
    Represents a single live, concentrated liquidity provision position in a single
    pool on Uniswap V3. Initialized with the position ID (i.e. NFT ID).
    '''

    def __init__(self, nft_id):
        self.nft_id = nft_id

    def calc_liq(tick, min_tick, max_tick, amt0, amt1):
        '''
        Calculate the (virtual) liquidity for a concentrated liquidity provision
        position, the L variable used throughout the white papers.
        '''

        sqrt_price, sqrt_min_price, sqrt_max_price = \
            [pyuv3.calc_tick_price(x) ** 0.5 for x in [tick, min_tick, max_tick]]
        if tick <= min_tick:
            return amt0 * ((sqrt_min_price * sqrt_max_price) / (sqrt_max_price - sqrt_min_price))
        elif tick >= max_tick:
            return amt1 / (sqrt_max_price - sqrt_min_price)
        else:
            liq0 = amt0 * ((sqrt_price * sqrt_max_price) / (sqrt_max_price - sqrt_price))
            liq1 = amt1 / (sqrt_price - sqrt_min_price)
            return np.min([liq0, liq1])

    def calc_fees(
        liquidity,
        current_tick, min_tick, max_tick,
        global_fee_growth0x128, global_fee_growth1x128,
        min_tick_fee_growth_outside0x128, min_tick_fee_growth_outside1x128,
        max_tick_fee_growth_outside0x128, max_tick_fee_growth_outside1x128,
        fee_growth_inside_last0x128, fee_growth_inside_last1x128,
        decimals0, decimals1,
    ):
        '''
        Calculate the accumulated fee income in a Uniswap V3 liquidity provision position,
        across the two tokens in the pool.

        Based on 'https://gist.github.com/Lucas-Kohorst/3b2727eaa60edebc27b21c7195261865/' but
        with bug fixes around under- and over-flow.
        '''

        # Check out the relevant formulas below which are from Uniswap Whitepaper Section 6.3 and 6.4
        # 𝑓𝑟 = 𝑓𝑔−𝑓𝑏(𝑖𝑙)−𝑓𝑎(𝑖𝑢)
        # 𝑓𝑢 = 𝑙·(𝑓𝑟(𝑡1)−𝑓𝑟(𝑡0))

        # Global fee growth per liquidity '𝑓𝑔' for both token 0 and token 1
        global_fee_growth0 = UFlow(global_fee_growth0x128, num_bits=256)
        global_fee_growth1 = UFlow(global_fee_growth1x128, num_bits=256)

        # Fee growth outside '𝑓𝑜' of our lower tick for both token 0 and token 1
        min_tick_fee_growth_outside0 = UFlow(min_tick_fee_growth_outside0x128, num_bits=256)
        min_tick_fee_growth_outside1 = UFlow(min_tick_fee_growth_outside1x128, num_bits=256)

        # Fee growth outside '𝑓𝑜' of our upper tick for both token 0 and token 1
        max_tick_fee_growth_outside0 = UFlow(max_tick_fee_growth_outside0x128, num_bits=256)
        max_tick_fee_growth_outside1 = UFlow(max_tick_fee_growth_outside1x128, num_bits=256)

        # NOTE assume intermediate values need to over- or under-flow the same as e.g. feeGrowthGlobal
        # These are '𝑓𝑏(𝑖𝑙)' and '𝑓𝑎(𝑖𝑢)' from the formula for both token 0 and token 1
        min_tick_fee_growth_below0, min_tick_fee_growth_below1 = UFlow(0, num_bits=256), UFlow(0, num_bits=256)
        max_tick_fee_growth_above0, max_tick_fee_growth_above1 = UFlow(0, num_bits=256), UFlow(0, num_bits=256)

        # These are the calculations for '𝑓𝑎(𝑖)' from the formula for both token 0 and token 1
        if current_tick >= max_tick:
            max_tick_fee_growth_above0 = global_fee_growth0 - max_tick_fee_growth_outside0
            max_tick_fee_growth_above1 = global_fee_growth1 - max_tick_fee_growth_outside1
        else:
            max_tick_fee_growth_above0 = max_tick_fee_growth_outside0
            max_tick_fee_growth_above1 = max_tick_fee_growth_outside1

        # These are the calculations for '𝑓b(𝑖)' from the formula for both token 0 and token 1
        if current_tick >= min_tick:
            min_tick_fee_growth_below0 = min_tick_fee_growth_outside0
            min_tick_fee_growth_below1 = min_tick_fee_growth_outside1
        else:
            min_tick_fee_growth_below0 = global_fee_growth0 - min_tick_fee_growth_outside0
            min_tick_fee_growth_below1 = global_fee_growth1 - min_tick_fee_growth_outside1

        # Calculations for '𝑓𝑟(𝑡1)' part of the '𝑓𝑢 = 𝑙·(𝑓𝑟(𝑡1)−𝑓𝑟(𝑡0))' formula for both token 0 and token 1
        fr_t1_0 = global_fee_growth0 - min_tick_fee_growth_below0 - max_tick_fee_growth_above0
        fr_t1_1 = global_fee_growth1 - min_tick_fee_growth_below1 - max_tick_fee_growth_above1

        # '𝑓𝑟(𝑡0)' part of the '𝑓𝑢 =𝑙·(𝑓𝑟(𝑡1)−𝑓𝑟(𝑡0))' formula for both token 0 and token 1
        fee_growth_inside_last0 = UFlow(fee_growth_inside_last0x128, num_bits=256)
        fee_growth_inside_last1 = UFlow(fee_growth_inside_last1x128, num_bits=256)

        # Calculations for the '𝑓𝑢 = 𝑙·(𝑓𝑟(𝑡1)−𝑓𝑟(𝑡0))' uncollected fees formula for both token 0 and token 1
        fees0 = int(liquidity) * ((fr_t1_0 - fee_growth_inside_last0).num / (2 ** 128))
        fees1 = int(liquidity) * ((fr_t1_1 - fee_growth_inside_last1).num / (2 ** 128))

        # Decimal adjustment to get final results
        adj_fees0 = fees0 / (10 ** int(decimals0))
        adj_fees1 = fees1 / (10 ** int(decimals1))

        return dict(
            token0=adj_fees0, token1=adj_fees1,
        )

    def calc_withdrawable_toks(liquidity, current_tick, min_tick, max_tick, sqrt_price_x96, decimals0, decimals1):
        '''
        Calculate the amount of each token that could be withdrawn from
        a Uniswap V3 liquidity position. Based on a Discord conversation
        with @Crypto_Rachel on #dev-chat on Uniswap.
        '''
        sqrt_price = int(sqrt_price_x96) / (2 ** 96) 
        sqrt_min_price = pyuv3.calc_tick_price(min_tick) ** 0.5
        sqrt_max_price = pyuv3.calc_tick_price(max_tick) ** 0.5

        amt0, amt1 = 0, 0
        if current_tick <= min_tick:
            amt0 = np.floor(int(liquidity) * ((sqrt_max_price - sqrt_min_price) / (sqrt_min_price * sqrt_max_price)))
        elif current_tick >= max_tick:
            amt1 = np.floor(int(liquidity) * (sqrt_max_price - sqrt_min_price))
        else:  # (current_tick > min_tick) and (current_tick < max_tick):
            amt0 = np.floor(int(liquidity) * ((sqrt_max_price - sqrt_price) / (sqrt_price * sqrt_max_price)))
            amt1 = np.floor(int(liquidity) * (sqrt_price - sqrt_min_price))

        adj_amt0 = amt0 / (10 ** int(decimals0))
        adj_amt1 = amt1 / (10 ** int(decimals1))

        return dict(
            token0=adj_amt0, token1=adj_amt1,
        )   

    def get_thegraph_query(self):
        '''
        Return a comprehensive GraphQL query for the current state of this Uniswap V3 liquidity
        provision position (NFT).
        '''
        # doubling the curly brackets to get f-string interpolation
        query = f"""
            query uniswapV3Position($nft_id: ID!) {{
                position(id: $nft_id) {{
                    token0 {{
                        decimals
                    }}
                    token1 {{
                        decimals
                    }}
                    pool {{
                        sqrtPrice
                        tick
                        feeGrowthGlobal0X128
                        feeGrowthGlobal1X128
                    }}
                    liquidity
                    feeGrowthInside0LastX128
                    feeGrowthInside1LastX128
                    tickLower {{
                        tickIdx
                        feeGrowthOutside0X128
                        feeGrowthOutside1X128
                    }}
                    tickUpper {{
                        tickIdx
                        feeGrowthOutside0X128
                        feeGrowthOutside1X128
                    }}
                }}
            }}
            """
        return query

    @contextlib.contextmanager
    def thegraph_results(self):
        result = thegraph.query(self.get_thegraph_query(), nft_id=self.nft_id)
        pos = result['position']
        pool = pos['pool']
        yield pos, pool

    def get_fees(self):
        '''
        Query this liquidity provision position (NFT) for the current fee income.
        '''
        with self.thegraph_results() as (pos, pool):
            return UniswapV3Position.calc_fees(
                pos['liquidity'],
                pool['tick'], pos['tickLower']['tickIdx'], pos['tickUpper']['tickIdx'],
                pool['feeGrowthGlobal0X128'], pool['feeGrowthGlobal1X128'],
                pos['tickLower']['feeGrowthOutside0X128'], pos['tickLower']['feeGrowthOutside1X128'],
                pos['tickUpper']['feeGrowthOutside0X128'], pos['tickUpper']['feeGrowthOutside1X128'],
                pos['feeGrowthInside0LastX128'], pos['feeGrowthInside1LastX128'],
                pos['token0']['decimals'], pos['token1']['decimals'],
            )

    def get_withdrawable_toks(self):
        '''
        Query this liquidity provision position (NFT) for the current amount of
        withdrawable tokens.
        '''
        with self.thegraph_results() as (pos, pool):
            return UniswapV3Position.calc_withdrawable_toks(
                pos['liquidity'],
                pool['tick'], pos['tickLower']['tickIdx'], pos['tickUpper']['tickIdx'],
                pool['sqrtPrice'],
                pos['token0']['decimals'], pos['token1']['decimals'],
            )

    def calc_amt1(price, min_price, max_price, amt0):
        '''
        Given an amount of token0 and a desired liquidity provision range, calculate
        the amount of token1 needed in order to provide liquidity at that range.
        '''
        sqrt_price, sqrt_min_price, sqrt_max_price = [p ** 0.5 for p in [price, min_price, max_price]]
        top_liq = amt0 * ((sqrt_price * sqrt_max_price) / (sqrt_max_price - sqrt_price))
        amt1 = top_liq * (sqrt_price - sqrt_min_price)
        return amt1

