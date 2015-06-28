<html>
<head>
    <title>Derby!</title>
    <style type="text/css">
    html * {
    font: 200 14px source-sans-pro, sans-serif;
    }
    table {
        border-collapse: collapse;
        -webkit-touch-callout: none;
        -webkit-user-select: none;
        -khtml-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        -o-user-select: none;
        user-select: none;
        cursor:default;
    }

    th, td {
    border: 1px solid black;
    overflow: hidden;
    }

    tr {
        height: 30px;
    }

    #goodcolumn {
        width: 25px;
        max-width: 25px;
        text-align: center;
    }

    #timecolumn {
        width: 100px;
        max-width: 100px;
        text-align: center;
    }
    #distcolumn {
        width: 150px;
        max-width: 150px;
        text-align: center;
    }
    #addrcolumn {
        word-wrap: break-word;
        width: 250px;
        max-width: 250px;
    }

    #sizecolumn {
        word-wrap: break-word;
        width: 100px;
        max-width: 100px;
    }

    .fieldrow:nth-of-type(even) {
        background-color: white;
    }

    .fieldrow:nth-of-type(odd) {
        background-color: #d3d3d3;
    }

    .fieldrow:hover{
        background-color: #8aacb8;
    }

    tbody {
        height: 625px;
        display: block;
        overflow-y: scroll;
    }
    thead{
        background-color:white;
        display: block;
    }

    div#selectorTable {
        float: left;
    }
    div#tableTitle {
        text-align: right;
        margin-right: 20px;
    }
    div#mapview {
        background-color: gray;
        width: 640px;
        height: 800px;
        float: left;
    }

    div#outerdiv {
        width: 1300px;
        height: 800px;
        max-width: 1300px;
        max-height: 800px;
        border: 1px solid black;
    }

    div#mapimage {
        width: 640px;
        height: 640px;
        max-width: 640px;
        max-height: 640px;
        border: 1px solid black;
    }

    div#mapedit {
        border: 1px solid black;
    }

    th.tablesorter-header:hover {
        background-image: url(3rdparty/tablesorter/css/images/black-unsorted.gif);
        background-repeat: no-repeat;
        background-position: center right;
    }

    th.tablesorter-headerSortDown, th.tablesorter-headerSortDown:hover {
        background-image: url(3rdparty/tablesorter/css/images/black-desc.gif);
        background-repeat: no-repeat;
        background-position: center right;
    }

    th.tablesorter-headerSortUp, th.tablesorter-headerSortUp:hover {
        background-image: url(3rdparty/tablesorter/css/images/black-asc.gif);
        background-repeat: no-repeat;
        background-position: center right;
    }

    th.tablesorter-infoOnly, th.tablesorter-infoOnly:hover {
        background-image: None;
    }

input[type="checkbox"].good {
    display: none;
}
input[type="checkbox"].good + label{
    background-color:red;
    height: 100%;
    width: 100%;
    display:inline-block;
    padding: 0 0 0 0px;
}

input[type="checkbox"].good:checked + label{
    background-color:green;
}

input[type="checkbox"].good:indeterminate + label{
    background-color:yellow;
}

a:link, a:visited{
    color: blue;
}

    </style>

    <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
    <script src="3rdparty/tablesorter/js/jquery.tablesorter.js"></script>
    <!-- tablesorter widget file - loaded after the plugin -->
    <!--script src="3rdparty/tablesorter/js/jquery.tablesorter.widgets.js"></script-->
    <script type="text/javascript">
    $(document).ready(function() {
        $('.fieldrow').click(function() {
            // Clear the last clicked row, but only if there was a last clicked row
            if( typeof window.$lastClicked !== 'undefined' ) {
                $lastClicked.css({
                    'background-color' : ''
                });
            }
            // Set the new background color
            $(this).css({
                'background-color': '#8aacb8'
            });

            // Get this row's key
            var fieldKey = $(this).attr('data-fieldKey');
            var lastField = null;
            if( typeof window.$currentField !== 'undefined' ) {
                lastField = window.$currentField;
            }

            window.$lastClicked = $(this);
            window.$currentField = fieldKey;

            $.post('mapView.php', { 'fieldKey': window.$currentField }, function(result) {
                $('#mapview').html( result );
            });
        });


        $('.good').click( function() {
            var isValid = $(this).prop( 'checked');
            var key = $(this).attr('data-fieldKey');
            $.ajax({
                url: 'update.php',
                type: "PUT",
                data: {
                    'isValid': isValid,
                    'fieldKey': key
                },
                success: function(result)
                {
                    $('#testDiv').html(result);
                    // Empty
                },
                error: function(jqXHR, textStatus, errorThrown)
                {
                   console.log(textStatus, errorThrown);
                }
            });
        });
        $('.indy').each( function() {
            $(this).prop("indeterminate", true);
        });
    });

    </script>
    </head>

    <body bgcolor="white">

        <?php
        //Set errors
        ini_set('display_errors', '1');
        error_reporting(E_ALL | E_STRICT);

        // Load config file
        $config = json_decode( file_get_contents( "../cacheImagery/config.json" ), true);

        // Connect to database
        $host = $config["host"];
        $port = $config["port"];
        $dbname = $config["dbname"];
        $user = $config["nominal"]["un"];
        $password = $config["nominal"]["pw"];

        $connString = "host=$host port=$port dbname=$dbname user=$user password=$password";
        $link = pg_connect($connString);

        if( !$link )
        {
            echo "dying";
            die("Could not connect: " . pg_last_error());
        }
        ?>

        <!-- Sortable list of fields-->

            <?php
            // Get all fields
            $result = pg_exec($link, "SELECT location.lat, location.lon, TRIM(location.address), field.angle, field.fieldid, field.fieldSize, field.good, travelcost.travelTime, travelcost.travelDist ".
                                     " FROM field " .
                                     " JOIN travelcost ON field.locationId = travelcost.destLocationId " .
                                     " NATURAL JOIN location " .
                                     " WHERE field.duplicateId IS NULL " .
                                     " ORDER BY travelcost.travelTime ASC;" );
            $numrows = pg_numrows($result);

            ?>
            <div id="outerdiv">
            <div id="selectorTable">
                <div id='tableTitle'>
                    +/- filter:
                    <a id='allField' href="showfields.php?pmfilter=all">All</a>
                    <a id='goodFields' href="showfields.php?pmfilter=good">Good</a>
                    <a id='indyFields' href="showfields.php?pmfilter=indy">Unviewed</a>
                    <a id='badFields' href="showfields.php?pmfilter=bad">Bad</a>
            <p>Showing fields 1 to <?php echo $numrows; ?> (of <?php echo $numrows; ?>)</p>
        </div>
            <?php

            // Constant. The maximum number of images to load
            $maxImages = 300;
            ?>

            <table id="fieldTable" class="tablesorter">
                <thead>
                <tr>
                    <th id="goodcolumn" class="tablesorter-infoOnly sorter-false">+/-</th>
                    <th id="timecolumn" class="tablesorter-header">Time</th>
                    <th id="distcolumn" class="tablesorter-header">Distance</th>
                    <th id="addrcolumn" class="tablesorter-infoOnly sorter-false">Address</th>
                    <th id="sizecolumn" class="tablesorter-header">Size</th>
                </tr>
                <tbody>

            <?php

            $showgood = true;
            $showindy = true;
            $showbad = true;

            if( isset( $_GET['pmfilter'] ) )
            {
                $filtervalue = $_GET['pmfilter'];
                if( $filtervalue === 'all')
                {
                    $showgood = true;
                    $showindy = true;
                    $showbad = true;
                }
                elseif( $filtervalue == 'good')
                {
                    $showgood = true;
                    $showindy = false;
                    $showbad = false;
                }
                elseif( $filtervalue == 'indy')
                {
                    $showgood = false;
                    $showindy = true;
                    $showbad = false;
                }
                elseif( $filtervalue == 'bad')
                {
                    $showgood = false;
                    $showindy = false;
                    $showbad = true;
                }
            }

            for($ri = 0; $ri < $numrows && $ri < $maxImages; $ri++) {
                $row = pg_fetch_array($result, $ri);

                // First column (map)
                $id = $row["fieldid"];
                $lat = $row["lat"];
                $lon = $row["lon"];
                $angle = $row["angle"];
                // Note: using btrim instead of addresses because of an apparent bug in what pg_exec
                // returns when doing a TRIM.
                $address=$row["btrim"];
                $timeSeconds = $row["traveltime"];
                $distMeters = $row["traveldist"];
                $sizeMeters = $row["fieldsize"];
                $goodchecked = "";
                $indy = "";

                if( $row["good"] === 't' )
                {
                    $goodchecked = "checked";
                    if( false == $showgood )
                    {
                        continue;
                    }
                }
                elseif( $row["good"] == 'f')
                {
                    if( false == $showbad )
                    {
                        continue;
                    }

                }
                elseif ($row["good"] != 'f') {
                    $indy = "indy";
                    $goodchecked = "checked";

                    if( false == $showindy )
                    {
                        continue;
                    }
                }
                $time = sprintf( "%.0f minutes", ($timeSeconds / 60) );
                $dist = sprintf( "%.1f miles", ($distMeters / 1609.34) );
                $size = sprintf( "%.0f ft", ($sizeMeters * 3.28084) );

                echo "<tr class=\"fieldrow\" data-fieldkey=\"$id\">";
                echo "<td id=\"goodcolumn\"><input type=\"checkbox\" class=\"good $indy\" data-fieldkey=\"$id\" id=\"goodcb$id\" name=\"good\" value=\"good\" $goodchecked/><label for=\"goodcb$id\"></label></td>";
                echo "<td id=\"timecolumn\">$time</td>";
                echo "<td id=\"distcolumn\">$dist</td>";
                echo "<td id=\"addrcolumn\">$address</td>";
                echo "<td id=\"sizecolumn\">$size</td>";
                echo "</tr>\n";
            }
            ?>
                </tbody>
            </table>
        </div>
        <div id="mapview">
            Select field to view map...
        </div>
    </div>
    <div id="testDiv"></div>
<script>
$(function(){
  $("#fieldTable").tablesorter({

      sortList: [[1 ,0]],
      // *** CSS CLASS NAMES ***
      tableClass: 'tablesorter',
      cssAsc: "tablesorter-headerSortUp",
      cssDesc: "tablesorter-headerSortDown",
      cssHeader: "tablesorter-header",
      cssHeaderRow: "tablesorter-headerRow",
      cssIcon: "tablesorter-icon",
      cssChildRow: "tablesorter-childRow",
      cssInfoBlock: "tablesorter-infoOnly",
      cssProcessing: "tablesorter-processing"
  });
});
</script>
        <?php
        pg_close($link);
        ?>
    </body>
    </html>
