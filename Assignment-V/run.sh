#! /bin/bash
if [ "$#" -ne 2 ]
then
    echo "Usage: ./run.sh test.txt manual.txt"
    exit 1
fi
chmod +x 111508043_Assign5_Code.py
./111508043_Assign5_Code.py $1 $2
