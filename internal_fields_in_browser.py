# -*- coding: utf-8 -*-
# Version: 1.1
# See github page to report issues or to contribute:
# https://github.com/hssm/anki-addons

from operator import itemgetter
import time

from aqt import mw
from aqt.browser import DataModel, Browser
from anki.hooks import wrap
from anki.find import Finder

CONF_KEY_CUSTOM_COLS = 'ifib_activeCols'

origColumnData = DataModel.columnData
orig_order = Finder._order

_customColumns = [# Notes
                ('nid', "Note ID"),
                ('nguid', "Note guid"),
                ('nmid', "Note mid"),
                ('nusn', "Note usn"),
                ('ntags', "Note tags"),
                ('nfields', "Note fields"),
                ('nflags', "Note flags"),
                ('ndata', "Note data"),
                # Cards
                ('cid', "Card ID"),
                ('cord', "Card order"),
                ('cusn', "Card usn"),
                ('ctype', "Card type"),
                ('cqueue', "Card queue"),
                ('cleft', "Card left"),
                ('codue', "Card odue"),
                ('cflags', "Card flags"),
                ('cfirst', "First review"),
                ('clast', "Latest review"),
                ('catime', "Answer Time"),
                ]

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
    elif type == "clast":
        last = mw.col.db.scalar(
            "select max(id) from revlog where cid = ?", c.id)
        if last:
            last = last / 1000
            return time.strftime("%Y-%m-%d", time.localtime(last))
    elif type == "catime":
        atime = mw.col.db.scalar(
            "select avg(time) from revlog where cid = ?", c.id)
        if atime:
            return round(atime / 1000)
            

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
    elif type == "clast":
        sort = "(select max(id) from revlog where cid = c.id)"
    elif type == "catime":
        sort = "(select avg(time) from revlog where cid = c.id)"

    if not sort:
        return orig_order(self, order)
    return " order by " + sort, self.col.conf['sortBackwards']

def mySetupColumns(self):
    self.columns.extend(_customColumns)
    # The custom fields will appear at the bottom of the list.
    
def myDataModel__init__(self, browser):
    
    # Load any custom columns that were saved in a previous session.
    #
    # First, we make sure those columns actually exist. If not, we ignore
    # them. This is to guard against the event that we remove or rename a
    # column in a later version. Also make sure the sortType is set to a
    # valid column.
    
    sortType = mw.col.conf['sortType']
    validSortType = False
    
    custCols = mw.col.conf.get(CONF_KEY_CUSTOM_COLS, [])
    
    for custCol in custCols:
        for type, name in _customColumns:
            if custCol == type:
                self.activeCols.append(custCol)
            if sortType == type:
                validSortType = True
    
    if not validSortType:
        mw.col.conf['sortType'] = 'noteCrt'

def myCloseEvent(self, evt):
    """Remove our columns from self.model.activeCols when closing.
    Otherwise, Anki would save them to the equivalent in the collection
    conf, which might have ill effects elsewhere. We save our custom
    types in a custom conf item instead."""
    
    # TODO: should we avoid saving the sortType? I will leave it in until
    # a problem with doing so is evident.
    #sortType = mw.col.conf['sortType']
    
    customCols = []
    origCols = []
    
    for col in self.model.activeCols:
        isOrig = True
        for custType, custName in _customColumns:
            if col == custType:
                customCols.append(col)
                isOrig = False
                break
        if isOrig:
            origCols.append(col)

    self.model.activeCols = origCols
    mw.col.conf[CONF_KEY_CUSTOM_COLS] = customCols
                

DataModel.columnData = myColumnData
DataModel.__init__ = wrap(DataModel.__init__, myDataModel__init__)
Browser.setupColumns = wrap(Browser.setupColumns, mySetupColumns)
Browser.closeEvent = wrap(Browser.closeEvent, myCloseEvent, "before")
Finder._order = my_order