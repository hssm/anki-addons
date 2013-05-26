# -*- coding: utf-8 -*-
# Version: 1.0
# See github page to report issues or to contribute:
# https://github.com/hssm/anki-addons

from anki.hooks import wrap
from aqt import *
from aqt.editor import Editor
import aqt.editor

# The approach here is to still let the old setFields function run as usual,
# but copy the HTML it generates into our own table. We do this instead of
# overriding the entire function for future-proofing; the content of the
# tables could easily change.

CONF_KEY_COLUMN_COUNT = 'multi_column_count'

aqt.editor._html = aqt.editor._html + """
<script>
var columnCount = 1;

function setColumnCount(n) {
    columnCount = n;
}

var origSetFields = setFields;
var mySetFields = function (fields, focusTo) {
    origSetFields(fields, focusTo);
        
    // In the original, there is a row for each field's name followed by a row
    // with that field's edit box. What we do is make an array of each name
    // and an array of each field, then lay them out again with n number of
    // elements in each row, where n is columnCount.
       
    var fNames = new Array();
    var fEdit = new Array();
    
    // These are the names on top of the edit boxes.
    $("#fields tr:nth-child(odd) td").each(function () {
        fNames.push(this.outerHTML);
    });
    
    // And these are the edit boxes themselves.
    $("#fields tr:nth-child(even) td").each(function () {
        // Make them evenly-spaced
        $(this).attr('width', 100/columnCount+'%%');
                
        // Make the div inside expand to fill the whole cell. It looks
        // ugly if there are a bunch that are different sizes.
        $('div', this).css('display', 'inline-table');
        $('div', this).css('-webkit-appearance', 'textarea');
        $('div', this).css('height', '100%%');
        $('div', this).css('width', '100%%');
        
        fEdit.push(this.outerHTML);
    });
    
    txt = ""
    for (var i = 0; i < fNames.length; ) {
        // A row of names
        txt += "<tr>"
        for (var j = 0; j < columnCount; j++) {
            var td = fNames[i+j];
            if (td === undefined) {
                break;
            }
            txt += td;
        }
        txt += "</tr>"
        
        // A row of edit boxes
        txt += "<tr>"
        for (var j = 0; j < columnCount; j++) {
            var td = fEdit[i+j];
            if (td === undefined) {
                break;
            }
            txt += td;
        } 
        txt += "</tr>"
        
        i += columnCount;
    }
    $("#fields").html("<table cellpadding=0 width=100%%>"+txt+"</table>");
};
var setFields = mySetFields;
</script>
"""

def onColumnCountChanged(editor, count):
    mw.pm.profile[CONF_KEY_COLUMN_COUNT] = count
    editor.loadNote()

def myEditorInit(self, mw, widget, parentWindow, addMode=False):

    count = mw.pm.profile.get(CONF_KEY_COLUMN_COUNT, 1)

    # TODO: These don't deserve their own row. Maybe place it next to the
    # tag editor.
    l = QLabel("Columns")
    n = QSpinBox(self.widget)
    n.setValue(count)
    n.connect(n,
              SIGNAL("valueChanged(int)"),
              lambda value: onColumnCountChanged(self, value))
    n.setMaximum(20)
    n.setMinimum(1)
    self.outerLayout.addWidget(l)
    self.outerLayout.addWidget(n)


def myLoadNote(self):
    count = mw.pm.profile.get(CONF_KEY_COLUMN_COUNT, 1)
    self.web.eval("setColumnCount(%d);" % count)

Editor.__init__ = wrap(Editor.__init__, myEditorInit)
Editor.loadNote = wrap(Editor.loadNote, myLoadNote, pos="before")