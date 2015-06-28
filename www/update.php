
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

parse_str( file_get_contents( 'php://input' ), $_PUT );
?>

<?php
// Update but only if everything is valid
if( isset( $_PUT['fieldKey'] ) )
{
    $key = $_PUT['fieldKey'];
    $sqlCmd = "UPDATE field ";

    if( isset( $_PUT['isValid']) )
    {
        $good = ( $_PUT['isValid'] == "false" ) ? 'false' : 'true';
        $sqlCmd .= " SET good = '$good' ";
    }
    if( isset( $_PUT['falsepos']) )
    {
        $falsepos = ( $_PUT['falsepos'] == "false" ) ? 'false' : 'true';
        $sqlCmd .= " SET falsePositive = '$falsepos' ";
    }
    $sqlCmd .= " WHERE fieldid = $key;";
    pg_exec( $link, $sqlCmd);
    echo $sqlCmd;
}
else {
    print_r($_PUT);
    echo "Nothing to update";
}
?>

<?php
pg_close($link);
?>
