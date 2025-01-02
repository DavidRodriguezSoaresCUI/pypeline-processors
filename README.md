# [pypeline-processors](https://github.com/DavidRodriguezSoaresCUI/pypeline-processors)

A collections of processors I wrote for the Pypeline project. Feel free to reuse them !

## Requirements

This project was developed for Python 3.10 and may not work on lower versions.

## Installation

From a terminal execute:

```bash
python -m pip install pypeline-processors-DavidRodriguezSoaresCUI
```

> Note that on some systems it may be necessary to specify python version as `python3` or `python3.10`

### Installation from source

Download/``git clone`` the project, open it in a terminal end execute ``python -m pip install .``

### Install optional dependencies

To install dependencies required for building documentation : ``python -m pip install .[doc]`` (or if you use `flit` : ``flit install --deps=doc``)

To install dependencies required for code analysis : ``python -m pip install .[analyse]`` (or if you use `flit` : ``flit install --deps=analyse``)

To install dependencies required for running tests : ``python -m pip install .[test]`` (or if you use `flit` : ``flit install --deps=test``)

## Run tests

First some requirements (step 3 needs to be re-run if you make changes) :

1. Download/``git clone`` the project and open it in a terminal
2. Install the testing requirements with ``python -m pip install .[test]``
3. Install the project with ``python -m pip install -e .``
   > It needs to be installed in editable mode for coverage to work

Then you can simply run ``pytest`` (from a terminal at the downloaded project directory)
