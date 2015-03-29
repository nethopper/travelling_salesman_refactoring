# Travelling salesman
This is the solution for the refactoring part of the Software Development coursework.
The software implements a solver for the travelling salesman problem, using an ant colony optimization algorithm.
The task was to take the initial code and make it more usable and maintainable.

This was achieved here by:

* Writing integration and unit tests
* Renaming classes and variable
* Extracting methods to adhere to the Single Level of Abstraction principle
* Implementing output using the `logging` library instead of `print` statements
* Implementing command-line arguments to control I/O and parameters
* Getting rid of implicit shared state in classes

## How to...
### Set up project
    git clone https://github.com/nethopper/travelling_salesman_refactoring.git
    virtualenv travelling_salesman_refactoring/
    cd travelling_salesman_refactoring/
    source bin/activate
    pip install -r requirements.txt
    pip install -e .

### Run tests
    py.test travelling_salesman/

Integration tests are marked as slow, so that they can be skipped with:

    py.test -m 'not slowtest' travelling_salesman/

### Create executable distribution
    pyinstaller travelling_salesman/travelling_salesman.py

### Run distribution
To see a list of available options:

    ./dist/travelling_salesman/travelling_salesman --help

To run the code using `data/citiesAndDistances.pickled` as input and output CSV to `data/ouput.csv` and print some progress information:

    ./dist/travelling_salesman/travelling_salesman --output data/output.csv -v data/citiesAndDistances.pickled
