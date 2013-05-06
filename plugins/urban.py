#!/usr/bin/python2
import requests
from lxml import html

UD_URL = 'http://urbandictionary.com/define.php?term=%s'

def urban_lookup(word):
    """ returns definitions for a given word from urban dictionary """

    resp = requests.get(UD_URL % word)
    if resp.ok:     # check for 200
        doc = html.fromstring(resp.read())
        return [d.text for d in doc.xpath('//div[@class="definition"]')]
    return []

def test_run(word):
    for i, d in enumerate(urban_lookup(word)):
        print "[%d] %s" % (i, d)

if __name__ == "__main__":
    try:
        test_run(sys.argv[1])
    except:
        print "Usage: ud.py word"
