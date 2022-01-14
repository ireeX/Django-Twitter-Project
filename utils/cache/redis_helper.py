from utils.cache.redis_client import RedisClient
from utils.cache.redis_serializers import DjangoModelSerializer
from django.conf import settings

class RedisHelper:

    @classmethod
    def _load_objects_to_cache(cls, key, objects):
        conn = RedisClient.get_connection()

        serialized_list = []
        # Limit the Redis cache size to avoid large memory usage
        # If data beyond the limit, retrieve from DB
        for obj in objects[:settings.REDIS_LIST_LENGTH_LIMIT]:
            serialized_data = DjangoModelSerializer.serialize(obj)
            serialized_list.append(serialized_data)

        if serialized_list:
            conn.rpush(key, *serialized_list)
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)

    @classmethod
    def load_objects(cls, key, queryset):
        conn = RedisClient.get_connection()
        # cache hit
        if conn.exists(key):
            serialized_list = conn.lrange(key, 0, -1)
            objects = []
            for serialized_data in serialized_list:
                deserialized_obj = DjangoModelSerializer.deserialize(serialized_data)
                objects.append(deserialized_obj)
            return objects
        # cache miss
        cls._load_objects_to_cache(key, queryset)
        return list(queryset)

    @classmethod
    def push_object(cls, key, obj, queryset):
        conn = RedisClient.get_connection()
        # cache miss
        if not conn.exists(key):
            cls._load_objects_to_cache(key, queryset)
            return
        # cache hit
        serialized_data = DjangoModelSerializer.serialize(obj)
        """
        A list is needed to maintain tweets by timeline.
        This is the reason for using Redis to cache tweets.
        """
        conn.lpush(key, serialized_data)
        conn.ltrim(key, 0, settings.REDIS_LIST_LENGTH_LIMIT - 1)