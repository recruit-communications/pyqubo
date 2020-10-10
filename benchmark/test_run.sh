#!/usr/bin/env bash
set -eu

INIT_SIZE=5
MAX_SIZE=100
STEP=5
TIMEOUT=1500

function run(){
    export PATH=/opt/python/cp36-cp36m/bin/:$PATH
    python -m pip install virtualenv
    python -m virtualenv $1
    . $1/bin/activate
    pip install -r requirements.txt
    pip install $2
    python benchmark_tsp.py -i $INIT_SIZE -m $MAX_SIZE -s $STEP -t $TIMEOUT
    deactivate
}

run latest pyqubo==1.0.0
run older pyqubo==0.4.0

exit 0
