#!/bin/sh

RESTART=1

while [ $RESTART -lt 0 ];
do
  echo 'updating code...'
  git remote update
  git pull origin
  sudo python main.py
  RESTART=$?
done

echo 'exited'
