#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2008-2011 Tobias Hieta <tobias@hieta.se>
#

import urllib2, urllib
import time
from StringIO import StringIO

from lxml import etree

DEVICE_ID='replaceme'

TIMEFRAME_DAY='day'
TIMEFRAME_WEEK='week'
TIMEFRAME_MONTH='month'
TIMEFRAME_ALL='all'

SECTION_PLAYER='players'
SECTION_CASTER='casters'
SECTION_EVENT='events'
SECTION_MATCHUP='matchups'

BASE_URL = 'http://sc2casts.com/iphone19/'


def sc2request(method, args={}):
    url = BASE_URL + method

    # filedate might be static, not sure
    args.update({"refdate":time.strftime('%d-%m-%Y'), "filedate":'30-05-2011', 'deviceid':DEVICE_ID})
    argstr = urllib.urlencode(args)
    url += '?%s' % argstr
    print url

    try:
        urldata = urllib2.urlopen(url).read()
    except:
        return None

    # SC2Cast guys should learn to wrap data like this in 
    # CDATA or replace it with proper codes
    urldata = urldata.replace('&', '&amp;')

    return etree.parse(StringIO(urldata))

class SC2Cast:
    def __init__(self):
        self.id = 0
        self.players = []
        self.races = []
        self.games = []
        self.caster = None
        self.event = None
        self.date = None
        self.bestof = None
        self.bestofnum = 0
        self.round = None
        self.rateup = 0
        self.ratedown = 0

    def getDetails(self):
        root = sc2request('view', {'series': self.id})
        self.fillFromNode(root.xpath('/currentseries')[0])

    def _subnodeText(self, root, elm):
        try:
            return root.xpath('./%s' % elm)[0].text
        except:
            return None

    def _subnodeInt(self, root, elm):
        ret = self._subnodeText(root, elm)
        if ret:
            return int(ret)
        return 0


    def fillFromNode(self, node):
        self.id = self._subnodeInt(node, 'seriesid')
        self.caster = self._subnodeText(node, 'caster')
        self.event = self._subnodeText(node, 'event')
        self.bestof = self._subnodeText(node, 'bestof')
        self.round = self._subnodeText(node, 'round')
        self.bestofnum = self._subnodeInt(node, 'bestofnum')
        self.rateup = self._subnodeInt(node, 'up')
        self.ratedown = self._subnodeInt(node, 'down')

        for player in node.xpath("./*[substring(name(),1,6) = 'player']"):
            self.players.append(player.text)

        for race in node.xpath("./*[substring(name(),1,4) = 'race']"):
            self.races.append(race.text)

        for game in node.xpath(".//games/game"):
            partlist = []
            for p in game.xpath('.//part'):
                partlist.append(p.text)
            self.games.append(partlist)


    def __str__(self):
        attrstr = 'games: %s, bestof: %s, up: %d, down: %d' % (self.games, self.bestof, self.rateup, self.ratedown)
        return "[%d] %s vs %s casted by %s\n  %s" % (self.id, self.players[0], self.players[1], self.caster, attrstr)

class SC2CastsClient:
    def getRecentCasts(self):
        root = sc2request('recent')
        periods = root.xpath('/periods/date_period')
        if not periods:
            return []

        ret = []
        for p in periods:
            date_name = p.xpath('./date_name')[0].text
            for s in p.xpath('.//series'):
                cast = SC2Cast()
                cast.date_name=date_name
                cast.fillFromNode(s)
                ret.append(cast)

        return ret

    def getTopCasts(self,timeframe=TIMEFRAME_DAY):
        root = sc2request('top', {timeframe:None})
        ret = []
        for serie in root.xpath('//series'):
            cast = SC2Cast()
            cast.fillFromNode(serie)
            ret.append(cast)
        return ret
    
    def browse(self, section=SECTION_PLAYER):
        root = sc2request('browse', {section:None})
        ret = []
        for item in root.xpath('//item'):
            ret.append((item.xpath('./name')[0].text, item.xpath('./id')[0].text))
        return ret

    def subBrowse(self, id):
        root = sc2request('browse', {'q':id})
        ret = []
        for serie in root.xpath('//series'):
            cast = SC2Cast()
            cast.fillFromNode(serie)
            ret.append(cast)
        return ret
        
    def search(self, query):
        root = sc2request('search', {'q':query})
        ret = []
        for serie in root.xpath('//series'):
            cast = SC2Cast()
            cast.fillFromNode(serie)
            ret.append(cast)
        return ret
 
if __name__ == '__main__':
    cl = SC2CastsClient()
    for s in cl.search('psy'):
        s.getDetails()
        print s

