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

    def _valid_proxy(self, protocol, shadow):
        if protocol not in ['http', 'https']:
            raise RuntimeError("代理传输协议只能是http或https")
        if shadow:
            protocol = 'shadow_' + protocol
        return protocol

    def add_proxy(self, protocol, host_port, shadow=None):
        valid_key = self._valid_proxy(protocol, shadow)
        self.conn.sadd(valid_key, host_port)

    def remove_proxy(self, protocol, host_port, shadow=None):
        valid_key = self._valid_proxy(protocol, shadow)
        self.conn.srem(valid_key, host_port)


proxies = RedisProxyPool()
