#!/bin/sh

RESTART=255

while [ $RESTART -eq 255 ];
do
  echo 'updating code...'
  git remote update
  git pull origin
  sudo python3 main.py
  RESTART=$?
  echo 'exit code: ' $RESTART
done

echo 'exited'
