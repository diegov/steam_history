#!/usr/bin/env python3

import sys

key = sys.argv[1]
username = sys.argv[2]

from app import get_game_data

games = get_game_data(username, key)

import csv

with open('games.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['appid', 'name', 'priority'])
    for game in games:
        writer.writerow([game['appid'], game['name']])
