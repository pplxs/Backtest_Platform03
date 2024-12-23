import json

from django_redis import get_redis_connection

redis_connection = get_redis_connection()

HSET_NAME = "RESOURCE_INFO"


# 系统信息管理
class SystemInfoManager():
    @classmethod
    def set(cls, tag_name, data):
        redis_connection.hset(HSET_NAME, tag_name, json.dumps(data))

    @classmethod
    def get_all(cls):
        return {k.decode(): json.loads(v.decode()) for k, v in redis_connection.hgetall(HSET_NAME).items()}
