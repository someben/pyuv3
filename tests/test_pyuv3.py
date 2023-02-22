#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import unittest

from pyuv3.pos import UniswapV3Position
from pyuv3.uint import Uint

class Pyuv3TestCase(unittest.TestCase):
    '''
    Tests for `uint.py` unsigned integer class
    '''

    def test_uint_math(self):
        self.assertEqual(Uint(123) + Uint(123), Uint(123 + 123))
        self.assertEqual(Uint(123) - Uint(42), Uint(123 - 42))
        self.assertEqual(Uint(32) * Uint(3), Uint(32 * 3))
        self.assertEqual(Uint(255) + Uint(42), Uint(41), "overflow")
        self.assertEqual(Uint(42) - Uint(123), Uint(256 - (123 - 42)), "(integer) underflow")
        self.assertEqual(Uint(150) * Uint(3), Uint((150 * 3) - 256), "overflow")
        self.assertEqual((Uint(42) * Uint(42)) / Uint(3), Uint(((42 * 42) / 3) % 256), "overflow")

    def test_calc_fees(self):
        current_tick = 202448
        liquidity = 34437203644513122
        min_tick, max_tick = 201440, 202420
        fee_growth_global0, fee_growth_global1 = 2253213535483313610098314899669678, 1072784013322967942802728003317579063698159
        min_tick_fee_growth_outside0, min_tick_fee_growth_outside1 = 2247931888560130286596359032224748, 1069567361020120092268195383287889318491711
        max_tick_fee_growth_outside0, max_tick_fee_growth_outside1 = 1698490820255640968866252630421341, 638962276135439184291913094187996677673716
        pos_fee_growth_inside_last0 = 115792089237316195423570985008687907853269984111186229530580461141282711402382
        pos_fee_growth_inside_last1 = 115792089237316195423570985008687907419621048823185763242590982075834998896484
        decimals0, decimals1 = 6, 18

        fees = UniswapV3Position.calc_fees(
            liquidity,
            current_tick, min_tick, max_tick,
            fee_growth_global0, fee_growth_global1,
            min_tick_fee_growth_outside0, min_tick_fee_growth_outside1,
            max_tick_fee_growth_outside0, max_tick_fee_growth_outside1,
            pos_fee_growth_inside_last0, pos_fee_growth_inside_last1,
            decimals0, decimals1,
        )
        assert pytest.approx(507.3518, 0.001) == fees['token0']
        assert pytest.approx(0.3080, 0.001) == fees['token1']

    def test_calc_withdrawable_toks(self):
        liquidity = 10669196109794039
        sqrt_price_x96 = 2282306120221836809729201765714520
        current_tick = 205377
        min_tick, max_tick = 204290, 206870
        decimals0, decimals1 = 6, 18
        toks = UniswapV3Position.calc_withdrawable_toks(liquidity, current_tick, min_tick, max_tick, sqrt_price_x96, decimals0, decimals1)
        assert pytest.approx(26630.3681, 0.001) == toks['token0']
        assert pytest.approx(16.2659, 0.001) == toks['token1']


if __name__ == '__main__':
    unittest.main()

