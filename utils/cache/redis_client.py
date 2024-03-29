from django.conf import settings
import redis


class RedisClient:
    conn = None

    @classmethod
    def get_connection(cls):
        # there is only one connection
        if cls.conn:
            return cls.conn
        cls.conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )
        return cls.conn

    @classmethod
    def clear(cls):
        """
        Clear all keys in cache, for testing purpose
        """
        if not settings.TESTING:
            return Exception("You can not flush Redis in production environment")
        conn = cls.get_connection()
        conn.flushdb()