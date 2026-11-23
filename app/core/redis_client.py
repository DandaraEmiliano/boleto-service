from os import getenv

from redis import Redis

redis_client = Redis.from_url(
    getenv("REDIS_URL", "redis://localhost:6379/0"),
    socket_connect_timeout=2,
    socket_timeout=5,
)
