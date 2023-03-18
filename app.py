#!/usr/bin/env python3

import json
import urllib.request
from urllib.parse import quote_plus
import datetime
import sys
import configparser

import storage


def get_steam_id(username: str, api_key: str) -> str:
    base_url = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={}&vanityurl={}"
    url = base_url.format(quote_plus(api_key), quote_plus(username))
    response = urllib.request.urlopen(url)
    data = json.load(response)
    if int(data['response']['success']) == 1:
        return str(data['response']['steamid'])
    else:
        raise Exception('Failed to find steam id for user {}. {}'.format(username, data))


def get_game_data(username: str, api_key: str):
    steam_id = get_steam_id(username, api_key)
    base_url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&include_appinfo=1&format=json"
    url = base_url.format(quote_plus(api_key), quote_plus(steam_id))
    response = urllib.request.urlopen(url)
    data = json.load(response)

    return [{
        'appid': g['appid'],
        'name': g['name'],
        'last_played': g.get('rtime_last_played'),
        'hours_forever': (g.get('playtime_forever') or 0.0) / 60.0,
    } for g in data['response']['games']]


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("alembic.ini")
    conn_string = config['alembic']['sqlalchemy.url']

    store = storage.Storage(conn_string)

    api_key: str = sys.argv[1]
    users = sys.argv[2:]

    run_at = datetime.datetime.utcnow()

    store.save(storage.update_session, values={"run_at": run_at})
    session_id = store.get_max_id(storage.update_session)

    for user in users:
        store.save(storage.user, key={'username': user})
        user_data = store.get(storage.user, key={'username': user})
        user_id: int = user_data['id']  # type: ignore

        game_data = get_game_data(user, api_key)

        for game in game_data:
            if not 'last_played' in game:
                continue

            last_played_ts = game['last_played']
            last_played = datetime.datetime.utcfromtimestamp(last_played_ts)

            if 'hours_forever' in game:
                total_hours = float(game['hours_forever'])
            else:
                total_hours = 0.0

            app_id = int(game['appid'])

            existing = store.get(storage.history_entry,
                                 key={"user_id": user_id,
                                      "app_id": app_id,
                                      "last_played": last_played,
                                      "total_hours": total_hours})

            values={"user_id": user_id,
                    "app_id": app_id,
                    "name": game['name'],
                    "last_played": last_played,
                    "total_hours": total_hours,
                    "session_id": session_id}

            key = {"id": existing["id"]} if existing is not None else None

            store.save(storage.history_entry, values=values, key=key)
