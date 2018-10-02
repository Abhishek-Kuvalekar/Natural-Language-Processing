#!/bin/bash
if [ "$#" -ne 2 ]
then
    echo "Usage: ./run.sh <training_file> <testing_file>"
    exit 1
fi
chmod +x viterbi.py
./viterbi.py $1 $2
rm *.pickle
