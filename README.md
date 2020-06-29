This repo contains tools for building the ACL2020 virtual conference website.
* [website repo](https://github.com/acl-org/acl-2020-virtual-conference)
* [sitedata](https://github.com/acl-org/acl-2020-virtual-conference-sitedata)

## Development

### Requirements
* [Python](https://www.python.org/downloads/) >= 3.7
* [virtualenv](https://virtualenv.pypa.io/en/latest/) >= 16.4.3
* [GNU Make](https://www.gnu.org/software/make/) >= 3.8.1

### Build
* Create a new sandbox (aka venv) and install required python libraries into it
    ```bash
    virtualenv --python=python3.7 venv
    source venv/bin/activate

    # Install Python packages
    pip install -r requirements-dev.txt
    ```
* Run `make` to execute all tests.

### Pull Request
* We force the following checks in before changes can be merged into master:
  [isort](https://pypi.org/project/isort/),
  [black](https://black.readthedocs.io/en/stable/),
  [pylint](https://www.pylint.org/),
  [mypy](http://mypy-lang.org/).
    * You can run `make` to executes all checks.
    * To fix any formatting or import errors, you can simply run `make format`.
    * For more details, see the `format` and `format-check` tasks in the [Makefile](./Makefile)
