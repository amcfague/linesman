var asInitVals = new Array();
var oTable;

$(document).ready(function() {
    $("#sessions a.delete").click(function() {
        // Get the enclosing row
        var parent_tr = $(this).closest("tr");

        // Fade out this row and delete it from the table
        $(parent_tr).fadeOut(200, function() {
            oTable.fnDeleteRow(parent_tr[0]);
        });

        // And of course, delete the row from our database
        $.ajax($(this).attr("href"));

        return false;
    }); 

    $("#delete_listed").click(function() {
        // Only remove the filtered nodes!
        nodes = oTable.fnGetFilteredNodes();

        // Next, confirm that this is what the user really wants!
        msg = "You are about to remove " + nodes.length + " saved sessions." +
              "\n\nPress OK to delete these sessions.";
        if(!confirm(msg))
            return false;

        for(i=0; i < nodes.length; i++) {
            // Remove these sessions from the backend
            $.ajax($(nodes[i]).find("a.delete").attr("href"));
            // And, of course, remove the rows
            oTable.fnDeleteRow(nodes[i]);
        }
        // Also clear the search input and manually trigger the keyup event
        $("tfoot input").val("").keyup();
        // Restore the "Filter by ..." text.
        $("tfoot input").blur();

        return false;
    });

    // Add the ability to retrieve a list of all filtered rows
    $.fn.dataTableExt.oApi.fnGetFilteredNodes = function ( oSettings )
    {
        var anRows = [];
        for ( var i=0, iLen=oSettings.aiDisplay.length ; i<iLen ; i++ )
        {
            var nRow = oSettings.aoData[ oSettings.aiDisplay[i] ].nTr;
            anRows.push( nRow );
        }
        return anRows;
    };

    // Date sorting!
    // Parses out a Pythong datetime object and sorts it.
    var parse_date_string = function(datestr) {
        var split_str = datestr.split(" ");
        var split_date = split_str[0].split("-");
        var split_time = split_str[1].split(":");
        return split_date.concat(split_time);
    };

    var date_lt = function(a, b) {
        for(var i in a) {
            if(a[i] == b[i])
                continue;

            return parseFloat(a[i]) < parseFloat(b[i]);
        }
        return false;
    };

    jQuery.fn.dataTableExt.oSort['python_date-asc']  = function(a,b) {
        var aDate = parse_date_string(a);
        var bDate = parse_date_string(b);
        return date_lt(bDate, aDate);
    };

    jQuery.fn.dataTableExt.oSort['python_date-desc'] = function(a,b) {
        var aDate = parse_date_string(a);
        var bDate = parse_date_string(b);
        return date_lt(aDate, bDate);
    };

    /*
     * Support functions to provide a little bit of 'user friendlyness' to the textboxes in 
     * the footer
     */
    $("tfoot input").each( function (i) {
        asInitVals[i] = this.value;
    } );
    
    $("tfoot input").focus( function () {
        if (this.className == "search_init") {
            this.className = "";
            this.value = "";
        }
    } );
    
    $("tfoot input").blur( function (i) {
        if (this.value == "") {
            this.className = "search_init";
            this.value = asInitVals[$("tfoot input").index(this)];
        }
    } );

    oTable = $('#sessions').dataTable( {
        aoColumns: [
            {"sType": "html"},
            {"sType": "numeric"},
            {"sType": "python_date"},
            {"bSearchable": false, "bSortable": false, "sWidth": "0"}
        ],
        aLengthMenu: [[20, 50, 100, -1], [20, 50, 100, "All"]],
        aaSorting: [[ 2, "desc" ]],
        bLengthChange: true,
        bPaginate: true,
        bStateSave: true,
        fnInitComplete: function(oSettings) {
            for(var i = 0; i < oSettings.aoPreSearchCols.length; i++) {
                if(oSettings.aoPreSearchCols[i].sSearch.length > 0) {
                    asInitVals[i] = $("tfoot input")[i].value;
                    $("tfoot input")[i].value = oSettings.aoPreSearchCols[i].sSearch;
                    $("tfoot input")[i].className = "";
                }
            }
        },
        iDisplayLength: 20,
        oLanguage: {
            "sSearch": "Search all columns:"
        },
        sDom: 'lprtip',
        sPaginationType: "full_numbers"
    } );
               
    $("tfoot input").keyup( function () {
        /* Filter on the column (the index) of this element */
        oTable.fnFilter( this.value, $("tfoot input").index(this) );
    } );

} );
