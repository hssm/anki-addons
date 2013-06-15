# -*- coding: utf-8 -*-
# Version: 1.5_beta
# See github page to report issues or to contribute:
# https://github.com/hssm/anki-addons

import time

from aqt import *
from aqt.browser import DataModel, Browser
from anki.hooks import wrap
from anki.find import Finder

CONF_KEY_CUSTOM_COLS = 'ifib_activeCols'

origColumnData = DataModel.columnData
orig_order = Finder._order

# NOTE: custom columns are prefixed with c if they are fetched from a
# card object and n if fetched from a note object.

# Likely the only useful ones
_goodColumns = [('cfirst', "First review"),
                ('clast', "Last review"),
                ('cavtime', "Time (Average)"),
                ('ctottime', "Time (Total)"),
                ('ntags', "Tags")]
# Notes
_noteColumns = [('nid', "Note ID"),
                ('nguid', "Note guid"),
                ('nmid', "Note mid"),
                ('nusn', "Note usn"),
                ('nfields', "Note fields"),
                ('nflags', "Note flags"),
                ('ndata', "Note data")]

# Cards
_cardColumns = [('cid', "Card ID"),
                ('cdid', "Card did"),
                ('codid', "Card odid"),
                ('cord', "Card order"),
                ('cusn', "Card usn"),
                ('ctype', "Card type"),
                ('cqueue', "Card queue"),
                ('cleft', "Card left"),
                ('codue', "Card odue"),
                ('cflags', "Card flags")]

# Later on, we combine all custom columns for easier iteration.
_customColumns = []

# Dictionary of field names to figure out if we can handle a column
_allFields = {}

def myColumnData(self, index):
    returned = origColumnData(self, index)
    if returned:
        return returned
    
    col = index.column()
    type = self.columnType(col)
    c = self.getCard(index)
    n = c.note()
    
    if type in _allFields:
        field = _allFields[type]
        if field in c.note().keys():
            return c.note()[field]
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
    elif type == "cavtime":
        atime = mw.col.db.scalar(
            "select avg(time) from revlog where cid = ?", c.id)
        if atime:
            return str(round(atime / 1000, 1)) + "s"
    elif type =="ctottime":
        atime = mw.col.db.scalar(
            "select sum(time) from revlog where cid = ?", c.id)
        if atime:
            return str(round(atime / 1000, 1)) + "s"
    elif type == "ntags":
        return " ".join(str(tag) for tag in n.tags)
    # Notes
    elif type == "nid":
        return n.id
    elif type == "nguid":
        return n.guid
    elif type == "nmid":
        return n.mid
    elif type == "nusn":
        return n.usn
    elif type == "nfields":
        return u"\u25A0".join(unicode(field) for field in n.fields)
    elif type == "nflags":
        return n.flags
    elif type == "ndata":
        return n.data
    # Cards
    elif type == "cid":
        return c.id
    elif type == "cdid":
        return c.did
    elif type == "codid":
        return c.odid
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


def my_order(self, order):
    if not order:
        return "", False
    elif order is not True:
        # custom order string provided
        return " order by " + order, False
    # use deck default
    type = self.col.conf['sortType']
    sort = None
        
    if type in _allFields:
        fldName = _allFields[type]
        sort = "(select valueForField(id, '%s', flds) from notes where id = c.nid)" % fldName
    elif type == "cfirst":
        sort = "(select min(id) from revlog where cid = c.id)"
    elif type == "clast":
        sort = "(select max(id) from revlog where cid = c.id)"
    elif type == "cavtime":
        sort = "(select avg(time) from revlog where cid = c.id)"
    elif type == "ctottime":
        sort = "(select sum(time) from revlog where cid = c.id)"
    elif type == "ntags":
        sort = "n.tags"
    elif type == "nid":
        sort = "n.id"
    elif type == "nguid":
        return "", False # Doesn't make sense to sort this
    elif type == "nmid":
        sort = "n.mid"
    elif type == "nusn":
        sort = "n.usn"
    elif type == "nfields":
        return "", False # or this
    elif type == "nflags":
        sort = "n.flags"
    elif type == "ndata":
        sort = "n.data"
    elif type == "cid":
        sort = "c.id"
    elif type == "cdid":
        sort = "c.did"
    elif type == "codid":
        sort = "c.odid"
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

    if not sort:
        return orig_order(self, order)
    return " order by " + sort, self.col.conf['sortBackwards']

def mySetupColumns(self):
    global _customColumns
    global _allFields

    # Create a new SQL function that we can use in our queries.
    mw.col.db._db.create_function("valueForField", 3, valueForField)

    # Build a list of all (note) fields in the collection. No dupes.
    fields = []
    for model in mw.col.models.all():
        for field in model['flds']:
            type = "_field_"+field['name']
            name = field['name']
            if (type, name) not in fields:
                fields.append((type, name))
                _allFields[type] = name
    
    _customColumns = _goodColumns + _noteColumns + _cardColumns + fields
    self.columns.extend(_customColumns)

def myOnHeaderContext(self, pos):
    gpos = self.form.tableView.mapToGlobal(pos)
    
    m = QMenu()
    # Sub-menus
    fm = QMenu("Fields")
    nm = QMenu("Notes")
    cm = QMenu("Cards")
        
    def addCheckableAction(menu, type, name):
        a = menu.addAction(name)
        a.setCheckable(True)
        a.setChecked(type in self.model.activeCols)
        a.connect(a, SIGNAL("toggled(bool)"),
                  lambda b, t=type: self.toggleField(t))
    
    for item in self.columns:
        type, name = item
        if item in _noteColumns:
            addCheckableAction(nm, type, name)
        elif item in _cardColumns:
            addCheckableAction(cm, type, name)
        elif item[0] in _allFields:
            addCheckableAction(fm, type, name)
        else:
            addCheckableAction(m, type, name)
    
    m.addMenu(fm)
    m.addMenu(nm)
    m.addMenu(cm)
    m.exec_(gpos)


def myDataModel__init__(self, browser):
    """Load any custom columns that were saved in a previous session."""
        
    # First, we make sure those columns actually exist. If not, we ignore
    # them. This is to guard against the event that we remove or rename a
    # column in a later version. Also make sure the sortType is set to a
    # valid column.
    
    sortType = mw.col.conf['sortType']
    validSortType = False
    
    custCols = mw.col.conf.get(CONF_KEY_CUSTOM_COLS, [])
    
    for custCol in custCols:
        for type, name in _customColumns:
            if custCol == type and custCol not in self.activeCols:
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
    
    #sortType = mw.col.conf['sortType']
    # TODO: should we avoid saving the sortType? I will leave it in until
    # a problem with doing so is evident.
        
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


def valueForField(nid, fldName, flds):
    note = mw.col.getNote(nid)
    if fldName in note.keys():
        index = note._fieldOrd(fldName)
        return anki.utils.splitFields(flds)[index]
    else:
        return


DataModel.columnData = myColumnData
DataModel.__init__ = wrap(DataModel.__init__, myDataModel__init__)
Browser.setupColumns = wrap(Browser.setupColumns, mySetupColumns)
Browser.onHeaderContext = myOnHeaderContext
Browser.closeEvent = wrap(Browser.closeEvent, myCloseEvent, "before")
Finder._order = my_order
