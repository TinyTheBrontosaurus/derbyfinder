#! /bin/bash

#Run all the scripts, but do a nohup and tail the logfile so it appears to be running in the fg

PRE='/usr/bin/time -f "Summary._timer:_%E,_cmd:_%C" unbuffer'
LOGFILE=Log_`date +%Y_%m_%d_%H%M_%S`.log
cmd="nohup $PRE ./runLocal.sh"
$cmd > $LOGFILE 2>&1  &
tail -n +1 -f $LOGFILE
