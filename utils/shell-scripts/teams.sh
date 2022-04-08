#!/bin/bash
source /home/nico/anaconda3/etc/profile.d/conda.sh

Lockfile=/tmp/team_Lock

if [ -f $Lockfile ]
then
  exit
fi

echo >$Lockfile

cd ~/sportwetten_ratings/utils || exit

conda activate scraper
python ~/sportwetten_ratings/utils/team.py
conda deactivate

rm $Lockfile
