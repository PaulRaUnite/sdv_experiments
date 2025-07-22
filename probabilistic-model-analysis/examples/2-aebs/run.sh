confnum=2
confIdx=1

for (( c=1; c<=$confnum; c++ ))
do
    printf  "\n!!!!! Generating C$c LTS !!!!!\n"
    if [ $c == 1 ]
    then
        cd configurations/C$c/
    else
        cd ../C$c/
    fi
    ./build.sh
done

printf  "\n!!!!! Running the simulator !!!!!\n"
cd ../..
python simulator.py

confIdx=1
for (( c=1; c<=$confnum; c++ ))
do
    printf  "\n!!!!! Computing C$c PTS !!!!!\n"
    if [ $c == 1 ]
    then
        cd configurations/C$c/
    else
        cd ../C$c/
    fi
    ./pts.sh

    printf  "\n!!!!! Querying C$c !!!!!\n"
    ./query.sh
done

printf  "\n!!!!! Plotting the graphs !!!!!\n"
cd ../..
python graphall.py
