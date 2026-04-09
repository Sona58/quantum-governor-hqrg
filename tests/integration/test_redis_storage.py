# -*- coding: utf-8 -*-

import redis

def test_redis_increment():
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.set('user:123:credits', 100)
    r.decrby('user:123:credits', 5)
    
    new_balance = int(r.get('user:123:credits'))
    assert new_balance == 95