# -*- coding: utf-8 -*-
# Version: 1.0
# See github page to report issues or to contribute:
# https://github.com/hssm/anki-addons
 
import aqt.editor

# The approach here is to still let the old setFields function run as usual,
# but copy the HTML it generates into our own table. We do this instead of
# overriding the entire function for future-proofing; the content of the 
# tables could easily change.

# TODO: make column count configurable.

aqt.editor._html = aqt.editor._html + """
<script>
var origSetFields = setFields;
var mySetFields = function(fields, focusTo) {
    origSetFields(fields, focusTo);
    
    var columnCount = 2;
    
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
        // BUT! They have width=100. Make it auto so they look nice.
        $(this).attr('width', 'auto');
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