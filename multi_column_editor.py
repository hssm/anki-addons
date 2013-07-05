# -*- coding: utf-8 -*-
# Version: 1.5
# See github page to report issues or to contribute:
# https://github.com/hssm/anki-addons

from anki.hooks import wrap, addHook
from aqt import *
from aqt.editor import Editor
import aqt.editor


# A Sensible maximum number of columns we are able to set
MAX_COLUMNS = 18

# Settings key to remember column count
CONF_KEY_COLUMN_COUNT = 'multi_column_count'

# Flag to enable hack to make Frozen Fields look normal
ffFix = False

aqt.editor._html = aqt.editor._html + """
<script>
var columnCount = 1;
function setColumnCount(n) {
    columnCount = n;
}

var ffFix = false; // Frozen Fields fix
function setFFFix(use) {
  ffFix = use;
}

// Event triggered when #fields is modified.
function makeColumns(event) {

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
    // We copy the content of each row into its own group's array and then
    // write out the table again using our own ordering.

    // Inject global variables for us to use from python.
    py.run("mceTrigger");
    
    // Hack to make Frozen Fields look right.
    if (ffFix) {
        // Apply fixed width to first <td>, which is a Frozen Fields cell,
        // or it will take up too much space.
        $("#fields td:first-child").each(function (){
            $(this).attr("width", "28px");
        });
    }
    
    s = '<style>';
    s += '.mceTable { table-layout: fixed; height: 100%%; width: 100%%;}'
    s += '.mceTable td .field { height: 100%%; }'
    s += '</style>';
    $('html > head').append(s);
    
    var fNames = [];
    var fEdit = [];
    
    $("#fields tr:nth-child(odd)").each(function () {
        fNames.push(this.innerHTML);
    });
    
    $("#fields tr:nth-child(even)").each(function () {
        fEdit.push(this.innerHTML);
    });
    
    txt = "";
    for (var i = 0; i < fNames.length;) {
        // A row of names
        txt += "<tr class='mceRow mceNameRow'>";
        for (var j = 0; j < columnCount; j++) {
            var td = fNames[i + j];
            if (td === undefined) {
                break;
            }
            txt += td;
        }
        txt += "</tr>";
    
        // A row of edit boxes
        txt += "<tr class='mceRow mceEditRow'>";
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
    
    // Unbind then rebind to avoid infinite loop
    $('#fields').unbind('DOMNodeInserted')
    $("#fields").html("<table class='mceTable'>" + txt + "</table>");
    $('#fields').bind('DOMNodeInserted', makeColumns);
}

// Attach event to restructure the table after it is populated
$('#fields').bind('DOMNodeInserted', makeColumns);
</script>
"""

def onColumnCountChanged(editor, count):
    "Save column count to settings and re-draw with new count."
    mw.pm.profile[CONF_KEY_COLUMN_COUNT] = count
    editor.loadNote()

def myEditorInit(self, mw, widget, parentWindow, addMode=False):
    count = mw.pm.profile.get(CONF_KEY_COLUMN_COUNT, 1)

    # TODO: These don't deserve their own row. Maybe place it next to the
    # tag editor (if I ever figure out how).
    l = QLabel("Columns")
    n = QSpinBox(self.widget)
    n.setValue(count)
    n.connect(n,
              SIGNAL("valueChanged(int)"),
              lambda value: onColumnCountChanged(self, value))
    n.setMaximum(MAX_COLUMNS)
    n.setMinimum(1)
    self.outerLayout.addWidget(l)
    self.outerLayout.addWidget(n)
    
    # If the user has the Frozen Fields add-on installed, tweak the
    # layout a bit to make it look right.
    global ffFix
    try:
        __import__("Frozen Fields")
        ffFix = True
    except:
        pass


def myBridge(self, str):
    """
    Called from JavaScript to inject some values before it needs
    them.
    """
    if str == "mceTrigger":
        count = mw.pm.profile.get(CONF_KEY_COLUMN_COUNT, 1)
        self.web.eval("setColumnCount(%d);" % count)
        if ffFix:
            self.web.eval("setFFFix(true)")
        
Editor.__init__ = wrap(Editor.__init__, myEditorInit)
Editor.bridge = wrap(Editor.bridge, myBridge, 'before')
