# -*- coding: utf-8 -*-
# Version: 1.0
# See github page to report issues or to contribute:
# https://github.com/ntsp/anki-addons

from operator import itemgetter
import time

from aqt import mw
from aqt.browser import DataModel, Browser
from anki.hooks import wrap
from anki.find import Finder

origColumnData = DataModel.columnData
orig_order = Finder._order

def myColumnData(self, index):
    returned = origColumnData(self, index)
    if returned:
        return returned
    
    col = index.column()
    type = self.columnType(col)
    c = self.getCard(index)
    n = c.note()
    # Notes
    if type == "nid":
        return n.id
    elif type == "nguid":
        return n.guid
    elif type == "nmid":
        return n.mid
    elif type == "nusn":
        return n.usn
    elif type == "ntags":
        return " ".join(str(tag) for tag in n.tags)
    elif type == "nfields":
        return " ".join(str(field) for field in n.fields)
    elif type == "nflags":
        return n.flags
    elif type == "ndata":
        return n.data
    # Cards
    elif type == "cid":
        return c.id
    elif type == "cord":
        return c.ord
    elif type == "cusn":
        return c.usn
    elif type == "ctype":
        return c.type
    elif type == "cqueue":
        return c.queue
    elif type == "cleft":
        return c.left
    elif type == "codue":
        return c.odue
    elif type == "cflags":
        return c.flags
    elif type == "cfirst":
        first = mw.col.db.scalar(
            "select min(id) from revlog where cid = ?", c.id)
        if first:
            first = first / 1000
            return time.strftime("%Y-%m-%d", time.localtime(first))
    elif type == "clatest":
        last = mw.col.db.scalar(
            "select max(id) from revlog where cid = ?", c.id)
        if last:
            last = last / 1000
            return time.strftime("%Y-%m-%d", time.localtime(last))


def mySetupColumns(self):
    self.columns.extend( # Notes
                        [('nid', _("Note ID")),
                        ('nguid', _("Note guid")),
                        ('nmid', _("Note mid")),
                        ('nusn', _("Note usn")),
                        ('ntags', _("Note tags")),
                        ('nfields', _("Note fields")),
                        ('nflags', _("Note flags")),
                        ('ndata', _("Note data")),
                        # Cards
                        ('cid', _("Card ID")),
                        ('cord', _("Card order")),
                        ('cusn', _("Card usn")),
                        ('ctype', _("Card type")),
                        ('cqueue', _("Card queue")),
                        ('cleft', _("Card left")),
                        ('codue', _("Card odue")),
                        ('cflags', _("Card flags")),
                        ('cfirst', _("First review")),
                        ('clatest', _("Latest review")),
                        ])


def my_order(self, order):
    if not order:
        return "", False
    elif order is not True:
        # custom order string provided
        return " order by " + order, False
    # use deck default
    type = self.col.conf['sortType']
    sort = None
    
    if type == "nid":
        sort = "n.id"
    if type == "nguid":
        return "", False # nahh not gonna sort this
    elif type == "nmid":
        sort = "n.mid"
    elif type == "nusn":
        sort = "n.usn"
    elif type == "ntags":
        sort = "n.tags"
    elif type == "nfields":
        return "", False # or this
    elif type == "nflags":
        sort = "n.flags"
    elif type == "ndata":
        sort = "n.data"
    elif type == "cid":
        sort = "c.id"
    elif type == "cord":
        sort = "c.ord"
    elif type == "cusn":
        sort = "c.usn"
    elif type == "ctype":
        sort = "c.type"
    elif type == "cqueue":
        sort = "c.queue"
    elif type == "cleft":
        sort = "c.left"
    elif type == "codue":
        sort = "c.odue"
    elif type == "cflags":
        sort = "c.flags"
    elif type == "cfirst":
        sort = "(select min(id) from revlog where cid = c.id)"
    elif type == "clatest":
        sort = "(select max(id) from revlog where cid = c.id)"
    
    if not sort:
        return orig_order(self, order)
    return " order by " + sort, self.col.conf['sortBackwards']

DataModel.columnData = myColumnData
Browser.setupColumns = wrap(Browser.setupColumns, mySetupColumns)
Finder._order = my_order