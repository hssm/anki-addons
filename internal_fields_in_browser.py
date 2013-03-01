# -*- coding: utf-8 -*-
# Version: 1.0
# See github page to report issues or to contribute:
# https://github.com/ntsp/anki-addons

from operator import itemgetter
import time

from aqt import mw
from aqt import *
from aqt.browser import DataModel, Browser
from anki.hooks import wrap, addHook

origColumnData = DataModel.columnData

def myColumnData(self, index):
    col = index.column()
    type = self.columnType(col)
    c = self.getCard(index)
    n = c.note()
    if type == "nid":
        return n.id
    elif type == "nguid":
        return n.guid
    elif type == "nmid":
        return n.mid
    elif type == "nmod":
        return time.strftime("%Y-%m-%d", time.localtime(n.mod))
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
    
    elif type == "cid":
        return c.id
    else:
        return origColumnData(self, index)


def mySetupColumns(self):
    self.columns.extend( # Notes
                        [('nid', _("Note ID")),
                        ('nguid', _("Note guid")),
                        ('nmid', _("Note mid")),
                        ('nmod', _("Note mod")),
                        ('nusn', _("Note usn")),
                        ('ntags', _("Tags")),
                        ('nfields', _("Fields")),
                        ('nflags', _("Flags")),
                        ('ndata', _("Note data")),
                        # Cards
                        ('cid', _("Card ID")),
                        ])
    self.columns.sort(key=itemgetter(1))

DataModel.columnData = myColumnData
Browser.setupColumns = wrap(Browser.setupColumns, mySetupColumns)