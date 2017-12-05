#!/bin/sh
set -e

TWINE_REPOSITORY_URL=${TWINE_REPOSITORY_URL:="https://upload.pypi.org/legacy/"}
TWINE_USERNAME=${TWINE_USERNAME:="xliiv"}

echo "pip"
pip install twine
pip install wheel


echo "cd"
# callspectpy
cd collector/
echo "coll"
python setup.py sdist bdist_wheel
echo "up"
#twine upload --user $TWINE_USERNAME --repository-url $TWINE_REPOSITORY_URL dist/*
echo "cd"
cd -

# callspect
echo "cd v"
cd viewer/
echo "up"
#twine upload --user $TWINE_USERNAME --repository-url $TWINE_REPOSITORY_URL dist/*
echo "cd"
cd -
