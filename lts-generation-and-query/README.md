
This directory contains experiment results for the LTS generation and probabilistic temporal logic querying.
In order to run the full experiments, the following software must be installed:
- CADP (https://cadp.inria.fr/)
- IF (https://www-verimag.imag.fr/~async/IF/)
- Python (https://www.python.org/)

The models directory contains timed automata expressed using the IF language.
To generate the LTS of a model, users can run the build.sh script inside each configuration directory:
```
./build.sh
```
The command will result in files named simple-final.aut and simple-final.bcg.
The .aut file represents the LTS file textually, whereas .bcg file can be used to visually analyse the LTS using a command in CADP:
```
simple-final.bcg
```

The query directory contains probabilistic temporal logic querying using CADP.
To perform the querying, users can run the query.sh script:
```
./query.sh
```
The script returns a text file named verdicts.txt, which can be visualised using a python script in the graph directory.
