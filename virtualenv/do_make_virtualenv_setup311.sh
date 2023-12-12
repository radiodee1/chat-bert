#!/usr/bin/env bash

# sudo may not be needed here
python3.11 -m pip install virtualenv
python3.11 -m pip install virtualenvwrapper
export WORKON_HOME=$HOME/.virtualenvs
mkdir -p $WORKON_HOME
export VIRTUALENVWRAPPER_PYTHON=$(which python3.11)
source $(which virtualenvwrapper.sh)

mkvirtualenv chatbert311 --python $(which python3.11)

## type `deactivate` to exit ##
