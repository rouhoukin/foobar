# -*- coding: utf-8 -*-
import logging
from logging import FileHandler
from logging.handlers import RotatingFileHandler, SysLogHandler
from logging import config
import os
import sys
from pathlib import Path
import getopt
import re
from datetime import datetime, timedelta
from dateutil.parser import parse
from time import time
import pandas as pd
import numpy as np
import json
import pymongo
from pymongo import errors, UpdateOne
import MetaTrader5 as mt5
import pytz
from time import time, sleep

mt5_paths = ["D:/rou/sync/tools/mt5/MT5_demo/terminal64.exe"]

# p_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
p_dir = os.path.abspath(os.getcwd())
me = os.path.splitext(os.path.basename(sys.argv[0]))[0]

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fHandler = FileHandler(me + ".log", encoding='utf-8')
fHandler.setLevel(logging.INFO)
fHandler.setFormatter(formatter)

errHandler = FileHandler(me + "_err.log", encoding='utf-8')
errHandler.setLevel(logging.ERROR)
errHandler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)

logger.addHandler(fHandler)
logger.addHandler(errHandler)
logger.addHandler(console)

paras = {
    'EURUSD': [24, 100000, [
                            'H1',
                            # 'M5',
                            # 'M15',
                            ]],
}

ped_secs = {
    'M1': 60, 'M5': 60 * 5, 'M15': 60 * 15, 'M30': 60 * 30,
    'H1': 60 * 60, 'H4': 60 * 60 * 4, 'D1': 60 * 60 * 24,
}

broker = 'DEMO'
client = pymongo.MongoClient('localhost', 27017)
force_rebuild = False
force_from = None
# force_from = '2024-01-01 00:00:00'


def get_newest_from_db(clt=client, cur='EURUSD', period=''):
    _col_nm = broker + '_' + cur + '_' + 'MT5'
    if len(period) > 0:
        _col_nm = broker + '_' + cur + '_' + 'MT5' + '_' + period

    _collection = clt['fx'][_col_nm]
    lst = list(_collection.find().sort("DT_MT4_OUT", pymongo.DESCENDING).limit(1))
    _newest = None
    if lst:
        _newest = dict(lst[0])['DT_MT4_OUT']

    # print('tg=', tg, 'newest=', _newest)
    logger.info("Get newest date={0} from DB ({1})".format(_newest, _col_nm))
    return _newest


def main(argv):
    logger.info("Start {0} ...".format(me))
    method = ''
    try:
        opts, args = getopt.getopt(argv[1:], 'hm:', ['method'])
    except getopt.GetoptError:
        print('usage:', me, '-m <method>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('usage:', me, '-m <method>')
            sys.exit()
        elif opt in ('-m', '--method'):
            method = arg

    if not method:
        print('usage:', me, '-m <method>')
        sys.exit()

    elif method == '1':  # gen each period data from mt5
        # TODO: 1 -2025/1/27
        logger.info("{0} Getting period data...".format(method))
        for mt5_path in mt5_paths:
            if not mt5.initialize(mt5_path, portable=True):
                logger.error("initialize() failed, error code = {0}".format(mt5.last_error()))
                exit(0)
            # display data on MetaTrader 5 version
            # print(mt5.version())
            # print(mt5.terminal_info())
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("not to connect at account")
                # shut down connection to the MetaTrader 5 terminal
                # mt5.shutdown()
                exit(0)

            # display trading account data 'as is'
            # print(account_info)
            # display trading account data in the form of a list
            # account = account_info_dict['login']
            # print(account)
            # exit(0)

            now = datetime.now()
            last_dt = (now - timedelta(weeks=12)).strftime('%Y-%m-%d %H')
            # latest_dt = '2022-11-01 00:00:00'
            # last_dt = parse(latest_dt)
            for target in paras.keys():
                # logger.info("Process {0}...".format(target))
                print(target)
                peds = paras[target][2]
                for ped in peds:
                    logger.info("Process {0} {1}...".format(target, ped))

                    first = False
                    # timezone = pytz.timezone("Etc/UTC")
                    latest_dt = get_newest_from_db(clt=client, cur=target, period=ped)
                    if not latest_dt:
                        first = True
                        latest_dt = (now - timedelta(seconds=ped_secs[ped] * 100000)).strftime('%Y-%m-%d %H')
                        # latest_dt = datetime.now(tz=timezone)
                    if force_from and force_from < latest_dt:
                        latest_dt = force_from
                    last_dt = parse(latest_dt) - timedelta(seconds=ped_secs[ped] * 60 * 24 * 5)
                    # print(last_dt)
                    # exit(0)
                    d = timedelta(days=1)
                    d_s = timedelta(hours=1)
                    if ped == 'M1':
                        p = mt5.TIMEFRAME_M1
                    elif ped == 'M5':
                        p = mt5.TIMEFRAME_M5
                    elif ped == 'M10':
                        p = mt5.TIMEFRAME_M10
                    elif ped == 'M15':
                        p = mt5.TIMEFRAME_M15
                    elif ped == 'M30':
                        p = mt5.TIMEFRAME_M30
                    elif ped == 'H1':
                        p = mt5.TIMEFRAME_H1

                    timezone = pytz.timezone("Etc/UTC")
                    # drg = pd.date_range(last_dt, datetime.now(), freq='W').shift(1)
                    drg = pd.date_range(last_dt, datetime.now() + timedelta(weeks=1), freq='W').shift(1)
                    # for m in drg:
                    #     m_str2 = (m - timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M')
                    #     m_str3 = m.strftime('%Y-%m-%d %H:%M')
                    #     print("From mt5 {2} rates from {0} to {1}".format(m_str2, m_str3, ped))
                    # exit(0)
                    for m in drg:
                        m_str = m.strftime('%Y-%m-%d %H:%M')
                        m_str2 = (m - timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M')
                        m_str3 = m.strftime('%Y-%m-%d %H:%M')
                        logger.info("From mt5 {2} rates from {0} to {1}".format(m_str2, m_str3, ped))

                        st_dt = m - timedelta(weeks=1)
                        ed_dt = m
                        # create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset
                        utc_from = datetime(st_dt.year, st_dt.month, st_dt.day, hour=st_dt.hour, tzinfo=timezone)
                        utc_to = datetime(ed_dt.year, ed_dt.month, ed_dt.day, hour=ed_dt.hour, tzinfo=timezone)
                        # print(utc_from)
                        # print(utc_to)
                        # exit(0)
                        rates = mt5.copy_rates_range(target, p, utc_from, utc_to)

                        df = pd.DataFrame(rates)
                        # convert time in seconds into the datetime format
                        df['time'] = pd.to_datetime(df['time'], unit='s')
                        # display data
                        # print(df)
                        # df.to_csv('out/out.csv', encoding='gbk', index=True)

                        # df.set_index('TS_UTC', drop=False, inplace=True)
                        df2 = df[['time', 'open', 'close', 'high', 'low']].copy()
                        df2['UPD_BY'] = now.strftime('%Y-%m-%d %H:%M:%S')
                        df2['DT_MT4_OUT'] = df2['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                        df2.drop(['time'], axis=1, inplace=True)
                        df2 = df2[(df2['DT_MT4_OUT'] >= m_str2) & (df2['DT_MT4_OUT'] < m_str3)]
                        # df2.to_csv('out/out2.csv', encoding='gbk', index=True)

                        col_nm = broker + '_' + target + '_MT5_' + ped
                        # print(col_nm)
                        # collection = client_rmt['foobar'][col_nm]
                        collection = client['foobar'][col_nm]
                        if len(df2['DT_MT4_OUT']) == 0:
                            logger.info("No data")
                            continue
                        logger.info("writing {0} records to {1}...".format(len(df2['DT_MT4_OUT']), col_nm))
                        # exit(0)
                        start = time()
                        collection.create_index([('DT_MT4_OUT', pymongo.ASCENDING)], unique=True)
                        try:
                            upserts = [UpdateOne({'DT_MT4_OUT': x['DT_MT4_OUT']}, {'$setOnInsert': x}, upsert=True) for x in json.loads(df2.T.to_json()).values()]
                            result = collection.bulk_write(upserts)
                            # collection.insert_many(json.loads(df2.T.to_json()).values())
                        except (SystemExit, KeyboardInterrupt):
                            raise
                        except errors.BulkWriteError as e:
                            logger.error(str(e), exc_info=False)
                            # print(str(e))
                            exit(1)
                            continue

                        logger.info("writing end. used {} second(s)".format(round(time() - start, 3)))
                        # exit(0)

        # shut down connection to the MetaTrader 5 terminal
        # mt5.shutdown()

        logger.info("{0} Getting period data end".format(method))


# TODO: main
if __name__ == "__main__":
    # print(p_dir)
    # print(me)
    # print('test')
    # exit(0)
    main(sys.argv)


