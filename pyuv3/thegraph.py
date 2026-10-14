#!/usr/bin/env python
# -*- coding: utf-8 -*-

import contextlib
import logging
import os

import backoff
import gql
import gql.transport.exceptions
import gql.transport.requests

# Uniswap V3 Ethereum mainnet subgraph on The Graph's decentralized network
UNISWAP_V3_SUBGRAPH_ID = '5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV'


def get_subgraph_url():
    '''
    URL of the Uniswap V3 subgraph. PYUV3_SUBGRAPH_URL overrides everything,
    otherwise build the gateway URL from THEGRAPH_API_KEY.
    '''
    url = os.environ.get('PYUV3_SUBGRAPH_URL')
    if url:
        return url
    api_key = os.environ.get('THEGRAPH_API_KEY')
    if not api_key:
        raise RuntimeError(
            'Set THEGRAPH_API_KEY (free at https://thegraph.com/studio/apikeys/) '
            'or PYUV3_SUBGRAPH_URL.')
    return f'https://gateway.thegraph.com/api/{api_key}/subgraphs/id/{UNISWAP_V3_SUBGRAPH_ID}'


@contextlib.contextmanager
def thegraph_uniswapv3_client(num_retries=5):
    '''
    Construct a GQL client against the Uniswap V3 subgraph.
    '''
    client = gql.Client(
        transport=gql.transport.requests.RequestsHTTPTransport(
            url=get_subgraph_url(),
            verify=True,
            retries=num_retries,
        )
    )
    yield client


@backoff.on_exception(backoff.expo, gql.transport.exceptions.TransportQueryError, max_tries=8)
def query(query, **query_params):
    '''
    Call the Uniswap V3 subgraph w/ an arbitrary query.
    '''
    with thegraph_uniswapv3_client() as client:
        logging.debug(f"Calling subgraph w/ '{query}' query & {query_params} parameters.")
        resp = client.execute(gql.gql(query), variable_values=query_params)
        return resp
