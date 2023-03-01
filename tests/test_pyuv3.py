#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import unittest

from pyuv3.pool import UniswapV3Pool
from pyuv3.pos import UniswapV3Position
from pyuv3.flowint import IFlow, UFlow

class FlowIntTestCase(unittest.TestCase):

    def test_iflow_cmp(self):
        self.assertTrue(IFlow(0) == IFlow(0))
        self.assertTrue(IFlow(3) == IFlow(3))
        self.assertTrue(IFlow(-2) == IFlow(-2))

        self.assertTrue(IFlow(1) > IFlow(0))
        self.assertTrue(IFlow(2) > IFlow(1))
        self.assertTrue(IFlow(0) > IFlow(-1))
        self.assertTrue(IFlow(-1) > IFlow(-2))

        self.assertTrue(IFlow(0) < IFlow(1))
        self.assertTrue(IFlow(1) < IFlow(2))
        self.assertTrue(IFlow(-1) < IFlow(0))
        self.assertTrue(IFlow(-2) < IFlow(-1))

        self.assertTrue(IFlow(1) >= IFlow(0))
        self.assertTrue(IFlow(2) >= IFlow(1))
        self.assertTrue(IFlow(2) >= IFlow(2))
        self.assertTrue(IFlow(0) >= IFlow(-1))
        self.assertTrue(IFlow(-1) >= IFlow(-2))
        self.assertTrue(IFlow(-1) >= IFlow(-1))

        self.assertTrue(IFlow(0) <= IFlow(1))
        self.assertTrue(IFlow(1) <= IFlow(2))
        self.assertTrue(IFlow(2) <= IFlow(2))
        self.assertTrue(IFlow(-1) <= IFlow(0))
        self.assertTrue(IFlow(-2) <= IFlow(-1))
        self.assertTrue(IFlow(-1) <= IFlow(-1))

    def test_uflow_cmp(self):
        self.assertTrue(UFlow(0) == UFlow(0))
        self.assertTrue(UFlow(3) == UFlow(3))

        self.assertTrue(UFlow(1) > UFlow(0))
        self.assertTrue(UFlow(2) > UFlow(1))

        self.assertTrue(UFlow(0) < UFlow(1))
        self.assertTrue(UFlow(1) < UFlow(2))

        self.assertTrue(UFlow(1) >= UFlow(0))
        self.assertTrue(UFlow(2) >= UFlow(1))
        self.assertTrue(UFlow(2) >= UFlow(2))

        self.assertTrue(UFlow(0) <= UFlow(1))
        self.assertTrue(UFlow(1) <= UFlow(2))
        self.assertTrue(UFlow(2) <= UFlow(2))

    def test_iflow_math(self):
        self.assertEqual(IFlow(13) + IFlow(0), IFlow(13))
        self.assertEqual(IFlow(13) + IFlow(7), IFlow(20))
        self.assertEqual(IFlow(13) + IFlow(-7), IFlow(6))
        self.assertEqual(IFlow(-13) + IFlow(0), IFlow(-13))
        self.assertEqual(IFlow(-13) + IFlow(7), IFlow(-6))
        self.assertEqual(IFlow(-13) + IFlow(-7), IFlow(-20))

        self.assertEqual(IFlow(127) + IFlow(1), IFlow(-128), 'overflow')
        self.assertEqual(IFlow(-128) + IFlow(-1), IFlow(127), '(integer) underflow')
        self.assertEqual(IFlow(100) + IFlow(50), IFlow(-106), 'big overflow')
        self.assertEqual(IFlow(-100) + IFlow(-50), IFlow(106), 'big (integer) underflow')

        self.assertEqual(IFlow(127) - IFlow(-1), IFlow(-128), 'overflow')
        self.assertEqual(IFlow(-128) - IFlow(1), IFlow(127), '(integer) underflow')
        self.assertEqual(IFlow(100) - IFlow(-50), IFlow(-106), 'big overflow')
        self.assertEqual(IFlow(-100) - IFlow(50), IFlow(106), 'big (integer) underflow')

        self.assertEqual(IFlow(13) * IFlow(0), IFlow(0))
        self.assertEqual(IFlow(-13) * IFlow(0), IFlow(0))
        self.assertEqual(IFlow(13) * IFlow(1), IFlow(13))
        self.assertEqual(IFlow(1) * IFlow(13), IFlow(13))

        self.assertEqual(IFlow(13) * IFlow(3), IFlow(39))
        self.assertEqual(IFlow(-13) * IFlow(3), IFlow(-39))
        self.assertEqual(IFlow(13) * IFlow(-3), IFlow(-39))
        self.assertEqual(IFlow(-13) * IFlow(-3), IFlow(39))

        self.assertEqual(IFlow(110) * IFlow(3), IFlow(74), 'overflow')
        self.assertEqual(IFlow(-110) * IFlow(3), IFlow(-74), '(integer) underflow')
        self.assertEqual(IFlow(110) * IFlow(-3), IFlow(-74), '(integer) underflow')
        self.assertEqual(IFlow(-110) * IFlow(-3), IFlow(74), 'overflow')

        self.assertEqual(IFlow(110) / IFlow(10), IFlow(11))
        self.assertEqual(IFlow(-110) / IFlow(10), IFlow(-11))
        self.assertEqual(IFlow(110) / IFlow(-10), IFlow(-11))
        self.assertEqual(IFlow(-110) / IFlow(-10), IFlow(11))

    def test_uflow_math(self):
        self.assertEqual(UFlow(123) + UFlow(123), UFlow(123 + 123))
        self.assertEqual(UFlow(123) - UFlow(42), UFlow(123 - 42))
        self.assertEqual(UFlow(32) * UFlow(3), UFlow(32 * 3))
        self.assertEqual(UFlow(255) + UFlow(42), UFlow(41), 'overflow')
        self.assertEqual(UFlow(42) - UFlow(123), UFlow(256 - (123 - 42)), '(integer) underflow')
        self.assertEqual(UFlow(150) * UFlow(3), UFlow((150 * 3) - 256), 'overflow')
        self.assertEqual((UFlow(42) * UFlow(42)) / UFlow(3), UFlow(((42 * 42) / 3) % 256), 'overflow')


class UniswapV3TestCase(unittest.TestCase):

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
        self.assertTrue(pytest.approx(507.3518, 0.001) == fees['token0'])
        self.assertTrue(pytest.approx(0.3080, 0.001) == fees['token1'])

    def test_calc_withdrawable_toks(self):
        liquidity = 10669196109794039
        sqrt_price_x96 = 2282306120221836809729201765714520
        current_tick = 205377
        min_tick, max_tick = 204290, 206870
        decimals0, decimals1 = 6, 18
        toks = UniswapV3Position.calc_withdrawable_toks(liquidity, current_tick, min_tick, max_tick, sqrt_price_x96, decimals0, decimals1)
        self.assertTrue(pytest.approx(26630.3681, 0.001) == toks['token0'])
        self.assertTrue(pytest.approx(16.2659, 0.001) == toks['token1'])

    def test_liq_net(self):
        min_int128, max_int128 = -170141183460469231731687303715884105728, 170141183460469231731687303715884105727
        min_uint128, max_uint128 = 0, 340282366920938463463374607431768211455
        self.assertEqual(UniswapV3Pool.calc_liq_net(UFlow(123, num_bits=128), IFlow(123, num_bits=128)), UFlow(123 * 2, num_bits=128))
        self.assertEqual(UniswapV3Pool.calc_liq_net(
            UFlow(max_uint128 - 1, num_bits=128), IFlow(1, num_bits=128)),
            UFlow(max_uint128, num_bits=128))
        self.assertEqual(UniswapV3Pool.calc_liq_net(
            UFlow(max_uint128 - 1, num_bits=128), IFlow(1, num_bits=128)),
            UFlow(max_uint128, num_bits=128))

if __name__ == '__main__':
    unittest.main()

