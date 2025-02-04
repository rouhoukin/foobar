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

paras4 = {
    'EURUSD': 1,

    'USDJPY': 2,
    'GBPUSD': 3,
    'USDCHF': 4,
    'AUDUSD': 5,
    'NZDUSD': 6,
    'USDCAD': 7,

    'EURJPY': 8,
    'EURCHF': 9,
    'EURGBP': 10,
    'EURAUD': 11,
    'EURNZD': 12,
    'EURCAD': 13,

    'CHFJPY': 14,
    'GBPJPY': 15,
    'AUDJPY': 16,
    'NZDJPY': 17,
    'CADJPY': 18,

    'GBPCHF': 19,
    'AUDCHF': 20,
    'NZDCHF': 21,
    'CADCHF': 22,

    'GBPAUD': 23,
    'GBPNZD': 24,
    'GBPCAD': 25,

    'AUDNZD': 26,
    'AUDCAD': 27,

    'NZDCAD': 28,

    'XAUUSD': 29,
    'XTIUSD': 30,
    'WS30': 31,
    'NDX': 32,
    'SP500': 33,
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

    _collection = clt['foobar'][_col_nm]
    lst = list(_collection.find().sort("DT_MT4_OUT", pymongo.DESCENDING).limit(1))
    _newest = None
    if lst:
        _newest = dict(lst[0])['DT_MT4_OUT']

    # print('tg=', tg, 'newest=', _newest)
    logger.info("Get newest date={0} from DB ({1})".format(_newest, _col_nm))
    return _newest


def get_first_from_db2(clt=client, colnm='DEMO_EURUSD_MT5_H1', fld='DT_MT4_OUT'):
    _col_nm = colnm
    _collection = clt['foobar'][_col_nm]
    logger.info("Read first data ({1}) from DB ({0})...".format(_col_nm, fld))

    lst = list(_collection.find().sort("DT_MT4_OUT", pymongo.ASCENDING).limit(1))
    _first = None
    if lst:
        _first = dict(lst[0])[fld]

    logger.info("Get first {0}={1} from DB ({2})".format(fld, _first, _col_nm))
    return _first


def get_first_from_db3(clt=client, colnm='DEMO_EURUSD_MT5_H1', fld='DT_MT4_OUT', qry=None, bak=1):
    if qry is None:
        qry = {}
    _col_nm = colnm
    _collection = clt['foobar'][_col_nm]
    logger.info("Read first data ({1}) from DB ({0}) as {2} ...".format(_col_nm, fld, qry))

    _first = None
    _first2 = None
    lst = list(_collection.find(qry).sort(fld, pymongo.ASCENDING).limit(bak))
    if lst:
        _first = dict(lst[0])[fld]
        _first2 = dict(lst[-1])[fld]

    logger.info("Get first {0}={1}/{2} from DB ({3})".format(fld, _first, _first2, _col_nm))
    return _first, _first2


def delete_from_db(clt=client, colnm='DEMO_H1_ANA_STG', qry=None):
    if qry is None:
        qry = {"key": {"$regex": "EURUSD DEMO"}}
    _col_nm = colnm
    _collection = clt['foobar'][_col_nm]
    logger.info("deleting records to {0} as {1}...".format(_col_nm, qry))

    start = time()
    try:
        res = _collection.delete_many(qry)
    except errors.BulkWriteError as e:
        logger.error(str(e), exc_info=False)
        print(str(e))

    logger.info("deleted {1} records. used {0} second(s)".format(round(time() - start, 3), res.deleted_count))


def get_newest_from_db3(clt=client, colnm='DEMO_EURUSD_MT5_H1_ANA', fld='DT_MT4_OUT', qry=None, bak=1):
    if qry is None:
        qry = {}
    _col_nm = colnm
    _collection = clt['foobar'][_col_nm]
    logger.info("Read newest data ({1}) from DB ({0}) as {2} ...".format(_col_nm, fld, qry))

    _newest = None
    _newest2 = None
    lst = list(_collection.find(qry).sort(fld, pymongo.DESCENDING).limit(bak))
    if lst:
        _newest = dict(lst[0])[fld]
        _newest2 = dict(lst[-1])[fld]

    logger.info("Get newest {0}={1}/{2} from DB ({3})".format(fld, _newest, _newest2, _col_nm))
    return _newest, _newest2


def read_df_from_db(clt=client, colnm='DEMO_EURUSD_MT5_ANA', s_fld='key', qry=None):
    if qry is None:
        qry = {"key": {"$regex": "EURUSD.*120_5"}}
    _col_nm = colnm
    _collection = clt['foobar'][_col_nm]
    logger.info("Read data ({1}) from DB ({0})...".format(_col_nm, qry))
    _df = pd.DataFrame(list(_collection.find(
        {"$query": qry,
         # "$orderby": {s_fld: 1}
         },
        {"_id": 0, "key": 0}
    )))
    logger.info("Read data {} OK".format(len(_df.index)))
    return _df


def read_cur_from_db2(clt=client, cur='EURUSD', period='H1', from_dt='2020-12-01 00', to_dt='2020-12-31 23'):
    _col_nm = broker + '_' + cur + '_MT5_' + period
    logger.info("Read data ({1}) - ({2}) from DB ({0})...".format(_col_nm, from_dt, to_dt))
    # print("Read data ({0}) from db, please wait...".format(col_nm))
    _collection = clt['foobar'][_col_nm]
    _df = pd.DataFrame(list(_collection.find(
        {"$query": {"$and": [{"DT_MT4_OUT": {"$gte": from_dt}}, {"DT_MT4_OUT": {"$lt": to_dt}}]},
         "$orderby": {"DT_MT4_OUT": 1}},
        {"_id": 0, "key": 0, "UPD_BY": 0}
    )))
    logger.info("Read data {} OK".format(len(_df.index)))
    # print("Read OK")
    return _df


def write_df_to_db(df, clt=client, colnm='DEMO_EURUSD_MT5_H1_ANA'):
    # _col_nm = broker + '_' + curtp + '_' + stg  + '_ANA'
    _col_nm = colnm
    _collection = clt['foobar'][_col_nm]
    # collection = client['fx'][_col_nm]
    _collection.create_index([('key', pymongo.ASCENDING)], unique=True)

    cnt = len(df.index)
    logger.info("writing {0} records to {1}...".format(cnt, _col_nm))
    start = time()

    cnt2 = 0
    for i, row in df.iterrows():
        data = row.to_dict()
        # print(data['key'])
        flt = {'key': data['key']}
        _collection.update_one(flt, {'$set': data}, upsert=True)
        cnt2 += 1
        if cnt2 % 5000 == 0:
            logger.info("writing {0}/{1}({2}%) data".format(cnt2, cnt, round(cnt2 / cnt * 100 - 0.5, 1)))

    logger.info("writing end. used {} second(s)".format(round(time() - start, 3)))


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
        # TODO: 1-2025/1/27
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

    elif method == '2':  # gen mt5 ana data
        logger.info("{0} Generate mt5 ana data...".format(method))
        now = datetime.now()
        ed = (now + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M')
        # TODO: 2-2025/1/28
        for target in paras.keys():
            r = paras[target][1]
            # logger.info("Process {0}...".format(target))
            # print(target)
            mss = {
                   'H1': [120, 5],
            }
            if target in ['XAUUSD', 'XTIUSD', 'WS30', 'NDX', 'SP500']:
                mss = {
                       'H1': [115, 5],
                }
            peds = paras[target][2]
            for ped in peds:
                logger.info("Process {0} {1}...".format(target, ped))
                ms = mss[ped]
                # timezone = pytz.timezone("Etc/UTC")
                col_nm = broker + '_' + target + '_MT5_' + ped + '_ANA'
                if force_rebuild:
                    delete_from_db(clt=client, colnm=col_nm, qry={})

                first = False
                query = {}
                if force_from:
                    query = {"key": {"$lte": force_from}}
                latest_dt2, latest_dt = get_newest_from_db3(clt=client, colnm=col_nm, fld='key', qry=query,
                                                   bak=ms[0] * ms[1])
                if latest_dt is None:
                    first = True
                    col_nm2 = broker + '_' + target + '_MT5_' + ped
                    first_dt = get_first_from_db2(clt=client, colnm=col_nm2, fld='DT_MT4_OUT')
                    latest_dt = first_dt
                last_dt = parse(latest_dt)
                # last_dt = parse('2023-11-28 00:00:00')
                # print(last_dt)
                # exit(0)
                sd = last_dt.strftime('%Y-%m-%d %H:%M')
                df = read_cur_from_db2(clt=client, cur=target, period=ped, from_dt=sd, to_dt=ed)
                # df.to_pickle('out/out_pickle')
                # exit(0)
                df.dropna(inplace=True)
                if df.empty:
                    # exit(0)
                    continue
                df['BROKER'] = broker
                df['NAME'] = target
                df['PERIOD'] = int(ped_secs[ped] / 60)
                df['UPD_BY'] = now.strftime('%Y-%m-%d %H:%M:%S')
                df['name_sort'] = df['NAME'].apply(lambda x: paras4[x])
                df['key'] = df['DT_MT4_OUT']

                df['T'] = pd.to_datetime(df['DT_MT4_OUT']).dt.strftime('%H:%M')
                df['open'] = round(df['open'], int(np.log10(r)))
                df['close'] = round(df['close'], int(np.log10(r)))
                df['high'] = round(df['high'], int(np.log10(r)))
                df['low'] = round(df['low'], int(np.log10(r)))
                df['last_close'] = df['close'].shift(1).fillna(method='bfill')
                df['next_close'] = df['close'].shift(-1).fillna(method='ffill')
                df['close_lst'] = df['last_close']
                df['close_nxt'] = df['next_close']
                df['high_lst'] = df['high'].shift(1).fillna(method='bfill')
                df['high_nxt'] = df['high'].shift(-1).fillna(method='ffill')
                df['low_lst'] = df['low'].shift(1).fillna(method='bfill')
                df['low_nxt'] = df['low'].shift(-1).fillna(method='ffill')
                df['lowest'] = df[['open', 'high', 'low', 'close', 'last_close']].min(axis=1)
                df['highest'] = df[['open', 'high', 'low', 'close', 'last_close']].max(axis=1)
                for p, ma in (('s', ms[0]), ('m', ms[0] * ms[1])):
                    # logger.info("Process {0}({1})...".format(p, ma))
                    df2 = pd.DataFrame()

                    for a, b in (
                            ('c', 'close'),
                            # ('l', 'low'), ('h', 'high')
                    ):
                        # logger.info("Process {0}({1})...".format(a, b))
                        df3 = pd.DataFrame()

                        _sma = '{0}_{1}_sma'.format(a, ma)
                        df3[_sma] = round(df[b].rolling(ma).mean(), int(np.log10(r * 10)))

                        df2 = pd.concat([df2, df3], axis=1)
                        pass

                    # _ma = 'c_{0}_ma'.format(ma)
                    # df2[_ma] = ma

                    _c_sma = 'c_{0}_sma'.format(ma)
                    _last_c_sma = 'c_{0}_sma_lst'.format(ma)
                    _next_c_sma = 'c_{0}_sma_nxt'.format(ma)
                    df2[_last_c_sma] = df2[_c_sma].shift(1).fillna(method='bfill')
                    df2[_next_c_sma] = df2[_c_sma].shift(-1).fillna(method='ffill')

                    # df2.to_csv('out/df2_{0}.csv'.format(method), encoding='gbk', index=True)
                    # exit(0)
                    df = pd.concat([df, df2], axis=1)
                    pass

                # df.to_csv('out/df_{0}.csv'.format(method), encoding='gbk', index=True)
                # df.to_pickle('out/out_pickle')
                # exit(0)
                # df = pd.DataFrame()
                # df = pd.read_pickle('out/out_pickle')
                if not latest_dt2 is None:
                    df.drop(df[df['DT_MT4_OUT'] <= latest_dt2].index, inplace=True)
                if df.empty:
                    # exit(0)
                    continue

                # df.to_pickle('out/out_pickle')
                # exit(0)
                # df['key'] = df['DT_MT4_OUT']
                col_nm = broker + '_' + target + '_MT5_' + ped + '_ANA'
                # write_df_many_to_db(df=df, clt=client_rmt, colnm=col_nm)
                write_df_to_db(df=df, clt=client, colnm=col_nm)
                # write_df_bulk_to_db(df=df, clt=client_rmt, colnm=col_nm)
                exit(0)

        logger.info("{0} Generate mt5 ana data end".format(method))

    elif method == '3':  # gen mt5 ana's agg data
        logger.info("{0} Generate mt5 ana's agg data...".format(method))
        now = datetime.now()
        ed = (now + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M')
        # TODO: 3-2025/1/29
        mss = {
            'H1': [120, 5],
        }
        for target in paras.keys():
            r = paras[target][1]
            peds = paras[target][2]
            for ped in peds:
                mas = mss[ped]
                ma, ma2r = mas
                ma2 = ma * ma2r
                logger.info("Process {0} {1} {2}_{3} ...".format(target, ped, ma, ma2r))
                if force_rebuild:
                    col_nm = broker + '_' + target + '_MT5_ANA_AGG'
                    query = {"key": {"$regex": "^{0} {1} {2}_{3}".format(target, ped, ma, ma2r)}}
                    delete_from_db(clt=client, colnm=col_nm, qry=query)

                col_nm = broker + '_' + target + '_MT5_ANA_AGG'
                query = {"key": {"$regex": "^{0} {1} {2}_{3}".format(target, ped, ma, ma2r)}}
                if force_from:
                    query["end"] = {"$lt": force_from}
                latest_dt2, latest_dt = get_newest_from_db3(clt=client, colnm=col_nm, fld='end', qry=query, bak=2)
                first = False
                if not latest_dt:
                    first = True
                    col_nm2 = broker + '_' + target + '_MT5_' + ped + '_ANA'
                    first_dt, _ = get_first_from_db3(clt=client, colnm=col_nm2, fld='key')
                    latest_dt = first_dt
                if not first:
                    last_dt = parse(latest_dt) + timedelta(seconds=ped_secs[ped] * 1)
                else:
                    last_dt = parse(latest_dt)
                print(last_dt)
                # exit(0)
                if force_from and latest_dt:
                    # delete AGG data
                    col_nm = broker + '_' + target + '_MT5_ANA_AGG'
                    query = {"start": {"$gte": latest_dt}}
                    delete_from_db(clt=client, colnm=col_nm, qry=query)
                # exit(0)
                col_nm = broker + '_' + target + '_MT5_' + ped + '_ANA'
                query = {"key": {"$gte": "{0}".format(last_dt.strftime('%Y-%m-%d %H:%M:%S'))}}
                df = read_df_from_db(clt=client, colnm=col_nm, qry=query)
                if df.empty:
                    # exit(0)
                    continue
                df['ma_120_600'] = np.where(df['c_120_sma'] > df['c_600_sma'], 1, 0)
                df['ma_120_600'] = np.where(df['c_120_sma'] < df['c_600_sma'], -1, 0)
                df['ma_120_600_grp'] = df['ma_120_600'].ne(df['ma_120_600'].shift()).cumsum()
                # df.to_pickle('out/out_pickle')
                # exit(0)
                # df = pd.read_pickle('out/out_pickle')
                aggfunc = {
                    'NAME': [('name', 'first')],
                    'PERIOD': [('period', 'first')],
                    'DT_MT4_OUT': [('start', lambda x: x.iat[0]), ('end', lambda x: x.iat[-1])],
                    'ma_120_600_grp': [('ma_120_600_grp', 'first'), ('ma_120_600_len', 'count')],

                    'open': [('open_st', 'first')],
                    'close': [('open', 'first'), ('close_st', 'first')],
                    'close_nxt': [('close', 'last')],
                    'high': [('highest', 'max'), ('high_st', 'first')],
                    'low': [('lowest', 'min'), ('low_st', 'first')],

                    'c_120_sma': [('c_120_sma_st', 'first'), ('c_120_sma_lst', 'last')],
                    'c_600_sma': [('c_600_sma_st', 'first'), ('c_600_sma_lst', 'last')],
                }
                grouper = df['ma_120_600_grp']
                v = df.assign(key=grouper).groupby('key').agg(aggfunc)
                v.columns = v.columns.droplevel(0)
                _df = v.reset_index(drop=True)

                df4 = _df.copy()
                # df4.to_pickle('out/out_pickle4')
                # exit(0)
                # df4 = pd.read_pickle('out/out_pickle4')

                df4['start_dt'] = pd.to_datetime(df4['start'])
                df4['year'] = df4['start_dt'].dt.year.apply(lambda x: '{0}'.format(x))
                df4['month'] = df4['start_dt'].dt.month.apply(lambda x: '{:02d}'.format(x))
                df4['week'] = df4['start_dt'].apply(lambda x: (x - timedelta(days=x.weekday())).strftime('%W(%d-)'))
                df4['week2'] = df4['start_dt'].apply(
                    lambda x: (x - timedelta(days=x.weekday())).strftime('%Y_%W(%m/%d-)'))
                df4['day'] = df4['start_dt'].dt.day.apply(lambda x: '{:02d}'.format(x))
                df4['day2'] = df4['start_dt'].dt.strftime('%d(%Y_%W)')
                df4['day3'] = df4['start_dt'].dt.strftime('%d(%Y_%m)')
                df4['hour'] = df4['start_dt'].dt.hour

                df5 = df4.copy()
                # df5.to_pickle('out/out_pickle5')
                # exit(0)
                # df5 = pd.read_pickle('out/out_pickle5')
                df5['type'] = 0
                df5.loc[
                    (df5['c_120_sma_st'] > df5['c_600_sma_st'])
                    & ~(df5['ma_120_600_grp'].isna()),
                    'type'
                ] = 1
                df5.loc[
                    (df5['c_120_sma_st'] < df5['c_600_sma_st'])
                    & ~(df5['ma_120_600_grp'].isna()),
                    'type'
                ] = -1
                df5.loc[df5['type'] > 0, 'ma_120_600_pft'] = (df5['close'] - df5['open']) * r
                df5.loc[df5['type'] < 0, 'ma_120_600_pft'] = (df5['open'] - df5['close']) * r
                df5['success'] = 0
                df5['fail'] = 0
                df5['grp'] = df5['ma_120_600_grp']

                df5.loc[df5['ma_120_600_pft'] > 0, 'success'] = 1
                df5.loc[df5['success'] == 0, 'fail'] = 1

                df5.loc[df5['type'] > 0, 'p_max'] = (df5['highest'] - df5['open']) * r
                df5.loc[df5['type'] < 0, 'p_max'] = (df5['open'] - df5['lowest']) * r

                # df5['p'] = df5['ma_120_600_pft']
                df5['p'] = 0
                df5.loc[df5['success'] > 0, 'p'] = df5['ma_120_600_pft']
                df5['r'] = 0
                df5.loc[df5['p'] > 0, 'r'] = 0
                df5.loc[df5['p'] == 0, 'r'] = df5['ma_120_600_pft'].abs()
                # df5.loc[df5['r'] > 0, 'pr'] = df5['p'] / df5['r']
                # df5.loc[df5['r'] > 0, 'pmr'] = df5['p_max'] / df5['r']

                df5['t'] = df5['ma_120_600_len']

                df5['p'] = round(df5['p'], 1)
                df5['r'] = round(df5['r'], 1)
                df5['p_max'] = round(df5['p_max'], 1)
                # df5['pr'] = round(df5['pr'], 1)
                # df5['pmr'] = round(df5['pmr'], 1)

                # df5.to_pickle('out/out_pickle5')
                # exit(0)

                col_nm = broker + '_' + target + '_MT5_ANA_AGG'
                df5['key'] = df5['name'] + ' ' + ped + ' ' + str(ma) + '_' + str(ma2r) + ' ' + df5['start']
                # df5['key'] = "{0} {1} {2}_{3} {4}".format(df5['name'], ped, ma, ma2r, df5['start'])
                df5['UPD_BY'] = now.strftime('%Y-%m-%d %H:%M:%S')
                collection = client['foobar'][col_nm]
                collection.create_index([('start', pymongo.ASCENDING)], unique=False)
                collection.create_index([('end', pymongo.ASCENDING)], unique=False)
                write_df_to_db(df=df5, clt=client, colnm=col_nm)

            pass

        logger.info("{0} Generate mt5 ana's agg data end".format(method))

    elif method == '4':     # gen mt5 ana stgs  data
        logger.info("{0} Generate mt5 ana stgs data...".format(method))
        now = datetime.now()
        stgs = [
            '120_5',
        ]
        mass = {
                'H1': {'W1': ['m', 'b', 'bb'], 'D1': ['s', 'm', 'b']},
                }
        for target in paras.keys():
            r = paras[target][1]
            peds = paras[target][2]
            for ped in peds:
                if not ped in mass:
                    continue
                mas = mass[ped]
                for ma in mas.keys():
                    mp = mas[ma][0]
                    mp2 = mas[ma][1]
                    mp3 = mas[ma][2]
                    for stg in stgs:
                        logger.info("Process {0} {1} {2} ...".format(target, ped, stg))
                        col_nm = broker + '_MT5_ANA_STG'
                        # if True:
                        if force_rebuild:
                            query = {"key": {"$regex": "{0} {2} {1}".format(target, stg, ped)}}
                            delete_from_db(clt=client, colnm=col_nm, qry=query)

                        query = {"key": {"$regex": "^{0} {2} {1}".format(target, stg, ped)}}
                        if force_from:
                            query["start"] = {"$lt": force_from}
                        _, latest_dt = get_newest_from_db3(clt=client, colnm=col_nm, fld='start', qry=query, bak=2)
                        first = False
                        if latest_dt:
                            latest_dt = latest_dt
                        else:
                            first = True
                            col_nm2 = broker + '_' + target + '_MT5_ANA_AGG'
                            query = {"key": {"$regex": "^{0} {1} {2}".format(target, ped, stg)}}
                            first_dt, _ = get_first_from_db3(clt=client, colnm=col_nm2, fld='start', qry=query)
                            latest_dt = first_dt
                        # for test
                        # latest_dt = "2023-07-21 17:58:00"
                        last_dt = parse(latest_dt)
                        print(last_dt)
                        # exit(0)
                        if force_from and latest_dt:
                            # delete STG data
                            col_nm = broker + '_MT5_ANA_STG'
                            query = {"key": {"$regex": "^{0} {2} {1}".format(target, stg, ped)},
                                     "start": {"$gte": latest_dt}}
                            delete_from_db(clt=client, colnm=col_nm, qry=query)
                        # exit(0)
                        col_nm = broker + '_' + target + '_MT5_ANA_AGG'
                        query = {"key": {"$regex": "^{0} {1} {2}".format(target, ped, stg)},
                                 "start": {"$gte": "{0}".format(last_dt.strftime('%Y-%m-%d %H:%M:%S'))}}
                        df = read_df_from_db(clt=client, colnm=col_nm, qry=query)
                        if df.empty:
                            continue
                        # df.to_csv('out/out.csv', encoding='gbk', index=True)
                        # df.to_pickle('out/out_pickle')
                        # exit(0)
                        # df = pd.DataFrame()
                        # df = pd.read_pickle('out/out_pickle')
                        # TODO: 4 -2025/2/2
                        key = '{0}{1}'.format(mp, stg)
                        '''
                        flt = pd.DataFrame()
                        if key == 'sBB3':
                            flt=df
                        else:
                            flt=df.copy()
                            pass
                        if flt.empty:
                            continue
                        df2 = flt.copy()
                        '''
                        df2 = df.copy()
                        df2['stg'] = stg
                        df2['stg_desp'] = stg
                        df3 = df2[
                            ['name', 'stg', 'stg_desp', 'year', 'month', 'week', 'week2', 'day', 'day2', 'day3',
                             'period',
                             'grp',
                             'success', 'fail',
                             'start', 'end', 'p', 'r',
                             't', 'p_max', 'type',
                             ]].copy()
                        # df3 = df2.copy()
                        df3['key'] = df3['name'] + ' ' + ped + ' ' + df3['stg'] + ' ' + df3['start']
                        df3['UPD_BY'] = now.strftime('%Y-%m-%d %H:%M:%S')
                        # df3_1.to_csv('out/out3_1.csv', encoding='gbk', index=True)
                        # df3_1.to_pickle('out/out_pickle3_1')
                        col_nm = '{0}_MT5_ANA_STG'.format(broker)
                        collection = client['foobar'][col_nm]
                        collection.create_index([('start', pymongo.ASCENDING)], unique=False)
                        collection.create_index([('end', pymongo.ASCENDING)], unique=False)
                        write_df_to_db(df=df3, clt=client, colnm=col_nm)

            pass

        logger.info("{0} Generate mt5 ana's stg data end".format(method))

    elif method == '5':     # gen stg ana fin data
        logger.info("{0} Generate mt5 ana stg fin data...".format(method))
        now = datetime.now()
        # TODO: 5 -2025/2/2
        mass = {
                'H1': {'W1': 'b', 'D1': 'm'},
                }
        stgs = [
                '120_5',
        ]
        for target in paras.keys():
            r = paras[target][1]
            peds = paras[target][2]
            for ped in peds:
                mas = mass[ped]
                for ma in mas.keys():
                    # mp = mas[ma]
                    for stg in stgs:
                        col_nm = broker + '_MT5_ANA_STG_FIN'
                        # if True:
                        if force_rebuild:
                            query = {"key": {"$regex": "{0} {3} {1} {2}".format(target, stg, '[1-5]', ped)}}
                            delete_from_db(clt=client, colnm=col_nm, qry=query)

                        # for single
                        col_nm = broker + '_MT5_ANA_STG'
                        collection = client['foobar'][col_nm]
                        collection.create_index([
                            ('name', pymongo.ASCENDING), ('period', pymongo.ASCENDING),
                            ('stg', pymongo.ASCENDING),
                        ])
                        collection.create_index([
                            ('name', pymongo.ASCENDING), ('period', pymongo.ASCENDING),
                            ('stg', pymongo.ASCENDING),
                            ('year', pymongo.ASCENDING), ('month', pymongo.ASCENDING),
                            ('week', pymongo.ASCENDING), ('day', pymongo.ASCENDING),
                        ])

                        # for daily
                        logger.info("Process {0} {1} {2} for daily ...".format(target, ped, stg))
                        col_nm = broker + '_MT5_ANA_STG_FIN'
                        query = {"key": {"$regex": "^{0} {3} {1} {2}".format(target, stg, '2', ped)}}
                        if force_from:
                            query["start"] = {"$lt": force_from}
                        # _, latest_dt = get_newest_from_db3(clt=client_rmt, colnm=col_nm, fld='end', qry=query, bak=2)
                        latest_dt, _ = get_newest_from_db3(clt=client, colnm=col_nm, fld='start', qry=query, bak=2)
                        first = False
                        if not latest_dt:
                            first = True
                            col_nm2 = broker + '_MT5_ANA_STG'
                            query = {"key": {"$regex": "^{0} {2} {1}".format(target, stg, ped)}}
                            first_dt, _ = get_first_from_db3(clt=client, colnm=col_nm2, fld='start', qry=query)
                            latest_dt = first_dt
                        if not latest_dt:
                            continue
                        last_dt = parse(latest_dt)
                        # print(last_dt)
                        # day
                        last_dt2 = parse(last_dt.strftime("%Y/%m/%d"))
                        print(last_dt2)
                        # exit(0)
                        col_nm = broker + '_MT5_ANA_STG'
                        query = {"key": {"$regex": "^{0} {2} {1}".format(target, stg, ped)},
                                 "start": {"$gte": "{0}".format(last_dt2.strftime('%Y-%m-%d %H:%M:%S'))}}
                        df = read_df_from_db(clt=client, colnm=col_nm, qry=query)
                        if len(df.index) == 0:
                            continue
                        aggfunc = {
                            'name': [('name', 'first')],
                            'stg': [('stg', 'first')],
                            'stg_desp': [('stg_desp', 'first')],
                            'start': [('start', 'first')],
                            'end': [('end', 'last')],
                            'year': [('year', 'first')],
                            'month': [('month', 'first')],
                            'week': [('week', 'first')],
                            'day': [('day', 'first')],
                            'period': [('period', 'first')],
                            'success': [('success', 'sum')],
                            'fail': [('fail', 'sum')],
                            'p': [('p', 'mean'), ('p_sum', 'sum')],
                            'r': [('r', 'mean'), ('r_sum', 'sum')],
                            't': [('t', 'mean')],
                            'p_max': [('p_max', 'mean'), ('p_max_s', 'sum')],
                        }
                        v = df.groupby(df['day2']).agg(aggfunc)
                        v.columns = v.columns.droplevel(0)
                        df3_2 = v.reset_index()
                        df3_2 = df3_2[
                            ['name', 'stg', 'stg_desp', 'year', 'month', 'week', 'day', 'period',
                             'success', 'fail', 'start', 'end', 'p', 'r',
                             't', 'p_max', 'p_sum','r_sum', 'p_max_s']]
                        df3_2['stg_sub'] = '2'
                        df3_2['stg_sub_desp'] = 'day'
                        df3_2.loc[df3_2['r_sum'] > 0, 'prs'] = df3_2['p_sum'] / df3_2['r_sum']
                        df3_2['prs'] = round(df3_2['prs'], 1)
                        df3_2['p'] = round(df3_2['p'], 1)
                        df3_2['r'] = round(df3_2['r'], 1)
                        df3_2['t'] = round(df3_2['t'], 1)
                        df3_2['p_max'] = round(df3_2['p_max'], 1)
                        df3_2['p_sum'] = round(df3_2['p_sum'], 1)
                        df3_2['r_sum'] = round(df3_2['r_sum'], 1)
                        df3_2['p_max_s'] = round(df3_2['p_max_s'], 1)
                        df3_2['key'] = df3_2['name'] + ' ' + ped + ' ' + df3_2['stg'] + ' ' + df3_2['stg_sub'].astype(str) + ' ' + \
                                       df3_2['year'].astype(str) + ' ' + df3_2['week'].astype(str) + ' ' + df3_2['day'].astype(str)
                        df3_2['UPD_BY'] = now.strftime('%Y-%m-%d %H:%M:%S')
                        # df3_2.to_csv('out/out3_2.csv', encoding='gbk', index=True)
                        # df3_2.to_pickle('out/out_pickle3_2')
                        col_nm = broker + '_MT5_ANA_STG_FIN'
                        collection = client['foobar'][col_nm]
                        collection.create_index([
                            ('name', pymongo.ASCENDING), ('period', pymongo.ASCENDING),
                            ('stg', pymongo.ASCENDING), ('stg_sub', pymongo.ASCENDING),
                            ('year', pymongo.ASCENDING), ('month', pymongo.ASCENDING),
                            ('week', pymongo.ASCENDING), ('day', pymongo.ASCENDING),
                        ])
                        collection.create_index([('start', pymongo.ASCENDING)], unique=False)
                        collection.create_index([('end', pymongo.ASCENDING)], unique=False)
                        write_df_to_db(df=df3_2, clt=client, colnm=col_nm)
                        # write_df_many_to_db(df=df3_2, clt=client_rmt, colnm=col_nm)
                        # exit(0)

                        # for weekly
                        logger.info("Process {0} {2} {1} for weekly ...".format(target, stg, ped))
                        col_nm = broker + '_MT5_ANA5_STG_FIN'
                        query = {"key": {"$regex": "^{0} {2} {1}".format(target, stg, '3', ped)}}
                        if force_from:
                            query["start"] = {"$lt": force_from}
                        # _, latest_dt = get_newest_from_db3(clt=client_rmt, colnm=col_nm, fld='end', qry=query, bak=2)
                        latest_dt, _ = get_newest_from_db3(clt=client, colnm=col_nm, fld='start', qry=query, bak=2)
                        first = False
                        if not latest_dt:
                            first = True
                            col_nm2 = broker + '_MT5_ANA_STG'
                            query = {"key": {"$regex": "^{0} {2} {1}".format(target, stg, ped)}}
                            first_dt, _ = get_first_from_db3(clt=client, colnm=col_nm2, fld='start', qry=query)
                            latest_dt = first_dt
                        if not latest_dt:
                            continue
                        last_dt = parse(latest_dt)
                        # print(last_dt)
                        # week
                        s = last_dt.strftime("%Y(%W)(1)")
                        print(s)
                        last_dt3 = datetime.strptime(s, "%Y(%W)(%w)")
                        print(last_dt3)
                        # exit(0)

                        col_nm = broker + '_MT5_ANA_STG'
                        query = {"key": {"$regex": "^{0} {2} {1}".format(target, stg, ped)},
                                 "start": {"$gte": "{0}".format(last_dt3.strftime('%Y-%m-%d %H:%M:%S'))}}
                        df = read_df_from_db(clt=client, colnm=col_nm, qry=query)
                        if len(df.index) == 0:
                            continue
                        aggfunc = {
                            'name': [('name', 'first')],
                            'stg': [('stg', 'first')],
                            'stg_desp': [('stg_desp', 'first')],
                            'start': [('start', 'first')],
                            'end': [('end', 'last')],
                            'year': [('year', 'first')],
                            'month': [('month', 'first')],
                            'week': [('week', 'first')],
                            'period': [('period', 'first')],
                            'success': [('success', 'sum')],
                            'fail': [('fail', 'sum')],
                            'p': [('p', 'mean'), ('p_sum', 'sum')],
                            'r': [('r', 'mean'), ('r_sum', 'sum')],
                            't': [('t', 'mean')],
                            'p_max': [('p_max', 'mean'), ('p_max_s', 'sum')],
                        }
                        v = df.groupby(df['week2']).agg(aggfunc)
                        v.columns = v.columns.droplevel(0)
                        df3_3 = v.reset_index()
                        df3_3 = df3_3[
                            ['name', 'stg', 'stg_desp', 'year', 'month', 'week', 'period',
                             'success', 'fail', 'start', 'end', 'p', 'r',
                             't', 'p_max', 'p_sum', 'r_sum', 'p_max_s', ]]
                        df3_3['stg_sub'] = '3'
                        df3_3['stg_sub_desp'] = 'week'
                        df3_3.loc[df3_3['r_sum'] > 0, 'prs'] = df3_3['p_sum'] / df3_3['r_sum']
                        df3_3['prs'] = round(df3_3['prs'], 1)
                        df3_3['p'] = round(df3_3['p'], 1)
                        df3_3['r'] = round(df3_3['r'], 1)
                        df3_3['t'] = round(df3_3['t'], 1)
                        df3_3['p_max'] = round(df3_3['p_max'], 1)
                        df3_3['p_sum'] = round(df3_3['p_sum'], 1)
                        df3_3['r_sum'] = round(df3_3['r_sum'], 1)
                        df3_3['p_max_s'] = round(df3_3['p_max_s'], 1)
                        df3_3['key'] = df3_3['name'] + ' ' + ped + ' ' + df3_3['stg'] + ' ' + df3_3['stg_sub'].astype(str) + ' ' + \
                                       df3_3['year'].astype(str) + ' ' + df3_3['week'].astype(str)
                        df3_3['UPD_BY'] = now.strftime('%Y-%m-%d %H:%M:%S')
                        # df3_3.to_csv('out/out3_3.csv', encoding='gbk', index=True)
                        # df3_3.to_pickle('out/out_pickle3_3')
                        col_nm = broker + '_MT5_ANA_STG_FIN'
                        write_df_to_db(df=df3_3, clt=client, colnm=col_nm)
                        # exit(0)

                        # for monthly
                        logger.info("Process {0} {2} {1} for monthly ...".format(target, ped, stg))
                        col_nm = broker + '_MT5_ANA_STG_FIN'
                        query = {"key": {"$regex": "^{0} {3} {1} {2}".format(target, stg, '4', ped)}}
                        if force_from:
                            query["start"] = {"$lt": force_from}
                        # _, latest_dt = get_newest_from_db3(clt=client_rmt, colnm=col_nm, fld='end', qry=query, bak=2)
                        latest_dt, _ = get_newest_from_db3(clt=client, colnm=col_nm, fld='start', qry=query, bak=2)
                        first = False
                        if not latest_dt:
                            first = True
                            col_nm2 = broker + '_MT5_ANA_STG'
                            query = {"key": {"$regex": "^{0} {2} {1}".format(target, stg, ped)}}
                            first_dt, _ = get_first_from_db3(clt=client, colnm=col_nm2, fld='start', qry=query)
                            latest_dt = first_dt
                        if not latest_dt:
                            continue
                        last_dt = parse(latest_dt)
                        # print(last_dt)
                        # month
                        last_dt4 = parse(last_dt.strftime("%Y/%m/1"))
                        print(last_dt4)
                        # exit(0)

                        col_nm = broker + '_MT5_ANA_STG'
                        query = {"key": {"$regex": "^{0} {2} {1}".format(target, stg, ped)},
                                 "start": {"$gte": "{0}".format(last_dt4.strftime('%Y-%m-%d %H:%M:%S'))}}
                        df = read_df_from_db(clt=client, colnm=col_nm, qry=query)
                        if len(df.index) == 0:
                            continue
                        aggfunc = {
                            'name': [('name', 'first')],
                            'stg': [('stg', 'first')],
                            'stg_desp': [('stg_desp', 'first')],
                            'start': [('start', 'first')],
                            'end': [('end', 'last')],
                            'period': [('period', 'first')],
                            'success': [('success', 'sum')],
                            'fail': [('fail', 'sum')],
                            'p': [('p', 'mean'), ('p_sum', 'sum')],
                            'r': [('r', 'mean'), ('r_sum', 'sum')],
                            't': [('t', 'mean')],
                            'p_max': [('p_max', 'mean'), ('p_max_s', 'sum')],
                        }
                        v = df.groupby([df['year'], df['month']]).agg(aggfunc)
                        v.columns = v.columns.droplevel(0)
                        df3_4 = v.reset_index()
                        df3_4 = df3_4[
                            ['name', 'stg', 'stg_desp', 'year', 'month', 'period',
                             'success', 'fail', 'start', 'end', 'p', 'r',
                             't', 'p_max', 'p_sum', 'r_sum', 'p_max_s', ]]
                        df3_4['stg_sub'] = '4'
                        df3_4['stg_sub_desp'] = 'month'
                        df3_4.loc[df3_4['r_sum'] > 0, 'prs'] = df3_4['p_sum'] / df3_4['r_sum']
                        df3_4['prs'] = round(df3_4['prs'], 1)
                        df3_4['p'] = round(df3_4['p'], 1)
                        df3_4['r'] = round(df3_4['r'], 1)
                        df3_4['t'] = round(df3_4['t'], 1)
                        df3_4['p_max'] = round(df3_4['p_max'], 1)
                        df3_4['p_sum'] = round(df3_4['p_sum'], 1)
                        df3_4['r_sum'] = round(df3_4['r_sum'], 1)
                        df3_4['p_max_s'] = round(df3_4['p_max_s'], 1)
                        df3_4['key'] = df3_4['name'] + ' ' + ped + ' ' + df3_4['stg'] + ' ' + df3_4['stg_sub'].astype(str) + ' ' + \
                                       df3_4['year'].astype(str) + ' ' + df3_4['month'].astype(str)
                        df3_4['UPD_BY'] = now.strftime('%Y-%m-%d %H:%M:%S')
                        # df3_4.to_csv('out/out3_4.csv', encoding='gbk', index=True)
                        # df3_4.to_pickle('out/out_pickle3_4')
                        col_nm = broker + '_MT5_ANA_STG_FIN'
                        write_df_to_db(df=df3_4, clt=client, colnm=col_nm)
                        # write_df_many_to_db(df=df3_4, clt=client_rmt, colnm=col_nm)
                        # exit(0)

                        # for yearly
                        logger.info("Process {0} {1} {2} for yearly ...".format(target, ped, stg))
                        col_nm = broker + '_MT5_ANA_STG_FIN'
                        query = {"key": {"$regex": "^{0} {3} {1} {2}".format(target, stg, '5', ped)}}
                        if force_from:
                            query["start"] = {"$lt": force_from}
                        # _, latest_dt = get_newest_from_db3(clt=client_rmt, colnm=col_nm, fld='end', qry=query, bak=2)
                        latest_dt, _ = get_newest_from_db3(clt=client, colnm=col_nm, fld='start', qry=query, bak=2)
                        first = False
                        if not latest_dt:
                            first = True
                            col_nm2 = broker + '_MT5_ANA_STG'
                            query = {"key": {"$regex": "^{0} {2} {1}".format(target, stg, ped)}}
                            first_dt, _ = get_first_from_db3(clt=client, colnm=col_nm2, fld='start', qry=query)
                            latest_dt = first_dt
                        if not latest_dt:
                            continue
                        last_dt = parse(latest_dt)
                        # print(last_dt)
                        # year
                        last_dt5 = parse(last_dt.strftime("%Y/1/1"))
                        print(last_dt5)
                        # exit(0)

                        col_nm = broker + '_MT5_ANA_STG'
                        query = {"key": {"$regex": "^{0} {2} {1}".format(target, stg, ped)},
                                 "start": {"$gte": "{0}".format(last_dt5.strftime('%Y-%m-%d %H:%M:%S'))}}
                        df = read_df_from_db(clt=client, colnm=col_nm, qry=query)
                        if len(df.index) == 0:
                            continue
                        aggfunc = {
                            'name': [('name', 'first')],
                            'stg': [('stg', 'first')],
                            'stg_desp': [('stg_desp', 'first')],
                            'start': [('start', 'first')],
                            'end': [('end', 'last')],
                            # 'year': [('year', 'first')],
                            'period': [('period', 'first')],
                            'success': [('success', 'sum')],
                            'fail': [('fail', 'sum')],
                            'p': [('p', 'mean'), ('p_sum', 'sum')],
                            'r': [('r', 'mean'), ('r_sum', 'sum')],
                            't': [('t', 'mean')],
                            'p_max': [('p_max', 'mean'), ('p_max_s', 'sum')],
                        }
                        v = df.groupby(df['year']).agg(aggfunc)
                        v.columns = v.columns.droplevel(0)
                        df3_5 = v.reset_index()
                        df3_5 = df3_5[
                            ['name', 'stg', 'stg_desp', 'year', 'period',
                             'success', 'fail', 'start', 'end', 'p', 'r',
                             't', 'p_max', 'p_sum', 'r_sum', 'p_max_s', ]]
                        df3_5['stg_sub'] = '5'
                        df3_5['stg_sub_desp'] = 'year'
                        df3_5.loc[df3_5['r_sum'] > 0, 'prs'] = df3_5['p_sum'] / df3_5['r_sum']
                        df3_5['prs'] = round(df3_5['prs'], 1)
                        df3_5['p'] = round(df3_5['p'], 1)
                        df3_5['r'] = round(df3_5['r'], 1)
                        df3_5['t'] = round(df3_5['t'], 1)
                        df3_5['p_max'] = round(df3_5['p_max'], 1)
                        df3_5['p_sum'] = round(df3_5['p_sum'], 1)
                        df3_5['r_sum'] = round(df3_5['r_sum'], 1)
                        df3_5['p_max_s'] = round(df3_5['p_max_s'], 1)
                        df3_5['key'] = df3_5['name'] + ' ' + ped + ' ' + df3_5['stg'] + ' ' + df3_5['stg_sub'].astype(str) + \
                                       ' ' + df3_5['year'].astype(str)
                        df3_5['UPD_BY'] = now.strftime('%Y-%m-%d %H:%M:%S')
                        # df3_5.to_csv('out/out3_5.csv', encoding='gbk', index=True)
                        # df3_5.to_pickle('out/out_pickle3_5')
                        col_nm = broker + '_MT5_ANA_STG_FIN'
                        # collection = client_rmt['fx'][col_nm]
                        write_df_to_db(df=df3_5, clt=client, colnm=col_nm)
                        # exit(0)


# TODO: main
if __name__ == "__main__":
    # print(p_dir)
    # print(me)
    # print('test')
    # exit(0)
    main(sys.argv)


