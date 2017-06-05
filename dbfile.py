from os import environ, path

SWITCHES = ['a', 'b']


def get_filename(switch, db_dir=environ.get('GSB_DB_DIR', '/tmp')):
    return path.join(db_dir, 'gsb_v4.' + switch + '.db')


def get_switch_info(switch, db_dir=environ.get('GSB_DB_DIR', '/tmp')):
    fname = get_filename(switch, db_dir)
    try:
        return {'switch': switch, 'name': fname, 'mtime': path.getmtime(fname), 'ctime': path.getctime(fname)}
    except:
        return {'switch': switch, 'name': fname, 'mtime': None, 'ctime': None}


# returns list of dicts of valid DB files
def get_alternatives(db_dir=environ.get('GSB_DB_DIR', '/tmp')):
    alternatives = sorted([get_switch_info(x, db_dir) for x in SWITCHES], key=lambda e: e['ctime'], reverse=True)
    for i in range(len(alternatives)):
        if i == 0 and alternatives[i]['ctime']:
            alternatives[i]['active'] = True
        else:
            alternatives[i]['active'] = False
    return alternatives


# return path of active DB file
def get_active(db_dir=environ.get('GSB_DB_DIR', '/tmp')):
    alternatives = filter(lambda e: e['active'] == True, get_alternatives(db_dir))
    if len(alternatives) == 0:
        return None
    else:
        return alternatives[0]


# return path of inactive DB file
def get_inactive(db_dir=environ.get('GSB_DB_DIR', '/tmp')):
    return filter(lambda e: e['active'] == False, get_alternatives(db_dir))[0]
