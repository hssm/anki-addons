# -*- coding: utf-8 -*-
# Version: 1.0
# See github page to report issues or contribute:
# https://github.com/ntsp/anki-addons

from anki.hooks import wrap
from aqt.browser import DataModel

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

# Ignore as secondary
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

# Note: the currect algorithm strips secondary codepoints regardless of the
# preceding character. This is likely to be sufficient for this add-on.

def my_search(self, txt, reset=True):
    if reset:
        self.beginReset()
    txt = ''.join([s for s in txt if s not in ignorables])
    self.cards = []
    self.cards = self.col.findCards(txt, order=True)

    if reset:
        self.endReset()
    
DataModel.search = my_search