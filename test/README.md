# Tests

SpiderFoot includes various test suites.


## Unit and Integration Tests

Unit and integration tests require test dependencies to be installed:

```
pip3 install -r test/requirements.txt
```

To run the tests locally, run `./test/run` from the SpiderFoot root directory.

These tests are run on all pull requests automatically.

Module integration tests are excluded.

In this customized repository, unit tests are also used to protect newer operational helpers added around:

- scan operational memory
- action risk policy classification
- dashboard helper formatting
- correlation explanation support in the web layer

To run all unit and integration tests, including module integration tests, run:

```
python3 -m pytest -n auto --flake8 --dist loadfile --durations=5 --cov-report html --cov=. .
```


## Module Integration Tests

The module integration tests check module integration with remote third-party data sources.

To run the tests:

```
python3 -m pytest -n auto --flake8 --dist loadfile --durations=5 --cov-report html --cov=. test/integration/modules/
```


## Acceptance Tests

The acceptance tests check that the web intereface is working as
intended and that SpiderFooot is operating correctly as a whole.

These tests use a headless browser (Firefox by default), and
must be run with `./test/acceptance` as current working directory.

Requires SpiderFoot web server to be running on default port (`5001`).

Requires test dependencies to be installed:

```
pip3 install -r test/acceptance/requirements.txt
```

To run the tests, start the SpiderFoot web interface on the default port:

```
python3 ./sf.py -l 127.0.0.1:5001
```

Then run robot (override the `BROWSER` variable if necessary):

```
cd test/acceptance
robot --variable BROWSER:Firefox --outputdir results scan.robot
```

## Additional validation notes for this customized project

Besides the standard test suites above, this repository currently benefits from a few lightweight validation steps during development:

- `python -m py_compile` on modified Python files to catch syntax and import issues quickly
- template rendering checks for important Mako views such as the scan dashboard
- `node --check` on extracted or embedded JavaScript when dashboard behavior is changed

These checks are especially useful when working on:

- the scan dashboard and operational summary
- the graph and correlation panels
- the AI-assisted reanalysis workflow

If `pytest` is not installed in the active environment, these lighter checks still provide a fast smoke test while keeping the local workflow moving.
