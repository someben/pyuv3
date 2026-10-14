# pyuv3

Python library for the arithmetic of Uniswap V3 concentrated liquidity:
the fee income a live position has earned, the tokens it could withdraw
right now, and the liquidity histogram of a whole pool. Exact 128-bit
fixed-point overflow semantics (`IFlow128`/`UFlow128`), so fee growth
matches the contracts, not a float approximation.

## Install

    pip install pyuv3

Live queries go through The Graph's decentralized network. Get a free
API key at https://thegraph.com/studio/apikeys/ and export it:

    export THEGRAPH_API_KEY=...

Or point at any Uniswap V3 subgraph (your own, or another chain):

    export PYUV3_SUBGRAPH_URL=https://...

## Usage

```python
from pyuv3.pool import UniswapV3Pool
from pyuv3.pos import UniswapV3Position

# USDC/WETH 0.05% pool on Ethereum mainnet
pool = UniswapV3Pool("0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640")
print(pool.get_current_inv_adj_price())   # USDC per WETH

# Liquidity histogram: {tick index: active liquidity}
liq = pool.get_liq_dist()

# Share of in-range liquidity a 1 WETH + 3,000 USDC position at
# 2,500-3,500 would own at a 3,000 price
print(pool.get_inv_prop_liq(3000, 2500, 3500, 3000, 1))

# Any LP position by its NFT ID
pos = UniswapV3Position(NFT_ID)
print(pos.get_fees())              # uncollected fees: {'token0': ..., 'token1': ...}
print(pos.get_withdrawable_toks()) # {'token0': ..., 'token1': ...}
```

The pure math works offline, no API key needed:

```python
import pyuv3
pyuv3.calc_tick_price(200000)            # 1.0001 ** tick
pyuv3.calc_inv_adj_price_tick(3000.0, 6, 18)  # tick for 3,000 USDC per WETH
```

## Tests

    pip install -r requirements.txt
    pytest

## License

Apache 2.0. By [Ben Gimpert](https://blog.someben.com/).
