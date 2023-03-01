#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from pyuv3.flowint import IFlow128, UFlow128
import pyuv3.thegraph as thegraph

class UniswapV3Pool():
    '''
    Represents a single live, concentrated liquidity provision pool
    on Uniswap V3. Initialized with the pool ID (i.e. contract address).
    '''

    def __init__(self, addr, ticks=None):
        '''
        Instatiate a reference to the pool at a certain address, also with an optional
        pre-computed or cached map of net liquidity. If the net liquidity map is not
        provided, it will be constructed when needed by calling the subgraph.
        '''
        self.addr = addr
        self.ticks = ticks

    def get_thegraph_tick_query(self):
        '''
        Return a GraphQL query for a page of the indexed tick state from
        this Uniswap V3 liquidity pool.
        '''
        # doubling the curly brackets to get f-string interpolation
        query = f"""
            query uniswapV3PoolTicks($pool_id: ID!, $num_skip: Int) {{
                ticks(where: {{ pool: $pool_id }}, skip: $num_skip) {{
                    tickIdx
                    liquidityNet
                }}
            }}
        """
        return query

    def get_ticks(self, max_num_pages=99):
        ticks = {}
        num_skip = 0
        for _ in range(max_num_pages):
            result = thegraph.query(self.get_thegraph_tick_query(), pool_id=self.addr, num_skip=num_skip)
            if len(result['ticks']) == 0:
                return ticks

            num_skip += len(result['ticks'])
            for tick_result in result['ticks']:
                tick_idx = int(tick_result['tickIdx'])
                ticks[tick_idx] = IFlow128(tick_result['liquidityNet'])

        raise TimeoutError(f"More than {max_num_pages:,d} pages of ticks for {self.addr} pool")

    def ensure_ticks(self):
        '''
        Ensure that the potentially-large array of ticks has been loaded
        from the subgraph. Only to be called once per instantiation of the
        pool.
        '''
        if self.ticks == None:
            logging.info(f"Loading ticks for '{self.addr}' pool.")
            self.ticks = sefl.get_ticks()

    def calc_liq_net(liq, dliq):
        '''
        Update a running tally of liquidity as we iterate over ticks in a pool. This
        is a port of the addDelta() library function from the Uniswap V3 v3-core's
        LiquidityMath.sol Solidity code at:
            https://github.com/Uniswap/v3-core/blob/main/contracts/libraries/LiquidityMath.sol
        '''
        import pdb; pdb.set_trace()
        if dliq < IFlow128(0):
            new_liq = liq - UFlow128(-dliq.num, num_bits=128)
            assert new_liq < liq, 'LS'
        else:  # dliq >= IFlow128(0)
            new_liq = liq + UFlow128(dliq.num, num_bits=128)
            assert new_liq >= liq, 'LA'
        return new_liq

    def get_liq_dist(self):
        '''
        Return the histogram-like distribution of liquidity in the pool, like
        that displayed in GUIs like the main one at `https://info.uniswap.org/#/pools`
        '''
        self.ensure_ticks()
        liq_dist = {}
        liq = UFlow128(0)
        for tick_idx in sorted(list(self.ticks)):
            dliq = self.ticks[tick_idx]
            if dliq == IFlow128(0): continue
            logging.debug(f"Liquidity delta {dliq:+d} at {tick_idx:d} tick index, {liq:d} running liquidity.")
            liq = UniswapV3Pool.calc_liq_net(liq, dliq)
            liq_dist[tick_idx] = liq
        return liq_dist

    def get_prop_liq(self, liq, at_tick):
        '''
        Query for what proportion of the pool's liquidity would be provided
        by the passed liquidity number. Used to estimate the amount of fee
        income earned by a position in a pool.
        '''
        self.ensure_ticks()
        return None

