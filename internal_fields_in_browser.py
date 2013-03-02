# -*- coding: utf-8 -*-
# Version: 1.0
# See github page to report issues or to contribute:
# https://github.com/ntsp/anki-addons

from operator import itemgetter
import time
from aqt import mw
from aqt.browser import DataModel, Browser
from anki.hooks import wrap, addHook

origColumnData = DataModel.columnData

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
    self.columns.sort(key=itemgetter(1))

DataModel.columnData = myColumnData
Browser.setupColumns = wrap(Browser.setupColumns, mySetupColumns)