
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

<style>
.staticmappic {
    overflow: hidden;
}
.overlaidmappicwrapper{
width:640px;
height:640px;
margin:0px 0px; }

.overlaidmappic{
width:100%; height:100%;
position:relative;}

.coveredImage{
width:100%; height:100%;
position:absolute; top:0px; left:0px;
}

.fieldOverlay{
width:100%; height:100%;
position:absolute; top:0px; left:0px;
}


<?php
    for( $ang = 0; $ang < 359; $ang = $ang + 15 )
    {
        echo ".rotate$ang {\n";
            echo "width: 640px;\n";
            echo "height: 640px;\n";
            echo "   -webkit-transform: rotate({$ang}deg);\n";
            echo "   -moz-transform: rotate({$ang}deg);\n";
            echo "   -o-transform: rotate({$ang}deg);\n";
            echo "   -ms-transform: rotate({$ang}deg);\n";
            echo "   transform: rotate({$ang}deg);\n";
            echo "}\n";
        }
?>
</style>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
<script type="text/javascript">
function fieldOverlay()
{
    var canvasSet = document.getElementsByClassName( 'fieldOverlay' );
    var shiftDist = $('.overlaidmappic').attr( 'data-shiftDist');

    // Calculated with cheesy script for around Boston. TODO: dynamically calculate
    var metersPerPixel = 0.22
    var feetPerMeter = 3.28084

    var homex = 320;
    // 100 feet for the image shift. 80 feet for the center-to-home shift
    var homey = 320 + shiftDist / metersPerPixel;
    var homesize = 20;

    // Create section borders
    var sectionBordersFt = [180, 270, 300, 400];
    sectionBorders = new Array( sectionBordersFt.length);
    for (var borderi = 0; borderi < sectionBordersFt.length; borderi++)
    {
        sectionBorders[borderi] = sectionBordersFt[borderi] / feetPerMeter / metersPerPixel;
    }
    var sectionColors  = ["rgba(139, 0, 34, 0.25)", "rgba(0, 128, 0, 0.25)","rgba(139, 0, 22, 0.25)"];

    // Iterate over all images
    for(var imagei = 0, imageCount = canvasSet.length; imagei < imageCount; imagei++) {
        // Get the individual image for the overlay
        canvas1 = canvasSet[imagei].getContext( '2d' );

        // Draw a red X over home plate
        canvas1.beginPath();
        canvas1.lineWidth = 4;
        canvas1.strokeStyle = '#8b0022';
        canvas1.moveTo( homex + homesize/2, homey + homesize/2 );
        canvas1.lineTo(  homex - homesize/2, homey - homesize/2 );
        canvas1.moveTo( homex + homesize/2, homey - homesize/2 );
        canvas1.lineTo(  homex - homesize/2, homey + homesize/2 );
        canvas1.stroke();

        // Draw the sections over the outfield
        for( var sectioni = 0, sectionCount = sectionColors.length; sectioni < sectionCount; sectioni++ )
        {
            var near = sectionBorders[sectioni];
            var far = sectionBorders[sectioni+1];
            var fill = sectionColors[sectioni];
            canvas1.fillStyle = fill;
            canvas1.lineWidth = 1;
            canvas1.strokeStyle = '#000000';
            canvas1.beginPath();
            canvas1.arc(homex, homey, near, Math.PI/4 - Math.PI/2, -Math.PI/4 -Math.PI/2, true);
            canvas1.arc(homex, homey, far, -Math.PI/4 -Math.PI/2, Math.PI/4 - Math.PI/2, false);
            canvas1.closePath();
            canvas1.stroke();
            canvas1.fill();
        }
    }

    $('#overlayToggle').click( function() {
        syncOverlayVis();
    });

    $('.falsepos').click( function() {
        var falsepos = $('#falsepos').prop( 'checked');
        $.ajax({
            url: 'update.php',
            type: "PUT",
            data: {
                'falsepos': falsepos,
                'fieldKey': window.$currentField
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
    })

    function syncOverlayVis() {
        // Make sure the class exists
        if( ( $('.fieldOverlay')[0])) {
            if( $('#overlayToggle').prop('checked' ) ) {
                setting = 'visible';
            }
            else {
                setting = 'hidden';
            }
            $('.fieldOverlay').css( {'visibility' : setting})
        }
    }
}
</script>

<?php
// Load the field primary key
if( isset( $_POST['fieldKey'] ) )
{
    $fieldKey = $_POST['fieldKey'];
}
else
{
    $fieldKey = '3';
}
?>
<div id="mapimage">
<?php
    // Get all fields
    $result = pg_exec($link, "SELECT location.lat, location.lon, field.angle, field.fieldSize, field.good::int, field.falsePositive::int " .
                             "FROM field " .
                             "NATURAL JOIN location " .
                             "WHERE field.fieldid = $fieldKey;" );
    $apikey=$config["imagery"]["apiKey"];
    $row = pg_fetch_array($result, 0);

    // TODO: Hokey method to calculate geodetic distances. Should calculate

    function moveLatLon( $lat, $lon, $dist, $angle )
    {
        $degPerMeterLat = 0.000009002478;
        $degPerMeterLon = 0.000012140776;
        $metersPerPixel = 0.22;

        $angR = -deg2rad( $angle );

        $deltaLat = cos( $angR ) * $dist * $degPerMeterLat;
        $deltaLon = sin( $angR ) * $dist * $degPerMeterLon;

        $shiftedPoint["lat"] = $deltaLat + $lat;
        $shiftedPoint["lon"] = $deltaLon + $lon;
        return $shiftedPoint;
    }

    $angle = $row["angle"];

    $feetPerMeter = 3.28084;
    $metersPerPixel = 0.22;
    $latPitcher = $row["lat"];
    $lonPitcher = $row["lon"];
    // Place home plate at the center of the image
    $shiftHome = -$row["fieldsize"] / 2.0;
    // Move home plate down by this many pixels. (320 is half the width. 260 gives a 60 pixel buffer past home)
    $shiftDist = 260 * $metersPerPixel;
    $shiftFull = $shiftDist + $shiftHome;
    $shiftedPoint = moveLatLon( $latPitcher, $lonPitcher, $shiftFull, $angle);
    $lat = $shiftedPoint["lat"];
    $lon = $shiftedPoint["lon"];

    $zoom="19";
    $scale="1";
    $size="640x640";
    $maptype="satellite";
    $format="png";

    $staticmap = "<img src=\"http://maps.googleapis.com/maps/api/staticmap?center=$lat,$lon&zoom=$zoom&scale=$scale&size=$size&maptype=$maptype&format=$format&key=$apikey\" alt=\"Field at $lat, $lon\">";
    ?>

    <div class="overlaidmappicwrapper">
    <div class="overlaidmappic" data-shiftDist="<?php echo $shiftDist;?>">
    <div class="staticmappic coveredimage">
    <div class="rotate<?php echo $angle; ?>">
    <?php echo "$staticmap"; ?>
    </div>
    </div>
    <canvas class = "fieldOverlay" width ="640" height="640"></canvas>
    </div>
    </div>
    <script>fieldOverlay();</script>


</div>
</div>
<div id="mapedit">
    <?php

    $falseposchecked = "";
    if( $row["falsepositive"] === 't' )
    {
        $falseposchecked = "checked";
    }
    $linkToGoogle = "https://maps.google.com/?q=$lat,$lon&z=$zoom&t=k";

     ?>
    <a target="_blank" href="<?php echo $linkToGoogle; ?>">Google Maps</a><br />
    <label><input id="overlayToggle" type="checkbox" name="overlay" value="overlay" checked>Show overlay </label><br />
    <label><input type="checkbox" class="falsepos" id="falsepos" name="falsepos" value="falsepos" <?php echo $falseposchecked; ?>>This is not a field </label><br />

</div>
<?php
pg_close($link);
?>
