import redis
from time import sleep

host1, port1 = '10.255.237.221', '6379' # Connessione della scuola
r = redis.Redis(host=host1, port=port1, password='1357642rVi0', socket_timeout=5)

CHANNEL_NAME = 'bigShot_bonus'
wait_time = 300
msg = 'Sent bonus'

while True:
    r.publish(CHANNEL_NAME, msg)
    print(msg)
    sleep(wait_time)