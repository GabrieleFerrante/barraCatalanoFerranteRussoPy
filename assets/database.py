import redis
import os
import urllib.request as url
from datetime import datetime
from random import *
from pathlib import Path

r = redis.Redis(host='93.145.175.242', port=63213, password='1357642rVi0', socket_timeout=5)

SET_EASY = 'bigShot_scores_EASY'
SET_NORMAL = 'bigShot_scores_NORMAL'
SET_HARD = 'bigShot_scores_HARD'

def check_connection(host='http://google.com'):
    try:
        url.urlopen(host)
        return True
    except:
        return False

def generate_id():
    return datetime.now().strftime("%d%m%Y%H%M%S%f")

def id_file(path : str, id : str):
    if not os.path.exists(str(Path(path).parent)):
        os.makedirs(str(Path(path).parent))
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(id)

def save_score(set : str, id : str, player_name : str, score : int):
    if check_connection():
        try:
            r.ping()
        except:
            return
    else:
        return

    member = player_name + '_' + id
    for _i in r.zrange(set, 0, -1):
        i = str(_i)[1:].replace('\'', '')
        _name, _id = i.split('_')
        if id == _id and player_name != _name:
            r.zrem(set, i)
    r.zadd(set, {member: score})

def get_score(set : str, id : str, player_name : str):
    if check_connection():
        try:
            r.ping()
        except:
            return 0
    else:
        return 0
    
    member = player_name + '_' + id
    score = r.zscore(set, member)
    if score != None:
        return int(score)
    else:
        return 0

if __name__ == '__main__':
    r.ping()