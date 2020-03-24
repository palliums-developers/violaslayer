#!/usr/bin/python3

import operator
import sys, os
import json

#cureent version
BVEXCHANGE_VER = {
        "major"     : 1,
        "minor"     : 1,
        "revision"  : 1
        }

'''
BVEXCHANGE_VER > argument return 1
BVEXCHANGE_VER = argument return 0
BVEXCHANGE_VER < argument return -1
'''
def cmp(major, minor, revision):
    cur_major = BVEXCHANGE_VER.get("major")
    cur_minor = BVEXCHANGE_VER.get("minor")
    cur_revision = BVEXCHANGE_VER.get("revision")
    if cur_major > major:
        return 1
    elif cur_major < major:
        return -1

    if cur_minor > minor:
        return 1
    elif cur_minor < minor:
        return -1

    if cur_revision > revision:
        return 1
    elif cur_revision < revision:
        return -1

    return 0



def test_cmp():
    try:
        ret = cmp(1, 1, 1)
        assert ret == 0, "cmp_ver error. 0"
        ret = cmp(1, 1, 2)
        assert ret == -1, "cmp_ver error. -1"
        ret = cmp(1, 1, 0)
        assert ret == 1, "cmp_ver error. 1"
    except Exception as e:
        print(e)

if __name__ == "__main__":
    test_cmp()
