import requests
import json
import os
import time

from si_prefix import si_format

DEBUG = 0

ticker_file_path = 'files/tickers.json'
ticker_reverse_file_path = 'files/tickers_reverse.json'

if not os.path.isfile(ticker_file_path):
    with open(ticker_file_path, 'w') as f:
        f.write('{}')

if not os.path.isfile(ticker_reverse_file_path):
    with open(ticker_reverse_file_path, 'w') as f:
        f.write('{}')

def get_current_time_millis():
    return int(round(time.time() * 1000))

def set_prefix(number):
    if number < 1000:
        return number
    else:
        return si_format(number, precision=2)


def get_new_ticker_file():
    url_ticker = 'https://s3-us-west-2.amazonaws.com/data.pooltool.io/stats/tickers.json'
    try:
        r = requests.get(url_ticker)
        if r.ok:
            return r.json()
    except requests.exceptions.RequestException as e:
        return 'error'


def handle_wallet_newpool(db):
    data = get_new_ticker_file()

    for poolid in data:

        if db.does_pool_id_exist(poolid):
            if not db.does_pool_ticker_exist(poolid, data[poolid]['ticker']):
                db.update_ticker(poolid, data[poolid]['ticker'])
        else:
            db.add_new_pool(poolid, data[poolid]['ticker'])

    print("DB is updated")


def clean_up_pools_table(db):
    pools = db.get_all_pools()

    for pool in pools:
        try:
            db.delete_pool(pool)
        except Exception as e:
            print("Could not delete pool")

    print("Clean up pools table DONE!")