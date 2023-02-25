#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Uint:
    '''
    Fixed-width unsigned integers, integers that explicitly under- or over-flow
    according to a particular number of bits.
    '''
    
    def __init__(self, num, num_bits=8):
        '''
        Initialize the class with a value that can be converted to an unsigned integer
        with the top-level int() call, and also a particular bit size.
        :param num: Integer value
        :param num_bits: Number of bits for this unsigned integer. Defaults to 8 for a
        traditional unsigned byte.
        '''
        int_num = int(num)
        assert int_num in range(2 ** num_bits), f"Value {int_x} out-of-range for {num_bits:,d} bits"
        self.num = int_num
        self.num_bits = num_bits
        self.mask = (2 ** num_bits) - 1  # 0xFFF... or 0b111...
        
    def __repr__(self):
        return f"uint{self.num}"
    
    def __eq__(self, o):
        return self.num == o.num
    
    def __add__(self, o):
        return Uint((self.num + o.num) & self.mask, num_bits=self.num_bits)

    def __sub__(self, o):
        return Uint((self.num - o.num) & self.mask, num_bits=self.num_bits)
    
    def __mul__(self, o):
        return Uint((self.num * o.num) & self.mask, num_bits=self.num_bits)
    
    def __truediv__(self, o):
        return Uint((self.num // o.num) & self.mask, num_bits=self.num_bits)

