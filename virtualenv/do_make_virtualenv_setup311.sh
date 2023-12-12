#!/usr/bin/env bash

python3 -m venv $HOME/.virtualenvs/chatbert311 --prompt chatbert311

. $HOME/.virtualenvs/chatbert311/bin/activate

pip install -U pipeline-ai

pipeline cluster login catalyst-api $LLAMA_PIPELINE -u https://mystic.ai -a 
## type `deactivate` to exit ##
