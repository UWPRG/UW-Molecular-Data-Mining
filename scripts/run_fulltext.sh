#!/bin/bash

# This script runs multiple parallel Elsevier fulltext calls

echo "starting first"
./Elsevier_fulltext_api.py --jobs 4 --job_id 1 &  #start the first job


echo "starting second"
./Elsevier_fulltext_api.py --jobs 4 --job_id 2 &  #start the second job

echo "starting third"
./Elsevier_fulltext_api.py --jobs 4 --job_id 3 &  #start the third job

echo "starting fourth"
./Elsevier_fulltext_api.py --jobs 4 --job_id 4 &  #start the fourth job

#echo "starting fifth"
#./Elsevier_fulltext_api.py --jobs 5 --job_id 5 &  #start the fifth job

wait

echo "all done davie boy"
