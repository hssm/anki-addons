# -*- coding: utf-8 -*-
# Version: 1.3
# See github page to report issues or to contribute:
# https://github.com/hssm/anki-addons

from anki.hooks import wrap
from aqt import *
from aqt.editor import Editor
import aqt.editor


CONF_KEY_COLUMN_COUNT = 'multi_column_count'

aqt.editor._html = aqt.editor._html + """
<script>
(function($) {
    $.fn.changeElementType = function(newType) {
        var attrs = {};
    
        $.each(this[0].attributes, function(idx, attr) {
            attrs[attr.nodeName] = attr.nodeValue;
        });
    
        this.replaceWith(function() {
            return $("<" + newType + "/>", attrs).append($(this).contents());
        });
    };
})(jQuery);


var columnCount = 1;

function setColumnCount(n) {
    columnCount = n;
}

var makeColumns = function(event) {

    // If the inserted object is not at the top level of the "fields" object,
    // ignore it. We're assuming that anything added to the "fields" table is
    // the entirety of the content of the table itself.
    if ($(event.target).parent()[0].id !== "fields") {
        return;
    }

    // In the original, there is a row for each field's name followed by a row
    // with that field's edit box. I.e.:
    // <tr><td>...Field name...</td></tr>
    // <tr><td>...Edit box...</td></tr>
    // What we do is copy the content (inside <tr>) of the field name rows into
    // an array, then copy the content of the edit box rows into a separate
    // array, then lay them out again with n number of elements in each row,
    // where n = columnCount.
    
    var fNames = [];
    var fEdit = [];
    
        
    $("#fields tr:nth-child(odd) > td").each(function (){
        $(this).changeElementType("span");
    });
    
    $("#fields tr:nth-child(even) > td").each(function (){
        $(this).changeElementType("span");
    });
    
    $("#fields tr:nth-child(odd)").each(function (){
        fNames.push("<td class='mceCell' width=" + 100/columnCount+"%%>" + this.innerHTML + "</td>");
    });
    
    $("#fields tr:nth-child(even)").each(function (){
        fEdit.push("<td class='mceCell' width=" + 100/columnCount+"%%>" + this.innerHTML + "</td>");
    });
    
    txt = "";
    for (var i = 0; i < fNames.length;) {
        // A row of names
        txt += "<tr>";
        for (var j = 0; j < columnCount; j++) {
            var td = fNames[i + j];
            if (td === undefined) {
                break;
            }
            txt += td;
        }
        txt += "</tr>";
        
        // A row of edit boxes
        txt += "<tr>";
        for (var j = 0; j < columnCount; j++) {
            var td = fEdit[i + j];
            if (td === undefined) {
                break;
            }
            txt += td;
        }
        txt += "</tr>";
        i += columnCount;
    }

    // Unbing then rebind to avoid infinite loop
    $('#fields').unbind('DOMNodeInserted')
    $("#fields").html("<table cellpadding=0 width=100%%>" + txt + "</table>");
    $('#fields').bind('DOMNodeInserted', makeColumns);
};
// Restructure the table after it is populated
$('#fields').bind('DOMNodeInserted', makeColumns);
</script>
"""

def onColumnCountChanged(editor, count):
    mw.pm.profile[CONF_KEY_COLUMN_COUNT] = count
    setEditorColumnCount(editor)
    editor.loadNote()

# TODO: Correctly set initial count on load
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
    n.setMaximum(15)
    n.setMinimum(1)
    self.outerLayout.addWidget(l)
    self.outerLayout.addWidget(n)


def setEditorColumnCount(editor):
    count = mw.pm.profile.get(CONF_KEY_COLUMN_COUNT, 1)
    editor.web.eval("setColumnCount(%d);" % count)

Editor.__init__ = wrap(Editor.__init__, myEditorInit)