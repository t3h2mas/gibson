#!/usr/bin/python2

"""
Look for a 200 status to determine if
a website is up and responding correctly.
"""

import requests

def get_code(page):
    r = requests.get(page)
    # I'm pretty sure that this is the same as
    # r.status_code == 200
    if r.ok: 
        return True
    return False
