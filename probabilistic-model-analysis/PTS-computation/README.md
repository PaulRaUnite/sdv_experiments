- The [source](./source/) directory contains the source code of the probabilistic model (i.e., PTS) computation, which is written in Java.

- A jar file, `ptsv.jar`, has been generated and can be used to run the computation with the following command:
``` java -cp ptsv.jar ptsv <lts> <traces> <number> ```
Here, `<lts>` is an LTS with .aut format, `<traces>` is directory that contains N traces named as T1.txt to TN.txt, and `<number>` is the number of traces (i.e., |N|).

- The outputs consist of: 
    - `<lts>-pts-rem.aut`, which is a PTS without 0 probability transitions, and 
    - `<lts>-pts.aut`, which is a PTS with the same number of states and transitions as the input LTS.

- The [example](./example/) directory contains an LTS ([simple.aut](./example/simple.aut)) and a set of traces (inside [test](./example/test/)). To compute the PTS, we use the following command:
``` java -cp ptsv.jar ptsv simple test 2 ```
This will produce `simple-rem-pts.aut` and `simple-pts.aut`