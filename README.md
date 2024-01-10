# codeforlife-package-python

This repo contains CFL's python package. This will be installed into all backend services.

## Installation

To install this package, do one of the following options.

*Ensure you're installing the package with the required python version. See [setup.py](setup.py).*

*Remember to replace the version number ("0.0.0") with your [desired version](https://github.com/ocadotechnology/codeforlife-package-python/releases).*

**Option 1:** Run `pipenv install` command:

```bash
pipenv install git+https://github.com/ocadotechnology/codeforlife-package-python.git@v0.0.0#egg=codeforlife
```

**Option 2:** Add a row to `[packages]` in `Pipfile`:

```toml
[packages]
codeforlife = {ref = "v0.0.0", git = "https://github.com/ocadotechnology/codeforlife-package-python.git"}
```

## Making Changes

To make changes, you must:

1. Branch off of main.
1. Push your changes on your branch.
1. Ensure the pipeline runs successfully on your branch.
1. Have your changes reviewed and approved by a peer.
1. Merge your branch into the `main` branch.
1. [Manually trigger](https://github.com/ocadotechnology/codeforlife-package-python/actions/workflows/main.yml)
the `Main` pipeline for the `main` branch.

### Installing your branch

You may wish to install and integrate your changes into a CFL backend before it's been peer-reviewed.

*Remember to replace the branch name ("my-branch") with your
[branch](https://github.com/ocadotechnology/codeforlife-package-python/branches)*.

```toml
[packages]
codeforlife = {ref = "my-branch", git = "https://github.com/ocadotechnology/codeforlife-package-python.git"}
```

## Version Release

New versions of this package are automatically created via a GitHub Actions [workflow](.github/workflows/python-package.yml). Versions are determined using the [semantic-release commit message format](https://semantic-release.gitbook.io/semantic-release/#commit-message-format).

A new package may only be released if:

1. there are no formatting errors;
1. all unit tests pass;
1. (TODO) test/code coverage is acceptable.

TROP LOL
LOL
ENCORE PLUS DE LOL
test11
