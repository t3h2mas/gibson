#!/usr/bin/python2

"""
Look for a 200 status to determine if
a website is up and responding correctly.
"""

import requests

def get_code(page):
    r = requests.get(page)
    if r.ok:
        return True
    return False
