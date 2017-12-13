#!/usr/bin/env python3

from lxml import html
import urllib.request
from cssselect import HTMLTranslator
import slimit
from slimit import ast
from slimit.parser import Parser
from slimit.visitors import nodevisitor
import ast as lit_parser
import datetime
import sys
import configparser

import storage

def parse_script(data):
    parser = Parser()
    tree = parser.parse(data)
    variables = [node for node in nodevisitor.visit(tree)
                 if isinstance(node, ast.VarDecl)]
    return variables


def eval_literal(value):
    if value == 'true':
        return True
    elif value == 'false':
        return False
    return lit_parser.literal_eval(value)


def to_map(parsed_object):
    def get_value(obj):
        if hasattr(obj, 'value'):
            return eval_literal(getattr(obj, 'value'))            
        elif hasattr(obj, 'items'):
            return [to_map(item) for item in obj.items]
        else:
            return to_map(obj)
        
    return {eval_literal(getattr(node.left, 'value', '')): get_value(node.right)
            for node in parsed_object.properties}


def get_game_data(username):
    wishlist_url = 'http://steamcommunity.com/id/%s/games/?tab=all' % (username,)

    response = urllib.request.urlopen(wishlist_url)
    html_data = response.read().decode('utf-8')
    doc = html.document_fromstring(html_data)
    translator = HTMLTranslator()
    row_selector = translator.css_to_xpath('script[language=javascript]')

    games = None
    for el in doc.xpath(row_selector):
        variables = parse_script(el.text_content())
        for variable in variables:
            if variable.identifier.value == 'rgGames':
                games = variable

    return[to_map(item) for item in games.initializer.items]


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("alembic.ini")
    conn_string = config['alembic']['sqlalchemy.url']

    store = storage.Storage(conn_string)

    users = sys.argv[1:]

    run_at = datetime.datetime.now()

    store.save(storage.update_session, values={"run_at": run_at})
    session_id = store.get_max_id(storage.update_session)

    for user in users:
        store.save(storage.user, key={'username': user})
        user_data = store.get(storage.user, key={'username': user})
        user_id = user_data['id']
        
        game_data = get_game_data(user)

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
