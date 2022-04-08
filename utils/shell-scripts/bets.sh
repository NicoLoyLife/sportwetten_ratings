#!/bin/bash
source /home/nico/anaconda3/etc/profile.d/conda.sh

Lockfile=/tmp/bet_Lock

if [ -f $Lockfile ]
then
  exit
fi

echo >$Lockfile

cd ~/sportwetten_ratings/utils || exit

conda activate scraper
python ~/sportwetten_ratings/utils/bet.py
conda deactivate

rm $Lockfile
