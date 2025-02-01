db.DEMO_EURUSD_MT5_ANA_AGG.aggregate ([
    {$project: {'_id':0,'key':1,'name':1,'period':1,'start':1,'end':1,'year':1,'week2':1,'day3':1,'type':1,'p_max':1,
    'p':1,'t':1,'r':1,'grp':1,'c_120_sma_st':1,'c_600_sma_st':1,'success':1,'fail':1,
    }},
    {$sort: {'key': -1}},
    {$group: {
              '_id': "$year",
              'year': {'$first': '$year'},
              's': {'$sum': '$success'}, 'f': {'$sum': '$fail'},
              'ps': {'$sum': '$p'}, 'rs': {'$sum': '$r'}, 'pms': {'$sum': '$p_max'}, 't': {'$avg': '$t'},
    }},
    {$addFields: {
        't': {'$round': ['$t', 1]},
    }},
    {$addFields: {
        'prs': {$cond: [{$ne: ['$rs', 0]}, {$round: [{$divide: ['$ps', '$rs']}, 1]}, NaN]
        },
    }},
    {$addFields: {
        'pmrs': {$cond: [{$ne: ['$rs', 0]}, {$round: [{$divide: ['$pms', '$rs']}, 1]}, NaN]},
    }},
    {$sort: {year: -1}},
    {$project: {
        'week': 0, 'month': 0, 'day': 0,
    }},
    {$limit: 200},
])
