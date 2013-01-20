# -*- coding: utf-8 -*-
# Version: 1.1
# See github page to report issues or contribute:
# https://github.com/ntsp/anki-addons

import time

from PyQt4 import QtCore, QtGui

from aqt import mw
from aqt import *
from aqt.browser import DataModel
from aqt.forms.browser import Ui_Dialog
from anki.hooks import wrap
from anki.find import Finder


# Note: the current algorithm strips secondary code points regardless of the
# preceding code point. This is likely to be sufficient for this add-on.
ignorables = [
# Always ignore
u'\u0600', u'\u0601', u'\u0602', u'\u0603', u'\u0604', u'\u0606', u'\u0607',
u'\u0608', u'\u0609', u'\u060A', u'\u060C', u'\u060D', u'\u060E', u'\u060F',
u'\u0610', u'\u0611', u'\u0612', u'\u0613', u'\u0614', u'\u0615', u'\u0616',
u'\u0617', u'\u0618', u'\u0619', u'\u061A', u'\u061B', u'\u061E', u'\u061F',
u'\u0640', u'\u066A', u'\u066B', u'\u066C', u'\u066D', u'\u06D4', u'\u06D6',
u'\u06D7', u'\u06D8', u'\u06D9', u'\u06DA', u'\u06DB', u'\u06DC', u'\u06DD',
u'\u06DE', u'\u06DF', u'\u06E0', u'\u06E1', u'\u06E2', u'\u06E3', u'\u06E4',
u'\u06E7', u'\u06E8', u'\u06E9', u'\u06EA', u'\u06EB', u'\u06EC', u'\u06ED',

# Secondary
u'\u064B', u'\uFE71', u'\uFE70', u'\u08F0', u'\u08E7', u'\u064C', u'\uFE72',
u'\uFC5E', u'\u08F1', u'\u08E8', u'\u064D', u'\uFE74', u'\uFC5F', u'\u08F2',
u'\u08E9', u'\u064E', u'\uFE77', u'\uFE76', u'\uFCF2', u'\uFC60', u'\u08E4',
u'\u08F4', u'\u08F5', u'\u064F', u'\uFE79', u'\uFE78', u'\uFCF3', u'\uFC61',
u'\u08E5', u'\u08FE', u'\u0650', u'\uFE7B', u'\uFE7A', u'\uFCF4', u'\uFC62',
u'\u08E6', u'\u08F6', u'\u0651', u'\uFE7D', u'\uFE7C', u'\uFC63', u'\u0652',
u'\uFE7F', u'\uFE7E', u'\u0653', u'\u0654', u'\u0655', u'\u065F', u'\u0656',
u'\u0657', u'\u0658', u'\u0659', u'\u065A', u'\u065B', u'\u065C', u'\u065D',
u'\u065E', u'\u08F7', u'\u08F8', u'\u08FD', u'\u08FB', u'\u08FC', u'\u08F9',
u'\u08FA', u'\u0670']


translationTable = dict.fromkeys(map(ord, ignorables), None)

def stripArabic(txt):
    """Return txt excluding ignorable Arabic diacritics."""
    return txt.translate(translationTable)


def mySearch(self, txt, reset=True):
    """Overriding browser.py -> DataModel.Search. Do a search using custom
    methods if the Arabic diacritics checkbox is checked."""

    if reset:
        self.beginReset()
    
    # NOTE: Only override the finder function on the click of the browser's
    # "search" button since this function is used elsewhere. We restore
    # it to the original one after we do our search.
    origFindText = Finder._findText 
    if self.browser.form.arToggleButton.isChecked():
        Finder._findText = myFindText
        txt = stripArabic(txt)

    self.cards = []
    self.cards = self.col.findCards(txt, order=True)

    # Put back original function after search
    Finder._findText = origFindText
    
    if reset:
        self.endReset()
    

def myFindText(self, val, args):
    """Build a custom SQL query to invoke a function to strip Arabic
    diacritics from the search space."""
    
    val = val.replace("*", "%")
    args.append("%"+val+"%")
    args.append("%"+val+"%")

    # NOTE: the "?" is assumed to be stripped already.
    return "(n.sfld like ? escape '\\' or "\
            "stripArabic(n.flds) like ? escape '\\')"

   
def mySetupUi(self, mw):
    """Add new items to the browser UI to allow toggling the add-on."""
    
    # Surely there's a better place for this ! 
    # Create a new SQL function that we can use in our queries.
    mw.col.db._db.create_function("stripArabic", 1, stripArabic)

    # Our UI stuff
    self.arToggleButton = QtGui.QCheckBox(self.widget)
    self.arToggleLabel = QtGui.QLabel("Strip Arabic\n Diacritics")

    # Remove existing elements from the grid layout
    while self.gridLayout.count():
        self.gridLayout.takeAt(0)
    
    # Put them back in in the order that we want, plus our own
    self.gridLayout.addWidget(self.searchEdit, 0, 0, 1, 1)
    self.gridLayout.addWidget(self.arToggleButton, 0, 1, 1, 1)
    self.gridLayout.addWidget(self.arToggleLabel, 0, 2, 1, 1)
    self.gridLayout.addWidget(self.searchButton, 0, 3, 1, 1)
    

Ui_Dialog.setupUi= wrap(Ui_Dialog.setupUi, mySetupUi)
DataModel.search = mySearch