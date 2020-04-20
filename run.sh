#!/bin/sh

RESTART=1

while [ $RESTART ];
do
  echo 'restarting...'
  RESTART=0
  sudo python main.py || RESTART=1
done

echo 'exited.'
