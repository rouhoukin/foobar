# -*- coding: utf-8 -*-
from datetime import timedelta
from datetime import datetime

# Let's just use the local mongod instance. Edit as needed.

# Please note that MONGO_HOST and MONGO_PORT could very well be left
# out as they already default to a bare bones local 'mongod' instance.
MONGO_HOST = 'localhost'
# MONGO_HOST = '192.168.31.140'
MONGO_PORT = 27017

ITEM_METHODS = ['GET']
RENDERERS = ['eve.render.JSONRenderer']
JSONP_ARGUMENT = 'callback'

# Skip these if your db has no auth. But it really should.
# MONGO_USERNAME = '<your username>'
# MONGO_PASSWORD = '<your password>'
# MONGO_AUTH_SOURCE = 'admin'  # needed if --auth mode is enabled

MONGO_DBNAME = 'foobar'
ITEMS = 'rows'
# PAGINATION_DEFAULT = 30
DEBUG = True
PAGINATION = False
PROJECTION = True

last_date = (datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d')
# last_date = (datetime.strptime('2020-11-27', '%Y-%m-%d')-timedelta(days=7)).strftime('%Y-%m-%d')

latest6 = {
    'item_title': 'latest',
    'datasource': {
        'source': 'DEMO_MT5_ANA_STG',
        # 'filter': {'name': 'EURUSD', 'stg_sub': '3'},
        # 'filter': {'stg': 'BB', 'stg_sub': '1', },
        'filter': {'stg': '120_5', },
        'default_sort': [('key', -1)],
        'projection': {'_id': 0, 'key': 1, 'name': 1},
    },
    # 'schema': ptrs_schema,
}

ptrs6_cur_11 = {
    'item_title': 'test',
    'datasource': {
        'source': 'DEMO_MT5_ANA_STG',
        'aggregation': {
            'pipeline': [
                {"$match": {"$and": [{"$or": [{'name': "$cur1"}, {'name': "$cur2"}]},
                                     {'year': "$year"},
                                     {'week': {'$regex': "$wk"}},
                                     {'day': "$day"},
                                     {'period': "$pd"},
                                     {'stg': "$stg"},
                                    ]}},
                {"$group": {"_id": {"start": "$start"},
                            "items": {"$addToSet": {"c": "$name", "stg": "$stg", "grp": "$grp", "type": "$type",
                                                    "s": "$success", "f": "$fail", "p": "$p", "r": "$r", "t": "$t",
                                                    "p_m": "$p_max",
                                                    # "pr": "$pr", "pmr": "$pmr",
                                                    "st": "$start"}}}
                },
                {"$sort": {"_id.start": -1}},
            ]
        }
    }
}
ptrs6_cur_22 = {
    'item_title': 'test',
    'datasource': {
        'source': 'DEMO_MT5_ANA_STG_FIN',
        'aggregation': {
            'pipeline': [
                {"$match": {"$and": [{"$or": [{'name': "$cur1"}, {'name': "$cur2"}]},
                                     {'year': "$year"},
                                     {'week': {'$regex': "$wk"}},
                                     {'period': "$pd"},
                                     {'stg': "$stg"},
                                     {'stg_sub': "2"}]}},
                {"$group": {"_id": {"year": "$year", "week": "$week", "day": "$day"},
                            "items": {"$addToSet": {"c": "$name", "stg": "$stg", "ma": "$ma",
                                                    "s": "$success", "f": "$fail", "p": "$p", "r": "$r", "t": "$t",
                                                    "p_m": "$p_max", "p_s": "$p_sum", "r_s": "$r_sum",
                                                    "p_ms": "$p_max_s",
                                                    # "pr": "$pr", "pmr": "$pmr", "prs": "$prs", "pmrs": "$pmrs",
                                                    }}}
                },
                {"$sort": {"_id.year": -1, "_id.week": -1, "_id.day": -1}},
            ]
        }
    }
}
ptrs6_cur_33 = {
    'item_title': 'test',
    'datasource': {
        'source': 'DEMO_MT5_ANA_STG_FIN',
        'aggregation': {
            'pipeline': [
                {"$match": {"$and": [{"$or": [{'name': "$cur1"}, {'name': "$cur2"}]},
                                     {'year': "$year"},
                                     {'month': "$month"},
                                     {'period': "$pd"},
                                     {'stg': "$stg"},
                                     {'stg_sub': "3"}]}},
                {"$group": {"_id": {"year": "$year", "week": "$week"},
                            "items": {"$addToSet": {"c": "$name", "stg": "$stg",
                                                    "s": "$success", "f": "$fail", "p": "$p", "r": "$r", "t": "$t",
                                                    "p_m": "$p_max", "p_s": "$p_sum", "r_s": "$r_sum", "p_ms": "$p_max_s",
                                                    # "pr": "$pr", "pmr": "$pmr", "prs": "$prs", "pmrs": "$pmrs",
                                                    }}}
                },
                {"$sort": {"_id.year": -1, "_id.week": -1}},
            ]
        }
    }
}
ptrs6_cur_44 = {
    'item_title': 'test',
    'datasource': {
        'source': 'DEMO_MT5_ANA_STG_FIN',
        'aggregation': {
            'pipeline': [
                {"$match": {"$and": [{"$or": [{'name': "$cur1"}, {'name': "$cur2"}]},
                                     {'year': "$year"},
                                     {'period': "$pd"},
                                     {'stg': "$stg"},
                                     {'stg_sub': "4"}]}},
                {"$group": {"_id": {"year": "$year", "month": "$month"},
                            "items": {"$addToSet": {"c": "$name", "stg": "$stg",
                                                    "s": "$success", "f": "$fail", "p": "$p", "r": "$r", "t": "$t",
                                                    "p_m": "$p_max", "p_s": "$p_sum", "r_s": "$r_sum", "p_ms": "$p_max_s",
                                                    # "pr": "$pr", "pmr": "$pmr", "prs": "$prs", "pmrs": "$pmrs",
                                                    }}}
                },
                {"$sort": {"_id.year": -1, "_id.month": -1}},
            ]
        }
    }
}
ptrs6_cur_5 = {
    'item_title': 'test',
    'datasource': {
        'source': 'DEMO_MT5_ANA_STG_FIN',
        'aggregation': {
            'pipeline': [
                {"$match": {"$and": [{"$or": [{'name': "$cur1"}, {'name': "$cur2"}]},
                                     {'period': "$pd"},
                                     {'stg': "$stg"},
                                     {'stg_sub': "5"}]}},
                {"$group": {"_id": {"year": "$year"},
                            "items": {"$addToSet": {"c": "$name", "stg": "$stg",
                                                    "s": "$success", "f": "$fail", "p": "$p", "r": "$r", "t": "$t",
                                                    "p_m": "$p_max", "p_s": "$p_sum", "r_s": "$r_sum", "p_ms": "$p_max_s",
                                                    # "pr": "$pr", "pmr": "$pmr", "prs": "$prs", "pmrs": "$pmrs",
                                                    }}}
                },
                {"$sort": {"_id.year": -1}},
            ]
        }
    }
}
ptrs6_stg_11 = {
    'item_title': 'test',
    'datasource': {
        'source': 'DEMO_MT5_ANA_STG',
        'aggregation': {
            'pipeline': [
                {"$match": {"$and": [{"$or": [{'stg': "$stg1"}, {'stg': "$stg2"}]},
                                     {'year': "$year"},
                                     {'week': {'$regex': "$wk"}},
                                     {'day': "$day"},
                                     {'name': "$cur"},
                                     {'period': "$pd"},
                                    ]}},
                {"$group": {"_id": {"start": "$start"},
                            "items": {"$addToSet": {"c": "$name", "stg": "$stg", "grp": "$grp", "type": "$type",
                                                    "s": "$success", "f": "$fail", "p": "$p", "r": "$r", "t": "$t",
                                                    "p_m": "$p_max",
                                                    # "pr": "$pr", "pmr": "$pmr",
                                                    "st": "$start"}}}
                },
                {"$sort": {"_id.start": -1}},
            ]
        }
    }
}
ptrs6_stg_22 = {
    'item_title': 'test',
    'datasource': {
        'source': 'DEMO_MT5_ANA_STG_FIN',
        'aggregation': {
            'pipeline': [
                {"$match": {"$and": [{"$or": [{'stg': "$stg1"}, {'stg': "$stg2"}]},
                                     {'year': "$year"},
                                     {'week': {'$regex': "$wk"}},
                                     {'name': "$cur"},
                                     {'period': "$pd"},
                                     {'stg_sub': "2"}]}},
                {"$group": {"_id": {"year": "$year", "week": "$week", "day": "$day"},
                            "items": {"$addToSet": {"c": "$name", "stg": "$stg",
                                                    "s": "$success", "f": "$fail", "p": "$p", "r": "$r",
                                                    "p_m": "$p_max", "r_s": "$r_sum", "p_ms": "$p_max_s",
                                                    # "pr": "$pr", "pmr": "$pmr", "prs": "$prs", "pmrs": "$pmrs",
                                                    }}}
                },
                {"$sort": {"_id.year": -1, "_id.week": -1, "_id.day": -1}},
            ]
        }
    }
}
ptrs6_stg_33 = {
    'item_title': 'test',
    'datasource': {
        'source': 'DEMO_MT5_ANA_STG_FIN',
        'aggregation': {
            'pipeline': [
                {"$match": {"$and": [{"$or": [{'stg': "$stg1"}, {'stg': "$stg2"}]},
                                     {'year': "$year"},
                                     {'month': "$month"},
                                     {'name': "$cur"},
                                     {'period': "$pd"},
                                     {'stg_sub': "3"}]}},
                {"$group": {"_id": {"year": "$year", "week": "$week"},
                            "items": {"$addToSet": {"c": "$name", "stg": "$stg",
                                                    "s": "$success", "f": "$fail", "p": "$p", "r": "$r",
                                                    "p_m": "$p_max", "p_s": "$p_sum", "r_s": "$r_sum",
                                                    "p_ms": "$p_max_s",
                                                    # "pr": "$pr", "pmr": "$pmr", "prs": "$prs", "pmrs": "$pmrs",
                                                    }}}
                },
                {"$sort": {"_id.year": -1, "_id.week": -1}},
            ]
        }
    }
}
ptrs6_stg_44 = {
    'item_title': 'test',
    'datasource': {
        'source': 'DEMO_MT5_ANA_STG_FIN',
        'aggregation': {
            'pipeline': [
                {"$match": {"$and": [{"$or": [{'stg': "$stg1"}, {'stg': "$stg2"}]},
                                     {'year': "$year"},
                                     {'name': "$cur"},
                                     {'period': "$pd"},
                                     {'stg_sub': "4"}]}},
                {"$group": {"_id": {"year": "$year", "month": "$month"},
                            "items": {"$addToSet": {"c": "$name", "stg": "$stg",
                                                    "s": "$success", "f": "$fail", "p": "$p", "r": "$r", "t": "$t",
                                                    "p_m": "$p_max", "p_s": "$p_sum", "p_ms": "$p_max_s",
                                                    # "pr": "$pr", "pmr": "$pmr", "prs": "$prs", "pmrs": "$pmrs",
                                                    }}}
                },
                {"$sort": {"_id.year": -1, "_id.month": -1}},
            ]
        }
    }
}
ptrs6_stg_5 = {
    'item_title': 'test',
    'datasource': {
        'source': 'DEMO_MT5_ANA_STG_FIN',
        'aggregation': {
            'pipeline': [
                {"$match": {"$and": [{"$or": [{'stg': "$stg1"}, {'stg': "$stg2"}]},
                                     {'name': "$cur"},
                                     {'period': "$pd"},
                                     {'stg_sub': "5"}]}},
                {"$group": {"_id": {"year": "$year"},
                            "items": {"$addToSet": {"c": "$name", "stg": "$stg",
                                                    "s": "$success", "f": "$fail", "p": "$p", "r": "$r", "t": "$t",
                                                    "p_m": "$p_max", "p_s": "$p_sum", "r_s": "$r_sum", "p_ms": "$p_max_s",
                                                    # "pr": "$pr", "pmr": "$pmr", "prs": "$prs", "pmrs": "$pmrs",
                                                    }}}
                },
                {"$sort": {"_id.year": -1}},
            ]
        }
    }
}
orders = {
    'item_title': 'test',
    'datasource': {
        'source': 'orders',
        'aggregation': {
            'pipeline': [
                # {"$match": {'symbol': "$sym"}},
                {"$group": {"_id": {"sym": "$symbol",
                                    "ot": {"$dateToString": {"format": "%Y-%m-%d %H:%M:00", "date": "$open_time"}},
                                    "mag": "$magic"},
                            "items": {"$addToSet":
                                          {"acc": "$account2", "tic": "$ticket", "tp": "$type2",
                                            # "ot": {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$open_time"}},
                                            "op": "$open_price",
                                            "ct": {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$close_time"}},
                                            "cp": "$close_price",
                                            "vol": "$volume", "oc_pt": "$cls-open_pt", "pft": "$profit", "coms": "$commission",
                                            "swp": "$swap", "com": "$comment"}
                                     }
                            }
                },
                {"$match": {"$and": [{'_id.ot': {"$gte": "$start"}}, {'_id.ot': {"$lte": "$end"}}]}},
                {"$sort": {"_id.sym": 1, "_id.ot": -1, "_id.mag": 1}},
            ]
        }
    }
}
orders2 = {
    'item_title': 'test',
    'datasource': {
        'source': 'orders2',
        'aggregation': {
            'pipeline': [
                # {"$match": {'symbol': "$sym"}},
                {"$group": {"_id": {"sym": "$symbol",
                                    "ot": "$open_time_s",
                                    "mag": "$magic"},
                            "items": {"$addToSet":
                                          {"acc": "$account2", "tic": "$tic_in", "tp": "$type_s",
                                            "op": "$open_price",
                                            "ct": "$close_time_s",
                                            "cp": "$close_price",
                                            "vol": "$volume", "oc_pt": "$op_cls_ppt", "pft": "$profit", "coms": "$commission",
                                            "swp": "$swap", "com": "$comment"}
                                     }
                            }
                },
                {"$match": {"$and": [{'_id.ot': {"$gte": "$start"}}, {'_id.ot': {"$lte": "$end"}}]}},
                {"$sort": {"_id.ot": -1, "_id.sym": 1, "_id.mag": 1}},
                # {"$sort": {"_id.sym": 1, "_id.ot": -1, "_id.mag": 1}},
            ]
        }
    }
}
DOMAIN = {
    'latest6': latest6,
    'ptrs6_cur_11': ptrs6_cur_11,
    'ptrs6_cur_22': ptrs6_cur_22,
    'ptrs6_cur_33': ptrs6_cur_33,
    'ptrs6_cur_44': ptrs6_cur_44,
    'ptrs6_cur_5': ptrs6_cur_5,
    'ptrs6_stg_11': ptrs6_stg_11,
    'ptrs6_stg_22': ptrs6_stg_22,
    'ptrs6_stg_33': ptrs6_stg_33,
    'ptrs6_stg_44': ptrs6_stg_44,
    'ptrs6_stg_5': ptrs6_stg_5,
    # 'orders': orders,
    # 'orders2': orders2,
}
