#! /bin/bash
if [ "$#" -ne 1 ]
then
    echo "Usage: $0 file"
    exit 1
fi
chmod +x 111508043_code-2.py
./111508043_code-2.py $1
