# codeforlife-package-python

This repo contains CFL's python package. This will be installed into all backend services.

## Installation

This package requires Python 3.7 to be installed. See the package's [setup](setup.py).

*Remember to replace the version number ("0.0.0") with your [desired version](https://github.com/ocadotechnology/codeforlife-package-python/releases).*

Install via pipenv:

```bash
pipenv install git+https://github.com/ocadotechnology/codeforlife-package-python.git@v0.0.0#egg=codeforlife
```

Or add a row to `[packages]` in Pipfile:

```toml
[packages]
codeforlife = {ref = "v0.0.0", git = "https://github.com/ocadotechnology/codeforlife-package-python.git"}
```

## Version Release

New versions of this package are automatically created via a GitHub Actions [workflow](.github/workflows/python-package.yml). Versions are determined using the [semantic-release commit message format](https://semantic-release.gitbook.io/semantic-release/#commit-message-format).

A new package may only be released if:

1. there are no formatting errors;
1. all unit tests pass;
1. (TODO) test/code coverage is acceptable.
