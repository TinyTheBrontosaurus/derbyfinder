#! /bin/bash

PRE='/usr/bin/time -f "Summary._timer:_%E,_cmd:_%C" unbuffer'
POST='| ts'

$PRE ./resetDb.py $POST
$PRE ./cacheDetectorImagery.py $POST
$PRE ./runDetector.py $POST
$PRE ./markDuplicates.py $POST
$PRE ./calculateTravelCost.py $POST
echo "Execution completed"