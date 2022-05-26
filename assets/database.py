import redis
import os
import urllib.request as url
from datetime import datetime
from random import *
from pathlib import Path
from time import sleep


host1, port1 = '10.255.237.221', '6379' # Connessione della scuola
r = redis.Redis(host=host1, port=port1, password='1357642rVi0', socket_timeout=5)

CHANNEL_NAME = 'bigShot_bonus'
pubsub = r.pubsub()
try:
    pubsub.subscribe(CHANNEL_NAME)
except:
    pass

SET_EASY = 'bigShot_scores_EASY'
SET_NORMAL = 'bigShot_scores_NORMAL'
SET_HARD = 'bigShot_scores_HARD'

def check_connection(host='http://google.com'):
    '''Controlla la connessione cercando di aprire un sito'''

    try:
        url.urlopen(host)
        return True
    except:
        return False

def receive_bonus(amount=30):
    bonus = False
    try:
        message = pubsub.get_message()['data']
        if message != 1:
            bonus = True
    except:
        pass
    
    return amount if bonus else 0

def generate_id():
    '''Genera un id basandoti sulla data e l\'ora'''

    return datetime.now().strftime("%d%m%Y%H%M%S%f")

def id_file(path : str, id : str):
    '''Genera un file dove salvare l\'id'''

    if not os.path.exists(str(Path(path).parent)):
        os.makedirs(str(Path(path).parent))
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(id)

def save_score(set : str, id : str, player_name : str, score : int):
    '''Salva il punteggio'''

    # Controlla se la connessione funziona. Se no ritorna None
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

def get_score(set : str, id : str, with_rank=False):
    '''Ritorna un punteggio in base all'id'''

    # Controlla se la connessione funziona. Se no ritorna 0
    if check_connection():
        try:
            r.ping()
        except:
            if with_rank:
                return (0, 0)
            return 0
    else:
        if with_rank:
            return (0, 0)
        return 0

    score = None
    rank = None

    # Cerca un membro del set che coincide con l'id
    scores = r.zrange(set, 0, -1)
    if len(scores) <= 0:
        if with_rank:
            return (0, 0)
        return 0
    
    for _i in scores:
        i = str(_i)[1:].replace('\'', '')
        _, _id = i.split('_')
        if str(_id) == str(id):
            score = r.zscore(set, i)
            rank = r.zrevrank(set, i) + 1
            if with_rank:
                return (int(score), rank)
            else:
                return int(score)

    # Se non trova niente ritorna 0
    if score == None:
        if with_rank:
            return (0, r.zcard(set) + 1)
        else:
            return 0

def get_leaderboard(set : str, players_number=10):
    '''Ritorna la classifica dei giocatori'''

    # Controlla se la connessione funziona. Se no ritorna una lista vuota
    if check_connection():
        try:
            r.ping()
        except:
            return []
    else:
        return []

    temp_leaderboard = r.zrange(set, 0, -1, withscores=True)[::-1][:players_number]
    leaderboard = []
    for player in temp_leaderboard:
        name = str(player[0])[1:].replace('\'', '').split('_')[0]
        score = int(player[1])
        leaderboard.append((name, score))
    return leaderboard

if __name__ == '__main__':

    loop = 0
    while loop < 30:
        print(receive_bonus())

        loop += 1
        sleep(5)