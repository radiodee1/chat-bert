#!/usr/bin/env bash

# sudo may not be needed here
python3.10 -m pip install virtualenv
python3.10 -m pip install virtualenvwrapper
export WORKON_HOME=$HOME/.virtualenvs
mkdir -p $WORKON_HOME
export VIRTUALENVWRAPPER_PYTHON=$(which python3.10)
source $(which virtualenvwrapper.sh)

mkvirtualenv chatbert310 --python $(which python3.10)

## type `deactivate` to exit ##
