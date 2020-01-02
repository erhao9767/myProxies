import random

import redis

import setting


class BaseProxyPool(object):
    proxies = {}
    shadow_proxies = {}

    def get_all(self, protocol):
        return self.proxies.get(protocol)

    def get_one(self, protocol):
        return random.choice(self.proxies.get(protocol))

    def get_shadow_all(self, protocol):
        return self.shadow_proxies.get(protocol)

    def get_shadow_one(self, protocol):
        return random.choice(self.shadow_proxies.get(protocol))


class RedisProxyPool(BaseProxyPool):

    def __init__(self):
        self.conn = None
        self._redis_db()

    def _redis_db(self):
        self.conn = redis.Redis(host=setting.REDIS_HOST, port=setting.REDIS_PROT, password=setting.REDIS_PWD)
        self.proxies['http'] = [str(i, 'utf8') for i in self.conn.smembers('http')]
        self.proxies['https'] = [str(i, 'utf8') for i in self.conn.smembers('https')]
        self.shadow_proxies['http'] = [str(i, 'utf8') for i in self.conn.smembers('shadow_http')]
        self.shadow_proxies['https'] = [str(i, 'utf8') for i in self.conn.smembers('shadow_https')]

    def add_proxy(self, protocol, iport):
        self.conn.sadd(protocol, iport)

    def add_shadow_proxy(self, protocol, iport):
        if protocol == "http":
            self.conn.sadd("shadow_http", iport)
            return
        self.conn.sadd("shadow_https", iport)


proxies = RedisProxyPool()
