This directory contains examples of probabilistic model analysis using IF and CADP. The running example used in the paper is in the directory [1-aebs-simple](./1-aebs-simple/). The directory [2-aebs](./2-aebs/) contains a more complex version of the running example. 

Each example takes the following files as input:
- an IF model inside each configuration (e.g., [1-aebs-simple/configurations/C1/simple.if](./1-aebs-simple/configurations/C1/simple.if)).
- a template for probabilistic query formulas in MCL5,
    - for instance, [1-aebs-simple/configurations/C1/propcontroller-template.mcl](./1-aebs-simple/configurations/C1/propcontroller-template.mcl) is a template to query the probability of having 0 to N useless actuations during a controller execution (N is set to 3),
- execution traces, which are generated automatically with a python script inside each example (e.g., [1-aebs-simple/simulator.py](./1-aebs-simple/simulator.py))

The script `run.sh` can be executed to run the following steps:
1. compile the IF model `simple.if` into an LTS `simple.aut`
2. simplify the LTS's labels and apply minimization algorithms, which results in a new LTS `simple-final.aut`
3. run the python simulator, which generates a set of traces inside `trace` directory in each configuration
4. compute the PTS using `ptsv.jar` to produce `simple-final-pts.aut`
5. apply the probabilistic querying on the PTS, which results in probabilities in a .txt file (e.g., `1-aebs-simple/configurations/C1/controller.txt`)
6. run the python script to plot the probabilities using matplotlib.

Additionally, in order to extract sequences ending with 0 probability transitions, the script `checkzero.sh` can be used with the following command:
``` ./checkzero.sh <configuration ID> ```
