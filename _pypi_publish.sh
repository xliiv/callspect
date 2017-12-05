#!/bin/sh
set -e

TWINE_REPOSITORY_URL="https://test.pypi.org/legacy/"
TWINE_USERNAME="xliiv"

pip install twine
pip install wheel


# callspectpy
cd collector/
python setup.py sdist bdist_wheel
twine upload --user $TWINE_USERNAME --repository-url $TWINE_REPOSITORY_URL dist/*
cd -

# callspect
cd viewer/
twine upload --user $TWINE_USERNAME --repository-url $TWINE_REPOSITORY_URL dist/*
cd -
