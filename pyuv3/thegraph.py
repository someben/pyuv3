#!/usr/bin/env python
# -*- coding: utf-8 -*-

import contextlib

import gql
import gql.transport.requests


@contextlib.contextmanager
def thegraph_uniswapv3_client(num_retries=5):
    '''
    Construct a GQL client against the Uniswap V3 subgraph.
    '''
    client = gql.Client(
        transport=gql.transport.requests.RequestsHTTPTransport(
            url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
            verify=True,
            retries=num_retries,
        )
    )
    yield client


def query(query, **query_params):
    '''
    Call the Uniswap V3 subgraph w/ an arbitrary query.
    '''
    with thegraph_uniswapv3_client() as client:
        resp = client.execute(gql.gql(query), variable_values=query_params)
        return resp

