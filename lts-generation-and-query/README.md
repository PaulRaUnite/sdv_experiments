
This directory contains experiment results for the LTS generation and probabilistic temporal logic querying.
In order to run the full experiments, the following software must be installed:
- CADP (https://cadp.inria.fr/)
- IF (https://www-verimag.imag.fr/~async/IF/)
- Python (https://www.python.org/)
- Java (https://www.java.com/en/download/manual.jsp)

The models directory contains timed automata expressed using the IF language (simple.if).
To generate the LTS of a model, users can run the build.sh script inside each configuration directory:
```
./build.sh
```
The command will result in files named simple-final.aut and simple-final.bcg.
The .aut file represents the LTS file textually, whereas .bcg file can be used to visually display the LTS using a command in CADP:
```
bcg_edit simple-final.bcg
```

The query directory contains probabilistic temporal logic querying using CADP.
To perform the querying, users can run the query.sh script:
```
./query.sh
```
This script takes the simple-final.aut (LTS), trace.txt (execution trace from the simulator), and props-template.mcl (probabilistic formula) files as input.
It returns an LTS that has been enriched with probabilities named simple-final-pts.aut
It also returns a file that contains the query results named verdicts.txt, which can be visualised using a python script in the graph directory.
