import redis
import os
import urllib.request as url
from datetime import datetime
from random import *
from pathlib import Path


host1, port1 = '10.255.237.221', '6379'
host2, port2 = '93.145.175.242', '63213'
r = redis.Redis(host=host1, port=port1, password='1357642rVi0', socket_timeout=5)

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

    # Controlla se la connessione funziona. Se no non fare niente
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

def get_score(set : str, id : str, rank=False):
    '''Ritorna un punteggio in base all'id'''

    # Controlla se la connessione funziona. Se no ritorna 0
    if check_connection():
        try:
            r.ping()
        except:
            return 0
    else:
        return 0

    score = None
    rank = None

    # Cerca un membro del set che coincide con l'id
    scores = r.zrange(set, 0, -1)
    if len(scores) <= 0:
        if not rank:
            return (0, r.zcard(set) + 2)
        return 0
        
    for _i in scores:
        i = str(_i)[1:].replace('\'', '')
        _, _id = i.split('_')
        if _id == id:
            score = r.zscore(set, i)
            rank = r.zrevrank(set, i) + 1

    # Se non trova niente ritorna 0
    if score != None:
        if not rank:
            return (int(score), rank)
        else:
            return int(score)
    else:
        if not rank:
            return (0, r.zcard(set) + 2)
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

    for j in range(100):
        save_score(SET_EASY, generate_id(), 'player' + str(j), round(randint(0, 1000), -1))
        save_score(SET_NORMAL, generate_id(), 'player' + str(j), round(randint(0, 1000), -1))
        save_score(SET_HARD, generate_id(), 'player' + str(j), round(randint(0, 1000), -1))
