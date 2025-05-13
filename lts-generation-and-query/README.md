
This directory contains experiment results for the LTS generation and probabilistic temporal logic querying.
In order to run the full experiments, the following software must be installed:
- CADP (https://cadp.inria.fr/)
- IF (https://www-verimag.imag.fr/~async/IF/)
- Python (https://www.python.org/)

The models directory contains timed automata expressed using the IF language.
To generate the LTS of a model, users can run the build.sh script.

The query directory contains probabilistic temporal logic querying using CADP.
To perform the querying, users can run the query.sh script.

The graph directory contains the visualization of the query results.
To show the graph, users can run the python code graphall.py.
