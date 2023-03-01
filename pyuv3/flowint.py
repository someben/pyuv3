#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np


class FlowInt:
    '''
    Fixed-width signed or unsigned integers, integers that explicitly under- or over-flow
    according to a particular number of bits. Abstract class that is sub-typed in this
    module.
    '''
    
    def __init__(self, num, is_signed=False, num_bits=8):
        '''
        Initialize the class with a value that can be converted to a signed or unsigned integer
        with the top-level int() call, and also a particular bit size.
        :param num: Integer value
        :param is_signed: Is this object a signed integer, or an unsiged integer with twice
        the range only on the positive side? Defaults to False for a traditional unsigned byte.
        :param num_bits: Number of bits for this signed or unsigned integer. Defaults to 8 for a
        traditional unsigned byte.
        '''
        self.num = int(num)
        self.is_signed = is_signed
        self.num_bits = num_bits

        self.two_pow = 2 ** num_bits
        self.min_signed_neg, self.max_signed_pos = -self.two_pow // 2, (self.two_pow // 2) - 1
        if self.is_signed:
            assert self.num in range(self.min_signed_neg, self.max_signed_pos + 1), f"Value {self.num} out-of-range for signed {num_bits:,d} bits"
        else:
            assert self.num in range(self.two_pow), f"Value {self.num} out-of-range for unsigned {num_bits:,d} bits"
        self.mask = self.two_pow - 1  # 0xFFF... or 0b111...

    def __format__(self, *fmt_args):
        '''
        Just use the underlying Python int()'s formatting.
        '''
        return self.num.__format__(*fmt_args)
    
    '''
    Comparison dunders cannot overflow, so just implement these with the underlying
    Python int() operators.
    '''
    def __eq__(self, o): return self.num == o.num
    def __lt__(self, o): return self.num < o.num
    def __le__(self, o): return self.num <= o.num
    def __gt__(self, o): return self.num > o.num
    def __ge__(self, o): return self.num >= o.num


class IFlow(FlowInt):
    """
    Fixed-width signed integers, an integer that explicitly under- or over-flows
    according to a particular number of bits.
    """

    def __init__(self, num, num_bits=8):
        super().__init__(num, is_signed=True, num_bits=num_bits)

    def __repr__(self):
        return f"iflow{self.num}"

    def __add__(self, o):
        result = self.num + o.num
        if result > self.max_signed_pos:
            return self.__class__(result - self.two_pow, num_bits=self.num_bits)
        elif result < self.min_signed_neg:
            return self.__class__(result + self.two_pow, num_bits=self.num_bits)
        return self.__class__(result, num_bits=self.num_bits)

    def __sub__(self, o):
        result = self.num - o.num
        if result > self.max_signed_pos:
            return self.__class__(result - self.two_pow, num_bits=self.num_bits)
        elif result < self.min_signed_neg:
            return self.__class__(result + self.two_pow, num_bits=self.num_bits)
        return self.__class__(result, num_bits=self.num_bits)
    
    def __mul__(self, o):
        result = self.num * o.num
        if result > self.max_signed_pos:
            return self.__class__(result % self.two_pow, num_bits=self.num_bits)
        elif result < self.min_signed_neg:
            return self.__class__(-(abs(result) % self.two_pow), num_bits=self.num_bits)
        return self.__class__(result, num_bits=self.num_bits)
    
    def __truediv__(self, o):
        result = self.num // o.num
        return self.__class__(result, num_bits=self.num_bits)


class UFlow(FlowInt):
    """
    Fixed-width unsigned integers, an integer that explicitly under- or over-flows
    according to a particular number of bits.
    """

    def __init__(self, num, num_bits=8):
        super().__init__(num, is_signed=False, num_bits=num_bits)

    def __repr__(self):
        return f"uflow{self.num}"
   
    def __add__(self, o):
        result = self.num + o.num
        return self.__class__(result & self.mask, num_bits=self.num_bits)

    def __sub__(self, o):
        result = self.num - o.num
        return self.__class__(result & self.mask, num_bits=self.num_bits)
    
    def __mul__(self, o):
        result = self.num * o.num
        return self.__class__(result & self.mask, num_bits=self.num_bits)
    
    def __truediv__(self, o):
        result = self.num // o.num
        return self.__class__(result & self.mask, num_bits=self.num_bits)


class IFlow128(IFlow):
    """
    Class for a common 128-bit signed integer type.
    """

    def __init__(self, num, num_bits=128):
        super().__init__(num, num_bits=num_bits)


class UFlow128(UFlow):
    """
    Class for a common 128-bit unsigned integer type.
    """

    def __init__(self, num, num_bits=128):
        super().__init__(num, num_bits=128)


