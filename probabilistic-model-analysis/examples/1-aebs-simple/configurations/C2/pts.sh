model="simple-final"
trace="trace"
numtrace=20

java -cp ptsv.jar ptsv $model $trace $numtrace
bcg_io $model"-pts.aut" $model"-pts.bcg"
