#!/usr/bin/python3

import sys
from enum import Enum
name="error"
class error(Enum):
    SUCCEED = "succeed"
    FAILED  = "failed"
    EXCEPT  = "except"
    ARG_INVALID = "argument invalid"
    SETTING_INVALID = "setting invalid"
    WALLET_INVALID = "wallet invalid"
    TRAN_INFO_INVALID = "transaction info invalid"
    DB_PROOF_INFO_INVALID = "proof db info invalid"



