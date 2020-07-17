#!/usr/bin/python3

import sys
from enum import Enum
name="values"

COINS = 100000000  # map to satoshi
MIN_EST_GAS = 1000   #estimate min gas value(satoshi), check wallet address's balance is enough

EX_TYPE_B2V = "b2v"
EX_TYPE_V2B = "v2b"


class work_mod(Enum):
    COMM        = 0
    BFILTER     = 1
    MARKPROOF   = 2
    B2VMAPPROOF = 4
    B2VUSDPROOF = 10
    B2VEURPROOF = 11
    B2VSGDPROOF = 12
    B2VGBPPROOF = 13
    B2LUSDPROOF = 20
    B2LEURPROOF = 21
    B2LSGDPROOF = 22
    B2LGBPPROOF = 23

