#!/bin/sh
set -e

TWINE_REPOSITORY_URL=${TWINE_REPOSITORY_URL:="https://upload.pypi.org/legacy/"}
TWINE_USERNAME=${TWINE_USERNAME:="xliiv"}

pip install twine
pip install wheel


# callspectpy
cd collector/
python setup.py sdist bdist_wheel
twine upload --user $TWINE_USERNAME --repository-url $TWINE_REPOSITORY_URL dist/*
cd -

# callspect
cd viewer/
python setup.py sdist bdist_wheel
twine upload --user $TWINE_USERNAME --repository-url $TWINE_REPOSITORY_URL dist/*
cd -
