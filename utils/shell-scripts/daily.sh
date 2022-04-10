#!/bin/bash
source /home/nico/anaconda3/etc/profile.d/conda.sh

Lockfile=/tmp/daily_Lock

if [ -f $Lockfile ]
then
  exit
fi

echo >$Lockfile

cd ~/sportwetten_ratings/utils || exit

conda activate scraper
python ~/sportwetten_ratings/utils/bet.py
python ~/sportwetten_ratings/utils/bookmaker.py
python ~/sportwetten_ratings/utils/country.py
python ~/sportwetten_ratings/utils/team.py
python ~/sportwetten_ratings/utils/odd.py
conda deactivate

rm $Lockfile
