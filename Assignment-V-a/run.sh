#! /bin/bash
if [ "$#" -ne 1 ]
then
    echo "Usage: ./run.sh test.txt"
    exit 1
fi
chmod +x 111508043_Assign5a_Code.py
./111508043_Assign5a_Code.py $1
